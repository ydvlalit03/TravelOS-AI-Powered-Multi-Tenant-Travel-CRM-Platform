"""Async database engine, session, and tenant Row-Level Security helpers.

Multi-tenancy is enforced at two layers:
  1. Application: every tenant-scoped query carries ``tenant_id``.
  2. Database: Postgres RLS policies filter rows by the ``app.current_tenant``
     GUC, set per request. The app connects as a NON-superuser role
     (``travelos_app``) so RLS is actually enforced (superusers bypass it).

Routes must NOT call ``session.commit()`` themselves — ``get_db`` wraps each
request in a single transaction and commits on success / rolls back on error.
This also makes ``SET LOCAL`` of the tenant GUC scoped to the request.
"""
import os
from collections.abc import AsyncGenerator
from uuid import UUID

from sqlalchemy import text
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.pool import NullPool

from app.core.config import settings

# Under pytest each test gets a fresh event loop; a pooled asyncpg connection
# would then be closed on a dead loop. NullPool opens/closes per checkout to
# avoid that. Production keeps normal pooling.
_engine_kwargs: dict = {"echo": settings.environment == "development"}
if os.getenv("PYTEST_VERSION") is not None:
    _engine_kwargs["poolclass"] = NullPool
else:
    _engine_kwargs["pool_pre_ping"] = True

engine = create_async_engine(settings.database_url, **_engine_kwargs)

async_session_factory = async_sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False, autoflush=False
)


async def set_tenant(session: AsyncSession, tenant_id: UUID | str) -> None:
    """Bind the current request's transaction to a tenant for RLS.

    Uses a transaction-local GUC so it never leaks across pooled connections.
    """
    await session.execute(
        text("SELECT set_config('app.current_tenant', :tid, true)"),
        {"tid": str(tenant_id)},
    )


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency: one transaction per request."""
    async with async_session_factory() as session:
        async with session.begin():
            yield session
