# Schema Generation Flow Documentation

## Overview

This document describes the **new schema generation flow** that integrates LLM-based semantic understanding with robust schema validation and normalization.

## 🎯 Flow Architecture

```
┌─────────────────┐
│   User Query    │
│ "Generate 20    │
│ employee data"  │
└────────┬────────┘
         │
         ▼
┌─────────────────────────────────────────────────────┐
│  STEP 1: LLM Schema Extraction                      │
│  (Semantic Understanding & Field Inference)         │
│                                                     │
│  • Analyzes user intent                            │
│  • Infers domain-specific fields                   │
│  • Determines data types                           │
│  • Applies semantic constraints                    │
│  • Understands field relationships                 │
│                                                     │
│  Output: Raw LLM schema (JSON)                     │
└────────┬────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────┐
│  STEP 2: Schema Mapper Validation                  │
│  (Validation & Normalization)                       │
│                                                     │
│  • Validates schema structure                      │
│  • Normalizes data types                           │
│  • Ensures field uniqueness                        │
│  • Validates constraints                           │
│  • Converts to Pydantic models                     │
│                                                     │
│  Output: Validated DatasetSchema object            │
└────────┬────────────────────────────────────────────┘
         │
         ▼
┌─────────────────┐
│ Perfect Schema  │
│ Ready for RAG/  │
│ Data Generation │
└─────────────────┘
```

---

## 📋 Detailed Flow

### **Step 1: LLM Schema Extraction**

**Location:** `backend/gemini_service.py` → `generate_schema_with_validation()`

**Purpose:** Use LLM's semantic understanding to extract a comprehensive schema from natural language

**What the LLM Does:**
1. **Domain Recognition** - Identifies the type of data (employees, customers, products, etc.)
2. **Field Inference** - Infers standard fields for the domain
3. **Type Determination** - Suggests appropriate data types
4. **Constraint Application** - Applies realistic constraints (age: 18-70, etc.)
5. **Relationship Understanding** - Recognizes field relationships (email ↔ name)

**Example Input:**
```
"Generate 20 employee records"
```

**Example LLM Output:**
```json
{
  "dataset_name": "employee_records",
  "rows": 20,
  "description": "Employee information dataset",
  "columns": [
    {
      "name": "employee_id",
      "type": "int",
      "description": "Unique employee identifier",
      "range": [1000, 9999],
      "nullable": false,
      "required": true
    },
    {
      "name": "first_name",
      "type": "string",
      "description": "Employee first name",
      "nullable": false,
      "required": true
    },
    {
      "name": "email",
      "type": "string",
      "description": "Employee email (derived from name)",
      "nullable": false,
      "required": true
    },
    {
      "name": "department",
      "type": "categorical",
      "description": "Department assignment",
      "values": ["Engineering", "Sales", "Marketing", "HR", "Finance"],
      "nullable": false,
      "required": true
    },
    {
      "name": "salary",
      "type": "float",
      "description": "Annual salary in USD",
      "range": [35000.00, 150000.00],
      "nullable": false,
      "required": true
    }
  ]
}
```

---

### **Step 2: Schema Mapper Validation**

**Location:** `backend/integrate/schema_mapper.py` → `map_llm_to_schema()`

**Purpose:** Validate and normalize the LLM output into a structured, type-safe schema

**What the Schema Mapper Does:**
1. **Type Normalization** - Maps various type names to standard `ColumnType` enum
   - `"integer"`, `"int"`, `"number"` → `ColumnType.INT`
   - `"decimal"`, `"float"`, `"double"` → `ColumnType.FLOAT`
   - `"category"`, `"categorical"`, `"enum"` → `ColumnType.CATEGORICAL`

2. **Structure Transformation** - Converts LLM format to schema format
   - `"range": [min, max]` → separate `min` and `max` fields
   - Extracts `values` for categorical fields

3. **Validation** - Ensures data integrity
   - Column names are unique
   - Required fields are present
   - Categorical columns have values defined
   - Numeric bounds are valid

4. **Pydantic Model Creation** - Creates type-safe objects
   - `DatasetSchema` object
   - List of `ColumnSchema` objects
   - Automatic validation on creation

**Example Output:**
```python
DatasetSchema(
    dataset_name="employee_records",
    rows=20,
    description="Employee information dataset",
    columns=[
        ColumnSchema(
            name="employee_id",
            type=ColumnType.INT,
            description="Unique employee identifier",
            min=1000.0,
            max=9999.0,
            nullable=False,
            required=True
        ),
        ColumnSchema(
            name="first_name",
            type=ColumnType.STRING,
            description="Employee first name",
            nullable=False,
            required=True
        ),
        ColumnSchema(
            name="department",
            type=ColumnType.CATEGORICAL,
            description="Department assignment",
            values=["Engineering", "Sales", "Marketing", "HR", "Finance"],
            nullable=False,
            required=True
        ),
        # ... more columns
    ],
    version="1.0",
    created_at="2026-02-11T16:37:01Z",
    source="llm"
)
```

