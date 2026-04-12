"""
Quick script to list available Gemini models - outputs just model names
"""
import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    print("ERROR: GEMINI_API_KEY not found in .env file")
    exit(1)

client = genai.Client(api_key=api_key)

print("Available models that support generateContent:")
print("=" * 50)

try:
    models = client.models.list()
    for model in models:
        name = model.name
        # Show only the model name (the part we need)
        print(name)
except Exception as e:
    print(f"Error: {e}")
