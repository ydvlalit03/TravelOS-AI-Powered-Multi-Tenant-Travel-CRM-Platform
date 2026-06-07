"""TravelOS FastAPI application entrypoint."""
from contextlib import asynccontextmanager

from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api.v1 import api_router
from app.core.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup / shutdown hooks (scheduler, warm caches) go here in later phases.
    yield


app = FastAPI(
    title="TravelOS API",
    version="0.1.0",
    description="AI-powered multi-tenant travel CRM & operations platform.",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)

# Serve generated creatives (posters, brochures) in dev. S3+CDN in Phase 5.
_storage_dir = Path("/app/storage")
_storage_dir.mkdir(parents=True, exist_ok=True)
app.mount("/storage", StaticFiles(directory=str(_storage_dir)), name="storage")


@app.get("/health", tags=["meta"])
async def health() -> dict[str, str]:
    return {"status": "ok", "environment": settings.environment}


@app.get("/", tags=["meta"])
async def root() -> dict[str, str]:
    return {"service": "TravelOS API", "docs": "/docs"}
