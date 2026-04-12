"""
Comprehensive Test Suite for Schema Mapper Module

Tests cover:
- Basic schema mapping
- Type normalization
- Validation and error handling
- Edge cases
- API endpoint functionality
"""

import pytest
import json
from pydantic import ValidationError
from schema_mapper import (
    ColumnType,
    ColumnSchema,
    DatasetSchema,
    normalize_type,
    map_llm_to_schema,
    schema_to_dict,
    schema_to_json,
    TYPE_MAPPING
)


# ============================================================================
# FIXTURES - Test Data Setup
# ============================================================================

@pytest.fixture
def basic_llm_output():
    """Basic LLM output with all required fields"""
    return {
        "dataset_name": "customer_data",
        "rows": 100,
        "columns": [
            {
                "name": "age",
                "type": "int",
                "range": [18, 65]
            },
            {
                "name": "region",
                "type": "categorical",
                "values": ["North America", "Europe", "Asia"]
            },
            {
                "name": "feedback",
                "type": "string"
            }
        ]
    }


@pytest.fixture
def advanced_llm_output():
    """Advanced LLM output with optional fields"""
    return {
        "dataset_name": "sales_transactions",
        "rows": 500,
        "description": "Q4 2025 sales data",
        "source": "llm",
        "columns": [
            {
                "name": "transaction_id",
                "type": "integer",
                "range": [1000, 99999],
                "description": "Unique transaction ID",
                "required": True,
                "nullable": False
            },
            {
                "name": "sale_amount",
                "type": "number",
                "range": [9.99, 9999.99],
                "description": "Sale amount in USD"
            },
            {
                "name": "region",
                "type": "categorical",
                "values": ["US", "EU", "APAC", "LATAM"]
            },
            {
                "name": "is_premium",
                "type": "bool",
                "nullable": True
            }
        ]
    }


# ============================================================================
# TESTS - Type Normalization
# ============================================================================

class TestTypeNormalization:
    """Test type normalization mapping"""
    
    def test_integer_variants(self):
        """Test various integer type names"""
        assert normalize_type("int") == ColumnType.INT
        assert normalize_type("integer") == ColumnType.INT
        assert normalize_type("INT") == ColumnType.INT
        assert normalize_type("Integer") == ColumnType.INT
    
    def test_float_variants(self):
        """Test various float type names"""
        assert normalize_type("float") == ColumnType.FLOAT
        assert normalize_type("number") == ColumnType.FLOAT
        assert normalize_type("decimal") == ColumnType.FLOAT
        assert normalize_type("double") == ColumnType.FLOAT
        assert normalize_type("FLOAT") == ColumnType.FLOAT
    
    def test_string_variants(self):
        """Test various string type names"""
        assert normalize_type("string") == ColumnType.STRING
        assert normalize_type("text") == ColumnType.STRING
        assert normalize_type("varchar") == ColumnType.STRING
        assert normalize_type("STRING") == ColumnType.STRING
    
    def test_categorical_variants(self):
        """Test various categorical type names"""
        assert normalize_type("categorical") == ColumnType.CATEGORICAL
        assert normalize_type("category") == ColumnType.CATEGORICAL
        assert normalize_type("enum") == ColumnType.CATEGORICAL
        assert normalize_type("CATEGORICAL") == ColumnType.CATEGORICAL
    
    def test_date_variants(self):
        """Test various date type names"""
        assert normalize_type("date") == ColumnType.DATE
        assert normalize_type("datetime") == ColumnType.DATE
        assert normalize_type("timestamp") == ColumnType.DATE
    
    def test_boolean_variants(self):
        """Test various boolean type names"""
        assert normalize_type("boolean") == ColumnType.BOOLEAN
        assert normalize_type("bool") == ColumnType.BOOLEAN
        assert normalize_type("BOOLEAN") == ColumnType.BOOLEAN
    
    def test_unknown_type_defaults_to_string(self):
        """Unknown types should default to string"""
        assert normalize_type("unknown_type") == ColumnType.STRING
        assert normalize_type("custom") == ColumnType.STRING
        assert normalize_type("") == ColumnType.STRING


