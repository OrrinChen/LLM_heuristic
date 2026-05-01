from __future__ import annotations

import json
from typing import Any

import pytest

from llm.model_client import (
    GeminiClientConfig,
    GeminiClientError,
    GeminiMutationProvider,
    extract_python_code,
)
from llm.mutation_engine import MutationEngine
from program_search.candidate_program import CandidateProgram
from reports.plots import build_report_plots, render_report_plots_markdown
from reports.tables import build_report_tables, render_report_tables_markdown


def test_report_tables_cover_benchmarks_robustness_failures_and_steps() -> None:
    tables = build_report_tables()

    assert tuple(tables["tables"]) == (
        "benchmark_comparison",
        "robustness_summary",
        "worst_generalization_gaps",
        "failure_taxonomy",
        "recommended_next_steps",
    )
    assert len(tables["benchmark_comparison"]["rows"]) == 16
    assert len(tables["robustness_summary"]["rows"]) == 3
    assert len(tables["worst_generalization_gaps"]["rows"]) == 5
    assert len(tables["failure_taxonomy"]["rows"]) == 9
    assert tables["benchmark_comparison"]["rows"][0] == {
        "benchmark": "Online Bin Packing",
        "method": "first_fit",
        "split": "validation",
        "score": "8.500000",
        "top_program_id": "seed-000-tight_fit",
    }


def test_report_tables_markdown_renders_publication_ready_sections() -> None:
    markdown = render_report_tables_markdown(build_report_tables())

    assert markdown.startswith("# Report Tables")
    assert "## Benchmark Comparison" in markdown
    assert "| benchmark | method | split | score | top_program_id |" in markdown
    assert "phase6-seed-000-travel_fast" in markdown
    assert "external_benchmark_adapter" in markdown


def test_report_plots_return_plot_ready_series_and_ascii_rendering() -> None:
    plots = build_report_plots()

    assert tuple(plots["plots"]) == (
        "bin_packing_evolution_best_score",
        "amazon_discovery_best_score",
        "robustness_generalization_gaps",
        "failure_rate_by_generation",
    )
    assert len(plots["bin_packing_evolution_best_score"]["points"]) == 4
    assert len(plots["amazon_discovery_best_score"]["points"]) == 3
    assert len(plots["robustness_generalization_gaps"]["points"]) == 15
    assert len(plots["failure_rate_by_generation"]["points"]) == 7
    assert plots["bin_packing_evolution_best_score"]["ascii"]
    assert "generation=0" in plots["bin_packing_evolution_best_score"]["ascii"]


def test_report_plots_markdown_contains_curve_and_gap_sections() -> None:
    markdown = render_report_plots_markdown(build_report_plots())

    assert markdown.startswith("# Report Plots")
    assert "## Bin Packing Evolution Best Score" in markdown
    assert "## Robustness Generalization Gaps" in markdown
    assert "routing-large-routes" in markdown
    assert "phase6-seed-000-travel_fast" in markdown


def test_extract_python_code_strips_markdown_fences() -> None:
    assert (
        extract_python_code(
            "```python\ndef score_candidate(state, candidate):\n    return 0\n```\n"
        )
        == "def score_candidate(state, candidate):\n    return 0\n"
    )


def test_gemini_provider_requires_environment_key(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)

    with pytest.raises(GeminiClientError, match="GEMINI_API_KEY"):
        GeminiMutationProvider.from_env()


def test_gemini_provider_calls_generate_content_and_strips_code(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("GEMINI_API_KEY", "test-secret")
    transport = FakeGeminiTransport(
        {
            "candidates": [
                {
                    "content": {
                        "parts": [
                            {
                                "text": (
                                    "```python\n"
                                    "def score_candidate(state, candidate):\n"
                                    "    gap = state['capacity'] - candidate['size']\n"
                                    "    return abs(gap)\n"
                                    "```\n"
                                )
                            }
                        ]
                    }
                }
            ]
        }
    )
    provider = GeminiMutationProvider.from_env(
        config=GeminiClientConfig(model="gemini-test", timeout_seconds=7),
        urlopen=transport,
    )

    code = provider.generate("Return a scoring function")

    assert code.startswith("def score_candidate")
    assert "```" not in code
    assert len(transport.requests) == 1
    request = transport.requests[0]
    assert request.full_url.endswith("/models/gemini-test:generateContent")
    assert request.get_header("X-goog-api-key") == "test-secret"
    body = json.loads(request.data.decode("utf-8"))
    assert body["contents"][0]["parts"][0]["text"] == "Return a scoring function"
    assert body["generationConfig"]["temperature"] == 0.2


def test_gemini_provider_allows_model_override_from_env(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("GEMINI_API_KEY", "test-secret")
    monkeypatch.setenv("GEMINI_MODEL", "gemini-env-model")
    transport = FakeGeminiTransport(
        {
            "candidates": [
                {
                    "content": {
                        "parts": [
                            {
                                "text": (
                                    "def score_candidate(state, candidate):\n"
                                    "    return 0\n"
                                )
                            }
                        ]
                    }
                }
            ]
        }
    )
    provider = GeminiMutationProvider.from_env(urlopen=transport)

    provider.generate("Return a scoring function")

    assert transport.requests[0].full_url.endswith(
        "/models/gemini-env-model:generateContent"
    )


def test_mutation_engine_accepts_gemini_provider_output(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("GEMINI_API_KEY", "test-secret")
    transport = FakeGeminiTransport(
        {
            "candidates": [
                {
                    "content": {
                        "parts": [
                            {
                                "text": (
                                    "def score_candidate(state, candidate):\n"
                                    "    remaining = state['capacity']\n"
                                    "    remaining -= candidate['size']\n"
                                    "    return abs(remaining)\n"
                                )
                            }
                        ]
                    }
                }
            ]
        }
    )
    provider = GeminiMutationProvider.from_env(urlopen=transport)
    parent = CandidateProgram.create(
        code=(
            "def score_candidate(state, candidate):\n"
            "    return state['capacity'] - candidate['size']\n"
        ),
        prompt="seed",
        generation=0,
    )

    child = MutationEngine(provider=provider).mutate(
        parent,
        benchmark_feedback="prefer tighter fit",
    )

    assert child.parent_id == parent.program_id
    assert child.generation == 1
    assert child.failure_reason is None


class FakeGeminiTransport:
    def __init__(self, payload: dict[str, Any], *, status: int = 200) -> None:
        self.payload = payload
        self.status = status
        self.requests: list[Any] = []

    def __call__(self, request: Any, *, timeout: float) -> "FakeGeminiResponse":
        self.requests.append(request)
        assert timeout > 0
        return FakeGeminiResponse(self.payload, status=self.status)


class FakeGeminiResponse:
    def __init__(self, payload: dict[str, Any], *, status: int) -> None:
        self.payload = payload
        self.status = status

    def __enter__(self) -> "FakeGeminiResponse":
        return self

    def __exit__(self, *_args: object) -> None:
        return None

    def read(self) -> bytes:
        return json.dumps(self.payload).encode("utf-8")
