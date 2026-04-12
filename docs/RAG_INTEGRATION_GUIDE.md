# RAG Integration Guide - Complete Flow

## Overview
This document explains where and how to integrate RAG (Retrieval-Augmented Generation) into the data generation pipeline.

## Complete Flow with RAG

```
┌─────────────────────────────────────────────────────────────────────────┐
│ 1. USER ENTERS QUERY                                                    │
│    "Generate employee data for a tech company"                          │
└────────────────────────────┬────────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ 2. RAG RETRIEVAL (Optional - NEW STEP)                                  │
│    ┌─────────────────────────────────────────────────────────────────┐  │
│    │ a) Query Analysis                                               │  │
│    │    - Extract keywords: "employee", "tech company"               │  │
│    │    - Identify domain: HR/Employment                             │  │
│    └─────────────────────────────────────────────────────────────────┘  │
│                             │                                            │
│                             ▼                                            │
│    ┌─────────────────────────────────────────────────────────────────┐  │
│    │ b) Vector Search in Knowledge Base                              │  │
│    │    - Search for relevant documents about:                       │  │
│    │      • Tech company employee structures                         │  │
│    │      • Typical tech roles and salaries                          │  │
│    │      • Common tech departments                                  │  │
│    └─────────────────────────────────────────────────────────────────┘  │
│                             │                                            │
│                             ▼                                            │
│    ┌─────────────────────────────────────────────────────────────────┐  │
│    │ c) Retrieve Top-K Documents                                     │  │
│    │    RAG Output:                                                  │  │
│    │    {                                                            │  │
│    │      "context": [                                               │  │
│    │        "Tech companies typically have roles: SWE, DevOps, PM",  │  │
│    │        "Average tech salaries: Junior $80k, Senior $150k",      │  │
│    │        "Common departments: Engineering, Product, Data"         │  │
│    │      ],                                                         │  │
│    │      "sources": ["doc1.pdf", "doc2.pdf"],                       │  │
│    │      "relevance_scores": [0.92, 0.87, 0.85]                     │  │
│    │    }                                                            │  │
│    └─────────────────────────────────────────────────────────────────┘  │
└────────────────────────────┬────────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ 3. LLM FIELD EXTRACTION (First LLM Call)                                │
│    Input: User query + RAG context (optional)                           │
│    Output: Comprehensive field list                                     │
│    fields = ["employee_id", "name", "role", "department", "salary", ...]│
└────────────────────────────┬────────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ 4. SCHEMA MAPPER ANALYSIS                                               │
│    Input: Field list                                                    │
│    Output: Relationships, constraints, correlations                     │
└────────────────────────────┬────────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ 5. BUILD ENHANCED PROMPT                                                │
│    Combine:                                                             │
│    ✓ Original user query                                                │
│    ✓ RAG context ← INJECTED HERE                                        │
│    ✓ Kaggle context (if available)                                      │
│    ✓ Schema relationships                                               │
│    ✓ Field constraints                                                  │
│    ✓ Generation rules                                                   │
└────────────────────────────┬────────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ 6. LLM DATA GENERATION (Second LLM Call)                                │
│    Input: Enhanced prompt with RAG context                              │
│    Output: High-quality synthetic data informed by RAG knowledge        │
└────────────────────────────┬────────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ 7. POST-PROCESSING                                                      │
│    Data validation and quality checks                                   │
└────────────────────────────┬────────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ 8. RETURN TO USER                                                       │
│    High-quality, context-aware synthetic data                           │
└─────────────────────────────────────────────────────────────────────────┘
```

## Where to Put RAG: Two Integration Points

### Option 1: Before Field Extraction (Recommended)
**When**: Before calling `generate_data_enhanced()`
**Where**: In your API endpoint or application layer

