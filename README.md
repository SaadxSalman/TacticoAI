# TacticoAI — Tactical Intelligence Graph-RAG Engine

> A real-time, multi-modal **Agentic & Graph-RAG** sports intelligence platform that fuses computer-vision tracking, event-stream telemetry, tactical playbooks, and injury analytics to deliver conversational, context-aware game strategies and performance insights.

![Python](https://img.shields.io/badge/Python-3.11%2B-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-green)
![Next.js](https://img.shields.io/badge/Next.js-14-black)
![License](https://img.shields.io/badge/License-MIT-yellow)

## Table of Contents

1. Overview
2. Why TacticoAI?
3. Architecture
4. Features
5. Tech Stack
6. Project Structure
7. Getting Started
8. Environment Variables
9. Running the Backend
10. Running the Frontend
11. API Reference
12. Example Queries
13. Data Model
14. Agentic Pipeline Deep Dive
15. Graph-RAG Schema
16. In-Memory Fallback Mode
17. Testing
18. Deployment
19. Roadmap
20. Contributing
21. License

## Overview

Standard RAG systems fail in sports analytics because game data is not flat text. It is **temporal** (events happen at specific minutes), **spatial** (players move on a pitch), and **relational** (Player -> plays for -> Team -> uses formation -> against defensive scheme). TacticoAI solves this with a **hybrid retrieval pipeline** combining:

- **Vector / Hybrid Search** (Qdrant or in-memory) for unstructured text: tactics, coaching manuals, referee transcripts, sports-science research.
- **Knowledge Graph** (Neo4j or in-memory) for structured relationships: players, teams, formations, matches, weaknesses.
- **Agentic Router** that classifies intent and dispatches to the right retriever(s).
- **Code Execution Engine** that runs Python on the fly for statistical aggregation over telemetry.
- **Self-Corrective RAG (CRAG)** evaluator that checks whether retrieved context actually answers the query before synthesis.
- **Reranker** (Cohere Rerank or heuristic fallback) to order results by relevance.
- **LLM Synthesis** (OpenAI) with deterministic fallback when no API key is configured.

The default demo domain is **soccer (football)** with a curated dataset of Premier League players, teams, matches, sprint telemetry, workload/injury data, and tactical knowledge chunks. The architecture is sport-agnostic.

## Why TacticoAI?

| Problem with naive RAG | TacticoAI Solution |
|---|---|
| Treats all data as text chunks | Separates structured (graph) from unstructured (vector) |
| No temporal awareness | Telemetry tagged with game, period, minute |
| No spatial/tactical context | Formation & defensive-weakness graph nodes |
| Hallucinates statistics | Code execution engine computes from raw data |
| Single retrieval pass | CRAG evaluator triggers expanded search when insufficient |
| No ranking | Cohere cross-encoder reranker (with fallback) |

## Architecture

```
                          [ Raw Game Inputs ]
        (Tracking Data, Event Streams, PDFs, Video Clips)
                                 |
                                 v
                     +-----------------------+
                     | Multi-Modal Ingestion |
                     +-----------+-----------+
                                 |
                +----------------+----------------+
                v                                 v
    +-----------------------+         +-----------------------+
    | Structural DB / Vector|         | Knowledge Graph       |
    | (Qdrant / pgvector)   |         | (Neo4j GraphRAG)      |
    +-----------+-----------+         +-----------+-----------+
                |                                 |
                +----------------+----------------+
                                 |
                                 v
                     +-----------------------+
                     | Intent & Router Agent |
                     +-----------+-----------+
                                 |
     +---------------------------+---------------------------+
     v                           v                           v
+--------------+         +--------------+         +----------------------+
| Vector/Hybrid|         | Graph / Neo4j|         | Code / Analytical    |
| Retriever    |         | Cypher Query |         | Execution Engine     |
+------+-------+         +------+-------+         +----------+-----------+
       |                        |                            |
       +------------------------+----------------------------+
                                |
                                v
                     +-----------------------+
                     | Cohere ReRank CrossEnc|
                     +-----------+-----------+
                                 |
                                 v
                     +-----------------------+
                     | Self-Correction / Eval|
                     | (CRAG)                |
                     +-----------+-----------+
                                 |
                                 v
                     +-----------------------+
                     |   Synthesis Engine    |
                     +-----------------------+
```
## Features

- **Temporal & Contextual Query Handling**
- **Real-Time Tactical Countering**
- **Injury & Load Analysis Integration**
- **Automated Video-Clip Synthesis**
- **Code Interpreter Execution Engine**
- **Self-Corrective RAG (CRAG)**
- **Graceful Fallbacks** (in-memory when no services)
- **Modern Dashboard** (Next.js 14 + Tailwind)

## Tech Stack

| Component | Stack |
|---|---|
| LLM Orchestration | Custom agentic pipeline (LangGraph-ready) |
| Vector Database | Qdrant / PostgreSQL (pgvector) - in-memory fallback |
| Graph Database | Neo4j - in-memory fallback |
| Reranker | Cohere Rerank - heuristic fallback |
| Embeddings | OpenAI text-embedding-3-large - deterministic fallback |
| Backend & API | FastAPI, Python 3.11+, Celery, Redis |
| Frontend | Next.js 14 (App Router), Tailwind CSS, Recharts |
| Tests | pytest |
## Project Structure

```
TacticoAI/
├── .env
├── .gitignore
├── README.md
├── src/
│   ├── config.py
│   ├── utils.py
│   ├── data.py
│   ├── bootstrap.py
│   ├── llm.py
│   ├── reranker.py
│   ├── code_executor.py
│   ├── vector_store.py
│   ├── graph_store.py
│   ├── agents/
│   ├── engine/rag_pipeline.py
│   ├── ingestion/
│   ├── api/main.py
│   └── tests/
└── frontend/
```

## Getting Started

### Prerequisites

- Python 3.11+
- Node.js 18+
- (Optional) Qdrant, Neo4j, Redis, PostgreSQL

### Clone

```bash
git clone https://github.com/SaadxSalman/TacticoAI.git
cd TacticoAI
```
## Environment Variables

All config in a single `.env` (gitignored). Key vars:

| Variable | Description |
|---|---|
| OPENAI_API_KEY | OpenAI key (optional) |
| ANTHROPIC_API_KEY | Anthropic key (optional) |
| COHERE_API_KEY / COHERE_RERANK_API_KEY | Cohere (optional) |
| NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD | Neo4j (optional) |
| QDRANT_HOST, QDRANT_PORT, QDRANT_API_KEY | Qdrant (optional) |
| PGVECTOR_CONNECTION_URL | Postgres+pgvector (optional) |
| REDIS_HOST, REDIS_PORT, REDIS_PASSWORD | Redis (optional) |
| NEXT_PUBLIC_API_URL | Backend URL for frontend |
| ENVIRONMENT, DEBUG, LOG_LEVEL | App settings |

> `.env` is gitignored; no `.env.example` by design.

## Running the Backend

```bash
pip install fastapi uvicorn pydantic pydantic-settings python-dotenv qdrant-client neo4j redis cohere openai numpy scikit-learn
uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload
```

Health: `GET http://localhost:8000/health`

## Running the Frontend

```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:3000`.
## API Reference

POST /api/v1/query - process natural language query.
GET /api/v1/players - list players.
GET /api/v1/players/{id}/statistics - player stats.
GET /api/v1/teams - list teams.
GET /api/v1/teams/{id}/formations - team formations.
GET /api/v1/injury-risk - injury risk for all players.
## Example Queries

- How many sprints did Mohamed Salah make in the second half?
- Find defensive weaknesses of Arsenal against a 4-3-3
- Which players have high injury risk?
- Compare Haaland and Salah performance
- What formation does Liverpool use?

## Data Model

TEAMS, PLAYERS, GAMES, SPRINTS, WORKLOAD, KNOWLEDGE_CHUNKS (see src/data.py).

## Agentic Pipeline Deep Dive

1. Router classifies intent.
2. Retrieval: vector hybrid + graph traversal.
3. Rerank (Cohere or heuristic).
4. CRAG evaluation of sufficiency.
5. Code execution for stats.
6. Synthesis (LLM or deterministic).

## Graph-RAG Schema

Nodes: Player, Team, Game, Formation, Pattern, Weakness.
Edges: PLAYS_FOR, PLAYED_IN, USES_FORMATION, COUNTERS.

## In-Memory Fallback Mode

Runs with zero external services: in-memory vector/graph, deterministic embeddings and synthesis, keyword reranker. Upgrades automatically when credentials provided.

## Testing

python -m pytest src/tests/ -q

## Deployment

Backend: containerize with Docker. Frontend: Vercel (set NEXT_PUBLIC_API_URL).

## Roadmap

- Real StatsBomb/NBA/NFL connectors
- LangGraph multi-agent orchestration
- Video keyframe extraction
- WebSockets streaming
- Multi-tenant auth

## Contributing

Fork, branch, conventional commits, open PR..
