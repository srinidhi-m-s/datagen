# Data Generation AI Platform

An AI-powered data generation platform that uses Google's Gemini API to generate synthetic datasets based on user queries.

## Features

- **Gemini API Integration**: Leverages Google's Gemini 1.5 Flash for intelligent data generation
-  **Schema-Aware Generation**: Creates data with semantic relationships based on user-specified schemas
-  **Modern UI**: Beautiful, responsive interface with dark mode and smooth animations
- 🔄 **Real-time Processing**: Live feedback during data generation
-  **Export Options**: Download generated data as CSV or JSON

## Architecture

### Current Implementation
- **Frontend**: Vanilla HTML/CSS/JavaScript with modern design
- **Backend**: FastAPI (Python) with Gemini API integration
- **AI Model**: Google Gemini 2.5 Flash (free tier)
- **Active Services**: RAG Service, Schema Validation Mapper, Semantic Relationship Analyzer

### Mock Components (Future Implementation)
- Kaggle API integration for dataset discovery
- RAG (Retrieval-Augmented Generation) for enhanced context

## Setup

### Prerequisites
- Python 3.8+
- Google Gemini API Key (free from [Google AI Studio](https://makersuite.google.com/app/apikey))

### Installation

1. Clone the repository
2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file in the root directory:
```
GEMINI_API_KEY=your_api_key_here
```

4. Run the application:
```bash
python backend/main.py
```

5. Open your browser to `http://localhost:8000`

## Usage

1. Enter your data requirements in natural language (e.g., "Generate 50 customer records with name, email, age, and purchase history")
2. Click "Generate Data"
3. Review the generated dataset
4. Download as CSV or JSON

## API Endpoints

- `POST /api/generate`: Generate data based on user query
- `GET /health`: Health check endpoint

## Gemini API Configuration

The application uses:
- **Model**: gemini-2.5-flash (free tier, fast responses)
- **Temperature**: 0.7 (balanced creativity)
- **Safety Settings**: Configured for data generation tasks
- **Prompt Engineering**: Optimized using Schema Mappers and RAG context

## Future Enhancements

- [ ] Kaggle API integration for real dataset discovery
- [ ] User authentication and saved queries
- [ ] Batch generation for large datasets
