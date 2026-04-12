"""
RAG Service for Data Generation
Retrieves relevant context from knowledge base to enhance data generation
"""

from typing import Dict, List, Any, Optional
import os
import json

class RAGService:
    """
    Retrieval-Augmented Generation service
    Provides context from knowledge base to improve data generation quality
    """
    
    def __init__(self):
        """Initialize RAG service"""
        self.knowledge_base = {}
        self.use_vector_db = False
        
        # Try to initialize vector database (optional)
        try:
            self._init_vector_db()
        except ImportError:
            print("Vector database not available. Using simple keyword-based retrieval.")
            print("Install chromadb and sentence-transformers for better RAG: pip install chromadb sentence-transformers")
    
    def _init_vector_db(self):
        """Initialize vector database (ChromaDB) if available"""
        try:
            import chromadb
            from sentence_transformers import SentenceTransformer
            
            # Initialize embedding model
            self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
            
            # Initialize vector database
            self.client = chromadb.PersistentClient(path="./chroma_db")
            
            # Get or create collection
            self.collection = self.client.get_or_create_collection(
                name="data_generation_kb",
                metadata={"description": "Knowledge base for data generation"}
            )
            
            self.use_vector_db = True
            print("✓ Vector database initialized successfully")
            
        except ImportError as e:
            print(f"Vector database libraries not installed: {e}")
            self.use_vector_db = False
    
    async def retrieve_context(self, query: str, top_k: int = 3) -> Dict[str, Any]:
        """
        Retrieve relevant context from knowledge base
        
        Args:
            query: User's query
            top_k: Number of top documents to retrieve
            
        Returns:
            Dictionary with context and metadata
        """
        if self.use_vector_db:
            return await self._retrieve_with_vector_db(query, top_k)
        else:
            return await self._retrieve_with_keywords(query, top_k)
    
    async def _retrieve_with_vector_db(self, query: str, top_k: int = 3) -> Dict[str, Any]:
        """Retrieve using vector database (semantic search)"""
        try:
            # Generate query embedding
            query_embedding = self.embedding_model.encode(query).tolist()
            
            # Search in vector database
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k
            )
            
            # Format results
            if results and results['documents'] and len(results['documents'][0]) > 0:
                context = {
                    "context": results['documents'][0],
                    "sources": results['metadatas'][0] if results['metadatas'] else [],
                    "distances": results['distances'][0] if results['distances'] else [],
                    "method": "vector_search"
                }
                return context
            else:
                return {
                    "context": [],
                    "sources": [],
                    "distances": [],
                    "method": "vector_search"
                }
                
        except Exception as e:
            print(f"Vector search failed: {str(e)}")
            return {
                "context": [],
                "sources": [],
                "distances": [],
                "error": str(e),
                "method": "vector_search"
            }
    
    async def _retrieve_with_keywords(self, query: str, top_k: int = 3) -> Dict[str, Any]:
        """Retrieve using simple keyword matching (fallback)"""
        query_lower = query.lower()
        query_words = set(query_lower.split())
        
        # Score documents based on keyword overlap
        scored_docs = []
        for doc_id, doc_data in self.knowledge_base.items():
            doc_text = doc_data.get("text", "").lower()
            doc_words = set(doc_text.split())
            
            # Calculate overlap score
            overlap = len(query_words.intersection(doc_words))
            if overlap > 0:
                scored_docs.append({
                    "text": doc_data.get("text", ""),
                    "metadata": doc_data.get("metadata", {}),
                    "score": overlap
                })
        
        # Sort by score and take top_k
        scored_docs.sort(key=lambda x: x["score"], reverse=True)
        top_docs = scored_docs[:top_k]
        
        return {
            "context": [doc["text"] for doc in top_docs],
            "sources": [doc["metadata"] for doc in top_docs],
            "scores": [doc["score"] for doc in top_docs],
            "method": "keyword_matching"
        }
    
    def add_documents(self, documents: List[str], metadatas: List[Dict] = None, ids: List[str] = None):
        """
        Add documents to knowledge base
        
        Args:
            documents: List of text documents
            metadatas: Optional metadata for each document
            ids: Optional IDs for documents
        """
        if not metadatas:
            metadatas = [{} for _ in documents]
        
        if not ids:
            ids = [f"doc_{i}" for i in range(len(self.knowledge_base), len(self.knowledge_base) + len(documents))]
        
        if self.use_vector_db:
            self._add_to_vector_db(documents, metadatas, ids)
        else:
            self._add_to_simple_kb(documents, metadatas, ids)
    
    def _add_to_vector_db(self, documents: List[str], metadatas: List[Dict], ids: List[str]):
        """Add documents to vector database"""
        try:
            # Generate embeddings
            embeddings = self.embedding_model.encode(documents).tolist()
            
            # Add to collection
            self.collection.add(
                embeddings=embeddings,
                documents=documents,
                metadatas=metadatas,
                ids=ids
            )
            print(f"✓ Added {len(documents)} documents to vector database")
            
        except Exception as e:
            print(f"Failed to add to vector database: {str(e)}")
    
    def _add_to_simple_kb(self, documents: List[str], metadatas: List[Dict], ids: List[str]):
        """Add documents to simple keyword-based knowledge base"""
        for doc_id, doc_text, metadata in zip(ids, documents, metadatas):
            self.knowledge_base[doc_id] = {
                "text": doc_text,
                "metadata": metadata
            }
        print(f"✓ Added {len(documents)} documents to knowledge base")
    
    def load_from_file(self, filepath: str):
        """
        Load knowledge base from JSON file
        
        Args:
            filepath: Path to JSON file with documents
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            documents = data.get("documents", [])
            metadatas = data.get("metadatas", None)
            ids = data.get("ids", None)
            
            self.add_documents(documents, metadatas, ids)
            print(f"✓ Loaded knowledge base from {filepath}")
            
        except Exception as e:
            print(f"Failed to load knowledge base: {str(e)}")
    
    def save_to_file(self, filepath: str):
        """
        Save simple knowledge base to JSON file
        
        Args:
            filepath: Path to save JSON file
        """
        if not self.use_vector_db:
            try:
                data = {
                    "documents": [v["text"] for v in self.knowledge_base.values()],
                    "metadatas": [v["metadata"] for v in self.knowledge_base.values()],
                    "ids": list(self.knowledge_base.keys())
                }
                
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2)
                
                print(f"✓ Saved knowledge base to {filepath}")
                
            except Exception as e:
                print(f"Failed to save knowledge base: {str(e)}")
        else:
            print("Vector database is persistent. No need to save manually.")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about the knowledge base"""
        if self.use_vector_db:
            try:
                count = self.collection.count()
                return {
                    "method": "vector_database",
                    "document_count": count,
                    "collection_name": self.collection.name
                }
            except:
                return {"method": "vector_database", "document_count": 0}
        else:
            return {
                "method": "keyword_matching",
                "document_count": len(self.knowledge_base)
            }


