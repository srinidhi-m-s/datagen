"""
Data Generation AI Platform - FastAPI Backend
With Schema Mapping, Filtering, and Performance Comparison
"""

import os
import sys
from pathlib import Path

# Add backend directory to path for imports
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir.parent))

from fastapi import FastAPI, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="Data Generation AI Platform",
    description="Generate realistic synthetic data using AI with semantic schema mapping",
    version="2.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request/Response Models
class DataGenerationRequest(BaseModel):
    query: str = Field(..., description="Natural language query describing desired data")
    use_kaggle: bool = Field(default=False, description="Use Kaggle dataset context")
    use_rag: bool = Field(default=False, description="Use RAG enhancement")
    enhanced_mode: bool = Field(default=True, description="Use enhanced mode with schema mapping")

class CompareRequest(BaseModel):
    query: str = Field(..., description="Natural language query for comparison")
    use_kaggle: bool = Field(default=False, description="Use Kaggle dataset context")
    use_rag: bool = Field(default=False, description="Use RAG enhancement")

class FilterRequest(BaseModel):
    data: List[Dict[str, Any]] = Field(..., description="Data to filter")
    filters: Dict[str, Any] = Field(..., description="Filter criteria")

class ValidationRequest(BaseModel):
    data: List[Dict[str, Any]] = Field(..., description="Data to validate")
    constraints: Optional[Dict[str, Any]] = Field(default=None, description="Validation constraints")

class SchemaAnalysisRequest(BaseModel):
    fields: List[str] = Field(..., description="List of field names to analyze")

class AnalyzeQueryRequest(BaseModel):
    query: str = Field(..., description="Query to analyze")

# Initialize services after app is defined
try:
    from backend.gemini_service import gemini_service
    from backend.mock_services import mock_kaggle_service, mock_rag_service
    from backend.schema_mapper import schema_mapper
    from backend.data_filter import data_filter
    from backend.performance_comparator import performance_comparator
    services_loaded = True
except Exception as e:
    services_loaded = False
    service_error = str(e)

# Mount static files
frontend_path = Path(__file__).parent.parent / "frontend"
if frontend_path.exists():
    app.mount("/static", StaticFiles(directory=str(frontend_path / "static")), name="static")

