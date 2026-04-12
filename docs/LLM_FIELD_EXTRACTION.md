# LLM-Powered Field Extraction Architecture

## Overview
This document explains how the enhanced field extraction system works using LLM preprocessing.

## Architecture Flow

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         USER ENTERS QUERY                               │
│  "Generate healthcare patient data with 20 records"                     │
└────────────────────────────┬────────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                    PREPROCESSING PHASE                                  │
│  ┌───────────────────────────────────────────────────────────────────┐  │
│  │  STEP 1: LLM Field Extraction (First LLM Call)                    │  │
│  │  ────────────────────────────────────────────────────────────────  │  │
│  │  Input: User query                                                │  │
│  │  Process: LLM analyzes domain and extracts comprehensive fields   │  │
│  │  Output:                                                          │  │
│  │    {                                                              │  │
│  │      "entity_type": "patient",                                    │  │
│  │      "fields": [                                                  │  │
│  │        "patient_id" (domain_standard, unique),                    │  │
│  │        "first_name" (inferred),                                   │  │
│  │        "last_name" (inferred),                                    │  │
│  │        "date_of_birth" (domain_standard),                         │  │
│  │        "medical_record_number" (domain_standard, unique),         │  │
│  │        "diagnosis" (domain_standard),                             │  │
│  │        "insurance_provider" (domain_standard),                    │  │
│  │        "admission_date" (inferred),                               │  │
│  │        "discharge_date" (inferred),                               │  │
│  │        "attending_physician" (domain_standard)                    │  │
│  │      ]                                                            │  │
│  │    }                                                              │  │
│  └───────────────────────────────────────────────────────────────────┘  │
│                             │                                            │
│                             ▼                                            │
│  ┌───────────────────────────────────────────────────────────────────┐  │
│  │  STEP 2: Schema Mapper Analysis                                   │  │
│  │  ────────────────────────────────────────────────────────────────  │  │
│  │  Input: Field list from LLM                                       │  │
│  │  Process: Analyze relationships, constraints, correlations        │  │
│  │  Output:                                                          │  │
│  │    - Field classifications (id, name, date, etc.)                 │  │
│  │    - Constraints (age: 0-120, etc.)                               │  │
│  │    - Relationships (email ↔ name)                                 │  │
│  │    - Dependencies (total = price × quantity)                      │  │
│  │    - Correlations (age ↔ salary)                                  │  │
│  └───────────────────────────────────────────────────────────────────┘  │
│                             │                                            │
│                             ▼                                            │
│  ┌───────────────────────────────────────────────────────────────────┐  │
│  │  STEP 3: Build Enhanced Prompt                                    │  │
│  │  ────────────────────────────────────────────────────────────────  │  │
│  │  Combine:                                                         │  │
│  │    ✓ Original user query                                          │  │
│  │    ✓ Schema relationship rules                                    │  │
│  │    ✓ Field constraints                                            │  │
│  │    ✓ RAG context (if available)                                   │  │
│  │    ✓ Kaggle context (if available)                                │  │
│  │    ✓ Generation instructions                                      │  │
│  └───────────────────────────────────────────────────────────────────┘  │
└────────────────────────────┬────────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                    LLM GENERATION PHASE                                 │
│  ┌───────────────────────────────────────────────────────────────────┐  │
│  │  STEP 4: Data Generation (Second LLM Call)                        │  │
│  │  ────────────────────────────────────────────────────────────────  │  │
│  │  Input: Enhanced prompt with all context                          │  │
│  │  Process: LLM generates data following all rules                  │  │
│  │  Output: High-quality synthetic data                              │  │
│  └───────────────────────────────────────────────────────────────────┘  │
└────────────────────────────┬────────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                    POST-PROCESSING PHASE                                │
│  ┌───────────────────────────────────────────────────────────────────┐  │
│  │  STEP 5: Data Post-Processor                                      │  │
│  │  ────────────────────────────────────────────────────────────────  │  │
│  │  - Fix email-name mismatches                                      │  │
│  │  - Ensure uniqueness of IDs                                       │  │
│  │  - Validate data types                                            │  │
│  │  - Apply final quality checks                                     │  │
│  └───────────────────────────────────────────────────────────────────┘  │
└────────────────────────────┬────────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                         RETURN TO USER                                  │
│  High-quality synthetic data with comprehensive schema                  │
└─────────────────────────────────────────────────────────────────────────┘
```

## Comparison: Pattern Matching vs LLM Extraction

### Pattern Matching (Old Method)
```python
Query: "Generate healthcare patient data"
↓
Pattern Match: ["patient"]  # Only finds "patient" keyword
↓
Limited fields, generic schema
```

### LLM Extraction (New Method)
```python
Query: "Generate healthcare patient data"
↓
LLM Analysis: 
  - Domain: Healthcare
  - Entity: Patient
  - Inferred fields: patient_id, first_name, last_name, date_of_birth,
                     medical_record_number, diagnosis, insurance_provider,
                     admission_date, discharge_date, attending_physician