```python
# In your API endpoint (e.g., app.py or main.py)

from backend.rag_service import rag_service  # You'll create this
from backend.gemini_service import gemini_service

async def generate_data_endpoint(user_query: str):
    # STEP 1: RAG Retrieval
    rag_context = await rag_service.retrieve_context(user_query)
    
    # STEP 2: Generate data with RAG context
    result = await gemini_service.generate_data_enhanced(
        user_query=user_query,
        rag_context=rag_context,  # ← RAG context injected here
        use_llm_extraction=True
    )
    
    return result
```

### Option 2: Inside Field Extraction (Advanced)
**When**: During LLM field extraction
**Where**: Enhance the `_extract_fields_with_llm()` method

```python
# In gemini_service.py

def _extract_fields_with_llm(self, query: str, rag_context: Dict = None) -> Dict[str, Any]:
    """Extract fields with RAG context"""
    
    extraction_prompt = f"""You are a data schema expert.
    
USER REQUEST: {query}

RELEVANT CONTEXT FROM KNOWLEDGE BASE:
{self._format_rag_context(rag_context) if rag_context else "No additional context"}

Based on the user request and context, extract comprehensive field list...
"""
    # ... rest of the method
```

## RAG Service Implementation

Here's how to create a RAG service:

### File: `backend/rag_service.py`

```python
"""
RAG Service for retrieving relevant context from knowledge base
"""

from typing import Dict, List, Any
import chromadb
from sentence_transformers import SentenceTransformer

class RAGService:
    """Retrieval-Augmented Generation service"""
    
    def __init__(self, collection_name: str = "data_generation_kb"):
        # Initialize embedding model
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Initialize vector database (ChromaDB)
        self.client = chromadb.PersistentClient(path="./chroma_db")
        
        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"description": "Knowledge base for data generation"}
        )
    
    async def retrieve_context(self, query: str, top_k: int = 3) -> Dict[str, Any]:
        """
        Retrieve relevant context from knowledge base
        
        Args:
            query: User's query
            top_k: Number of top documents to retrieve
            
        Returns:
            Dictionary with context and metadata
        """
        try:
            # Generate query embedding
            query_embedding = self.embedding_model.encode(query).tolist()
            
            # Search in vector database
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k
            )
            
            # Format results
            if results and results['documents']:
                context = {
                    "context": results['documents'][0],  # List of relevant texts
                    "sources": results['metadatas'][0] if results['metadatas'] else [],
                    "distances": results['distances'][0] if results['distances'] else []
                }
                return context
            else:
                return {"context": [], "sources": [], "distances": []}
                
        except Exception as e:
            print(f"RAG retrieval failed: {str(e)}")
            return {"context": [], "sources": [], "distances": []}
    
    def add_documents(self, documents: List[str], metadatas: List[Dict] = None):
        """
        Add documents to knowledge base
        
        Args:
            documents: List of text documents
            metadatas: Optional metadata for each document
        """
        # Generate embeddings
        embeddings = self.embedding_model.encode(documents).tolist()
        
        # Generate IDs
        ids = [f"doc_{i}" for i in range(len(documents))]
        
        # Add to collection
        self.collection.add(
            embeddings=embeddings,
            documents=documents,
            metadatas=metadatas or [{} for _ in documents],
            ids=ids
        )

# Create singleton instance
rag_service = RAGService()
```

## How RAG Context is Used

Looking at your existing code (lines 108-114 in `gemini_service.py`):

```python
# Add RAG context if available
if rag_context:
    prompt_parts.append("=== CONTEXT FROM KNOWLEDGE BASE ===")
    if isinstance(rag_context, dict) and rag_context.get("context"):
        for ctx in rag_context["context"]:
            prompt_parts.append(f"- {ctx}")
    prompt_parts.append("")
```

The RAG context is inserted into the prompt **before** schema mapping, so the LLM sees:

