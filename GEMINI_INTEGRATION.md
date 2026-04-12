# Gemini API Integration Guide

## Overview

This application uses **Google's Gemini 1.5 Flash** model for AI-powered data generation. Gemini is a powerful, free-tier LLM that excels at understanding natural language and generating structured data.

## Why Gemini 1.5 Flash?

- ✅ **Free Tier Available**: Generous free quota for development
- ✅ **Fast Response Times**: Optimized for quick generation
- ✅ **High Quality Output**: Excellent at structured data generation
- ✅ **Large Context Window**: Can handle complex queries
- ✅ **JSON Support**: Native understanding of structured formats

## API Configuration

### Model Settings

```python
model_name='gemini-1.5-flash'
generation_config={
    'temperature': 0.7,      # Balanced creativity (0.0-1.0)
    'top_p': 0.95,           # Nucleus sampling
    'top_k': 40,             # Top-k sampling
    'max_output_tokens': 8192 # Maximum response length
}
```

### Temperature Explained

- **0.0-0.3**: Very consistent, deterministic output (good for factual data)
- **0.4-0.7**: Balanced creativity and consistency (recommended for data generation)
- **0.8-1.0**: More creative and varied output (good for diverse datasets)

Current setting: **0.7** - Provides realistic variety while maintaining consistency

## Prompt Engineering

### Our Approach

The application uses a carefully crafted prompt template that:

1. **Sets Context**: Establishes the AI as a data generation expert
2. **Analyzes Query**: Extracts user intent and requirements
3. **Provides Instructions**: Clear guidelines for output format
4. **Ensures Quality**: Emphasizes realistic values and relationships
5. **Enforces Format**: Requires pure JSON output

### Prompt Template Structure

```
You are a data generation expert...

USER REQUEST: {user_query}

INSTRUCTIONS:
1. Analyze the request
2. Generate realistic data
3. Maintain relationships
4. Output as JSON array

EXAMPLE FORMAT:
[{"field": "value"}]
```

## Advanced Features

### 1. Query Analysis

The system can analyze user queries to extract:
- Entity type (customers, products, etc.)
- Record count
- Field names
- Constraints and requirements

```python
result = gemini_service.analyze_query(user_query)
```

### 2. JSON Extraction

Robust parsing handles various response formats:
- Removes markdown code blocks
- Extracts JSON arrays using regex
- Validates structure
- Provides helpful error messages

### 3. Schema Detection

Automatically detects data types from generated records:
```python
schema = {
    "id": "int",
    "name": "str",
    "email": "str",
    "age": "int"
}
```

## Safety Settings

Safety filters are set to `BLOCK_NONE` for data generation tasks:

```python
safety_settings=[
    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"}
]
```

**Note**: This is appropriate for synthetic data generation but adjust for other use cases.

## Error Handling

The integration includes comprehensive error handling:

### API Key Validation
```python
if not api_key or api_key == "your_gemini_api_key_here":
    raise ValueError("GEMINI_API_KEY not found...")
```

### Response Validation
- Checks for empty responses
- Validates JSON structure
- Ensures data is an array
- Provides detailed error messages

### Common Errors and Solutions

| Error | Cause | Solution |
|-------|-------|----------|
| `GEMINI_API_KEY not found` | Missing or invalid API key | Add valid key to `.env` file |
| `Empty response from Gemini API` | API issue or invalid request | Check query and try again |
| `Failed to parse JSON` | Malformed response | Retry or simplify query |
| `Rate limit exceeded` | Too many requests | Wait and retry (free tier limits) |

## Rate Limits (Free Tier)

Google Gemini API free tier includes:
- **15 requests per minute**
- **1,500 requests per day**
- **1 million tokens per day**

For production use, consider:
- Implementing request queuing
- Adding retry logic with exponential backoff
- Upgrading to paid tier if needed

## Optimization Tips

### 1. Query Optimization
```
❌ Bad: "Give me some data"
✅ Good: "Generate 50 customer records with name, email, age, and phone"
```

