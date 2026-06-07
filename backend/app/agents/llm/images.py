"""Image generation providers (posters / creatives), free-tier first.

- PollinationsProvider: no API key, no signup. Default for dev.
- GeminiImageProvider: Gemini 2.5 Flash Image ("Nano Banana"), ~500 free/day,
  called over the REST API so we don't pull in an extra SDK.

Both return raw PNG/JPEG bytes; the storage layer persists them.
"""
from __future__ import annotations

import abc
import base64
from urllib.parse import quote

import httpx

from app.core.config import settings


class ImageProvider(abc.ABC):
    @abc.abstractmethod
    async def generate(self, prompt: str, *, width: int = 1024, height: int = 1024) -> bytes:
        """Generate a single image and return its raw bytes."""


class PollinationsProvider(ImageProvider):
    """Free, keyless image generation (Flux). https://pollinations.ai"""

    BASE = "https://image.pollinations.ai/prompt"

    async def generate(self, prompt: str, *, width: int = 1024, height: int = 1024) -> bytes:
        url = f"{self.BASE}/{quote(prompt)}"
        params = {"width": width, "height": height, "nologo": "true", "model": "flux"}
        async with httpx.AsyncClient(timeout=120) as client:
            resp = await client.get(url, params=params)
            resp.raise_for_status()
            return resp.content


class GeminiImageProvider(ImageProvider):
    """Gemini Flash Image via the Generative Language REST API."""

    def __init__(self) -> None:
        if not settings.gemini_api_key:
            raise RuntimeError("GEMINI_API_KEY is required for the gemini image provider")
        self.model = settings.gemini_image_model
        self.api_key = settings.gemini_api_key

    async def generate(self, prompt: str, *, width: int = 1024, height: int = 1024) -> bytes:
        url = (
            f"https://generativelanguage.googleapis.com/v1beta/models/"
            f"{self.model}:generateContent"
        )
        body = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"responseModalities": ["IMAGE"]},
        }
        async with httpx.AsyncClient(timeout=120) as client:
            resp = await client.post(
                url, params={"key": self.api_key}, json=body
            )
            resp.raise_for_status()
            data = resp.json()
        for part in data["candidates"][0]["content"]["parts"]:
            inline = part.get("inlineData") or part.get("inline_data")
            if inline:
                return base64.b64decode(inline["data"])
        raise RuntimeError("Gemini returned no image data")


def build_image_provider(name: str | None = None) -> ImageProvider:
    name = name or settings.llm_image_provider
    if name == "gemini":
        return GeminiImageProvider()
    if name == "pollinations":
        return PollinationsProvider()
    raise ValueError(f"Unknown image provider: {name}")