---

## 🔧 Implementation Details

### **API Endpoint**

**Endpoint:** `POST /api/generate-schema`

**Request Body:**
```json
{
  "query": "Generate 50 customer records with purchase history",
  "use_kaggle": false,
  "use_rag": false,
  "enhanced_mode": true
}
```

**Response:**
```json
{
  "success": true,
  "schema": {
    "dataset_name": "customer_records",
    "rows": 50,
    "columns": [...],
    "version": "1.0",
    "created_at": "2026-02-11T16:37:01Z"
  },
  "metadata": {
    "dataset_name": "customer_records",
    "rows": 50,
    "column_count": 8,
    "version": "1.0",
    "created_at": "2026-02-11T16:37:01Z",
    "source": "llm"
  },
  "llm_raw_output": {...},
  "query": "Generate 50 customer records with purchase history",
  "flow": "llm_extraction → schema_validation"
}
```

---

## 🎨 Key Features

### **1. Semantic Understanding (LLM)**
- ✅ Infers domain-standard fields automatically
- ✅ Understands field relationships
- ✅ Applies realistic constraints
- ✅ Handles natural language queries

### **2. Robust Validation (Schema Mapper)**
- ✅ Type normalization across different LLM outputs
- ✅ Pydantic-based validation
- ✅ Ensures data integrity
- ✅ Produces consistent output format

### **3. Clean Separation of Concerns**
- ✅ LLM focuses on semantic understanding
- ✅ Schema Mapper focuses on validation
- ✅ Each component has a single responsibility
- ✅ Easy to test and maintain

---

## 📊 Comparison with Old Approach

| Aspect | **Old Approach** | **New Flow** |
|--------|------------------|--------------|
| **Field Extraction** | Pattern matching | LLM semantic understanding |
| **Type Handling** | Manual mapping | Normalized by schema mapper |
| **Validation** | Ad-hoc checks | Pydantic model validation |
| **Flexibility** | Limited to predefined patterns | Handles any domain |
| **Accuracy** | Misses implied fields | Infers domain standards |
| **Maintainability** | Scattered logic | Clean separation |

---

## 🚀 Usage Examples

### **Example 1: Simple Query**
```python
# Query
"Generate 10 product records"

# LLM extracts:
# - product_id, name, description, price, category, stock, rating, etc.

# Schema Mapper validates:
# - Ensures price is float with min > 0
# - Validates category has values
# - Normalizes types
```

### **Example 2: Complex Query**
```python
# Query
"Create a dataset of 100 e-commerce transactions with customer info, 
 product details, and payment information"

# LLM extracts:
# - transaction_id, customer_id, customer_name, customer_email
# - product_id, product_name, quantity, unit_price
# - total_amount, payment_method, transaction_date, status

# Schema Mapper validates:
# - All numeric fields have proper ranges
# - Categorical fields (payment_method, status) have values
# - Email fields are properly typed
```

---

## 🔍 Error Handling

### **LLM Extraction Errors**
- Invalid JSON → Returns error with details
- Missing required fields → Returns error
- Malformed structure → Returns error

### **Schema Validation Errors**
- Type mismatch → Pydantic ValidationError
- Missing categorical values → ValueError
- Duplicate column names → ValueError
- Invalid constraints → ValueError

All errors are caught and returned in a structured format:
```json
{
  "success": false,
  "error": "Detailed error message",
  "query": "original query",
  "flow": "llm_extraction → schema_validation"
}
```

---

## 📝 Code References

### **Main Implementation**
- **LLM Service:** `backend/gemini_service.py` (line 532-747)
- **Schema Mapper:** `backend/integrate/schema_mapper.py`
- **API Endpoint:** `backend/main.py` (line 315-361)

### **Models**
- **DatasetSchema:** `backend/integrate/schema_mapper.py` (line 116-177)
- **ColumnSchema:** `backend/integrate/schema_mapper.py` (line 64-113)
- **ColumnType Enum:** `backend/integrate/schema_mapper.py` (line 21-28)

---

## 🎯 Benefits

1. **Better Quality** - LLM understands domain semantics
2. **Type Safety** - Pydantic validation ensures correctness
3. **Flexibility** - Handles any domain without hardcoding
4. **Maintainability** - Clean separation of concerns
5. **Extensibility** - Easy to add new features
6. **Reliability** - Robust error handling

---

## 🔮 Future Enhancements

1. **Schema Caching** - Cache validated schemas for reuse
2. **Schema Templates** - Pre-defined templates for common domains
3. **Multi-table Support** - Generate related tables with foreign keys
4. **Schema Evolution** - Version control for schema changes
5. **Custom Validators** - User-defined validation rules

---

## 📚 Related Documentation

- [RAG Integration Guide](./RAG_INTEGRATION_GUIDE.md)
- [Architecture Overview](../ARCHITECTURE.md)
- [Project Structure](../PROJECT_STRUCTURE.md)

---

**Last Updated:** 2026-02-11  
**Version:** 1.0