↓
Comprehensive, domain-specific schema
```

## Benefits

1. **Domain Intelligence**: Understands healthcare, e-commerce, finance, etc.
2. **Field Inference**: Adds relevant fields not explicitly mentioned
3. **Type Awareness**: Suggests appropriate data types
4. **Uniqueness Detection**: Identifies which fields should be unique
5. **Comprehensive Coverage**: Much more complete than pattern matching

## Example Output

### Input Query
```
"Generate e-commerce order data"
```

### LLM Field Extraction Output
```json
{
  "entity_type": "order",
  "record_count": 10,
  "fields": [
    {"name": "order_id", "type": "integer", "source": "domain_standard", "is_unique": true},
    {"name": "customer_name", "type": "string", "source": "domain_standard", "is_unique": false},
    {"name": "customer_email", "type": "email", "source": "domain_standard", "is_unique": false},
    {"name": "product_name", "type": "string", "source": "domain_standard", "is_unique": false},
    {"name": "quantity", "type": "integer", "source": "domain_standard", "is_unique": false},
    {"name": "unit_price", "type": "float", "source": "domain_standard", "is_unique": false},
    {"name": "total_amount", "type": "float", "source": "inferred", "is_unique": false},
    {"name": "order_date", "type": "date", "source": "domain_standard", "is_unique": false},
    {"name": "shipping_address", "type": "string", "source": "domain_standard", "is_unique": false},
    {"name": "payment_method", "type": "string", "source": "domain_standard", "is_unique": false},
    {"name": "order_status", "type": "string", "source": "domain_standard", "is_unique": false}
  ]
}
```

### Schema Mapper Output
```
=== SEMANTIC SCHEMA RELATIONSHIPS ===

FIELD CLASSIFICATIONS:
  - order_id: id
  - customer_name: name
  - customer_email: email
  - product_name: name
  - quantity: quantity
  - unit_price: price
  - total_amount: price
  - order_date: date
  - shipping_address: location
  - payment_method: general
  - order_status: status

FIELD CONSTRAINTS:
  - unit_price: type=float, min=0, decimal_places=2
  - total_amount: type=float, min=0, decimal_places=2
  - quantity: type=int, min=0

RELATIONSHIP RULES:
  1. ID fields (order_id) should be unique and sequential
  2. Email addresses should semantically relate to names
  3. Higher quantity values correlate with higher total_amount values

FIELD DEPENDENCIES:
  - total_amount depends on unit_price, quantity (multiply)
```

## Usage

```python
# Enable LLM extraction (default)
result = await gemini_service.generate_data_enhanced(
    user_query="Generate employee data",
    use_llm_extraction=True  # New parameter
)

# Disable LLM extraction (use pattern matching)
result = await gemini_service.generate_data_enhanced(
    user_query="Generate employee data",
    use_llm_extraction=False
)
```

## Performance Considerations

- **LLM Extraction**: Adds ~1-2 seconds (one extra LLM call)
- **Benefit**: Much more comprehensive and accurate field lists
- **Fallback**: Automatically falls back to pattern matching if LLM fails
- **Trade-off**: Slightly slower but significantly better quality
