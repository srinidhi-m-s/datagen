# Test Schema Flow - Usage Guide

## 🎯 **Yes! The test script now accepts different user queries!**

You can provide your query in **3 different ways**:

---

## **Method 1: Interactive Mode (Recommended)**

Just run the script and it will ask you for a query:

```bash
python backend/test_schema_flow.py
```

**Output:**
```
🚀 Starting Schema Generation Flow Test...

====================================================================================================
SCHEMA GENERATION FLOW TEST - Interactive Mode
====================================================================================================

Enter your data generation query (or press Enter for default):
Examples:
  - Generate 10 employee records
  - Create 20 customer records with purchase history
  - Generate 50 product records for an e-commerce store

Your query: _
```

**Then type your query and press Enter!**

---

## **Method 2: Command Line Argument**

Pass your query as a command line argument:

```bash
python backend/test_schema_flow.py "Generate 20 customer records with purchase history"
```

```bash
python backend/test_schema_flow.py "Create 50 product records for an e-commerce store"
```

```bash
python backend/test_schema_flow.py "Generate 100 transaction records with customer and product details"
```

---

## **Method 3: Default Query**

Just press Enter when prompted (or run with no arguments and press Enter):

```bash
python backend/test_schema_flow.py
# Press Enter when asked for query
```

**Uses default:** `"Generate 15 employee records"`

---

## 📋 **Example Queries to Try**

### **Simple Queries:**
```bash
python backend/test_schema_flow.py "Generate 10 employee records"
python backend/test_schema_flow.py "Create 20 customer records"
python backend/test_schema_flow.py "Generate 30 product records"
```

### **Complex Queries:**
```bash
python backend/test_schema_flow.py "Generate 50 customer records with name, email, age, phone, address, and membership tier"

python backend/test_schema_flow.py "Create 25 product records with SKU, name, category, price, stock quantity, and description"

python backend/test_schema_flow.py "Generate 40 transaction records with transaction ID, customer ID, product, amount, date, and payment method"
```

### **Domain-Specific Queries:**
```bash
# E-commerce
python backend/test_schema_flow.py "Generate 100 e-commerce orders with customer info, products, and payment details"

# Healthcare
python backend/test_schema_flow.py "Create 50 patient records with demographics, medical history, and appointments"

# Finance
python backend/test_schema_flow.py "Generate 75 financial transactions with account details, amounts, and timestamps"

# Education
python backend/test_schema_flow.py "Create 60 student records with enrollment info, grades, and courses"
```

---

## 🎨 **What You'll See**

For any query you provide, the script will show:

1. **STEP 1: LLM OUTPUT**
   - Raw JSON from Gemini
   - Dataset name, rows, columns

2. **STEP 2: SCHEMA MAPPER OUTPUT**
   - Validated and normalized schema
   - Type-safe Pydantic output

3. **TRANSFORMATION COMPARISON**
   - Table showing LLM type → Normalized type

4. **KEY TRANSFORMATIONS**
   - Detailed view of first 4 columns

5. **VALIDATION COMPLETE**
   - Final metadata and summary

---

## 💡 **Tips**

- **Be specific:** More details = better schema
- **Include field names:** "with name, email, age" helps the LLM
- **Specify row count:** "Generate 50..." tells it how many rows
- **Add context:** "for an e-commerce store" adds domain knowledge

---

## 🚀 **Quick Test**

Try this right now:

```bash
python backend/test_schema_flow.py "Generate 25 movie records with title, director, year, genre, and rating"
```

You'll see the complete flow from LLM extraction to validated schema! 🎉

---

## ⚠️ **Requirements**

Make sure you have:
- ✅ `GEMINI_API_KEY` set in your `.env` file
- ✅ Internet connection (to call Gemini API)
- ✅ Backend dependencies installed

---

**The script is fully interactive and ready to test any query you want!** 🎯
