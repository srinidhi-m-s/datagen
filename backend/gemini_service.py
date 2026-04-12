"""
Gemini API Service
Handles all interactions with Google's Gemini API for data generation
Now with Schema Mapping, Filtering, and Performance Comparison
"""

import os
import json
import re
from typing import Dict, List, Any, Optional
from google import genai
from google.genai import types
from dotenv import load_dotenv

# Import schema validation from integrate module (for the new strict Pydantic validation)
from backend.integrate.schema_mapper import map_llm_to_schema, DatasetSchema, schema_to_dict

# Import the old schema mapper for semantic relationship analysis
from backend.schema_mapper import schema_mapper
from backend.data_filter import data_filter
from backend.performance_comparator import performance_comparator
from backend.data_post_processor import data_post_processor

# Load environment variables
load_dotenv()

class GeminiService:
    """Service class for Gemini API interactions"""
    
    def __init__(self):
        """Initialize Gemini API with configuration"""
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key or api_key == "your_gemini_api_key_here":
            raise ValueError(
                "GEMINI_API_KEY not found in environment variables. "
                "Please set it in your .env file. "
                "Get your free API key from: https://makersuite.google.com/app/apikey"
            )
        
        # Initialize the new Gemini client
        self.client = genai.Client(api_key=api_key)
        
        # Model configuration
        self.model_name = os.getenv('GEMINI_MODEL', 'gemini-2.5-flash')  # Configurable model (default gemini-2.5-flash)
        
        self.generation_config = types.GenerateContentConfig(
            temperature=0.7,  # Balanced creativity and consistency
            top_p=0.95,
            top_k=40,
            max_output_tokens=8192,
        )
    
    def _create_basic_prompt(self, user_query: str) -> str:
        """
        Create a basic prompt WITHOUT schema mapping (Normal LLM mode)
        
        Args:
            user_query: User's natural language query
            
        Returns:
            Basic prompt for Gemini API
        """
        prompt = f"""You are a data generation expert. Generate realistic synthetic data based on the request.

USER REQUEST: {user_query}

Generate realistic data as a valid JSON array. Output ONLY the JSON array, nothing else.

Example format:
[
  {{"id": 1, "name": "John Doe", "email": "john@example.com"}},
  {{"id": 2, "name": "Jane Smith", "email": "jane@example.com"}}
]

Generate the data now:"""
        
        return prompt
    
    def _create_enhanced_prompt(self, user_query: str, fields: List[str] = None, 
                                 rag_context: Dict = None, kaggle_context: Dict = None) -> str:
        """
        Create an enhanced prompt WITH schema mapping, RAG context, etc. (Enhanced LLM mode)
        
        Args:
            user_query: User's natural language query
            fields: List of field names to generate
            rag_context: Context from RAG system
            kaggle_context: Context from Kaggle datasets
            
        Returns:
            Enhanced prompt for Gemini API
        """
        prompt_parts = [
            "You are a data generation expert specialized in creating realistic, high-quality synthetic data.",
            "",
            f"USER REQUEST: {user_query}",
            ""
        ]
        
        # Add Kaggle context if available
        if kaggle_context:
            prompt_parts.append("=== REFERENCE DATA FROM KAGGLE ===")
            if kaggle_context.get("schema"):
                prompt_parts.append(f"Schema: {json.dumps(kaggle_context['schema'], indent=2)}")
            if kaggle_context.get("samples"):
                prompt_parts.append(f"Sample Data: {json.dumps(kaggle_context['samples'][:3], indent=2)}")
            if kaggle_context.get("patterns"):
                prompt_parts.append(f"Patterns: {json.dumps(kaggle_context['patterns'], indent=2)}")
            prompt_parts.append("")
        
        # Add RAG context if available
        if rag_context:
            prompt_parts.append("=== CONTEXT FROM KNOWLEDGE BASE ===")
            if isinstance(rag_context, dict) and rag_context.get("context"):
                for ctx in rag_context["context"]:
                    prompt_parts.append(f"- {ctx}")
            prompt_parts.append("")
        
        # Add schema relationship mapping
        if fields:
            relationship_prompt = schema_mapper.generate_relationship_prompt(fields)
            prompt_parts.append(relationship_prompt)
        
        # Add generation instructions
        prompt_parts.extend([
            "=== GENERATION INSTRUCTIONS (CRITICAL) ===",
            "You MUST follow these rules strictly:",
            "",
            "1. DATA TYPES:",
            "   - id fields: Use unique sequential integers (1, 2, 3...)",
            "   - age: Integer between 18 and 70",
            "   - price/amount/salary: Decimal numbers (e.g., 49.99, 75000.00)",
            "   - email: Must contain parts of the person's name (e.g., john.smith@gmail.com for John Smith)",
            "   - phone: Format +1-XXX-XXX-XXXX",
            "   - date: ISO format YYYY-MM-DD",
            "",
            "2. UNIQUENESS:",
            "   - ALL id fields MUST be unique",
            "   - ALL email addresses MUST be unique",
            "   - Phone numbers SHOULD be unique",
            "",
            "3. RELATIONSHIPS:",
            "   - Email addresses MUST be derived from person names (first.last@domain.com)",
            "   - Higher experience = higher salary (positive correlation)",
            "   - Age and experience should be logically consistent",
            "",
            "4. DATA VARIETY:",
            "   - Use diverse values for categorical fields",
            "   - Vary names, cities, departments across records",
            "   - Include realistic distributions (not all same values)",
            "",
            "5. NO NULL VALUES:",
            "   - Every field must have a valid value",
            "   - Do not use null, None, or empty strings",
            "",
            "OUTPUT FORMAT:",
            "- Output ONLY a valid JSON array of objects",
            "- No markdown code blocks, no explanations, no additional text",
            "",
            "Example of CORRECT output:",
            '[{"id": 1, "name": "John Smith", "email": "john.smith@gmail.com", "age": 28, "salary": 65000.00}]',
            "",
            "Generate the requested data now:"
        ])
        
        return "\n".join(prompt_parts)
    
    def _extract_json_from_response(self, response_text: str) -> List[Dict[str, Any]]:
        """
        Extract and parse JSON from Gemini's response
        
        Args:
            response_text: Raw response from Gemini API
            
        Returns:
            Parsed JSON data as list of dictionaries
        """
        # Remove markdown code blocks if present
        cleaned = re.sub(r'```json\s*', '', response_text)
        cleaned = re.sub(r'```\s*', '', cleaned)
        cleaned = cleaned.strip()
        
        # Try to find JSON array in the response
        json_match = re.search(r'\[.*\]', cleaned, re.DOTALL)
        if json_match:
            json_str = json_match.group(0)
        else:
            json_str = cleaned
        
        try:
            data = json.loads(json_str)
            if not isinstance(data, list):
                raise ValueError("Generated data is not a JSON array")
            return data
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse JSON from response: {str(e)}\nResponse: {cleaned[:500]}")
    
    def _extract_fields_with_llm(self, query: str) -> Dict[str, Any]:
        """
        Use LLM to intelligently extract comprehensive field list from user query
        This provides:
        - Domain-specific fields
        - Contextual field inference
        - Comprehensive field lists
        - Field type suggestions
        
        Args:
            query: User's natural language query
            
        Returns:
            Dictionary with extracted fields and metadata
        """
        try:
            extraction_prompt = f"""You are a data schema expert. Analyze this data generation request and extract a comprehensive list of fields.

USER REQUEST: {query}

Your task:
1. Identify the domain/entity type (e.g., employees, customers, products, transactions)
2. Extract explicitly mentioned fields
3. Infer relevant fields based on the domain that weren't explicitly mentioned
4. Suggest appropriate data types for each field
5. Identify which fields should be unique identifiers

Provide a JSON response with this structure:
{{
  "entity_type": "string (e.g., 'employee', 'customer', 'product')",
  "record_count": number (default 10 if not specified),
  "fields": [
    {{
      "name": "field_name",
      "type": "string|integer|float|boolean|date|email|phone",
      "source": "explicit|inferred|domain_standard",
      "is_unique": boolean,
      "description": "brief description"
    }}
  ]
}}

IMPORTANT RULES:
- Include standard fields for the domain (e.g., employees always need id, name, email)
- Infer related fields (e.g., if "name" is mentioned, include first_name, last_name, or full_name)
- For contact info, include email and phone
- For financial data, include amounts with proper decimal types
- Always include an ID field if not explicitly mentioned
- Use snake_case for field names

Example for "Generate employee data":
{{
  "entity_type": "employee",
  "record_count": 10,
  "fields": [
    {{"name": "employee_id", "type": "integer", "source": "domain_standard", "is_unique": true, "description": "Unique employee identifier"}},
    {{"name": "first_name", "type": "string", "source": "inferred", "is_unique": false, "description": "Employee first name"}},
    {{"name": "last_name", "type": "string", "source": "inferred", "is_unique": false, "description": "Employee last name"}},
    {{"name": "email", "type": "email", "source": "domain_standard", "is_unique": true, "description": "Employee email address"}},
    {{"name": "phone", "type": "phone", "source": "domain_standard", "is_unique": false, "description": "Contact phone number"}},
    {{"name": "department", "type": "string", "source": "domain_standard", "is_unique": false, "description": "Department name"}},
    {{"name": "hire_date", "type": "date", "source": "domain_standard", "is_unique": false, "description": "Date of hire"}},
    {{"name": "salary", "type": "float", "source": "domain_standard", "is_unique": false, "description": "Annual salary"}}
  ]
}}

Now analyze this request: {query}

Respond ONLY with valid JSON, no other text."""

            response = self.client.models.generate_content(
                model=self.model_name,
                contents=extraction_prompt,
                config=self.generation_config
            )
            
            # Extract and parse JSON
            cleaned = re.sub(r'```json\s*', '', response.text)
            cleaned = re.sub(r'```\s*', '', cleaned).strip()
            
            analysis = json.loads(cleaned)
            
            # Extract just the field names for backward compatibility
            field_names = [field["name"] for field in analysis.get("fields", [])]
            
            return {
                "success": True,
                "fields": field_names,
                "detailed_analysis": analysis,
                "method": "llm"
            }
            
        except Exception as e:
            # Fallback to pattern matching if LLM extraction fails
            print(f"LLM field extraction failed: {str(e)}, falling back to pattern matching")
            fallback_fields = self._extract_fields_from_query(query)
            return {
                "success": False,
                "fields": fallback_fields,
                "error": str(e),
                "method": "fallback"
            }
    
    def _extract_fields_from_query(self, query: str) -> List[str]:
        """
        Extract field names from user query
        
        Args:
            query: User's natural language query
            
        Returns:
            List of extracted field names
        """
        # Common fields to look for
        common_fields = [
            "id", "name", "first_name", "last_name", "full_name",
            "email", "phone", "address", "city", "state", "country", "zip_code",
            "age", "gender", "birth_date", "date_of_birth",
            "price", "amount", "total", "cost", "salary",
            "quantity", "count", "stock",
            "category", "type", "status", "department",
            "product", "order", "customer", "employee",
            "rating", "score", "review",
            "date", "created_at", "updated_at",
            "description", "title", "sku"
        ]
        
        query_lower = query.lower()
        found_fields = []
        
        for field in common_fields:
            if field in query_lower or field.replace("_", " ") in query_lower:
                found_fields.append(field)
        
        return found_fields if found_fields else ["id", "name"]
    
    async def generate_data_normal(self, user_query: str) -> Dict[str, Any]:
        """
        Generate data using NORMAL mode (basic prompt, no enhancements)
        
        Args:
            user_query: Natural language description of desired data
            
        Returns:
            Dictionary containing generated data and metrics
        """
        try:
            # Start timer
            start_time = performance_comparator.start_timer()
            
            # Create basic prompt
            prompt = self._create_basic_prompt(user_query)
            
            # Generate content
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=self.generation_config
            )
            
            # Stop timer
            response_time = performance_comparator.stop_timer(start_time)
            
            # Extract data
            response_text = response.text
            if not response_text:
                raise ValueError("Empty response from Gemini API")
            
            data = self._extract_json_from_response(response_text)
            
            # Extract schema from data
            schema = {}
            unique_fields = []
            if data and len(data) > 0:
                for key, value in data[0].items():
                    schema[key] = type(value).__name__
                    if "id" in key.lower():
                        unique_fields.append(key)
            
            # Record metrics
            metrics = performance_comparator.record_metrics(
                mode="normal",
                query=user_query,
                response_time_ms=response_time,
                data=data,
                expected_schema=schema,
                unique_fields=unique_fields
            )
            
            # Validate data
            validation = data_filter.validate_data(data)
            
            return {
                "success": True,
                "mode": "normal",
                "data": data,
                "record_count": len(data),
                "schema": schema,
                "query": user_query,
                "metrics": metrics.to_dict(),
                "validation": validation
            }
            
        except Exception as e:
            return {
                "success": False,
                "mode": "normal",
                "error": str(e),
                "query": user_query
            }
    
    async def generate_data_enhanced(self, user_query: str, 
                                     rag_context: Dict = None,
                                     kaggle_context: Dict = None,
                                     use_llm_extraction: bool = True) -> Dict[str, Any]:
        """
        Generate data using ENHANCED mode (with schema mapping, RAG, filtering)
        
        Args:
            user_query: Natural language description of desired data
            rag_context: Context from RAG system
            kaggle_context: Context from Kaggle datasets
            use_llm_extraction: Whether to use LLM for field extraction (default True)
            
        Returns:
            Dictionary containing generated data and metrics
        """
        try:
            # Start timer
            start_time = performance_comparator.start_timer()
            
            # Extract fields from query using LLM or pattern matching
            if use_llm_extraction:
                extraction_result = self._extract_fields_with_llm(user_query)
                fields = extraction_result["fields"]
                field_analysis = extraction_result.get("detailed_analysis", {})
            else:
                fields = self._extract_fields_from_query(user_query)
                field_analysis = None
            
            # Create enhanced prompt
            prompt = self._create_enhanced_prompt(
                user_query, 
                fields=fields,
                rag_context=rag_context,
                kaggle_context=kaggle_context
            )
            
            # Generate content
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=self.generation_config
            )
            
            # Stop timer
            response_time = performance_comparator.stop_timer(start_time)
            
            # Extract data
            response_text = response.text
            if not response_text:
                raise ValueError("Empty response from Gemini API")
            
            data = self._extract_json_from_response(response_text)
            
            # ===== POST-PROCESSING TO IMPROVE QUALITY SCORES =====
            # This is the key enhancement that improves data quality
            data = data_post_processor.process(data)
            
            # Extract schema from data
            schema = {}
            unique_fields = []
            if data and len(data) > 0:
                for key, value in data[0].items():
                    schema[key] = type(value).__name__
                    if "id" in key.lower():
                        unique_fields.append(key)
            
            # Analyze schema relationships
            schema_analysis = schema_mapper.analyze_schema(list(schema.keys()))
            
            # Build relationships for metrics
            relationships = [
                {"type": "uniqueness", "field": f} for f in unique_fields
            ]
            # Add email-name relationship if both exist
            if "email" in [f.lower() for f in schema.keys()] and "name" in [f.lower() for f in schema.keys()]:
                relationships.append({
                    "type": "email_name_match",
                    "name_field": "name",
                    "email_field": "email"
                })
            
            # Record metrics
            metrics = performance_comparator.record_metrics(
                mode="enhanced",
                query=user_query,
                response_time_ms=response_time,
                data=data,
                expected_schema=schema,
                relationships=relationships,
                unique_fields=unique_fields
            )
            
            # Validate data
            validation = data_filter.validate_data(data)
            
            result = {
                "success": True,
                "mode": "enhanced",
                "data": data,
                "record_count": len(data),
                "schema": schema,
                "schema_analysis": schema_analysis,
                "query": user_query,
                "metrics": metrics.to_dict(),
                "validation": validation,
                "extraction_method": extraction_result.get("method") if use_llm_extraction else "pattern_matching"
            }
            
            # Add LLM field analysis if available
            if field_analysis:
                result["field_analysis"] = field_analysis
            
            return result
            
        except Exception as e:
            return {
                "success": False,
                "mode": "enhanced",
                "error": str(e),
                "query": user_query
            }
    
    async def generate_schema_with_validation(self, user_query: str, 
                                              rag_context: Dict = None,
                                              kaggle_context: Dict = None) -> Dict[str, Any]:
        """
        NEW FLOW: User Query → LLM Schema Extraction → Schema Mapper Validation
        
        This method implements the clean flow:
        1. User provides natural language query
        2. LLM extracts comprehensive schema with semantic understanding
        3. Schema mapper validates and normalizes the schema
        4. Returns perfect, validated schema ready for data generation
        
        Args:
            user_query: Natural language description of desired data
            rag_context: Optional context from RAG system
            kaggle_context: Optional context from Kaggle datasets
            
        Returns:
            Dictionary containing validated schema and metadata
        """
        try:
            # ============================================================
            # STEP 1: LLM SCHEMA EXTRACTION (Semantic Understanding)
            # ============================================================
            schema_extraction_prompt = f"""You are a data schema expert. Analyze this data generation request and create a comprehensive, semantically-aware schema.

USER REQUEST: {user_query}

Your task is to create a complete schema specification that includes:
1. Dataset name (infer from context)
2. Number of rows to generate (default 10 if not specified)
3. Comprehensive list of columns with:
   - Column names (use snake_case)
   - Data types (int, float, string, categorical, date, boolean)
   - Value ranges for numeric fields
   - Allowed values for categorical fields
   - Descriptions explaining the purpose of each field
   - Semantic relationships between fields

SEMANTIC UNDERSTANDING RULES:
- Infer domain-standard fields (e.g., employees need id, name, email, department, salary)
- Understand relationships (e.g., email should derive from name)
- Apply realistic constraints (e.g., age: 18-70, salary: 30000-150000)
- Include correlated fields (e.g., experience correlates with salary)
- Ensure data integrity (unique IDs, valid email formats, etc.)

OUTPUT FORMAT (JSON):
{{
  "dataset_name": "descriptive_name",
  "rows": 10,
  "description": "Brief description of the dataset",
  "columns": [
    {{
      "name": "column_name",
      "type": "int|float|string|categorical|date|boolean",
      "description": "What this column represents",
      "range": [min, max],  // For numeric types (int/float)
      "values": ["val1", "val2"],  // For categorical type
      "nullable": false,
      "required": true
    }}
  ]
}}

EXAMPLE for "Generate employee data with 20 records":
{{
  "dataset_name": "employee_records",
  "rows": 20,
  "description": "Employee information dataset",
  "columns": [
    {{
      "name": "employee_id",
      "type": "int",
      "description": "Unique employee identifier",
      "range": [1000, 9999],
      "nullable": false,
      "required": true
    }},
    {{
      "name": "first_name",
      "type": "string",
      "description": "Employee first name",
      "nullable": false,
      "required": true
    }},
    {{
      "name": "last_name",
      "type": "string",
      "description": "Employee last name",
      "nullable": false,
      "required": true
    }},
    {{
      "name": "email",
      "type": "string",
      "description": "Employee email (derived from name)",
      "nullable": false,
      "required": true
    }},
    {{
      "name": "department",
      "type": "categorical",
      "description": "Department assignment",
      "values": ["Engineering", "Sales", "Marketing", "HR", "Finance"],
      "nullable": false,
      "required": true
    }},
    {{
      "name": "age",
      "type": "int",
      "description": "Employee age in years",
      "range": [22, 65],
      "nullable": false,
      "required": true
    }},
    {{
      "name": "salary",
      "type": "float",
      "description": "Annual salary in USD",
      "range": [35000.00, 150000.00],
      "nullable": false,
      "required": true
    }},
    {{
      "name": "hire_date",
      "type": "date",
      "description": "Date of hire",
      "nullable": false,
      "required": true
    }},
    {{
      "name": "is_active",
      "type": "boolean",
      "description": "Employment status",
      "nullable": false,
      "required": true
    }}
  ]
}}

Now analyze this request: {user_query}

Respond ONLY with valid JSON matching the format above. Include all relevant fields for the domain."""

            # Add context if available
            if kaggle_context:
                schema_extraction_prompt += f"\n\nKAGGLE REFERENCE:\n{json.dumps(kaggle_context, indent=2)}"
            
            if rag_context:
                schema_extraction_prompt += f"\n\nKNOWLEDGE BASE CONTEXT:\n{json.dumps(rag_context, indent=2)}"
            
            # Call LLM for schema extraction
            print(" Step 1: LLM extracting schema with semantic understanding...")
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=schema_extraction_prompt,
                config=self.generation_config
            )
            
            # Parse LLM response
            cleaned = re.sub(r'```json\s*', '', response.text)
            cleaned = re.sub(r'```\s*', '', cleaned).strip()
            llm_schema_output = json.loads(cleaned)
            
            print(f"✅ LLM extracted schema: {llm_schema_output.get('dataset_name', 'unknown')}")
            print(f"   Columns: {len(llm_schema_output.get('columns', []))}")
            
            # ============================================================
            # STEP 2: SCHEMA MAPPER VALIDATION & NORMALIZATION
            # ============================================================
            print("🔍 Step 2: Validating and normalizing schema with schema_mapper...")
            
            # Pass LLM output to schema mapper for validation
            validated_schema = map_llm_to_schema(llm_schema_output)
            
            print(f"✅ Schema validated successfully!")
            print(f"   Dataset: {validated_schema.dataset_name}")
            print(f"   Rows: {validated_schema.rows}")
            print(f"   Columns: {len(validated_schema.columns)}")
            
            # Convert to dict for JSON serialization
            schema_dict = schema_to_dict(validated_schema)
            
            # ============================================================
            # STEP 3: RETURN VALIDATED SCHEMA
            # ============================================================
            return {
                "success": True,
                "schema": schema_dict,
                "validated_schema_object": validated_schema,  # Pydantic object
                "llm_raw_output": llm_schema_output,  # Original LLM output
                "metadata": {
                    "dataset_name": validated_schema.dataset_name,
                    "rows": validated_schema.rows,
                    "column_count": len(validated_schema.columns),
                    "version": validated_schema.version,
                    "created_at": validated_schema.created_at,
                    "source": validated_schema.source
                },
                "query": user_query,
                "flow": "llm_extraction → schema_validation"
            }
            
        except json.JSONDecodeError as e:
            return {
                "success": False,
                "error": f"Failed to parse LLM schema output: {str(e)}",
                "query": user_query,
                "flow": "llm_extraction → schema_validation"
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Schema generation failed: {str(e)}",
                "query": user_query,
                "flow": "llm_extraction → schema_validation"
            }
    

    async def generate_data(self, user_query: str, enhanced: bool = True,
                           rag_context: Dict = None, kaggle_context: Dict = None) -> Dict[str, Any]:
        """
        Generate synthetic data (main entry point)
        
        Args:
            user_query: Natural language description of desired data
            enhanced: Whether to use enhanced mode (default True)
            rag_context: Context from RAG system
            kaggle_context: Context from Kaggle datasets
            
        Returns:
            Dictionary containing generated data and metadata
        """
        if enhanced:
            return await self.generate_data_enhanced(user_query, rag_context, kaggle_context)
        else:
            return await self.generate_data_normal(user_query)
    
    async def compare_modes(self, user_query: str, 
                           rag_context: Dict = None,
                           kaggle_context: Dict = None) -> Dict[str, Any]:
        """
        Generate data using both modes and compare performance
        
        Args:
            user_query: Natural language description of desired data
            rag_context: Context from RAG system
            kaggle_context: Context from Kaggle datasets
            
        Returns:
            Comparison report with data from both modes
        """
        # Generate with normal mode
        normal_result = await self.generate_data_normal(user_query)
        
        # Generate with enhanced mode
        enhanced_result = await self.generate_data_enhanced(
            user_query, rag_context, kaggle_context
        )
        
        # Compare if both succeeded
        comparison = None
        if normal_result.get("success") and enhanced_result.get("success"):
            from backend.performance_comparator import GenerationMetrics
            
            normal_metrics = GenerationMetrics(**normal_result["metrics"])
            enhanced_metrics = GenerationMetrics(**enhanced_result["metrics"])
            
            comparison = performance_comparator.compare_modes(normal_metrics, enhanced_metrics)
        
        return {
            "success": True,
            "normal_result": normal_result,
            "enhanced_result": enhanced_result,
            "comparison": comparison,
            "statistics": performance_comparator.get_statistics()
        }
    
    def analyze_query(self, user_query: str) -> Dict[str, Any]:
        """
        Analyze user query to extract intent and parameters
        
        Args:
            user_query: User's natural language query
            
        Returns:
            Analysis results including detected entities and intent
        """
        try:
            analysis_prompt = f"""Analyze this data generation request and extract key information:

REQUEST: {user_query}

Provide a JSON response with:
- entity_type: What type of data (e.g., "customers", "products", "transactions")
- record_count: How many records requested (default to 10 if not specified)
- fields: List of field names mentioned or implied
- constraints: Any specific requirements or constraints

Respond ONLY with valid JSON, no other text."""

            response = self.client.models.generate_content(
                model=self.model_name,
                contents=analysis_prompt,
                config=self.generation_config
            )
            
            # Extract and parse JSON
            cleaned = re.sub(r'```json\s*', '', response.text)
            cleaned = re.sub(r'```\s*', '', cleaned).strip()
            
            analysis = json.loads(cleaned)
            return {
                "success": True,
                "analysis": analysis
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }


# Create a singleton instance
gemini_service = GeminiService()
