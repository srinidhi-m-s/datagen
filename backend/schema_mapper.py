"""
Schema Relationship Mapping Service
Handles semantic relationships between data fields
"""

from typing import Dict, List, Any, Optional
import json

class SchemaRelationshipMapper:
    """Maps semantic relationships between schema fields"""
    
    def __init__(self):
        # Predefined semantic relationships
        self.relationship_rules = {
            # Field type relationships
            "id_fields": ["id", "customer_id", "product_id", "order_id", "user_id", "employee_id", "transaction_id"],
            "name_fields": ["name", "first_name", "last_name", "full_name", "customer_name", "product_name"],
            "email_fields": ["email", "email_address", "customer_email", "user_email"],
            "date_fields": ["date", "created_at", "updated_at", "order_date", "birth_date", "hire_date"],
            "price_fields": ["price", "amount", "total", "cost", "salary", "revenue", "purchase_amount"],
            "quantity_fields": ["quantity", "count", "stock", "units", "items"],
            "status_fields": ["status", "state", "order_status", "payment_status"],
            "category_fields": ["category", "type", "department", "class", "group"],
            "location_fields": ["city", "country", "address", "state", "region", "location", "zip_code"],
            "contact_fields": ["phone", "phone_number", "mobile", "contact"],
        }
        
        # Semantic constraints
        self.field_constraints = {
            "age": {"type": "int", "min": 0, "max": 120, "typical_range": [18, 80]},
            "price": {"type": "float", "min": 0, "decimal_places": 2},
            "quantity": {"type": "int", "min": 0},
            "rating": {"type": "float", "min": 0, "max": 5},
            "percentage": {"type": "float", "min": 0, "max": 100},
            "email": {"type": "str", "pattern": "email"},
            "phone": {"type": "str", "pattern": "phone"},
            "date": {"type": "str", "pattern": "date"},
        }
        
        # Field dependencies (semantic relationships)
        self.field_dependencies = {
            "full_name": {"depends_on": ["first_name", "last_name"], "rule": "concatenate"},
            "total": {"depends_on": ["price", "quantity"], "rule": "multiply"},
            "age": {"depends_on": ["birth_date"], "rule": "calculate_from_date"},
            "order_total": {"depends_on": ["unit_price", "quantity"], "rule": "multiply"},
            "discount_price": {"depends_on": ["price", "discount"], "rule": "subtract_percentage"},
        }
        
        # Cross-field correlations
        self.correlations = {
            ("age", "salary"): "positive", 
            ("experience", "salary"): "positive",
            ("price", "quantity"): "negative",  # Higher price often means lower quantity sold
            ("rating", "reviews"): "positive",  # Higher rated products have more reviews
            ("age", "purchase_amount"): "slight_positive",
        }
    
    def analyze_schema(self, fields: List[str]) -> Dict[str, Any]:
        """
        Analyze a list of fields and identify relationships
        
        Args:
            fields: List of field names
            
        Returns:
            Schema analysis with relationships
        """
        analysis = {
            "fields": fields,
            "field_types": {},
            "relationships": [],
            "constraints": {},
            "dependencies": [],
            "correlations": []
        }
        
        # Classify each field
        for field in fields:
            field_lower = field.lower()
            
            # Detect field type
            field_type = self._classify_field(field_lower)
            analysis["field_types"][field] = field_type
            
            # Get constraints
            constraint = self._get_constraints(field_lower)
            if constraint:
                analysis["constraints"][field] = constraint
        
        # Find dependencies between fields
        analysis["dependencies"] = self._find_dependencies(fields)
        
        # Find correlations
        analysis["correlations"] = self._find_correlations(fields)
        
        # Generate relationship descriptions
        analysis["relationships"] = self._generate_relationships(analysis)
        
        return analysis
    
    def _classify_field(self, field: str) -> str:
        """Classify field into a semantic category"""
        for category, keywords in self.relationship_rules.items():
            if any(keyword in field for keyword in keywords):
                return category.replace("_fields", "")
        return "general"
    
    def _get_constraints(self, field: str) -> Optional[Dict]:
        """Get constraints for a field based on its name"""
        for key, constraint in self.field_constraints.items():
            if key in field:
                return constraint
        return None
    
    def _find_dependencies(self, fields: List[str]) -> List[Dict]:
        """Find dependencies between fields"""
        dependencies = []
        fields_lower = [f.lower() for f in fields]
        
        for field, dep_info in self.field_dependencies.items():
            if field in fields_lower:
                # Check if dependent fields exist
                deps = dep_info["depends_on"]
                existing_deps = [d for d in deps if d in fields_lower]
                if existing_deps:
                    dependencies.append({
                        "field": field,
                        "depends_on": existing_deps,
                        "rule": dep_info["rule"]
                    })
        
        return dependencies
    
    def _find_correlations(self, fields: List[str]) -> List[Dict]:
        """Find correlations between fields"""
        correlations = []
        fields_lower = [f.lower() for f in fields]
        
        for (field1, field2), correlation in self.correlations.items():
            if field1 in fields_lower and field2 in fields_lower:
                correlations.append({
                    "field1": field1,
                    "field2": field2,
                    "correlation": correlation
                })
        
        return correlations
    
    def _generate_relationships(self, analysis: Dict) -> List[str]:
        """Generate human-readable relationship descriptions"""
        relationships = []
        
        # ID relationships
        id_fields = [f for f, t in analysis["field_types"].items() if t == "id"]
        if id_fields:
            relationships.append(f"ID fields ({', '.join(id_fields)}) should be unique and sequential")
        
        # Price-quantity relationships
        price_fields = [f for f, t in analysis["field_types"].items() if t == "price"]
        quantity_fields = [f for f, t in analysis["field_types"].items() if t == "quantity"]
        if price_fields and quantity_fields:
            relationships.append(f"Price fields ({', '.join(price_fields)}) and quantity fields ({', '.join(quantity_fields)}) may have inverse correlation")
        
        # Name-email relationships
        name_fields = [f for f, t in analysis["field_types"].items() if t == "name"]
        email_fields = [f for f, t in analysis["field_types"].items() if t == "email"]
        if name_fields and email_fields:
            relationships.append(f"Email addresses should semantically relate to names (e.g., john.doe@email.com for John Doe)")
        
        # Add correlation descriptions
        for corr in analysis["correlations"]:
            if corr["correlation"] == "positive":
                relationships.append(f"Higher {corr['field1']} values correlate with higher {corr['field2']} values")
            elif corr["correlation"] == "negative":
                relationships.append(f"Higher {corr['field1']} values correlate with lower {corr['field2']} values")
        
        return relationships
    
    def generate_relationship_prompt(self, fields: List[str]) -> str:
        """
        Generate a prompt section describing field relationships
        
        Args:
            fields: List of field names
            
        Returns:
            Prompt text describing relationships
        """
        analysis = self.analyze_schema(fields)
        
        prompt_parts = ["\n=== SEMANTIC SCHEMA RELATIONSHIPS ===\n"]
        
        # Field types
        prompt_parts.append("FIELD CLASSIFICATIONS:")
        for field, field_type in analysis["field_types"].items():
            prompt_parts.append(f"  - {field}: {field_type}")
        
        # Constraints
        if analysis["constraints"]:
            prompt_parts.append("\nFIELD CONSTRAINTS:")
            for field, constraint in analysis["constraints"].items():
                constraint_str = ", ".join(f"{k}={v}" for k, v in constraint.items())
                prompt_parts.append(f"  - {field}: {constraint_str}")
        
        # Relationships
        if analysis["relationships"]:
            prompt_parts.append("\nRELATIONSHIP RULES:")
            for i, rel in enumerate(analysis["relationships"], 1):
                prompt_parts.append(f"  {i}. {rel}")
        
        # Dependencies
        if analysis["dependencies"]:
            prompt_parts.append("\nFIELD DEPENDENCIES:")
            for dep in analysis["dependencies"]:
                prompt_parts.append(f"  - {dep['field']} depends on {', '.join(dep['depends_on'])} ({dep['rule']})")
        
        prompt_parts.append("\nIMPORTANT: Maintain these semantic relationships in generated data!\n")
        
        return "\n".join(prompt_parts)


# Create singleton instance
schema_mapper = SchemaRelationshipMapper()
