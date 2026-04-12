"""
Groq API Service
Handles all LLM interactions using Groq (primary provider).
Mirrors the GeminiService interface so it can be swapped in transparently.
"""

import os
import json
import re
from typing import Dict, List, Any, Optional
from groq import Groq
from dotenv import load_dotenv

from backend.integrate.schema_mapper import map_llm_to_schema, DatasetSchema, schema_to_dict
from backend.schema_mapper import schema_mapper
from backend.data_filter import data_filter
from backend.performance_comparator import performance_comparator
from backend.data_post_processor import data_post_processor

load_dotenv()


class GroqService:
    """Primary LLM service using Groq API (very generous free tier)."""

    def __init__(self):
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key or api_key == "your_groq_api_key_here":
            raise ValueError(
                "GROQ_API_KEY not found in environment variables. "
                "Get a free key from https://console.groq.com/keys"
            )
        self.client = Groq(api_key=api_key)
        # Best free model on Groq — 14 400 req/day, 6 000 tokens/min
        self.model_name = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _chat(self, prompt: str, max_tokens: int = 8192) -> str:
        """Send a single user message and return the assistant reply text."""
        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=max_tokens,
        )
        return response.choices[0].message.content

    def _extract_json_from_response(self, text: str) -> List[Dict[str, Any]]:
        cleaned = re.sub(r'```json\s*', '', text)
        cleaned = re.sub(r'```\s*', '', cleaned).strip()
        match = re.search(r'\[.*\]', cleaned, re.DOTALL)
        json_str = match.group(0) if match else cleaned
        data = json.loads(json_str)
        if not isinstance(data, list):
            raise ValueError("Generated data is not a JSON array")
        return data

    def _create_basic_prompt(self, user_query: str) -> str:
        return f"""You are a data generation expert. Generate realistic synthetic data based on the request.

USER REQUEST: {user_query}

Generate realistic data as a valid JSON array. Output ONLY the JSON array, nothing else.

Example format:
[
  {{"id": 1, "name": "John Doe", "email": "john@example.com"}},
  {{"id": 2, "name": "Jane Smith", "email": "jane@example.com"}}
]

Generate the data now:"""

    def _create_enhanced_prompt(self, user_query: str, fields: List[str] = None,
                                rag_context: Dict = None, kaggle_context: Dict = None) -> str:
        parts = [
            "You are a data generation expert specialized in creating realistic, high-quality synthetic data.",
            "",
            f"USER REQUEST: {user_query}",
            "",
        ]
        if kaggle_context:
            parts.append("=== REFERENCE DATA FROM KAGGLE ===")
            if kaggle_context.get("schema"):
                parts.append(f"Schema: {json.dumps(kaggle_context['schema'], indent=2)}")
            if kaggle_context.get("samples"):
                parts.append(f"Sample Data: {json.dumps(kaggle_context['samples'][:3], indent=2)}")
            parts.append("")
        if rag_context and isinstance(rag_context, dict) and rag_context.get("context"):
            parts.append("=== CONTEXT FROM KNOWLEDGE BASE ===")
            for ctx in rag_context["context"]:
                parts.append(f"- {ctx}")
            parts.append("")
        if fields:
            relationship_prompt = schema_mapper.generate_relationship_prompt(fields)
            parts.append(relationship_prompt)
        parts.extend([
            "=== GENERATION INSTRUCTIONS (CRITICAL) ===",
            "1. id fields: unique sequential integers",
            "2. age: integer 18-70",
            "3. price/salary: decimal numbers",
            "4. email: derived from person name (first.last@domain.com)",
            "5. phone: +1-XXX-XXX-XXXX",
            "6. date: ISO format YYYY-MM-DD",
            "7. ALL id and email fields MUST be unique",
            "8. No null or empty values",
            "",
            "OUTPUT FORMAT: ONLY a valid JSON array, no markdown, no explanations.",
            "",
            "Generate the requested data now:",
        ])
        return "\n".join(parts)

    # ------------------------------------------------------------------
    # Public API (mirrors GeminiService)
    # ------------------------------------------------------------------

    def _extract_fields_from_query(self, query: str) -> List[str]:
        common = [
            "id", "name", "first_name", "last_name", "email", "phone",
            "address", "city", "age", "salary", "department", "date",
            "price", "category", "status",
        ]
        q = query.lower()
        found = [f for f in common if f in q or f.replace("_", " ") in q]
        return found or ["id", "name"]

    def _extract_fields_with_llm(self, query: str) -> Dict[str, Any]:
        try:
            prompt = f"""You are a data schema expert. Extract a field list for this data generation request.

USER REQUEST: {query}

Respond ONLY with valid JSON:
{{
  "entity_type": "string",
  "record_count": 10,
  "fields": [
    {{"name": "field_name", "type": "string|integer|float|boolean|date|email|phone",
      "source": "explicit|inferred|domain_standard", "is_unique": false, "description": "..."}}
  ]
}}"""
            raw = self._chat(prompt, max_tokens=1024)
            cleaned = re.sub(r'```json\s*', '', raw)
            cleaned = re.sub(r'```\s*', '', cleaned).strip()
            analysis = json.loads(cleaned)
            field_names = [f["name"] for f in analysis.get("fields", [])]
            return {"success": True, "fields": field_names, "detailed_analysis": analysis, "method": "llm"}
        except Exception as e:
            fallback = self._extract_fields_from_query(query)
            return {"success": False, "fields": fallback, "error": str(e), "method": "fallback"}

    async def generate_data_normal(self, user_query: str) -> Dict[str, Any]:
        try:
            start_time = performance_comparator.start_timer()
            prompt = self._create_basic_prompt(user_query)
            response_text = self._chat(prompt)
            response_time = performance_comparator.stop_timer(start_time)

            data = self._extract_json_from_response(response_text)
            schema = {}
            unique_fields = []
            if data:
                for key, value in data[0].items():
                    schema[key] = type(value).__name__
                    if "id" in key.lower():
                        unique_fields.append(key)

            metrics = performance_comparator.record_metrics(
                mode="normal", query=user_query, response_time_ms=response_time,
                data=data, expected_schema=schema, unique_fields=unique_fields
            )
            validation = data_filter.validate_data(data)
            return {
                "success": True, "mode": "normal", "data": data,
                "record_count": len(data), "schema": schema, "query": user_query,
                "metrics": metrics.to_dict(), "validation": validation,
            }
        except Exception as e:
            return {"success": False, "mode": "normal", "error": str(e), "query": user_query}

    async def generate_data_enhanced(self, user_query: str,
                                     rag_context: Dict = None,
                                     kaggle_context: Dict = None,
                                     use_llm_extraction: bool = True) -> Dict[str, Any]:
        try:
            start_time = performance_comparator.start_timer()
            if use_llm_extraction:
                extraction_result = self._extract_fields_with_llm(user_query)
                fields = extraction_result["fields"]
                field_analysis = extraction_result.get("detailed_analysis", {})
            else:
                fields = self._extract_fields_from_query(user_query)
                field_analysis = None
                extraction_result = {"method": "pattern_matching"}

            prompt = self._create_enhanced_prompt(user_query, fields=fields,
                                                  rag_context=rag_context,
                                                  kaggle_context=kaggle_context)
            response_text = self._chat(prompt)
            response_time = performance_comparator.stop_timer(start_time)

            data = self._extract_json_from_response(response_text)
            data = data_post_processor.process(data)

            schema = {}
            unique_fields = []
            if data:
                for key, value in data[0].items():
                    schema[key] = type(value).__name__
                    if "id" in key.lower():
                        unique_fields.append(key)

            schema_analysis = schema_mapper.analyze_schema(list(schema.keys()))
            relationships = [{"type": "uniqueness", "field": f} for f in unique_fields]

            metrics = performance_comparator.record_metrics(
                mode="enhanced", query=user_query, response_time_ms=response_time,
                data=data, expected_schema=schema, relationships=relationships,
                unique_fields=unique_fields
            )
            validation = data_filter.validate_data(data)

            result = {
                "success": True, "mode": "enhanced", "data": data,
                "record_count": len(data), "schema": schema,
                "schema_analysis": schema_analysis, "query": user_query,
                "metrics": metrics.to_dict(), "validation": validation,
                "extraction_method": extraction_result.get("method", "pattern_matching"),
            }
            if field_analysis:
                result["field_analysis"] = field_analysis
            return result
        except Exception as e:
            return {"success": False, "mode": "enhanced", "error": str(e), "query": user_query}

    async def generate_data(self, user_query: str, enhanced: bool = True,
                            rag_context: Dict = None, kaggle_context: Dict = None) -> Dict[str, Any]:
        if enhanced:
            return await self.generate_data_enhanced(user_query, rag_context, kaggle_context)
        return await self.generate_data_normal(user_query)

    async def generate_schema_with_validation(self, user_query: str,
                                              rag_context: Dict = None,
                                              kaggle_context: Dict = None) -> Dict[str, Any]:
        try:
            schema_extraction_prompt = f"""You are a data schema expert. Create a JSON schema for this request.

USER REQUEST: {user_query}

OUTPUT FORMAT (JSON only, no markdown):
{{
  "dataset_name": "descriptive_name",
  "rows": 10,
  "description": "Brief description",
  "columns": [
    {{
      "name": "column_name",
      "type": "int|float|string|categorical|date|boolean",
      "description": "What this column represents",
      "range": [min, max],
      "values": ["val1", "val2"],
      "nullable": false,
      "required": true
    }}
  ]
}}

Rules:
- Always include an id field
- Use snake_case for column names
- For categorical fields include "values" array
- For numeric fields include "range" [min, max]
- Default to 10 rows if not specified

Now analyze: {user_query}

Respond ONLY with valid JSON."""

            if kaggle_context:
                schema_extraction_prompt += f"\n\nKAGGLE REFERENCE:\n{json.dumps(kaggle_context, indent=2)}"
            if rag_context:
                schema_extraction_prompt += f"\n\nKNOWLEDGE BASE:\n{json.dumps(rag_context, indent=2)}"

            print("🤖 Step 1: Groq LLM extracting schema...")
            raw = self._chat(schema_extraction_prompt, max_tokens=2048)

            cleaned = re.sub(r'```json\s*', '', raw)
            cleaned = re.sub(r'```\s*', '', cleaned).strip()
            llm_schema_output = json.loads(cleaned)

            print(f"✅ Groq extracted schema: {llm_schema_output.get('dataset_name', 'unknown')}")

            print("🔍 Step 2: Validating schema with schema_mapper...")
            validated_schema = map_llm_to_schema(llm_schema_output)
            schema_dict = schema_to_dict(validated_schema)

            print(f"✅ Schema validated — {len(validated_schema.columns)} columns")

            return {
                "success": True,
                "schema": schema_dict,
                "validated_schema_object": validated_schema,
                "llm_raw_output": llm_schema_output,
                "metadata": {
                    "dataset_name": validated_schema.dataset_name,
                    "rows": validated_schema.rows,
                    "column_count": len(validated_schema.columns),
                    "version": validated_schema.version,
                    "created_at": validated_schema.created_at,
                    "source": validated_schema.source,
                },
                "query": user_query,
                "flow": "groq_extraction → schema_validation",
                "provider": "groq",
            }
        except json.JSONDecodeError as e:
            return {"success": False, "error": f"Failed to parse Groq schema output: {str(e)}", "query": user_query}
        except Exception as e:
            return {"success": False, "error": f"Schema generation failed: {str(e)}", "query": user_query}

    async def compare_modes(self, user_query: str,
                            rag_context: Dict = None,
                            kaggle_context: Dict = None) -> Dict[str, Any]:
        normal_result = await self.generate_data_normal(user_query)
        enhanced_result = await self.generate_data_enhanced(user_query, rag_context, kaggle_context)
        comparison = None
        if normal_result.get("success") and enhanced_result.get("success"):
            from backend.performance_comparator import GenerationMetrics
            normal_metrics = GenerationMetrics(**normal_result["metrics"])
            enhanced_metrics = GenerationMetrics(**enhanced_result["metrics"])
            comparison = performance_comparator.compare_modes(normal_metrics, enhanced_metrics)
        return {
            "success": True,
            "normal": normal_result,
            "enhanced": enhanced_result,
            "comparison": comparison,
        }

    def analyze_query(self, query: str) -> Dict[str, Any]:
        try:
            result = self._extract_fields_with_llm(query)
            return {"success": True, "analysis": result}
        except Exception as e:
            return {"success": False, "error": str(e)}
