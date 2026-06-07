# TravelOS — AI-Powered Multi-Tenant Travel CRM & Operations Platform

An operating system for small (1–2 person) travel agencies. It runs the whole trip lifecycle
through AI agents with **human-in-the-loop** at every critical step:

> itinerary → creative (posters/captions/docs) → hotel & transport sourcing →
> Instagram/WhatsApp publishing → ads → **leads → CRM auto-followup → deal close**

Multi-tenant from day one: each agency gets an isolated workspace.

## Stack
- **Frontend:** React 19 + TypeScript + Vite, Tailwind, shadcn-style UI, **Framer Motion** (heavy animation)
- **Backend:** FastAPI + **LangGraph** agents (HITL interrupts), async SQLAlchemy
- **Data:** PostgreSQL 16 + pgvector (Row-Level Security multi-tenancy), Redis, APScheduler
- **LLM (free-tier first, pluggable):** Gemini 2.5 Flash (text), Groq Llama-3.3-70B (fast CRM), Gemini Flash Image / Pollinations (posters)
- **Infra:** Docker Compose (dev) → AWS ECS + RDS + ElastiCache + S3 (prod)

## Modules
| # | Module | Agents |
|---|--------|--------|
| 1 | Trip / Itinerary Builder | Itinerary Agent |
| 2 | Creative Studio | Creative Agent (posters, captions, docs) |
| 3 | Sourcing | Hotel Agent, Transport Agent |
| 4 | Publishing | Instagram Graph API (WhatsApp Phase 2) |
| 5 | CRM + Leads | Lead / Followup Agent (Meta Lead Ads webhook → auto-followup) |

## Quick start (dev)
```bash
cp .env.example .env        # fill in GEMINI_API_KEY at minimum
docker compose up --build
# Backend  → http://localhost:8000/docs
# Frontend → http://localhost:5173
```

Run backend without Docker:
```bash
cd backend && python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload
```

## Roadmap (phases)
- **Phase 0** — Foundation: multi-tenant auth, animated onboarding, dashboard shell ← *current*
- **Phase 1** — Trip + Creative agents
- **Phase 2** — CRM + Leads (Meta webhook, Email/SMS followups)
- **Phase 3** — Sourcing + Instagram publishing
- **Phase 4** — WhatsApp Cloud API, video, analytics
- **Phase 5** — AWS production

Full design doc: `docs/PLAN.md`.