# ============================================================================
# TESTS - ColumnSchema Validation
# ============================================================================

class TestColumnSchema:
    """Test ColumnSchema validation"""
    
    def test_valid_numeric_column(self):
        """Create valid numeric column"""
        col = ColumnSchema(
            name="age",
            type=ColumnType.INT,
            min=0,
            max=150
        )
        assert col.name == "age"
        assert col.type == ColumnType.INT
        assert col.min == 0
        assert col.max == 150
    
    def test_valid_categorical_column(self):
        """Create valid categorical column"""
        col = ColumnSchema(
            name="region",
            type=ColumnType.CATEGORICAL,
            values=["US", "EU", "APAC"]
        )
        assert col.name == "region"
        assert col.type == ColumnType.CATEGORICAL
        assert col.values == ["US", "EU", "APAC"]
    
    def test_valid_string_column(self):
        """Create valid string column"""
        col = ColumnSchema(
            name="description",
            type=ColumnType.STRING,
            nullable=True
        )
        assert col.name == "description"
        assert col.nullable is True
    
    def test_column_name_validation(self):
        """Test column name validation"""
        # Empty name should raise error
        with pytest.raises(ValidationError):
            ColumnSchema(
                name="",
                type=ColumnType.STRING
            )
        
        # Non-string name should raise error
        with pytest.raises(ValidationError):
            ColumnSchema(
                name=123,
                type=ColumnType.STRING
            )
    
    def test_categorical_requires_values(self):
        """Categorical columns require values"""
        with pytest.raises(ValidationError):
            ColumnSchema(
                name="region",
                type=ColumnType.CATEGORICAL
            )
    
    def test_numeric_bounds_validation(self):
        """Numeric bounds validation"""
        # Valid bounds
        col = ColumnSchema(
            name="age",
            type=ColumnType.INT,
            min=18,
            max=65
        )
        assert col.min == 18.0
        assert col.max == 65.0
        
        # String numbers should be converted
        col = ColumnSchema(
            name="score",
            type=ColumnType.FLOAT,
            min="0.0",
            max="100.0"
        )
        assert col.min == 0.0
        assert col.max == 100.0


# ============================================================================
# TESTS - DatasetSchema Validation
# ============================================================================

class TestDatasetSchema:
    """Test DatasetSchema validation"""
    
    def test_valid_dataset_schema(self):
        """Create valid dataset schema"""
        schema = DatasetSchema(
            dataset_name="test_data",
            rows=100,
            columns=[
                ColumnSchema(name="col1", type=ColumnType.INT),
                ColumnSchema(name="col2", type=ColumnType.STRING)
            ]
        )
        assert schema.dataset_name == "test_data"
        assert schema.rows == 100
        assert len(schema.columns) == 2
    
    def test_dataset_name_validation(self):
        """Test dataset name validation"""
        # Empty name should raise error
        with pytest.raises(ValidationError):
            DatasetSchema(
                dataset_name="",
                rows=100,
                columns=[ColumnSchema(name="col1", type=ColumnType.STRING)]
            )
    
    def test_rows_must_be_positive(self):
        """Rows must be positive integer"""
        with pytest.raises(ValidationError):
            DatasetSchema(
                dataset_name="test",
                rows=0,
                columns=[ColumnSchema(name="col1", type=ColumnType.STRING)]
            )
        
        with pytest.raises(ValidationError):
            DatasetSchema(
                dataset_name="test",
                rows=-10,
                columns=[ColumnSchema(name="col1", type=ColumnType.STRING)]
            )
    
    def test_unique_column_names_required(self):
        """Column names must be unique"""
        with pytest.raises(ValidationError):
            DatasetSchema(
                dataset_name="test",
                rows=100,
                columns=[
                    ColumnSchema(name="col1", type=ColumnType.INT),
                    ColumnSchema(name="col1", type=ColumnType.STRING)  # Duplicate!
                ]
            )


# ============================================================================
# TESTS - Schema Mapping
# ============================================================================

