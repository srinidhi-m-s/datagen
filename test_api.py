"""
API Testing Script
Test the Gemini API integration without running the full server
"""

import os
import sys
import asyncio
from dotenv import load_dotenv

# Add backend directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from gemini_service import gemini_service

async def test_api():
    """Test the Gemini API integration"""
    
    print("=" * 60)
    print("  Gemini API Integration Test")
    print("=" * 60)
    print()
    
    # Test queries
    test_queries = [
        "Generate 5 customer records with name, email, and age",
        "Create 3 product records with SKU, name, and price",
        "Generate 4 employee records with ID, name, and department"
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"Test {i}/{len(test_queries)}: {query}")
        print("-" * 60)
        
        try:
            result = await gemini_service.generate_data(query)
            
            if result["success"]:
                print(f"✅ Success!")
                print(f"   Records generated: {result['record_count']}")
                print(f"   Schema: {result['schema']}")
                print(f"   Sample data (first record):")
                if result['data']:
                    print(f"   {result['data'][0]}")
            else:
                print(f"❌ Failed: {result.get('error', 'Unknown error')}")
        
        except Exception as e:
            print(f"❌ Error: {str(e)}")
        
        print()
    
    print("=" * 60)
    print("  Testing Complete")
    print("=" * 60)

if __name__ == "__main__":
    # Load environment variables
    load_dotenv()
    
    # Check API key
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key or api_key == "your_gemini_api_key_here":
        print("❌ ERROR: GEMINI_API_KEY not set in .env file")
        print("   Please add your API key to the .env file")
        print("   Get your free API key from: https://makersuite.google.com/app/apikey")
        sys.exit(1)
    
    print(f"✅ API Key found: {api_key[:10]}...")
    print()
    
    # Run tests
    asyncio.run(test_api())
