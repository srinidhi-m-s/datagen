"""
Schema Mapping Module - Converts LLM output to structured DatasetSchema

This module bridges the LLM module and RAG module by:
1. Accepting raw LLM output (dict format)
2. Validating and normalizing the structure
3. Providing DatasetSchema objects for downstream RAG processing
"""

from typing import Optional, List, Dict, Any
from enum import Enum
from pydantic import BaseModel, Field, field_validator, model_validator, ConfigDict
from datetime import datetime, timezone
import json


# ============================================================================
# ENUMS AND TYPE DEFINITIONS
# ============================================================================

class ColumnType(str, Enum):
    """Supported column data types"""
    INT = "int"
    FLOAT = "float"
    STRING = "string"
    CATEGORICAL = "categorical"
    DATE = "date"
    BOOLEAN = "boolean"


# Type normalization mapping for LLM outputs
# Handles various naming conventions from different LLMs
TYPE_MAPPING = {
    # Integer types
    "integer": ColumnType.INT,
    "int": ColumnType.INT,
    "number": ColumnType.FLOAT,
    # Float types
    "float": ColumnType.FLOAT,
    "decimal": ColumnType.FLOAT,
    "double": ColumnType.FLOAT,
    # String types
    "string": ColumnType.STRING,
    "text": ColumnType.STRING,
    "varchar": ColumnType.STRING,
    # Categorical types
    "categorical": ColumnType.CATEGORICAL,
    "category": ColumnType.CATEGORICAL,
    "enum": ColumnType.CATEGORICAL,
    # Date types
    "date": ColumnType.DATE,
    "datetime": ColumnType.DATE,
    "timestamp": ColumnType.DATE,
    # Boolean types
    "boolean": ColumnType.BOOLEAN,
    "bool": ColumnType.BOOLEAN,
}


# ============================================================================
# PYDANTIC MODELS - Data Validation and Serialization
# ============================================================================

class ColumnSchema(BaseModel):
    """
    Schema definition for a single column in a dataset
    
    Attributes:
        name: Column identifier
        type: Data type (int, float, string, categorical, date, boolean)
        description: Optional human-readable description
        min: Minimum value (for numeric types)
        max: Maximum value (for numeric types)
        values: Allowed values (for categorical types)
        nullable: Whether column can contain null values
        required: Whether this column must be present in generated data
    """
    name: str = Field(..., description="Column name")
    type: ColumnType = Field(..., description="Column data type")
    description: Optional[str] = Field(None, description="Column description")
    min: Optional[float] = Field(None, description="Min value (numeric columns)")
    max: Optional[float] = Field(None, description="Max value (numeric columns)")
    values: Optional[List[str]] = Field(None, description="Allowed values (categorical columns)")
    nullable: bool = Field(False, description="Whether null values are allowed")
    required: bool = Field(True, description="Whether this column is required")

    @field_validator("name")
    @classmethod
    def validate_name(cls, v):
        if not v or not isinstance(v, str):
            raise ValueError("Column name must be a non-empty string")
        if len(v) > 255:
            raise ValueError("Column name must be less than 255 characters")
        return v.strip()

    @field_validator("min", "max", mode="before")
    @classmethod
    def validate_numeric_bounds(cls, v):
        if v is not None and not isinstance(v, (int, float)):
            try:
                return float(v)
            except (ValueError, TypeError):
                raise ValueError("min/max must be numeric")
        return v

    @model_validator(mode="after")
    def validate_categorical_has_values(self):
        """Categorical columns must have values defined"""
        if self.type == ColumnType.CATEGORICAL and not self.values:
            raise ValueError("Categorical columns must have 'values' defined")
        if self.values and not isinstance(self.values, list):
            raise ValueError("Values must be a list")
        return self


