<div align="center">

# 🧳 TravelOS

### The AI operating system for travel agencies — one inbox, every agent, you stay in control.

From a new trek idea to a closed booking: itineraries, posters, reels, hotel & transport deals,
Instagram publishing, and a full lead CRM — run by AI agents, **approved by a human at every step.**

[![🌐 Live Demo](https://img.shields.io/badge/🌐_Live_Demo-13.60.214.190-2DD4BF?style=for-the-badge)](http://13.60.214.190)
[![CI](https://img.shields.io/badge/CI-passing-22C55E?style=for-the-badge&logo=githubactions&logoColor=white)](#)
[![Tests](https://img.shields.io/badge/tests-17_passing-8B5CF6?style=for-the-badge)](#)
[![Runs Keyless](https://img.shields.io/badge/runs-keyless_in_dev-FF6B35?style=for-the-badge)](#)

<sub>⚡ Live demo runs on a free-tier box and may be parked after the showcase window.</sub>

</div>

---

## 🧠 What is this?

Most travel agencies are 1–2 people doing **everything** by hand: writing itineraries, designing
posters, chasing hotels for rates, posting on Instagram, running ads, and then drowning in the
leads those ads bring. TravelOS turns that whole pipeline into a single **multi-tenant** workspace
where AI agents do the grunt work and the human just **reviews and approves**.

> The whole product is built on one belief: **AI should be reliable in production, not just
> impressive in a demo.** So every agent *drafts* — and nothing goes out (no message sent, no post
> published, no deal emailed) until a human clicks approve.

---

## ✨ What it does

| # | Module | The agent does… | You do… |
|---|--------|-----------------|---------|
| 1 | 🗺️ **Trip Builder** | Streams a day-by-day itinerary + costing (LangGraph) | Tweak & approve |
| 2 | 🎨 **Creative Studio** | Posters, captions, a PDF brochure, and an auto-playing **reel** | Pick the winners |
| 3 | 🏨 **Sourcing** | Drafts outreach to hotel & transport vendors, tracks deals | Approve → it sends |
| 4 | 📣 **Publishing** | Schedules & posts to **Instagram** (Graph API) | One-click publish |
| 5 | 👥 **CRM + Leads** | Captures leads (Meta Ads / web / **WhatsApp**), classifies intent, auto-follows-up | Work the 7-stage Kanban |
| 📊 | **Analytics** | Live funnel, conversion %, source mix | Watch it grow |

Every draft lands in a single **Approval Center** — the human-in-the-loop heartbeat of the system.

---

## 🛠️ Built with

**Agents & Backend**

![Python](https://img.shields.io/badge/Python_3.12-3776AB?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![LangGraph](https://img.shields.io/badge/LangGraph-1C3C3C?style=for-the-badge&logo=langchain&logoColor=white)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-D71F00?style=for-the-badge&logo=sqlalchemy&logoColor=white)

**Frontend**

![React](https://img.shields.io/badge/React_19-61DAFB?style=for-the-badge&logo=react&logoColor=black)
![TypeScript](https://img.shields.io/badge/TypeScript-3178C6?style=for-the-badge&logo=typescript&logoColor=white)
![Vite](https://img.shields.io/badge/Vite-646CFF?style=for-the-badge&logo=vite&logoColor=white)
![Tailwind](https://img.shields.io/badge/Tailwind-06B6D4?style=for-the-badge&logo=tailwindcss&logoColor=white)
![Framer Motion](https://img.shields.io/badge/Framer_Motion-8B5CF6?style=for-the-badge&logo=framer&logoColor=white)

**Data, AI & Infra**

![PostgreSQL](https://img.shields.io/badge/PostgreSQL_+_pgvector-4169E1?style=for-the-badge&logo=postgresql&logoColor=white)
![Redis](https://img.shields.io/badge/Redis-DC382D?style=for-the-badge&logo=redis&logoColor=white)
![Gemini](https://img.shields.io/badge/Gemini-8E75B2?style=for-the-badge&logo=googlegemini&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)
![AWS](https://img.shields.io/badge/AWS_EC2-FF9900?style=for-the-badge&logo=amazonaws&logoColor=white)
![Terraform](https://img.shields.io/badge/Terraform-7B42BC?style=for-the-badge&logo=terraform&logoColor=white)
![GitHub Actions](https://img.shields.io/badge/Actions_CI/CD-2088FF?style=for-the-badge&logo=githubactions&logoColor=white)

---

## 🏛️ Architecture

```
┌──────────────────────────────────────────────────────────────┐
│  React + Vite SPA (Framer Motion)  ·  Onboarding → Dashboard   │
│  Trips · Creative · Sourcing · Publishing · Leads · Analytics  │
└───────────────┬──────────────────────────────────────────────┘
                │  REST + SSE (live agent streams)
┌───────────────▼──────────────────────────────────────────────┐
│  FastAPI  ·  JWT auth  ·  per-request tenant binding           │
│  ┌─────────────────── LangGraph agents ──────────────────┐    │
│  │ Itinerary · Creative · Hotel · Transport · Lead/Follow │    │
│  │ every graph drafts → Approval Center → publish/send    │    │
│  └────────────────────────────────────────────────────────┘   │
│  Postgres + pgvector (Row-Level Security)  ·  Redis  ·  S3     │
│  APScheduler worker → auto follow-ups & scheduled posts        │
└───────────────┬──────────────────────────────────────────────┘
   Meta Lead Ads · WhatsApp Cloud API · Instagram Graph · Email/SMS
```

**Multi-tenancy is real, not bolted on:** every business table carries a `tenant_id` and Postgres
**Row-Level Security** filters rows by the current tenant — enforced at the database, not just in
app code. (There's a test that proves Agency A literally cannot read Agency B's data.)

---

## 🧪 Why it's built this way

- **Human-in-the-loop everywhere** — agents propose, humans dispose. No silent sends.
- **Keyless by default** — built-in mock LLM/image providers mean the whole app runs end-to-end
  with **zero API keys**. Drop in a free `GEMINI_API_KEY` and real AI lights up, no code change.
- **Tested, not vibes** — 17 backend tests cover auth, tenant isolation, every agent flow, the
  scheduler, and the webhooks. CI runs them against real Postgres + pgvector on every push.
- **Production-shaped** — Gunicorn + a separate scheduler worker, S3 asset storage, Terraform for
  AWS, and **push-to-deploy** CI/CD.

---

## 🚀 Quick start (local, keyless)

```bash
git clone <this-repo> TravelOS && cd TravelOS
cp .env.example .env
docker compose up --build
# Backend  → http://localhost:8000/docs
# Frontend → http://localhost:5173
```

No keys needed — it runs on built-in mocks. Want real AI? Add a free key from
[Google AI Studio](https://aistudio.google.com/apikey):

```bash
GEMINI_API_KEY=...          # in .env
LLM_TEXT_PROVIDER=gemini
LLM_IMAGE_PROVIDER=gemini
```

---

## ☁️ Deploy

| Target | Guide |
|--------|-------|
| 🆓 One free-tier EC2 box (Docker, single origin) | [`docs/AWS_FREE_TIER.md`](docs/AWS_FREE_TIER.md) |
| 🏗️ Full AWS production (ECS · RDS · ElastiCache · S3 · CloudFront, via Terraform) | [`docs/DEPLOY.md`](docs/DEPLOY.md) · [`infra/terraform`](infra/terraform) |

**Push-to-deploy** is wired: a self-hosted GitHub Actions runner on the demo box rebuilds it on
every push to `main` — no inbound ports opened.

---

## 🗺️ Roadmap

- [x] **Phase 0** — Foundation: multi-tenant auth, animated onboarding, dashboard shell
- [x] **Phase 1** — Trip + Creative agents (itinerary, posters, captions, brochure)
- [x] **Phase 2** — CRM + Leads (Meta webhook, web capture, Email/SMS follow-ups, Kanban)
- [x] **Phase 3** — Sourcing + Instagram publishing
- [x] **Phase 4** — WhatsApp Cloud API, reels, analytics
- [x] **Phase 5** — Production: Gunicorn + worker, S3, Docker, Terraform, CI/CD

Design doc → [`docs/PLAN.md`](docs/PLAN.md)

---

<div align="center">

**Built by [@ydvlalit03](https://github.com/ydvlalit03)** 🏔️

*ship fast · eval faster · build things that actually work*

</div>
