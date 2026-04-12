# System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         USER  INTERFACE                          │
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │  Modern Web Application (HTML/CSS/JavaScript)             │ │
│  │  • Dark theme with gradients                              │ │
│  │  • Natural language query input                           │ │
│  │  • Real-time data visualization                           │ │
│  │  • CSV/JSON export functionality                          │ │
│  └───────────────────────────────────────────────────────────┘ │
│                              ↓                                  │
└─────────────────────────────────────────────────────────────────┘
                               ↓
┌─────────────────────────────────────────────────────────────────┐
│                      FASTAPI BACKEND                            │
│                                                                 │
│  ┌─────────────────┐  ┌─────────────────┐  ┌───────────────┐  │
│  │   API Routes    │  │  Request/       │  │    CORS &     │  │
│  │                 │  │  Response       │  │  Middleware   │  │
│  │ • /api/generate │  │  Validation     │  │               │  │
│  │ • /api/analyze  │  │  (Pydantic)     │  │               │  │
│  │ • /health       │  │                 │  │               │  │
│  └─────────────────┘  └─────────────────┘  └───────────────┘  │
│                              ↓                                  │
└─────────────────────────────────────────────────────────────────┘
                               ↓
┌─────────────────────────────────────────────────────────────────┐
│                       SERVICE LAYER                             │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  ⭐ GEMINI API SERVICE (Active)                          │  │
│  │  ┌────────────────────────────────────────────────────┐  │  │
│  │  │ • Prompt Engineering                               │  │  │
│  │  │ • Schema Extraction & Mapping (integrate/)         │  │  │
│  │  │ • Semantic Relationship Analysis                   │  │  │
│  │  │ • Normal vs Enhanced Performance Mode              │  │  │
│  │  └────────────────────────────────────────────────────┘  │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  ⭐ RAG SERVICE (Active)                                 │  │
│  │  • Domain-specific Knowledge base retrieval              │  │
│  │  • Context augmentation mapping                          │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  🔄 MOCK KAGGLE SERVICE (Future Implementation)         │  │
│  │  • Dataset discovery                                     │  │
│  │  • Context enrichment                                    │  │
│  └──────────────────────────────────────────────────────────┘  │
│                              ↓                                  │
└─────────────────────────────────────────────────────────────────┘
                               ↓
┌─────────────────────────────────────────────────────────────────┐
│                    GOOGLE GEMINI API                            │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Model: Gemini 2.5 Flash                                 │  │
│  │  • Temperature: 0.7 (balanced creativity)                │  │
│  │  • Max Tokens: 8192                                      │  │
│  │  • Free Tier: 15 req/min, 1500 req/day                  │  │
│  └──────────────────────────────────────────────────────────┘  │
│                              ↓                                  │
└─────────────────────────────────────────────────────────────────┘
                               ↓
                    ┌──────────────────┐
                    │  AI Processing   │
                    │  & Generation    │
                    └──────────────────┘
                               ↓
┌─────────────────────────────────────────────────────────────────┐
│                      RESPONSE FLOW                              │
│                                                                 │
│  Raw Response → JSON Extraction → Validation → Schema Detection│
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Generated Data:                                          │  │
│  │  [                                                        │  │
│  │    {"id": 1, "name": "John", "email": "john@example.com"},│  │
│  │    {"id": 2, "name": "Jane", "email": "jane@example.com"} │  │
│  │  ]                                                        │  │
│  └──────────────────────────────────────────────────────────┘  │
│                              ↓                                  │
└─────────────────────────────────────────────────────────────────┘
                               ↓
┌─────────────────────────────────────────────────────────────────┐
│                    FRONTEND DISPLAY                             │
│                                                                 │
│  ┌─────────────────┐  ┌─────────────────┐  ┌───────────────┐  │
│  │  Schema Display │  │  Data Table     │  │  Export       │  │
│  │  • Field names  │  │  • Interactive  │  │  • CSV        │  │
│  │  • Data types   │  │  • Scrollable   │  │  • JSON       │  │
│  └─────────────────┘  └─────────────────┘  └───────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

## Data Flow Sequence

