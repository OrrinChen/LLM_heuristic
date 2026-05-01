from __future__ import annotations

import json
import os
from dataclasses import dataclass, replace
from typing import Any, Callable, Mapping, Optional
from urllib.error import HTTPError, URLError
from urllib.request import Request
from urllib.request import urlopen as default_urlopen

UrlOpen = Callable[..., Any]


class GeminiClientError(RuntimeError):
    """Raised when the Gemini mutation client cannot produce candidate code."""


@dataclass(frozen=True)
class GeminiClientConfig:
    model: str = "gemini-2.5-flash"
    api_key_env: str = "GEMINI_API_KEY"
    model_env: str = "GEMINI_MODEL"
    endpoint_base: str = "https://generativelanguage.googleapis.com/v1beta"
    timeout_seconds: float = 30.0
    temperature: float = 0.2
    max_output_tokens: int = 1024

    @property
    def generate_content_url(self) -> str:
        base = self.endpoint_base.rstrip("/")
        return f"{base}/models/{self.model}:generateContent"


class GeminiMutationProvider:
    """Gemini-backed mutation provider for constrained scoring functions.

    The provider only handles prompt-to-text transport. Static validation and
    sandbox execution remain owned by ``MutationEngine`` and the evaluators.
    """

    def __init__(
        self,
        *,
        api_key: str,
        config: Optional[GeminiClientConfig] = None,
        urlopen: UrlOpen = default_urlopen,
    ) -> None:
        if not api_key:
            raise GeminiClientError("Gemini API key is empty")
        self.api_key = api_key
        self.config = config or GeminiClientConfig()
        self.urlopen = urlopen

    @classmethod
    def from_env(
        cls,
        *,
        config: Optional[GeminiClientConfig] = None,
        urlopen: UrlOpen = default_urlopen,
    ) -> "GeminiMutationProvider":
        resolved = config or GeminiClientConfig()
        api_key = os.environ.get(resolved.api_key_env)
        if not api_key:
            raise GeminiClientError(
                f"{resolved.api_key_env} must be set for live Gemini mutation"
            )
        model = os.environ.get(resolved.model_env)
        if model:
            resolved = replace(resolved, model=model)
        return cls(api_key=api_key, config=resolved, urlopen=urlopen)

    def generate(self, prompt: str) -> str:
        request = Request(
            self.config.generate_content_url,
            data=json.dumps(self._request_payload(prompt)).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "X-goog-api-key": self.api_key,
            },
            method="POST",
        )
        try:
            with self.urlopen(
                request,
                timeout=self.config.timeout_seconds,
            ) as response:
                payload = json.loads(response.read().decode("utf-8"))
        except HTTPError as exc:
            raise GeminiClientError(_http_error_message(exc)) from exc
        except (URLError, OSError, json.JSONDecodeError) as exc:
            raise GeminiClientError(f"Gemini request failed: {exc}") from exc

        return extract_python_code(_extract_generated_text(payload))

    def _request_payload(self, prompt: str) -> Mapping[str, object]:
        return {
            "contents": [
                {
                    "role": "user",
                    "parts": [{"text": prompt}],
                }
            ],
            "generationConfig": {
                "temperature": self.config.temperature,
                "maxOutputTokens": self.config.max_output_tokens,
                "responseMimeType": "text/plain",
            },
        }


def extract_python_code(text: str) -> str:
    stripped = text.strip()
    if not stripped.startswith("```"):
        return stripped + "\n"

    lines = stripped.splitlines()
    if not lines:
        return ""
    if lines[0].startswith("```"):
        lines = lines[1:]
    if lines and lines[-1].strip() == "```":
        lines = lines[:-1]
    return "\n".join(lines).strip() + "\n"


def _extract_generated_text(payload: Mapping[str, Any]) -> str:
    candidates = payload.get("candidates")
    if not isinstance(candidates, list) or not candidates:
        raise GeminiClientError("Gemini response did not include candidates")

    content = candidates[0].get("content")
    if not isinstance(content, dict):
        raise GeminiClientError("Gemini response candidate did not include content")

    parts = content.get("parts")
    if not isinstance(parts, list):
        raise GeminiClientError("Gemini response content did not include parts")

    text_parts = [part.get("text") for part in parts if isinstance(part, dict)]
    text = "\n".join(part for part in text_parts if isinstance(part, str)).strip()
    if not text:
        raise GeminiClientError("Gemini response did not include text")
    return text


def _http_error_message(exc: HTTPError) -> str:
    detail = exc.reason
    try:
        payload = json.loads(exc.read().decode("utf-8"))
    except (OSError, json.JSONDecodeError):
        payload = None
    if isinstance(payload, dict):
        error = payload.get("error")
        if isinstance(error, dict) and error.get("message"):
            detail = str(error["message"])
    return f"Gemini request failed with HTTP {exc.code}: {detail}"