class TestSchemaMapping:
    """Test LLM to Schema mapping"""
    
    def test_basic_mapping(self, basic_llm_output):
        """Map basic LLM output"""
        schema = map_llm_to_schema(basic_llm_output)
        
        assert schema.dataset_name == "customer_data"
        assert schema.rows == 100
        assert len(schema.columns) == 3
        
        # Check first column (int)
        assert schema.columns[0].name == "age"
        assert schema.columns[0].type == ColumnType.INT
        assert schema.columns[0].min == 18
        assert schema.columns[0].max == 65
        
        # Check second column (categorical)
        assert schema.columns[1].name == "region"
        assert schema.columns[1].type == ColumnType.CATEGORICAL
        assert schema.columns[1].values == ["North America", "Europe", "Asia"]
        
        # Check third column (string)
        assert schema.columns[2].name == "feedback"
        assert schema.columns[2].type == ColumnType.STRING
    
    def test_advanced_mapping(self, advanced_llm_output):
        """Map advanced LLM output with optional fields"""
        schema = map_llm_to_schema(advanced_llm_output)
        
        assert schema.dataset_name == "sales_transactions"
        assert schema.rows == 500
        assert schema.description == "Q4 2025 sales data"
        assert schema.source == "llm"
        assert len(schema.columns) == 4
        
        # Check column with all optional fields
        col = schema.columns[0]
        assert col.name == "transaction_id"
        assert col.description == "Unique transaction ID"
        assert col.required is True
        assert col.nullable is False
    
    def test_type_normalization_in_mapping(self):
        """Test type normalization during mapping"""
        llm_output = {
            "dataset_name": "test",
            "rows": 10,
            "columns": [
                {"name": "col1", "type": "NUMBER", "range": [0, 100]},
                {"name": "col2", "type": "category", "values": ["A", "B"]},
                {"name": "col3", "type": "bool"}
            ]
        }
        
        schema = map_llm_to_schema(llm_output)
        
        assert schema.columns[0].type == ColumnType.FLOAT  # "NUMBER" -> FLOAT
        assert schema.columns[1].type == ColumnType.CATEGORICAL  # "category" -> CATEGORICAL
        assert schema.columns[2].type == ColumnType.BOOLEAN  # "bool" -> BOOLEAN
    
    def test_range_handling(self):
        """Test range to min/max conversion"""
        llm_output = {
            "dataset_name": "test",
            "rows": 10,
            "columns": [
                {"name": "col1", "type": "int", "range": [50, 10]},  # Out of order
                {"name": "col2", "type": "float", "range": [0, 100]},
                {"name": "col3", "type": "string"}  # No range
            ]
        }
        
        schema = map_llm_to_schema(llm_output)
        
        # Out of order should be corrected
        assert schema.columns[0].min == 10
        assert schema.columns[0].max == 50
        
        # Normal range
        assert schema.columns[1].min == 0.0
        assert schema.columns[1].max == 100.0
        
        # String column has no min/max
        assert schema.columns[2].min is None
        assert schema.columns[2].max is None
    
    def test_missing_dataset_name(self):
        """Default dataset name when missing"""
        llm_output = {
            "rows": 10,
            "columns": [{"name": "col1", "type": "string"}]
        }
        
        schema = map_llm_to_schema(llm_output)
        assert schema.dataset_name == "generated_dataset"
    
    def test_missing_rows(self):
        """Default rows when missing"""
        llm_output = {
            "dataset_name": "test",
            "columns": [{"name": "col1", "type": "string"}]
        }
        
        schema = map_llm_to_schema(llm_output)
        assert schema.rows == 100


# ============================================================================
# TESTS - Error Handling
# ============================================================================

