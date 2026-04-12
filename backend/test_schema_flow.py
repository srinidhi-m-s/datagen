"""
Test Script for Schema Generation Flow
Demonstrates: User Query → LLM Extraction → Schema Validation

Usage:
    python backend/test_schema_flow.py
    python backend/test_schema_flow.py "Generate 20 customer records"
"""

import asyncio
import json
import sys
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_dir.parent))

from backend.gemini_service import gemini_service


async def test_schema_generation(query=None):
    """Test the new schema generation flow with user-provided or default query"""
    
    # Get query from command line argument, or ask user, or use default
    if query is None:
        if len(sys.argv) > 1:
            # Query provided as command line argument
            query = " ".join(sys.argv[1:])
        else:
            # Ask user for input
            print("\n" + "=" * 100)
            print("SCHEMA GENERATION FLOW TEST - Interactive Mode")
            print("=" * 100)
            print("\nEnter your data generation query (or press Enter for default):")
            print("Examples:")
            print("  - Generate 10 employee records")
            print("  - Create 20 customer records with purchase history")
            print("  - Generate 50 product records for an e-commerce store")
            print()
            user_input = input("Your query: ").strip()
            
            if user_input:
                query = user_input
            else:
                query = "Generate 15 employee records"
                print(f"Using default query: {query}")
    
    if not query:
        print("❌ Error: No query provided!")
        return
    
    print("\n" + "=" * 100)
    print(" " * 35 + "SCHEMA GENERATION FLOW TEST")
    print("=" * 100)
    print(f"\n📝 User Query: \"{query}\"\n")
    
    try:
        # Call the new flow
        result = await gemini_service.generate_schema_with_validation(query)
        
        if not result.get("success"):
            print(f"❌ FAILED: {result.get('error')}")
            return
        
        # ========================================================================
        # STEP 1: SHOW LLM OUTPUT
        # ========================================================================
        print("\n" + "=" * 100)
        print("🤖 STEP 1: LLM OUTPUT (Raw JSON from Gemini)")
        print("=" * 100)
        print("\nThe LLM analyzes the query and generates this schema:")
        print()
        
        llm_output = result.get("llm_raw_output", {})
        print(json.dumps(llm_output, indent=2))
        
        # ========================================================================
        # STEP 2: SHOW SCHEMA MAPPER OUTPUT
        # ========================================================================
        print("\n\n" + "=" * 100)
        print("🔍 STEP 2: SCHEMA MAPPER OUTPUT (Validated & Normalized)")
        print("=" * 100)
        print("\nThe schema mapper validates and normalizes the LLM output:")
        print()
        
        schema = result.get("schema", {})
        print(json.dumps(schema, indent=2))
        
        # ========================================================================
        # COMPARISON TABLE
        # ========================================================================
        print("\n\n" + "=" * 100)
        print("🔄 TRANSFORMATION COMPARISON")
        print("=" * 100)
        print()
        print("┌─────────────────────┬──────────────────────┬──────────────────────┐")
        print("│ Column Name         │ LLM Type             │ Normalized Type      │")
        print("├─────────────────────┼──────────────────────┼──────────────────────┤")
        
        for llm_col, schema_col in zip(llm_output.get('columns', []), schema.get('columns', [])):
            llm_type = llm_col.get('type', 'N/A')
            schema_type = schema_col.get('type', 'N/A')
            name = llm_col.get('name', 'N/A')
            
            # Pad for alignment
            name_padded = name[:19].ljust(19)
            llm_type_padded = llm_type[:20].ljust(20)
            schema_type_padded = schema_type[:20].ljust(20)
            
            print(f"│ {name_padded} │ {llm_type_padded} │ {schema_type_padded} │")
        
        print("└─────────────────────┴──────────────────────┴──────────────────────┘")
        
        # ========================================================================
        # KEY TRANSFORMATIONS
        # ========================================================================
        print("\n" + "=" * 100)
        print("🎯 KEY TRANSFORMATIONS")
        print("=" * 100)
        
        for llm_col, schema_col in zip(llm_output.get('columns', [])[:4], schema.get('columns', [])[:4]):
            print(f"\n📌 {llm_col.get('name')}:")
            print(f"   LLM Type:        '{llm_col.get('type')}'")
            print(f"   Normalized Type: '{schema_col.get('type')}'")
            
            # Show range transformation
            if 'range' in llm_col:
                llm_range = llm_col['range']
                schema_min = schema_col.get('min')
                schema_max = schema_col.get('max')
                print(f"   LLM Range:       {llm_range}")
                print(f"   Normalized:      min={schema_min}, max={schema_max}")
            
            # Show values transformation
            if 'values' in llm_col:
                values = llm_col['values']
                print(f"   Categorical Values: {values}")
        
        # ========================================================================
        # SUMMARY
        # ========================================================================
        print("\n\n" + "=" * 100)
        print("✅ VALIDATION COMPLETE")
        print("=" * 100)
        
        metadata = result.get("metadata", {})
        print(f"\n📊 Final Validated Schema:")
        print(f"   • Dataset Name:  {metadata.get('dataset_name')}")
        print(f"   • Rows:          {metadata.get('rows')}")
        print(f"   • Column Count:  {metadata.get('column_count')}")
        print(f"   • Version:       {metadata.get('version')}")
        print(f"   • Created At:    {metadata.get('created_at')}")
        print(f"   • Source:        {metadata.get('source')}")
        print(f"   • Flow:          {result.get('flow')}")
        
        print("\n🎯 This validated schema is ready for:")
        print("   ✓ RAG processing")
        print("   ✓ Data generation")
        print("   ✓ Storage/caching")
        
        print("\n" + "=" * 100)
        print("TEST COMPLETE")
        print("=" * 100 + "\n")
    
    except Exception as e:
        print(f"\n❌ EXCEPTION: {str(e)}\n")


if __name__ == "__main__":
    print("\n🚀 Starting Schema Generation Flow Test...\n")
    asyncio.run(test_schema_generation())
