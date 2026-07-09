from __future__ import annotations

from typing import Any

import httpx
from tenacity import AsyncRetrying, RetryError, stop_after_attempt, wait_exponential


class RetrySafeHttpClient:
    """Small async HTTP client wrapper with exponential-backoff retries."""

    def __init__(
        self,
        timeout_seconds: float = 20.0,
        max_attempts: int = 3,
        proxy_url: str | None = None,
        default_headers: dict[str, str] | None = None,
    ) -> None:
        self.timeout_seconds = timeout_seconds
        self.max_attempts = max_attempts
        self.proxy_url = proxy_url
        self.default_headers = default_headers or {}

    async def get_json(
        self,
        url: str,
        params: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        async for attempt in AsyncRetrying(
            stop=stop_after_attempt(self.max_attempts),
            wait=wait_exponential(multiplier=1, min=1, max=8),
            reraise=True,
        ):
            with attempt:
                client_kwargs: dict[str, Any] = {"timeout": self.timeout_seconds}
                if self.proxy_url:
                    client_kwargs["proxy"] = self.proxy_url
                merged_headers = {**self.default_headers, **(headers or {})}
                async with httpx.AsyncClient(**client_kwargs) as client:
                    response = await client.get(url, params=params, headers=merged_headers or None)
                    response.raise_for_status()
                    payload = response.json()
                    if isinstance(payload, dict):
                        return payload
                    return {"items": payload}

        raise RetryError("HTTP request retries exhausted")

    async def get_text(
        self,
        url: str,
        params: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
    ) -> str:
        async for attempt in AsyncRetrying(
            stop=stop_after_attempt(self.max_attempts),
            wait=wait_exponential(multiplier=1, min=1, max=8),
            reraise=True,
        ):
            with attempt:
                client_kwargs: dict[str, Any] = {"timeout": self.timeout_seconds}
                if self.proxy_url:
                    client_kwargs["proxy"] = self.proxy_url
                merged_headers = {**self.default_headers, **(headers or {})}
                async with httpx.AsyncClient(**client_kwargs) as client:
                    response = await client.get(url, params=params, headers=merged_headers or None)
                    response.raise_for_status()
                    return response.text

        raise RetryError("HTTP request retries exhausted")