class TestErrorHandling:
    """Test error handling in mapping"""
    
    def test_input_must_be_dict(self):
        """Input must be a dictionary"""
        with pytest.raises(ValueError, match="must be a dictionary"):
            map_llm_to_schema("not a dict")
        
        with pytest.raises(ValueError):
            map_llm_to_schema([1, 2, 3])
    
    def test_rows_validation(self):
        """Rows must be positive integer"""
        with pytest.raises(ValueError, match="positive integer"):
            map_llm_to_schema({
                "dataset_name": "test",
                "rows": -5,
                "columns": [{"name": "col", "type": "string"}]
            })
    
    def test_column_spec_must_be_dict(self):
        """Each column spec must be a dictionary"""
        with pytest.raises(ValueError, match="must be a dictionary"):
            map_llm_to_schema({
                "dataset_name": "test",
                "rows": 10,
                "columns": ["not a dict"]
            })
    
    def test_column_name_required(self):
        """Column name is required"""
        with pytest.raises(ValueError, match="Column name is required"):
            map_llm_to_schema({
                "dataset_name": "test",
                "rows": 10,
                "columns": [{"type": "string"}]  # Missing name
            })
    
    def test_categorical_requires_values(self):
        """Categorical columns must have values"""
        with pytest.raises(ValueError, match="must have 'values'"):
            map_llm_to_schema({
                "dataset_name": "test",
                "rows": 10,
                "columns": [{"name": "col", "type": "categorical"}]  # Missing values
            })


# ============================================================================
# TESTS - Serialization
# ============================================================================

class TestSerialization:
    """Test schema serialization"""
    
    def test_schema_to_dict(self, basic_llm_output):
        """Convert schema to dictionary"""
        schema = map_llm_to_schema(basic_llm_output)
        schema_dict = schema_to_dict(schema)
        
        assert isinstance(schema_dict, dict)
        assert schema_dict["dataset_name"] == "customer_data"
        assert schema_dict["rows"] == 100
        assert len(schema_dict["columns"]) == 3
    
    def test_schema_to_json(self, basic_llm_output):
        """Convert schema to JSON string"""
        schema = map_llm_to_schema(basic_llm_output)
        schema_json = schema_to_json(schema)
        
        assert isinstance(schema_json, str)
        
        # Parse JSON to verify it's valid
        parsed = json.loads(schema_json)
        assert parsed["dataset_name"] == "customer_data"
        assert parsed["rows"] == 100
    
    def test_schema_roundtrip(self, basic_llm_output):
        """Schema should be convertible to JSON and back"""
        schema1 = map_llm_to_schema(basic_llm_output)
        json_str = schema_to_json(schema1)
        schema_dict = json.loads(json_str)
        schema2 = DatasetSchema(**schema_dict)
        
        assert schema1.dataset_name == schema2.dataset_name
        assert schema1.rows == schema2.rows
        assert len(schema1.columns) == len(schema2.columns)


# ============================================================================
# TESTS - Edge Cases
# ============================================================================

class TestEdgeCases:
    """Test edge cases and special scenarios"""
    
    def test_very_large_row_count(self):
        """Handle very large row counts"""
        llm_output = {
            "dataset_name": "big_data",
            "rows": 1_000_000_000,
            "columns": [{"name": "col", "type": "string"}]
        }
        
        schema = map_llm_to_schema(llm_output)
        assert schema.rows == 1_000_000_000
    
    def test_single_column_dataset(self):
        """Handle single column datasets"""
        llm_output = {
            "dataset_name": "simple",
            "rows": 10,
            "columns": [{"name": "value", "type": "int", "range": [0, 100]}]
        }
        
        schema = map_llm_to_schema(llm_output)
        assert len(schema.columns) == 1
    
    def test_many_columns(self):
        """Handle datasets with many columns"""
        columns = [
            {"name": f"col_{i}", "type": "string"}
            for i in range(100)
        ]
        
        llm_output = {
            "dataset_name": "many_cols",
            "rows": 10,
            "columns": columns
        }
        
        schema = map_llm_to_schema(llm_output)
        assert len(schema.columns) == 100
    
    def test_special_characters_in_names(self):
        """Handle special characters in names"""
        llm_output = {
            "dataset_name": "data-set_2025",
            "rows": 10,
            "columns": [
                {"name": "column_1", "type": "string"},
                {"name": "col-2", "type": "int", "range": [0, 100]}
            ]
        }
        
        schema = map_llm_to_schema(llm_output)
        assert schema.dataset_name == "data-set_2025"
        assert schema.columns[0].name == "column_1"
        assert schema.columns[1].name == "col-2"


# ============================================================================
# RUN TESTS
# ============================================================================

if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v", "--tb=short"])