### 2. Batch Generation
For large datasets, generate in batches:
- Request 50-100 records at a time
- Combine results client-side
- Avoids token limits and timeouts

### 3. Caching
Consider caching common queries:
```python
# Future enhancement
cache_key = hash(query)
if cache_key in cache:
    return cache[cache_key]
```

## Fine-Tuning Options

### Current Implementation: Prompt Engineering

The application uses **prompt engineering** rather than model fine-tuning because:

1. **No Training Data Required**: Works immediately
2. **Flexible**: Easy to adjust for different use cases
3. **Cost-Effective**: No fine-tuning costs
4. **Free Tier Compatible**: Uses standard API

### Future: Custom Fine-Tuning

For specialized use cases, you could fine-tune Gemini:

```python
# Example: Fine-tuning (requires paid tier)
import google.generativeai as genai

# Prepare training data
training_data = [
    {"input": "Generate customer data", "output": "[{...}]"},
    # More examples...
]

# Fine-tune model (pseudo-code)
tuned_model = genai.tune_model(
    base_model="gemini-1.5-flash",
    training_data=training_data
)
```

**Note**: Fine-tuning is not available in the free tier and is not necessary for this application.

## Alternative: Few-Shot Learning

Instead of fine-tuning, use few-shot learning in prompts:

```python
prompt = """
Generate customer data.

Example 1:
Input: "5 customers"
Output: [{"id": 1, "name": "John Doe", ...}]

Example 2:
Input: "3 products"
Output: [{"sku": "A001", "name": "Widget", ...}]

Now generate: {user_query}
"""
```

## Monitoring and Debugging

### Enable Detailed Logging

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Track API Usage

Monitor your usage at: https://makersuite.google.com/app/apikey

### Response Inspection

The application logs:
- Raw API responses
- Parsed JSON data
- Error details
- Generation metadata

## Best Practices

1. ✅ **Validate API Key**: Check key is set before starting
2. ✅ **Handle Errors Gracefully**: Provide helpful error messages
3. ✅ **Parse Robustly**: Handle various response formats
4. ✅ **Set Appropriate Limits**: Don't request too much data at once
5. ✅ **Monitor Usage**: Track API calls to avoid rate limits
6. ✅ **Secure Keys**: Never commit API keys to version control

## Testing the Integration

### 1. Health Check
```bash
curl http://localhost:8000/health
```

### 2. Simple Generation
```bash
curl -X POST http://localhost:8000/api/generate \
  -H "Content-Type: application/json" \
  -d '{"query": "Generate 5 customer records with name and email"}'
```

### 3. Query Analysis
```bash
curl -X POST http://localhost:8000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{"query": "Create 10 products with SKU and price"}'
```

## Upgrading to Gemini Pro

For more complex queries, upgrade to Gemini Pro:

```python
# In gemini_service.py
self.model = genai.GenerativeModel(
    model_name='gemini-1.5-pro',  # Changed from flash
    # ... rest of config
)
```

**Gemini Pro Benefits**:
- Higher quality output
- Better reasoning
- Larger context window
- More complex query handling

**Trade-offs**:
- Slower response times
- Higher costs (if using paid tier)

## Resources

- [Gemini API Documentation](https://ai.google.dev/docs)
- [Get API Key](https://makersuite.google.com/app/apikey)
- [Pricing Information](https://ai.google.dev/pricing)
- [Python SDK Reference](https://ai.google.dev/api/python)
- [Best Practices Guide](https://ai.google.dev/docs/best_practices)

## Support

For issues with:
- **This Application**: Check QUICKSTART.md and README.md
- **Gemini API**: Visit [Google AI Studio](https://makersuite.google.com/)
- **API Quota**: Monitor at [API Console](https://console.cloud.google.com/)

---

**Current Status**: ✅ Fully Integrated and Tested

The Gemini API integration is production-ready and optimized for data generation tasks. The free tier is sufficient for development and moderate usage.