```
1. User enters query: "Generate 50 customers with name, email, age"
                              ↓
2. Frontend validates input and sends POST request
                              ↓
3. Backend receives request at /api/generate endpoint
   (Optional: User selects Normal vs Enhanced mode)
                              ↓
4. For Enhanced Mode: LLM extracts schema, Pydantic Schema Mapper validates.
   RAG service fetches domain context if enabled.
                              ↓
5. Gemini Service creates optimized prompt (including semantic relationships)
                              ↓
6. Prompt sent to Google Gemini 2.5 API
                              ↓
7. Gemini processes and generates structured data
                              ↓
8. Response parsed and validated
                              ↓
9. Schema extracted and Performance Comparator calculates metrics
                              ↓
10. JSON response with data and metrics sent to frontend
                              ↓
10. Frontend displays data in table
                              ↓
11. User can download as CSV or JSON
```

## Technology Stack

```
┌─────────────────────────────────────────┐
│           FRONTEND                      │
├─────────────────────────────────────────┤
│ • HTML5 (Semantic)                      │
│ • CSS3 (Modern features)                │
│ • JavaScript (ES6+)                     │
│ • Google Fonts (Inter, JetBrains Mono)  │
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│           BACKEND                       │
├─────────────────────────────────────────┤
│ • FastAPI 0.109.0                       │
│ • Uvicorn 0.27.0                        │
│ • Python 3.8+                           │
│ • Pydantic 2.5.3                        │
│ • Python-dotenv 1.0.0                   │
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│           AI/ML                         │
├─────────────────────────────────────────┤
│ • Google Generative AI SDK              │
│ • Gemini 2.5 Flash Model                │
│ • RAG Prompt Engineering                │
│ • LLM Semantic Schema Extraction        │
└─────────────────────────────────────────┘
```

## Security Architecture

```
┌─────────────────────────────────────────┐
│     Environment Variables (.env)        │
│  • GEMINI_API_KEY (sensitive)           │
│  • Not committed to version control     │
│  • Loaded at runtime only               │
└─────────────────────────────────────────┘
                ↓
┌─────────────────────────────────────────┐
│     Backend Security                    │
│  • CORS configured                      │
│  • Input validation (Pydantic)          │
│  • Error sanitization                   │
│  • No sensitive data in responses       │
└─────────────────────────────────────────┘
                ↓
┌─────────────────────────────────────────┐
│     API Communication                   │
│  • HTTPS to Google APIs                 │
│  • API key in headers                   │
│  • Rate limiting (Google side)          │
└─────────────────────────────────────────┘
```

## Deployment Architecture

```
Development:
┌──────────────────────────────────────┐
│  Local Machine                       │
│  • Python backend (port 8000)        │
│  • Static files served by FastAPI    │
│  • Hot reload enabled                │
└──────────────────────────────────────┘

Production (Future):
┌──────────────────────────────────────┐
│Cloud Platform (e.g., Railway, Render)│
│  • Dockerized application            │
│  • Environment variables in cloud    │
│  • HTTPS enabled                     │
│  • CDN for static files              │
└──────────────────────────────────────┘
```

## Key Design Decisions

1. **Gemini 2.5 Flash**: Chosen for speed and free tier availability
2. **Schema Mapper Architecture**: Separated semantic analysis (old approach) from strict Pydantic validation (integrate/) for a robust two-step schema generation.
3. **RAG Integration**: Actively retrieves localized data knowledge bases to augment basic queries.
4. **Mock Kaggle Services**: Placeholder for future Kaggle API datasets.
5. **Vanilla Frontend**: No framework overhead, fast loading
5. **FastAPI**: Modern, fast, with automatic API documentation
6. **Dark Theme**: Modern aesthetic, reduces eye strain
7. **Client-side Export**: No server processing for downloads

## Performance Characteristics

```
Response Times:
├─ API Request Processing: < 100ms
├─ Gemini API Call: 2-5 seconds
├─ JSON Parsing: < 50ms
└─ Frontend Rendering: < 100ms

Total: ~2-5 seconds per generation

Scalability:
├─ Free Tier: 15 requests/minute
├─ Concurrent Users: Limited by rate limits
└─ Data Size: Up to 100 records recommended
```
