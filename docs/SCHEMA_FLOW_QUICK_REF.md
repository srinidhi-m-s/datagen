# Schema Generation Flow - Quick Reference

## 🎯 The Flow

```
USER QUERY
    ↓
    "Generate 20 employee records"
    ↓
┌───────────────────────────────────────────────┐
│  STEP 1: LLM Schema Extraction                │
│  File: gemini_service.py                      │
│  Method: generate_schema_with_validation()    │
│                                               │
│  What it does:                                │
│  ✓ Analyzes user intent                       │
│  ✓ Infers domain fields (id, name, email...)  │
│  ✓ Determines data types                      │
│  ✓ Applies semantic constraints               │
│  ✓ Understands relationships                  │
│                                               │
│  Output: Raw LLM JSON                         │
│  {                                            │
│    "dataset_name": "employees",               │
│    "rows": 20,                                │
│    "columns": [                               │
│      {                                        │
│        "name": "employee_id",                 │
│        "type": "int",                         │
│        "range": [1000, 9999]                  │
│      },                                       │
│      ...                                      │
│    ]                                          │
│  }                                            │
└───────────────┬───────────────────────────────┘
                ↓
┌───────────────────────────────────────────────┐
│  STEP 2: Schema Mapper Validation            │
│  File: integrate/schema_mapper.py             │
│  Function: map_llm_to_schema()                │
│                                               │
│  What it does:                                │
│  ✓ Normalizes types (int/integer → INT)      │
│  ✓ Validates structure                        │
│  ✓ Ensures uniqueness                         │
│  ✓ Converts to Pydantic models                │
│  ✓ Validates constraints                      │
│                                               │
│  Output: Validated DatasetSchema              │
│  DatasetSchema(                               │
│    dataset_name="employees",                  │
│    rows=20,                                   │
│    columns=[                                  │
│      ColumnSchema(                            │
│        name="employee_id",                    │
│        type=ColumnType.INT,                   │
│        min=1000.0,                            │
│        max=9999.0                             │
│      ),                                       │
│      ...                                      │
│    ]                                          │
│  )                                            │
└───────────────┬───────────────────────────────┘
                ↓
        PERFECT SCHEMA
        Ready for RAG/Data Generation
```

## 📡 API Endpoint

**POST** `/api/generate-schema`

**Request:**
```json
{
  "query": "Generate 20 employee records",
  "use_kaggle": false,
  "use_rag": false
}
```

**Response:**
```json
{
  "success": true,
  "schema": { ... },
  "metadata": {
    "dataset_name": "employees",
    "rows": 20,
    "column_count": 8
  },
  "flow": "llm_extraction → schema_validation"
}
```

## 🔧 Code Usage

```python
from backend.gemini_service import gemini_service

# Generate schema
result = await gemini_service.generate_schema_with_validation(
    "Generate 50 customer records"
)

if result["success"]:
    schema = result["schema"]
    validated_obj = result["validated_schema_object"]
    
    # Use the schema for data generation, RAG, etc.
    print(f"Dataset: {schema['dataset_name']}")
    print(f"Columns: {len(schema['columns'])}")
```

## ✨ Key Benefits

| Feature | Benefit |
|---------|---------|
| **LLM Semantic Understanding** | Automatically infers domain-standard fields |
| **Schema Validation** | Ensures type safety and data integrity |
| **Type Normalization** | Handles different LLM output formats |
| **Pydantic Models** | Type-safe, validated objects |
| **Clean Separation** | LLM does semantics, mapper does validation |

## 📚 Files

- **Implementation:** `backend/gemini_service.py` (line 532+)
- **Validation:** `backend/integrate/schema_mapper.py`
- **API:** `backend/main.py` (line 315+)
- **Docs:** `docs/SCHEMA_GENERATION_FLOW.md`
- **Test:** `backend/test_schema_flow.py`

## 🧪 Testing

```bash
# Run the test script
python backend/test_schema_flow.py

# Or test via API
curl -X POST http://localhost:8000/api/generate-schema \
  -H "Content-Type: application/json" \
  -d '{"query": "Generate 10 employee records"}'
```

## 🎨 Type Normalization Examples

The schema mapper handles various LLM output formats:

```python
# LLM might say:        Schema mapper normalizes to:
"integer"           →   ColumnType.INT
"int"               →   ColumnType.INT
"number"            →   ColumnType.FLOAT
"decimal"           →   ColumnType.FLOAT
"category"          →   ColumnType.CATEGORICAL
"enum"              →   ColumnType.CATEGORICAL
"datetime"          →   ColumnType.DATE
"bool"              →   ColumnType.BOOLEAN
```

## 🔍 Validation Checks

The schema mapper validates:

- ✅ Column names are unique
- ✅ Dataset name is valid
- ✅ Row count is positive
- ✅ Categorical columns have values
- ✅ Numeric bounds are valid
- ✅ Required fields are present
- ✅ Types are normalized

## 🚀 Next Steps

1. **Test the flow** - Run `test_schema_flow.py`
2. **Try the API** - Use `/api/generate-schema` endpoint
3. **Integrate with RAG** - Use validated schemas for RAG processing
4. **Generate data** - Use schemas for actual data generation

---

**Quick Start:** See `docs/SCHEMA_GENERATION_FLOW.md` for full documentation
