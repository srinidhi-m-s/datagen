# DataGen AI — Synthetic Data Generation Platform

An AI-powered platform that generates realistic synthetic datasets from natural language queries. Describe what data you need, and the system produces structured, semantically consistent records ready to download.

---

## How It Works

The system uses a two-stage LLM pipeline:

**Stage 1 — Schema Extraction**
The LLM reads your query and extracts a structured schema — field names, data types, constraints, and value ranges. This passes through a Pydantic validation layer (Schema Mapper) that normalizes types and enforces constraints before any data is generated.

**Stage 2 — Data Generation**
The validated schema, combined with RAG domain knowledge and semantic relationship rules, forms an enhanced prompt. The LLM generates realistic records following rules.

The generated data then goes through post-processing (fix duplicate IDs, clean strings) and validation (schema compliance, uniqueness checks) before being returned.

---

## Tech Stack

- **Frontend** — Vanilla HTML / CSS / JavaScript
- **Backend** — Python FastAPI
- **Primary LLM** — Groq (`llama-3.3-70b-versatile`) — 14,400 req/day free tier
- **Fallback LLM** — Google Gemini (`gemini-2.0-flash`)
- **RAG** — Keyword-based retrieval (ChromaDB + sentence-transformers )
- **Deployment** — Render

---

## Features

- Natural language query input — describe your data in plain English
- Two-stage LLM pipeline for higher quality and consistency
- Schema Mapper — validates and normalizes LLM output via Pydantic
- RAG-enhanced generation — domain knowledge for realistic values (salaries, categories, etc.)
- Normal vs Enhanced mode comparison — real backend scoring on schema compliance, relationship integrity, and data quality
- Post-processing — auto-fixes duplicate IDs and emails
- Export as CSV or JSON
- Email notification — get notified at your email when generation completes
- Response time metrics per generation run

---

## Project Structure

```
datagen/
├── backend/
│   ├── main.py                  # FastAPI app, all API routes
│   ├── llm_router.py            # Routes calls to Groq or Gemini with auto-fallback
│   ├── groq_service.py          # Primary LLM service (Groq)
│   ├── gemini_service.py        # Fallback LLM service (Gemini)
│   ├── schema_mapper.py         # Semantic relationship analyzer (feeds into prompts)
│   ├── data_filter.py           # Data validation and filtering
│   ├── data_post_processor.py   # Fixes duplicates and cleans output
│   ├── performance_comparator.py# Scores and compares generation modes
│   ├── rag_service.py           # RAG knowledge base retrieval
│   ├── Email.py                 # Gmail SMTP email notification
│   └── integrate/
│       └── schema_mapper.py     # Pydantic schema validation (LLM output → typed schema)
├── frontend/
│   ├── index.html               # Single-page UI
│   └── static/
│       ├── css/styles.css
│       └── js/app.js
├── requirements.txt
├── render.yaml                  # Render deployment config
└── .env                         # API keys (not committed)
```

---

## Setup

### Prerequisites
- Python 3.11+
- Groq API key (free) — [console.groq.com](https://console.groq.com/keys)
- Gemini API key (free, fallback) — [makersuite.google.com](https://makersuite.google.com/app/apikey)

### Installation

1. Clone the repository and navigate to the project folder

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure your `.env` file:
```
GROQ_API_KEY=your_groq_key_here
GROQ_MODEL=llama-3.3-70b-versatile
GEMINI_API_KEY=your_gemini_key_here
GEMINI_MODEL=gemini-2.0-flash
HOST=0.0.0.0
PORT=8000
```

4. Run the app:
```bash
# Windows
start.bat

# Or manually
cd backend
python main.py
```

5. Open [http://localhost:8000](http://localhost:8000)

---

## LLM Provider Routing

The `llm_router.py` tries Groq first on every request. If Groq returns a 429 (rate limit) or 503 (unavailable), it automatically retries on Gemini — no manual intervention needed. Both providers implement the same interface so the swap is transparent.

---

## Comparison Modes

**Normal vs Enhanced**
Clicking Compare runs both pipelines on the same query and scores each result on:
- Schema compliance (40%) — are all expected fields present?
- Relationship score (30%) — are IDs unique, does email match name?
- Data quality (30%) — are there null/empty values?


## Deployment on Render

The `render.yaml` is pre-configured. Set these environment variables in the Render dashboard:

```
GROQ_API_KEY
GEMINI_API_KEY
GROQ_MODEL=llama-3.3-70b-versatile
GEMINI_MODEL=gemini-2.0-flash
PYTHON_VERSION=3.11.9
```

Start command: `uvicorn backend.main:app --host 0.0.0.0 --port $PORT`
