# AI-Powered Market Intelligence & Trend Analytics Platform

Production-grade backend built with FastAPI + MongoDB that ingests market/news data from a real third-party API, performs NLP-style processing (keywords, sentiment, trend scoring), and serves analytics endpoints.

## Architecture

Third-Party API (News API) -> Ingestion Pipeline -> MongoDB (`raw_data`) -> Processing Pipeline -> MongoDB (`processed_data`) -> FastAPI Analytics Endpoints -> Deployment (Render/Railway)

## Tech Stack

- FastAPI
- MongoDB Atlas + Motor (async driver)
- News API (external data source)
- Pydantic v2
- Uvicorn

## Features Implemented

### Core Requirements

- Data ingestion from News API
- Data normalization and raw storage in `raw_data`
- Data processing and transformed storage in `processed_data`
- Keyword extraction
- Rule-based sentiment classification (`positive`, `negative`, `neutral`)
- Trend score calculation
- Trend detection via aggregation
- Time-series analysis (daily counts + growth trend)
- Search endpoint with pagination
- Robust error handling and validation

### Advanced Features Chosen

- Background Tasks (`POST /ingest?run_in_background=true`)
- In-memory TTL caching for analytics endpoints

## Project Structure

```
.
├── app
│   ├── core
│   │   ├── config.py
│   │   ├── database.py
│   │   └── logging_config.py
│   ├── models
│   │   └── schemas.py
│   ├── routers
│   │   ├── analytics.py
│   │   ├── ingest.py
│   │   └── search.py
│   ├── services
│   │   ├── analytics.py
│   │   ├── cache.py
│   │   ├── news_api.py
│   │   └── processor.py
│   ├── utils
│   │   └── text.py
│   └── main.py
├── .env.example
├── Procfile
├── render.yaml
└── requirements.txt
```

## Setup Instructions

### 1. Create and activate virtual environment

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure environment variables

```bash
copy .env.example .env
```

Set your values in `.env`:

- `MONGODB_URI` (MongoDB Atlas connection string)
- `MONGODB_DB`
- `NEWS_API_KEY`

### 4. Run server

```bash
uvicorn app.main:app --reload
```

Swagger docs:

- http://127.0.0.1:8000/docs

## API Endpoints

### 1) `POST /ingest`

Fetch and store data from News API.

Query param:

- `run_in_background` (default `true`)

Request body example:

```json
{
  "query": "business OR economy OR AI",
  "category": "business",
  "language": "en",
  "page_size": 50,
  "from_days": 7
}
```

### 2) `GET /trends?days=7&page=1&page_size=20`

Returns top keywords based on processed records.

### 3) `GET /insights?page=1&page_size=10`

Returns aggregated insights:

- total processed
- sentiment distribution
- top keywords
- top sources
- sample items

### 4) `GET /search?q=keyword&page=1&page_size=20`

Search in title/content/source/keywords with pagination.

### 5) `GET /analytics/summary?days=7`

Returns summary statistics:

- raw and processed counts
- sentiment totals
- average trend score
- daily time-series counts
- growth percentage

## MongoDB Collections

### `raw_data` (sample)

```json
{
  "title": "...",
  "source": "Reuters",
  "published_at": "...",
  "content": "...",
  "category": "business",
  "url": "..."
}
```

### `processed_data` (sample)

```json
{
  "title": "...",
  "sentiment": "positive",
  "keywords": ["ai", "economy"],
  "score": 0.0123,
  "trend_score": 12.8
}
```

## Deployment

### Render

- Use included `render.yaml` (Blueprint deploy)
- Add environment variables in Render dashboard:
  - `MONGODB_URI`
  - `NEWS_API_KEY`
- Deploy command is already configured via `startCommand`

### Railway

- Set same env variables in Railway project settings
- Start command:

```bash
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

## Testing with cURL

```bash
curl -X POST "http://127.0.0.1:8000/ingest?run_in_background=false" \
  -H "Content-Type: application/json" \
  -d "{\"query\":\"AI market\",\"category\":\"business\",\"language\":\"en\",\"page_size\":20,\"from_days\":7}"

curl "http://127.0.0.1:8000/trends?days=7"
curl "http://127.0.0.1:8000/insights"
curl "http://127.0.0.1:8000/search?q=ai"
curl "http://127.0.0.1:8000/analytics/summary?days=7"
```

## Notes

- This implementation uses News API (`/everything`) for richer keyword/sentiment extraction.
- Caching TTL is configurable via `CACHE_TTL_SECONDS`.
- For production hardening, consider Redis caching, authentication, and scheduled ingestion jobs.
