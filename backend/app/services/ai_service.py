from __future__ import annotations

import asyncio
import json
import logging
import re
from abc import ABC, abstractmethod
from typing import Any
import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)


class AIServiceError(Exception):
    """Domain exception for AI provider failures."""
    pass


class AIServiceRateLimitError(AIServiceError):
    """Raised when free-tier rate limits (HTTP 429) are reached."""
    pass


class BaseAIProvider(ABC):
    """Abstract interface for AI completions and structured generations."""

    @abstractmethod
    async def generate_text(self, prompt: str, system_instruction: str | None = None, model: str | None = None) -> str:
        """Generate text from prompt."""

    @abstractmethod
    async def generate_structured(self, prompt: str, system_instruction: str | None = None, model: str | None = None) -> dict[str, Any]:
        """Generate structured JSON output from prompt."""


def clean_json_markdown(text: str) -> str:
    """Strip markdown code block fences (```json ... ```) from model output."""
    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```[a-zA-Z]*\n?", "", cleaned)
        cleaned = re.sub(r"\n?```$", "", cleaned)
    return cleaned.strip()


class GeminiFreeProvider(BaseAIProvider):
    """Google AI Studio Free Tier provider using Gemini 1.5 Flash or configured free model."""

    def __init__(self) -> None:
        self.api_key = settings.GEMINI_API_KEY
        self.base_url = "https://generativelanguage.googleapis.com/v1beta/models"

    async def _execute_with_retry(self, url: str, payload: dict[str, Any]) -> dict[str, Any]:
        """Execute request with exponential backoff on HTTP 429."""
        if not self.api_key:
            raise AIServiceError("GEMINI_API_KEY is not configured. Set it in .env or switch to Ollama.")

        url_with_key = f"{url}?key={self.api_key}"
        backoff_delays = [1.0, 2.0, 4.0]

        async with httpx.AsyncClient(timeout=15.0) as client:
            for attempt, delay in enumerate(backoff_delays, start=1):
                try:
                    response = await client.post(url_with_key, json=payload)
                    if response.status_code == 429:
                        logger.warning("Gemini free-tier rate limit reached (HTTP 429). Attempt %s/%s. Retrying in %ss", attempt, len(backoff_delays), delay)
                        if attempt == len(backoff_delays):
                            raise AIServiceRateLimitError("Gemini free-tier quota momentarily reached. Please wait a few seconds and retry.")
                        await asyncio.sleep(delay)
                        continue

                    response.raise_for_status()
                    return response.json()
                except httpx.HTTPStatusError as e:
                    if e.response.status_code == 429:
                        raise AIServiceRateLimitError("Gemini free-tier rate limit exceeded. Please retry in a few moments.") from e
                    raise AIServiceError(f"Gemini API error: {e.response.text}") from e
                except httpx.RequestError as e:
                    raise AIServiceError(f"Network error connecting to Gemini API: {str(e)}") from e

        raise AIServiceError("Failed to obtain response from Gemini API after retries.")

    async def generate_text(self, prompt: str, system_instruction: str | None = None, model: str | None = None) -> str:
        target_model = model or settings.AI_MODEL_CHAT
        url = f"{self.base_url}/{target_model}:generateContent"

        contents = [{"parts": [{"text": prompt}]}]
        payload: dict[str, Any] = {"contents": contents}

        if system_instruction:
            payload["systemInstruction"] = {"parts": [{"text": system_instruction}]}

        data = await self._execute_with_retry(url, payload)
        try:
            return data["candidates"][0]["content"]["parts"][0]["text"]
        except (KeyError, IndexError) as e:
            raise AIServiceError("Malformed response from Gemini API.") from e

    async def generate_structured(self, prompt: str, system_instruction: str | None = None, model: str | None = None) -> dict[str, Any]:
        target_model = model or settings.AI_MODEL_ANALYSIS
        url = f"{self.base_url}/{target_model}:generateContent"

        contents = [{"parts": [{"text": prompt}]}]
        payload: dict[str, Any] = {
            "contents": contents,
            "generationConfig": {"responseMimeType": "application/json"},
        }
        if system_instruction:
            payload["systemInstruction"] = {"parts": [{"text": system_instruction}]}

        data = await self._execute_with_retry(url, payload)
        try:
            text = data["candidates"][0]["content"]["parts"][0]["text"]
            cleaned = clean_json_markdown(text)
            return json.loads(cleaned)
        except (KeyError, IndexError, json.JSONDecodeError) as e:
            logger.error("Failed to parse JSON response: %s", data)
            raise AIServiceError("Gemini output could not be parsed into valid JSON.") from e