```
USER REQUEST: Generate employee data for a tech company

=== CONTEXT FROM KNOWLEDGE BASE ===
- Tech companies typically have roles: Software Engineer, DevOps, Product Manager
- Average tech salaries: Junior $80k, Mid $120k, Senior $150k
- Common departments: Engineering, Product, Data Science, DevOps

=== SEMANTIC SCHEMA RELATIONSHIPS ===
[Schema mapping rules...]

=== GENERATION INSTRUCTIONS ===
[Generation rules...]

Generate the data now:
```

## Example RAG Integration

### Complete Example:

```python
# File: backend/app.py or your API endpoint

from fastapi import FastAPI
from backend.rag_service import rag_service
from backend.gemini_service import gemini_service

app = FastAPI()

@app.post("/generate-data")
async def generate_data(request: dict):
    user_query = request.get("query")
    use_rag = request.get("use_rag", True)
    
    # Step 1: Retrieve RAG context (if enabled)
    rag_context = None
    if use_rag:
        rag_context = await rag_service.retrieve_context(user_query)
    
    # Step 2: Generate data with RAG context
    result = await gemini_service.generate_data_enhanced(
        user_query=user_query,
        rag_context=rag_context,
        use_llm_extraction=True
    )
    
    return result

@app.post("/add-knowledge")
async def add_knowledge(request: dict):
    """Add documents to RAG knowledge base"""
    documents = request.get("documents", [])
    metadatas = request.get("metadatas", None)
    
    rag_service.add_documents(documents, metadatas)
    
    return {"status": "success", "count": len(documents)}
```

## RAG Context Format

The `rag_context` should be a dictionary:

```python
{
    "context": [
        "Relevant fact 1",
        "Relevant fact 2",
        "Relevant fact 3"
    ],
    "sources": [
        {"file": "doc1.pdf", "page": 5},
        {"file": "doc2.pdf", "page": 12},
        {"file": "doc3.pdf", "page": 3}
    ],
    "distances": [0.15, 0.23, 0.31]  # Lower is more relevant
}
```

## Benefits of RAG Integration

1. **Domain Knowledge**: Inject industry-specific knowledge
2. **Realistic Data**: Generate data based on real-world patterns
3. **Consistency**: Ensure data matches known facts
4. **Customization**: Tailor data to specific use cases
5. **Quality**: Higher quality through informed generation

## Example Use Cases

### Use Case 1: Tech Company Employees
```python
# Add knowledge to RAG
rag_service.add_documents([
    "Tech companies have roles: SWE, DevOps, PM, Designer, Data Scientist",
    "Typical tech salaries: Junior $80k, Mid $120k, Senior $150k+",
    "Common tech stacks: Python, JavaScript, React, Node.js, AWS"
])

# Generate with RAG
result = await gemini_service.generate_data_enhanced(
    user_query="Generate tech company employee data",
    rag_context=await rag_service.retrieve_context("tech company employees")
)
```

### Use Case 2: E-commerce Products
```python
# Add knowledge
rag_service.add_documents([
    "Popular product categories: Electronics, Clothing, Home & Garden",
    "Price ranges: Electronics $50-$2000, Clothing $20-$200",
    "Typical ratings: 3.5-4.8 stars, 10-500 reviews"
])

# Generate with RAG
result = await gemini_service.generate_data_enhanced(
    user_query="Generate e-commerce product catalog",
    rag_context=await rag_service.retrieve_context("e-commerce products")
)
```

## Summary: Where RAG Fits

```
API Layer (app.py)
    ↓
    RAG Retrieval ← PUT RAG HERE (Option 1 - Recommended)
    ↓
    rag_context = {...}
    ↓
gemini_service.generate_data_enhanced(rag_context=rag_context)
    ↓
    Field Extraction (can also use RAG here - Option 2)
    ↓
    Schema Mapper
    ↓
    Build Enhanced Prompt (RAG context injected here - lines 108-114)
    ↓
    LLM Generation
    ↓
    Post-Processing
    ↓
    Return Data
```

**Recommendation**: Put RAG retrieval **before** calling `generate_data_enhanced()` (Option 1) for maximum flexibility and separation of concerns.