# Routes
@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve the main HTML page"""
    index_path = frontend_path / "index.html"
    if index_path.exists():
        return FileResponse(str(index_path))
    return HTMLResponse("<h1>Data Generation AI Platform</h1><p>Frontend not found</p>")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": "2.0.0",
        "services_loaded": services_loaded,
        "features": [
            "schema_mapping",
            "data_filtering",
            "performance_comparison",
            "normal_vs_enhanced_modes"
        ]
    }

@app.post("/api/generate")
async def generate_data(request: DataGenerationRequest):
    """
    Generate synthetic data using AI
    
    Supports two modes:
    - Normal: Basic LLM generation
    - Enhanced: With schema mapping, relationships, and validation
    """
    if not services_loaded:
        raise HTTPException(status_code=500, detail=f"Services not loaded: {service_error}")
    
    try:
        if not request.query or len(request.query.strip()) == 0:
            raise HTTPException(status_code=400, detail="Query cannot be empty")
        
        # Get optional contexts
        kaggle_context = None
        rag_context = None
        
        if request.use_kaggle:
            kaggle_result = await mock_kaggle_service.search_datasets(request.query)
            kaggle_context = kaggle_result
        
        if request.use_rag:
            rag_result = await mock_rag_service.get_context(request.query)
            rag_context = rag_result
        
        # Generate data
        result = await gemini_service.generate_data(
            request.query,
            enhanced=request.enhanced_mode,
            rag_context=rag_context,
            kaggle_context=kaggle_context
        )
        
        if not result.get("success"):
            raise HTTPException(status_code=500, detail=result.get("error", "Data generation failed"))
        
        response = {
            "success": True,
            "mode": result.get("mode", "enhanced"),
            "data": result["data"],
            "metadata": {
                "record_count": result["record_count"],
                "schema": result["schema"],
                "query": result["query"]
            },
            "metrics": result.get("metrics"),
            "validation": result.get("validation"),
            "schema_analysis": result.get("schema_analysis")
        }
        
        if kaggle_context:
            response["kaggle_context"] = kaggle_context
        if rag_context:
            response["rag_context"] = rag_context
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.post("/api/compare")
async def compare_modes(request: CompareRequest):
    """
    Compare Normal LLM vs Enhanced LLM performance
    
    Generates data using both modes and provides detailed comparison metrics
    """
    if not services_loaded:
        raise HTTPException(status_code=500, detail=f"Services not loaded: {service_error}")
    
    try:
        if not request.query or len(request.query.strip()) == 0:
            raise HTTPException(status_code=400, detail="Query cannot be empty")
        
        # Get optional contexts
        kaggle_context = None
        rag_context = None
        
        if request.use_kaggle:
            kaggle_result = await mock_kaggle_service.search_datasets(request.query)
            kaggle_context = kaggle_result
        
        if request.use_rag:
            rag_result = await mock_rag_service.get_context(request.query)
            rag_context = rag_result
        
        # Compare modes
        result = await gemini_service.compare_modes(
            request.query,
            rag_context=rag_context,
            kaggle_context=kaggle_context
        )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.post("/api/filter")
async def filter_data(request: FilterRequest):
    """
    Filter generated data based on criteria
    
    Supports: eq, ne, gt, lt, gte, lte, contains, in
    """
    if not services_loaded:
        raise HTTPException(status_code=500, detail=f"Services not loaded: {service_error}")
    
    try:
        filtered = data_filter.filter_data(request.data, request.filters)
        
        return {
            "success": True,
            "original_count": len(request.data),
            "filtered_count": len(filtered),
            "data": filtered
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Filter error: {str(e)}")

@app.post("/api/validate")
async def validate_data(request: ValidationRequest):
    """
    Validate data against schema and constraints
    """
    if not services_loaded:
        raise HTTPException(status_code=500, detail=f"Services not loaded: {service_error}")
    
    try:
        validation = data_filter.validate_data(request.data, request.constraints)
        
        return {
            "success": True,
            "validation": validation
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Validation error: {str(e)}")

@app.post("/api/analyze-schema")
async def analyze_schema(request: SchemaAnalysisRequest):
    """
    Analyze schema fields and identify semantic relationships
    """
    if not services_loaded:
        raise HTTPException(status_code=500, detail=f"Services not loaded: {service_error}")
    
    try:
        analysis = schema_mapper.analyze_schema(request.fields)
        relationship_prompt = schema_mapper.generate_relationship_prompt(request.fields)
        
        return {
            "success": True,
            "analysis": analysis,
            "relationship_prompt": relationship_prompt
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Schema analysis error: {str(e)}")

@app.post("/api/analyze")
async def analyze_query(request: AnalyzeQueryRequest):
    """
    Analyze a query to extract intent and parameters
    """
    if not services_loaded:
        raise HTTPException(status_code=500, detail=f"Services not loaded: {service_error}")
    
    try:
        result = gemini_service.analyze_query(request.query)
        
        if not result["success"]:
            raise HTTPException(status_code=500, detail=result.get("error", "Analysis failed"))
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis error: {str(e)}")

@app.get("/api/statistics")
async def get_statistics():
    """
    Get performance statistics from all generation runs
    """
    if not services_loaded:
        raise HTTPException(status_code=500, detail=f"Services not loaded: {service_error}")
    
    try:
        stats = performance_comparator.get_statistics()
        return {
            "success": True,
            "statistics": stats
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Statistics error: {str(e)}")

@app.post("/api/generate-schema")
async def generate_schema(request: DataGenerationRequest):
    """
    Generate validated schema using the new flow:
    User Query → LLM Schema Extraction → Schema Mapper Validation
    
    This endpoint demonstrates the clean integration between LLM and schema_mapper.
    The LLM does semantic understanding and field extraction, then the schema_mapper
    validates and normalizes the output to produce a perfect schema.
    """
    if not services_loaded:
        raise HTTPException(status_code=500, detail=f"Services not loaded: {service_error}")
    
    try:
        if not request.query or len(request.query.strip()) == 0:
            raise HTTPException(status_code=400, detail="Query cannot be empty")
        
        # Get optional contexts
        kaggle_context = None
        rag_context = None
        
        if request.use_kaggle:
            kaggle_result = await mock_kaggle_service.search_datasets(request.query)
            kaggle_context = kaggle_result
        
        if request.use_rag:
            rag_result = await mock_rag_service.get_context(request.query)
            rag_context = rag_result
        
        # Generate validated schema using new flow
        result = await gemini_service.generate_schema_with_validation(
            request.query,
            rag_context=rag_context,
            kaggle_context=kaggle_context
        )
        
        if not result.get("success"):
            raise HTTPException(status_code=500, detail=result.get("error", "Schema generation failed"))
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

# Startup event
@app.on_event("startup")
async def startup_event():
    """Display startup message"""
    print("\n" + "="*62)
    print("║" + " "*60 + "║")
    print("║        Data Generation AI Platform v2.0                   ║")
    print("║        Powered by Google Gemini API                       ║")
    print("║        With Schema Mapping & Performance Comparison       ║")
    print("║" + " "*60 + "║")
    print("="*62)
    print()
    print("🚀 Server starting on http://0.0.0.0:8000")
    print("📚 API Documentation: http://0.0.0.0:8000/docs")
    print("🏥 Health Check: http://0.0.0.0:8000/health")
    print("📊 Performance Stats: http://0.0.0.0:8000/api/statistics")
    print()
    print("⚠️  Make sure you have set GEMINI_API_KEY in your .env file")
    print("    Get your free API key: https://makersuite.google.com/app/apikey")
    print()
    print("🆕 New Features in v2.0:")
    print("    - Schema Relationship Mapping")
    print("    - Data Filtering & Validation")
    print("    - Normal vs Enhanced Mode Comparison")
    print("    - Performance Metrics Tracking")
    print()

# Main entry point
if __name__ == "__main__":
    import uvicorn
    
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    
    uvicorn.run(
        "backend.main:app",
        host=host,
        port=port,
        reload=True
    )
