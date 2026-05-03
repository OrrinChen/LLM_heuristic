from __future__ import annotations

import hashlib
import json
import os
from dataclasses import dataclass, replace
from time import perf_counter
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
    input_cost_per_1k_tokens: float = 0.0
    output_cost_per_1k_tokens: float = 0.0

    @property
    def generate_content_url(self) -> str:
        base = self.endpoint_base.rstrip("/")
        return f"{base}/models/{self.model}:generateContent"


@dataclass(frozen=True)
class GenerationMetadata:
    model_name: str
    prompt_version: str
    temperature: float
    raw_response_hash: str
    cleaned_code_hash: str
    input_tokens: int
    output_tokens: int
    total_tokens: int
    latency_seconds: float
    estimated_cost_usd: float


@dataclass(frozen=True)
class GeneratedCode:
    code: str
    metadata: GenerationMetadata


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
        return self.generate_with_metadata(prompt).code

    def generate_with_metadata(
        self,
        prompt: str,
        *,
        prompt_version: str = "score-bin-mutation-v1",
    ) -> GeneratedCode:
        request = Request(
            self.config.generate_content_url,
            data=json.dumps(self._request_payload(prompt)).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "X-goog-api-key": self.api_key,
            },
            method="POST",
        )
        started = perf_counter()
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
        latency = perf_counter() - started

        raw_text = _extract_generated_text(payload)
        return build_generated_code(
            raw_text,
            prompt=prompt,
            model_name=self.config.model,
            prompt_version=prompt_version,
            temperature=self.config.temperature,
            latency_seconds=latency,
            usage_metadata=payload.get("usageMetadata"),
            input_cost_per_1k_tokens=self.config.input_cost_per_1k_tokens,
            output_cost_per_1k_tokens=self.config.output_cost_per_1k_tokens,
        )

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


def build_generated_code(
    raw_text: str,
    *,
    prompt: str,
    model_name: str,
    prompt_version: str,
    temperature: float,
    latency_seconds: float,
    usage_metadata: Optional[object] = None,
    input_cost_per_1k_tokens: float = 0.0,
    output_cost_per_1k_tokens: float = 0.0,
) -> GeneratedCode:
    code = extract_python_code(raw_text)
    input_tokens, output_tokens, total_tokens = _token_counts(
        prompt,
        raw_text,
        usage_metadata,
    )
    estimated_cost = (input_tokens / 1000.0) * input_cost_per_1k_tokens + (
        output_tokens / 1000.0
    ) * output_cost_per_1k_tokens
    return GeneratedCode(
        code=code,
        metadata=GenerationMetadata(
            model_name=model_name,
            prompt_version=prompt_version,
            temperature=temperature,
            raw_response_hash=_sha256(raw_text),
            cleaned_code_hash=_sha256(code),
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            total_tokens=total_tokens,
            latency_seconds=latency_seconds,
            estimated_cost_usd=estimated_cost,
        ),
    )


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


def _token_counts(
    prompt: str,
    raw_text: str,
    usage_metadata: Optional[object],
) -> tuple[int, int, int]:
    if isinstance(usage_metadata, dict):
        prompt_tokens = _int_field(usage_metadata, "promptTokenCount")
        output_tokens = _int_field(usage_metadata, "candidatesTokenCount")
        total_tokens = _int_field(usage_metadata, "totalTokenCount")
        if prompt_tokens is not None and output_tokens is not None:
            return (
                prompt_tokens,
                output_tokens,
                total_tokens or prompt_tokens + output_tokens,
            )
    prompt_tokens = _estimate_tokens(prompt)
    output_tokens = _estimate_tokens(raw_text)
    return prompt_tokens, output_tokens, prompt_tokens + output_tokens


def _int_field(payload: Mapping[str, object], key: str) -> Optional[int]:
    value = payload.get(key)
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        return int(value)
    return None


def _estimate_tokens(text: str) -> int:
    return max(1, len(text.replace("\n", " ").split()))


def _sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


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
