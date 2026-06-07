"""Factory for chat models and image providers, selected by config.

Keeping selection here means agents just call ``get_chat_model()`` and stay
provider-agnostic. Swap Gemini/Groq (or a paid model later) via env only.
"""
from __future__ import annotations

from functools import lru_cache
from typing import TYPE_CHECKING

from app.agents.llm.images import ImageProvider, build_image_provider
from app.core.config import settings

if TYPE_CHECKING:
    from langchain_core.language_models.chat_models import BaseChatModel


def get_chat_model(
    provider: str | None = None,
    *,
    temperature: float = 0.7,
    **kwargs,
) -> "BaseChatModel":
    """Return a configured LangChain chat model for the given provider.

    provider: "gemini" (default, generous free tier) or "groq" (fast, low latency
    — good for CRM reply drafting). Falls back to the configured default.
    """
    provider = provider or settings.llm_text_provider

    if provider == "gemini":
        from langchain_google_genai import ChatGoogleGenerativeAI

        if not settings.gemini_api_key:
            raise RuntimeError("GEMINI_API_KEY is not set")
        return ChatGoogleGenerativeAI(
            model=settings.gemini_text_model,
            google_api_key=settings.gemini_api_key,
            temperature=temperature,
            **kwargs,
        )

    if provider == "groq":
        from langchain_groq import ChatGroq

        if not settings.groq_api_key:
            raise RuntimeError("GROQ_API_KEY is not set")
        return ChatGroq(
            model=settings.groq_model,
            api_key=settings.groq_api_key,
            temperature=temperature,
            **kwargs,
        )

    raise ValueError(f"Unknown text provider: {provider}")


@lru_cache
def get_image_provider(name: str | None = None) -> ImageProvider:
    return build_image_provider(name)