# Create singleton instance
rag_service = RAGService()


# Example usage and default knowledge base
def initialize_default_knowledge():
    """Initialize with some default domain knowledge"""
    
    default_docs = [
        # Employee/HR domain
        "Tech companies typically have roles: Software Engineer, DevOps Engineer, Product Manager, Designer, Data Scientist, QA Engineer",
        "Typical tech salaries in USD: Junior $60k-$90k, Mid-level $90k-$130k, Senior $130k-$180k, Staff/Principal $180k-$250k",
        "Common tech departments: Engineering, Product, Design, Data Science, DevOps, QA, Marketing, Sales",
        "Tech company benefits often include: Health insurance, 401k matching, Stock options, Remote work, Unlimited PTO",
        
        # E-commerce domain
        "Popular e-commerce product categories: Electronics, Clothing, Home & Garden, Books, Sports, Toys, Beauty",
        "E-commerce price ranges: Electronics $50-$2000, Clothing $20-$200, Home items $30-$500",
        "Typical product ratings: 3.5-4.8 stars with 10-500 reviews for popular items",
        "Common payment methods: Credit Card, Debit Card, PayPal, Apple Pay, Google Pay",
        
        # Healthcare domain
        "Common medical departments: Emergency, Cardiology, Neurology, Pediatrics, Oncology, Orthopedics",
        "Healthcare insurance providers: Blue Cross, Aetna, UnitedHealth, Cigna, Kaiser Permanente",
        "Common diagnoses: Hypertension, Diabetes, Asthma, Arthritis, Depression, Anxiety",
        
        # Finance domain
        "Transaction types: Purchase, Refund, Transfer, Withdrawal, Deposit, Payment",
        "Common merchant categories: Grocery, Gas Station, Restaurant, Online Shopping, Utilities",
        "Typical transaction amounts: Grocery $50-$200, Gas $30-$80, Restaurant $20-$100"
    ]
    
    metadatas = [
        {"domain": "hr", "topic": "roles"},
        {"domain": "hr", "topic": "salaries"},
        {"domain": "hr", "topic": "departments"},
        {"domain": "hr", "topic": "benefits"},
        {"domain": "ecommerce", "topic": "categories"},
        {"domain": "ecommerce", "topic": "pricing"},
        {"domain": "ecommerce", "topic": "ratings"},
        {"domain": "ecommerce", "topic": "payments"},
        {"domain": "healthcare", "topic": "departments"},
        {"domain": "healthcare", "topic": "insurance"},
        {"domain": "healthcare", "topic": "diagnoses"},
        {"domain": "finance", "topic": "transactions"},
        {"domain": "finance", "topic": "merchants"},
        {"domain": "finance", "topic": "amounts"}
    ]
    
    rag_service.add_documents(default_docs, metadatas)
    print("✓ Initialized default knowledge base")


# Initialize on import
initialize_default_knowledge()
