"""
Data Generation AI Platform - FastAPI Backend
With Schema Mapping, Filtering, and Performance Comparison
"""

import os
import sys
import csv
import json
from io import StringIO
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
    output_format: str = Field(default="auto", description="Output format: auto|json|csv|jsonl|markdown")

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

class EmailNotificationRequest(BaseModel):
    receiver_email: str = Field(..., description="Recipient email address")
    user_prompt: str = Field(..., description="The original data generation prompt")
    record_count: int = Field(default=0, description="Number of records generated")

# Initialize services after app is defined
# LLM Router: tries Groq first, falls back to Gemini automatically
try:
    from backend.llm_router import llm_service as gemini_service  # aliased for backward compat
    from backend.mock_services import mock_kaggle_service, mock_rag_service
    from backend.schema_mapper import schema_mapper
    from backend.data_filter import data_filter
    from backend.performance_comparator import performance_comparator
    services_loaded = True
except Exception as e:
    services_loaded = False
    service_error = str(e)


def _detect_output_format(query: str, requested_format: str) -> str:
    if requested_format and requested_format.lower() in {"json", "csv", "jsonl", "markdown"}:
        return requested_format.lower()

    q = query.lower()
    if "jsonl" in q or "ndjson" in q:
        return "jsonl"
    if "csv" in q:
        return "csv"
    if "markdown table" in q or "table format" in q or "as table" in q:
        return "markdown"
    if "json" in q:
        return "json"
    return "json"


def _format_output(data: List[Dict[str, Any]], output_format: str) -> str:
    if not data:
        return "[]" if output_format in {"json", "jsonl"} else ""

    if output_format == "json":
        return json.dumps(data, indent=2)

    if output_format == "jsonl":
        return "\n".join(json.dumps(row) for row in data)

    if output_format == "csv":
        headers = list(data[0].keys())
        stream = StringIO()
        writer = csv.DictWriter(stream, fieldnames=headers)
        writer.writeheader()
        writer.writerows(data)
        return stream.getvalue()

    if output_format == "markdown":
        headers = list(data[0].keys())
        lines = [
            "| " + " | ".join(headers) + " |",
            "| " + " | ".join(["---"] * len(headers)) + " |",
        ]
        for row in data:
            values = [str(row.get(h, "")).replace("|", "\\|") for h in headers]
            lines.append("| " + " | ".join(values) + " |")
        return "\n".join(lines)

    return json.dumps(data, indent=2)

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
        
        # Step 1: Build validated schema from prompt
        schema_result = await gemini_service.generate_schema_with_validation(
            request.query,
            rag_context=rag_context,
            kaggle_context=kaggle_context
        )

        if not schema_result.get("success"):
            raise HTTPException(status_code=500, detail=schema_result.get("error", "Schema generation failed"))

        # Reuse schema columns from step 1 to avoid a redundant LLM field-extraction call
        # This reduces API usage from 3 calls → 2 calls per request
        extracted_fields = [col["name"] for col in schema_result["schema"]["columns"]]
        schema_context = {
            "context": [
                f"Validated dataset: {schema_result['metadata']['dataset_name']}",
                f"Rows requested: {schema_result['metadata']['rows']}",
                f"Columns: {', '.join(extracted_fields)}",
            ]
        }
        merged_rag_context = rag_context or {"context": []}
        if isinstance(merged_rag_context, dict):
            merged_rag_context.setdefault("context", [])
            merged_rag_context["context"].extend(schema_context["context"])

        # Step 2: Generate data — skip LLM field extraction (use_llm_extraction=False)
        # because we already have the fields from step 1
        result = await gemini_service.generate_data_enhanced(
            request.query,
            rag_context=merged_rag_context,
            kaggle_context=kaggle_context,
            use_llm_extraction=False  # ← skips 1 extra API call
        )
        
        if not result.get("success"):
            raise HTTPException(status_code=500, detail=result.get("error", "Data generation failed"))
        
        output_format = _detect_output_format(request.query, request.output_format)
        formatted_output = _format_output(result["data"], output_format)

        response = {
            "success": True,
            "mode": result.get("mode", "enhanced"),
            "data": result["data"],
            "output_format": output_format,
            "formatted_output": formatted_output,
            "metadata": {
                "record_count": result["record_count"],
                "schema": result["schema"],
                "query": result["query"],
                "mapped_schema": schema_result["schema"],
                "schema_flow": schema_result.get("flow", "llm_extraction → schema_validation")
            },
            "metrics": result.get("metrics"),
            "validation": result.get("validation"),
            "schema_analysis": result.get("schema_analysis")
        }
        
        if kaggle_context:
            response["kaggle_context"] = kaggle_context
        if rag_context:
            response["rag_context"] = rag_context
        response["schema_mapping"] = schema_result
        
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

@app.post("/api/send-email")
async def send_email_notification(request: EmailNotificationRequest):
    """Send an email notification when data generation is complete."""
    try:
        from backend.Email import send_notification_email
        send_notification_email(
            receiver_email=request.receiver_email,
            user_prompt=request.user_prompt,
            record_count=request.record_count,
        )
        return {"success": True, "message": f"Email sent to {request.receiver_email}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send email: {str(e)}")


# Startup event
@app.on_event("startup")
async def startup_event():
    """Display startup message"""
    print()
    print(" Server starting on http://0.0.0.0:8000")

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