class DatasetSchema(BaseModel):
    """
    Complete schema definition for a dataset
    
    Attributes:
        dataset_name: Name identifier for the dataset
        rows: Number of rows to generate
        columns: List of column schemas
        description: Optional dataset description
        version: Schema version (for tracking changes)
        created_at: Timestamp of schema creation
        source: Tag indicating where this schema came from (e.g., 'llm', 'manual')
    """
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "dataset_name": "customer_data",
            "rows": 100,
            "columns": [
                {
                    "name": "age",
                    "type": "int",
                    "min": 18,
                    "max": 65,
                    "required": True
                },
                {
                    "name": "gender",
                    "type": "categorical",
                    "values": ["male", "female", "other"],
                    "required": True
                }
            ]
        }
    })
    
    dataset_name: str = Field(..., description="Dataset name")
    rows: int = Field(..., ge=1, description="Number of rows")
    columns: List[ColumnSchema] = Field(..., min_length=1, description="Column definitions")
    description: Optional[str] = Field(None, description="Dataset description")
    version: str = Field("1.0", description="Schema version")
    created_at: Optional[str] = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(),
        description="Creation timestamp"
    )
    source: str = Field("llm", description="Source of this schema (e.g., 'llm', 'manual', 'kaggle')")

    @field_validator("dataset_name")
    @classmethod
    def validate_dataset_name(cls, v):
        if not v or not isinstance(v, str):
            raise ValueError("Dataset name must be a non-empty string")
        if len(v) > 255:
            raise ValueError("Dataset name must be less than 255 characters")
        return v.strip()

    @field_validator("columns")
    @classmethod
    def validate_unique_column_names(cls, v):
        names = [col.name for col in v]
        if len(names) != len(set(names)):
            raise ValueError("Column names must be unique")
        return v


# ============================================================================
# SCHEMA MAPPING FUNCTIONS
# ============================================================================

def normalize_type(raw_type: str) -> ColumnType:
    """
    Normalize column type from LLM output to standard ColumnType
    
    Args:
        raw_type: Type string from LLM (case-insensitive)
        
    Returns:
        Normalized ColumnType enum value
        
    Raises:
        ValueError: If type cannot be mapped to a known ColumnType
    """
    normalized = raw_type.lower().strip() if isinstance(raw_type, str) else str(raw_type)
    
    if normalized in TYPE_MAPPING:
        return TYPE_MAPPING[normalized]
    
    # Default to string for unknown types
    return ColumnType.STRING


def map_llm_to_schema(llm_output: Dict[str, Any]) -> DatasetSchema:
    """
    Convert LLM output dictionary to structured DatasetSchema
    
    This is the main integration point for the LLM module. It accepts
    raw LLM output and produces a validated, structured schema suitable
    for the RAG module's data generation pipeline.
    
    Args:
        llm_output: Raw output from LLM containing:
            - dataset_name (str): Name of the dataset
            - rows (int): Number of rows to generate
            - columns (List[Dict]): Column specifications with:
                - name (str): Column name
                - type (str): Data type
                - range (List[2]): [min, max] for numeric types
                - values (List[str]): Allowed values for categorical types
                - description (str, optional): Column description
                - nullable (bool, optional): Whether null values allowed
                
    Returns:
        DatasetSchema: Validated, structured schema object
        
    Raises:
        ValidationError: If LLM output doesn't conform to schema requirements
        ValueError: If required fields are missing or malformed
        
    Example:
        >>> llm_output = {
        ...     "dataset_name": "sales",
        ...     "rows": 1000,
        ...     "columns": [
        ...         {"name": "sales_amount", "type": "float", "range": [0, 10000]},
        ...         {"name": "region", "type": "categorical", "values": ["US", "EU", "ASIA"]}
        ...     ]
        ... }
        >>> schema = map_llm_to_schema(llm_output)
        >>> schema.model_dump_json()
    """
    
    if not isinstance(llm_output, dict):
        raise ValueError("LLM output must be a dictionary")
    
    # Extract basic dataset information
    dataset_name = llm_output.get("dataset_name", "generated_dataset")
    rows = llm_output.get("rows", 100)
    description = llm_output.get("description")
    source = llm_output.get("source", "llm")
    
    # Validate basic fields
    if not isinstance(rows, int) or rows < 1:
        raise ValueError("rows must be a positive integer")
    
    columns = []
    
    # Process each column specification
    for col_spec in llm_output.get("columns", []):
        if not isinstance(col_spec, dict):
            raise ValueError(f"Each column must be a dictionary, got {type(col_spec)}")
        
        col_name = col_spec.get("name", "").strip()
        if not col_name:
            raise ValueError("Column name is required and cannot be empty")
        
        # Normalize the column type
        raw_type = col_spec.get("type", "string")
        col_type = normalize_type(raw_type)
        
        # Handle numeric columns: convert range [min, max] to min/max fields
        min_val, max_val = None, None
        if col_type in [ColumnType.INT, ColumnType.FLOAT]:
            range_spec = col_spec.get("range")
            if range_spec and isinstance(range_spec, (list, tuple)) and len(range_spec) >= 2:
                try:
                    min_val = float(range_spec[0])
                    max_val = float(range_spec[1])
                    if min_val > max_val:
                        min_val, max_val = max_val, min_val
                except (ValueError, TypeError):
                    pass  # Keep as None if conversion fails
        
        # Handle categorical columns: extract allowed values
        values = None
        if col_type == ColumnType.CATEGORICAL:
            values = col_spec.get("values", [])
            if not values:
                raise ValueError(f"Categorical column '{col_name}' must have 'values' defined")
            if not isinstance(values, list):
                values = list(values) if hasattr(values, '__iter__') else [str(values)]
        
        # Extract optional fields
        col_description = col_spec.get("description")
        nullable = col_spec.get("nullable", False)
        required = col_spec.get("required", True)
        
        # Create ColumnSchema object with validation
        column = ColumnSchema(
            name=col_name,
            type=col_type,
            description=col_description,
            min=min_val,
            max=max_val,
            values=values,
            nullable=nullable,
            required=required
        )
        columns.append(column)
    
    # Create and return the validated DatasetSchema
    schema = DatasetSchema(
        dataset_name=dataset_name,
        rows=rows,
        columns=columns,
        description=description,
        source=source
    )
    
    return schema