class OllamaProvider(BaseAIProvider):
    """Local offline Ollama provider ($0 cost, 100% offline)."""

    def __init__(self) -> None:
        self.base_url = settings.OLLAMA_BASE_URL.rstrip("/")

    async def generate_text(self, prompt: str, system_instruction: str | None = None, model: str | None = None) -> str:
        target_model = model or settings.AI_MODEL_CHAT
        url = f"{self.base_url}/api/generate"
        payload = {
            "model": target_model,
            "prompt": prompt,
            "system": system_instruction or "",
            "stream": False,
        }
        async with httpx.AsyncClient(timeout=90.0) as client:
            try:
                res = await client.post(url, json=payload)
                res.raise_for_status()
                return res.json().get("response", "")
            except Exception as e:
                raise AIServiceError(f"Error calling local Ollama instance at {self.base_url}: {str(e)}") from e

    async def generate_structured(self, prompt: str, system_instruction: str | None = None, model: str | None = None) -> dict[str, Any]:
        target_model = model or settings.AI_MODEL_ANALYSIS
        url = f"{self.base_url}/api/generate"
        payload = {
            "model": target_model,
            "prompt": f"{prompt}\nReturn strictly JSON with no markdown wrapping.",
            "system": system_instruction or "You are a JSON generator. Output only valid JSON.",
            "format": "json",
            "stream": False,
        }
        async with httpx.AsyncClient(timeout=90.0) as client:
            try:
                res = await client.post(url, json=payload)
                res.raise_for_status()
                raw_text = res.json().get("response", "{}")
                return json.loads(clean_json_markdown(raw_text))
            except Exception as e:
                raise AIServiceError(f"Error parsing Ollama JSON response: {str(e)}") from e


class GroqProvider(BaseAIProvider):
    """Groq Free Tier provider (ultra-fast, low-latency Llama inference)."""

    def __init__(self) -> None:
        self.api_key = settings.GROQ_API_KEY
        self.base_url = "https://api.groq.com/openai/v1/chat/completions"

    async def generate_text(self, prompt: str, system_instruction: str | None = None, model: str | None = None) -> str:
        if not self.api_key:
            raise AIServiceError("GROQ_API_KEY is not configured.")
        target_model = model or "llama-3.3-70b-versatile"
        messages = []
        if system_instruction:
            messages.append({"role": "system", "content": system_instruction})
        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": target_model,
            "messages": messages,
            "temperature": 0.7,
        }
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        async with httpx.AsyncClient(timeout=15.0) as client:
            try:
                res = await client.post(self.base_url, json=payload, headers=headers)
                if res.status_code == 429:
                    raise AIServiceRateLimitError("Groq rate limit reached.")
                res.raise_for_status()
                return res.json()["choices"][0]["message"]["content"]
            except Exception as e:
                raise AIServiceError(f"Groq API error: {str(e)}") from e

    async def generate_structured(self, prompt: str, system_instruction: str | None = None, model: str | None = None) -> dict[str, Any]:
        if not self.api_key:
            raise AIServiceError("GROQ_API_KEY is not configured.")
        target_model = model or "llama-3.3-70b-versatile"
        sys_msg = (system_instruction or "") + "\nYou must return strictly valid JSON. Do not include markdown codeblocks or preamble."
        messages = [
            {"role": "system", "content": sys_msg},
            {"role": "user", "content": prompt},
        ]
        payload = {
            "model": target_model,
            "messages": messages,
            "response_format": {"type": "json_object"},
            "temperature": 0.2,
        }
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        async with httpx.AsyncClient(timeout=15.0) as client:
            try:
                res = await client.post(self.base_url, json=payload, headers=headers)
                if res.status_code == 429:
                    raise AIServiceRateLimitError("Groq rate limit reached.")
                res.raise_for_status()
                raw = res.json()["choices"][0]["message"]["content"]
                return json.loads(clean_json_markdown(raw))
            except Exception as e:
                raise AIServiceError(f"Groq structured generation error: {str(e)}") from e


class AIService:
    """Unified AI service delegating to the configured provider."""

    def __init__(self) -> None:
        provider_name = settings.AI_PROVIDER.lower()
        if provider_name == "ollama":
            self.provider: BaseAIProvider = OllamaProvider()
        elif provider_name == "groq" or (not settings.GEMINI_API_KEY and settings.GROQ_API_KEY):
            self.provider = GroqProvider()
        else:
            # Default to Gemini free tier
            self.provider = GeminiFreeProvider()

    async def generate_text(self, prompt: str, system_instruction: str | None = None, model: str | None = None) -> str:
        return await self.provider.generate_text(prompt, system_instruction, model)

    async def generate_structured(self, prompt: str, system_instruction: str | None = None, model: str | None = None) -> dict[str, Any]:
        return await self.provider.generate_structured(prompt, system_instruction, model)


ai_service = AIService()


def get_ai_service() -> AIService:
    """Return singleton AI service instance."""
    return ai_service


