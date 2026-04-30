from __future__ import annotations

import math

import pytest

from llm.mutation_engine import DeterministicMutationProvider, MutationEngine
from llm.prompt_builder import PromptBuilder
from program_search.archive import ProgramArchive
from program_search.candidate_program import CandidateProgram
from program_search.evaluator import EvaluationResult
from sandbox.restricted_exec import execute_scoring_function
from sandbox.static_checks import ValidationConfig, validate_candidate_code

VALID_CODE = """
def score_candidate(state, candidate):
    remaining = state["capacity"] - candidate["size"]
    if remaining < 0:
        return 1000000
    return remaining + candidate.get("priority", 0)
"""


def test_static_checks_accept_single_allowed_scoring_function() -> None:
    result = validate_candidate_code(VALID_CODE)

    assert result.ok is True
    assert result.failure_reason is None
    assert result.function_name == "score_candidate"


@pytest.mark.parametrize(
    ("code", "expected_reason"),
    [
        (
            "import os\n\ndef score_candidate(state, candidate):\n    return 1\n",
            "import_not_allowed",
        ),
        (
            "def helper():\n    return 1\n\n"
            "def score_candidate(state, candidate):\n    return 1\n",
            "multiple_top_level_statements",
        ),
        ("def choose(state, candidate):\n    return 1\n", "missing_allowed_function"),
        (
            "def score_candidate(state, candidate):\n    return open('x').read()\n",
            "dangerous_call",
        ),
        (
            "def score_candidate(state, candidate):\n    return socket.socket()\n",
            "dangerous_name",
        ),
        (
            "def score_candidate(state, candidate):\n"
            "    return SECRET_LABELS[candidate['id']]\n",
            "disallowed_global",
        ),
    ],
)
def test_static_checks_reject_unsafe_or_out_of_contract_code(
    code: str, expected_reason: str
) -> None:
    result = validate_candidate_code(code)

    assert result.ok is False
    assert result.failure_reason is not None
    assert result.failure_reason.code == expected_reason


def test_static_checks_can_validate_a_named_bin_packing_function() -> None:
    code = """
def score_bin(item_size, bin_remaining_capacity, bin_features):
    return bin_remaining_capacity - item_size
"""

    result = validate_candidate_code(
        code, ValidationConfig(allowed_function="score_bin")
    )

    assert result.ok is True
    assert result.function_name == "score_bin"


def test_restricted_exec_returns_deterministic_numeric_result() -> None:
    first = execute_scoring_function(
        VALID_CODE,
        {"capacity": 10},
        {"size": 4, "priority": 2},
    )
    second = execute_scoring_function(
        VALID_CODE,
        {"capacity": 10},
        {"size": 4, "priority": 2},
    )

    assert first.ok is True
    assert second.ok is True
    assert first.value == 8
    assert second.value == first.value
    assert first.failure_reason is None
    assert first.runtime >= 0


def test_restricted_exec_records_static_validation_failure() -> None:
    result = execute_scoring_function(
        "def score_candidate(state, candidate):\n    return open('x')\n", {}, {}
    )

    assert result.ok is False
    assert result.value is None
    assert result.failure_reason is not None
    assert result.failure_reason.code == "dangerous_call"


def test_restricted_exec_records_timeout_failure() -> None:
    code = """
def score_candidate(state, candidate):
    while True:
        pass
"""

    result = execute_scoring_function(code, {}, {}, timeout_seconds=0.01)

    assert result.ok is False
    assert result.value is None
    assert result.failure_reason is not None
    assert result.failure_reason.code == "timeout"


def test_restricted_exec_records_runtime_exception() -> None:
    code = """
def score_candidate(state, candidate):
    return 1 / 0
"""

    result = execute_scoring_function(code, {}, {})

    assert result.ok is False
    assert result.failure_reason is not None
    assert result.failure_reason.code == "runtime_error"
    assert "ZeroDivisionError" in result.failure_reason.message


def test_restricted_exec_rejects_non_numeric_scores() -> None:
    code = """
def score_candidate(state, candidate):
    return "low"
"""

    result = execute_scoring_function(code, {}, {})

    assert result.ok is False
    assert result.failure_reason is not None
    assert result.failure_reason.code == "non_numeric_score"