def schema_to_dict(schema: DatasetSchema) -> Dict[str, Any]:
    """
    Convert DatasetSchema to dictionary format (for JSON serialization to RAG)
    
    Args:
        schema: DatasetSchema object
        
    Returns:
        Dictionary representation suitable for RAG module
    """
    return schema.model_dump(exclude_none=True)


def schema_to_json(schema: DatasetSchema, indent: int = 4) -> str:
    """
    Convert DatasetSchema to JSON string
    
    Args:
        schema: DatasetSchema object
        indent: JSON indentation level
        
    Returns:
        JSON string representation
    """
    return schema.model_dump_json(indent=indent, exclude_none=True)


# ============================================================================
# EXAMPLE USAGE AND TESTING
# ============================================================================

if __name__ == "__main__":
    # Example 1: Basic dataset mapping
    sample_llm_output = {
        "dataset_name": "customer_data",
        "rows": 10,
        "columns": [
            {
                "name": "age",
                "type": "number",
                "range": [18, 65],
                "description": "Customer age in years"
            },
            {
                "name": "gender",
                "type": "categorical",
                "values": ["male", "female", "other"],
                "required": True
            },
            {
                "name": "location",
                "type": "string"
            },
            {
                "name": "is_premium",
                "type": "boolean"
            }
        ]
    }
    
    print("=" * 80)
    print("SCHEMA MAPPING - Example 1: Basic Dataset")
    print("=" * 80)
    
    try:
        schema = map_llm_to_schema(sample_llm_output)
        print("\n[OK] Schema successfully mapped from LLM output\n")
        print("Mapped Schema (JSON output for RAG module):")
        print(schema_to_json(schema))
    except Exception as e:
        print(f"[ERROR] Schema mapping failed: {e}")
    
    # Example 2: Advanced dataset with multiple numeric types
    advanced_llm_output = {
        "dataset_name": "sales_transactions",
        "rows": 500,
        "description": "E-commerce sales data for Q4 2025",
        "source": "llm",
        "columns": [
            {
                "name": "transaction_id",
                "type": "int",
                "range": [1000, 9999],
                "description": "Unique transaction identifier"
            },
            {
                "name": "sale_amount",
                "type": "float",
                "range": [9.99, 9999.99],
                "description": "Sale amount in USD"
            },
            {
                "name": "region",
                "type": "categorical",
                "values": ["North America", "Europe", "Asia-Pacific", "Latin America"],
                "description": "Geographic region"
            },
            {
                "name": "customer_feedback",
                "type": "string",
                "nullable": True,
                "description": "Optional customer comment"
            }
        ]
    }
    
    print("\n" + "=" * 80)
    print("SCHEMA MAPPING - Example 2: Advanced Sales Dataset")
    print("=" * 80)
    
    try:
        schema = map_llm_to_schema(advanced_llm_output)
        print("\n[OK] Advanced schema successfully mapped\n")
        print(f"Dataset: {schema.dataset_name}")
        print(f"Rows: {schema.rows}")
        print(f"Columns: {len(schema.columns)}")
        print(f"Created: {schema.created_at}\n")
        print("Output for RAG module:")
        print(schema_to_json(schema))
    except Exception as e:
        print(f"[ERROR] Schema mapping failed: {e}")
