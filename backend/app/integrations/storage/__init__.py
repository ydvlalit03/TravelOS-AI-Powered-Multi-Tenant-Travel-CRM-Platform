"""Object storage abstraction. Local filesystem in dev, S3 in prod (Phase 5).

Files are namespaced per tenant and served (local) under ``/storage``.
"""
from __future__ import annotations

import abc
import uuid
from pathlib import Path

from app.core.config import settings

STORAGE_DIR = Path("/app/storage")
STORAGE_URL_PREFIX = "/storage"


class StorageBackend(abc.ABC):
    @abc.abstractmethod
    def save(self, tenant_id: str, data: bytes, ext: str) -> str:
        """Persist bytes and return a servable URL path."""


class LocalStorage(StorageBackend):
    def save(self, tenant_id: str, data: bytes, ext: str) -> str:
        name = f"{uuid.uuid4().hex}.{ext}"
        folder = STORAGE_DIR / tenant_id
        folder.mkdir(parents=True, exist_ok=True)
        (folder / name).write_bytes(data)
        return f"{STORAGE_URL_PREFIX}/{tenant_id}/{name}"


class S3Storage(StorageBackend):  # pragma: no cover - wired in Phase 5
    def save(self, tenant_id: str, data: bytes, ext: str) -> str:
        raise NotImplementedError("S3 storage is implemented in Phase 5")


def get_storage() -> StorageBackend:
    if settings.storage_backend == "s3":
        return S3Storage()
    return LocalStorage()