def test_candidate_program_records_required_fields_and_failure_reason() -> None:
    candidate = CandidateProgram.create(
        code=VALID_CODE,
        prompt="mutate only score_candidate",
        parent_id="seed-1",
        generation=2,
        benchmark_scores={"toy": 1.5},
        runtime=0.25,
        failure_reason="timeout",
    )

    assert candidate.program_id
    assert candidate.parent_id == "seed-1"
    assert candidate.generation == 2
    assert candidate.code == VALID_CODE
    assert candidate.prompt == "mutate only score_candidate"
    assert candidate.benchmark_scores == {"toy": 1.5}
    assert candidate.runtime == 0.25
    assert candidate.failure_reason == "timeout"
    assert candidate.created_at.endswith("Z")


def test_archive_records_failed_and_surviving_candidates_with_lineage() -> None:
    archive = ProgramArchive()
    seed = CandidateProgram.create(code=VALID_CODE, prompt="seed", generation=0)
    child = CandidateProgram.create(
        code=VALID_CODE,
        prompt="child",
        parent_id=seed.program_id,
        generation=1,
    )
    failed = CandidateProgram.create(
        code="def score_candidate(state, candidate):\n    return open('x')\n",
        prompt="bad child",
        parent_id=seed.program_id,
        generation=1,
    )

    archive.record(
        seed,
        EvaluationResult.success(
            candidate_id=seed.program_id,
            benchmark_name="toy",
            score=2.0,
            runtime=0.01,
        ),
    )
    archive.record(
        child,
        EvaluationResult.success(
            candidate_id=child.program_id,
            benchmark_name="toy",
            score=1.0,
            runtime=0.01,
        ),
    )
    archive.record(
        failed,
        EvaluationResult.failure(
            candidate_id=failed.program_id,
            benchmark_name="toy",
            failure_reason="dangerous_call: open is not allowed",
            runtime=0.0,
        ),
    )

    assert archive.get(seed.program_id) == seed
    assert archive.get(child.program_id) == child
    assert archive.failures()[0].program_id == failed.program_id
    assert archive.survivors()[0].program_id == seed.program_id
    assert archive.survivors()[1].program_id == child.program_id
    assert [record.program_id for record in archive.lineage_for(child.program_id)] == [
        seed.program_id,
        child.program_id,
    ]


def test_prompt_builder_constrains_model_to_allowed_function_body() -> None:
    prompt = PromptBuilder(allowed_function="score_candidate").build_mutation_prompt(
        parent_code=VALID_CODE,
        benchmark_feedback="toy score: 8.0",
    )

    assert "Return only Python code" in prompt
    assert "def score_candidate(state, candidate):" in prompt
    assert "Do not define helper functions" in prompt
    assert "Do not import modules" in prompt
    assert VALID_CODE in prompt


def test_mutation_engine_validates_provider_output_before_creating_child() -> None:
    parent = CandidateProgram.create(code=VALID_CODE, prompt="seed", generation=0)
    provider = DeterministicMutationProvider(
        """
def score_candidate(state, candidate):
    return abs(state["capacity"] - candidate["size"])
"""
    )

    child = MutationEngine(provider=provider).mutate(
        parent,
        benchmark_feedback="prefer tighter fit",
    )

    assert child.parent_id == parent.program_id
    assert child.generation == 1
    assert child.failure_reason is None
    assert child.program_id != parent.program_id


def test_mutation_engine_records_invalid_provider_output_as_failed_child() -> None:
    parent = CandidateProgram.create(code=VALID_CODE, prompt="seed", generation=0)
    provider = DeterministicMutationProvider(
        "def score_candidate(state, candidate):\n    return open('x')\n"
    )

    child = MutationEngine(provider=provider).mutate(
        parent,
        benchmark_feedback="prefer tighter fit",
    )

    assert child.parent_id == parent.program_id
    assert child.generation == 1
    assert child.failure_reason is not None
    assert "dangerous_call" in child.failure_reason


def test_restricted_exec_allows_small_math_builtin_surface() -> None:
    code = """
def score_candidate(state, candidate):
    return min(abs(candidate["x"]), max(1, state["scale"]))
"""

    result = execute_scoring_function(code, {"scale": 4}, {"x": -7})

    assert result.ok is True
    assert math.isclose(result.value or 0, 4.0)
