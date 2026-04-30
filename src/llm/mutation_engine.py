from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Protocol

from llm.prompt_builder import PromptBuilder
from program_search.candidate_program import CandidateProgram
from sandbox.static_checks import ValidationConfig, validate_candidate_code


class CodeMutationProvider(Protocol):
    """Provider protocol for future LLM clients."""

    def generate(self, prompt: str) -> str:
        """Return candidate Python code for the supplied prompt."""
        raise NotImplementedError


@dataclass(frozen=True)
class DeterministicMutationProvider:
    """Test provider that returns a fixed code mutation without API access."""

    code: str

    def generate(self, prompt: str) -> str:  # noqa: ARG002
        return self.code


class MutationEngine:
    def __init__(
        self,
        *,
        provider: CodeMutationProvider,
        prompt_builder: Optional[PromptBuilder] = None,
        validation_config: Optional[ValidationConfig] = None,
    ) -> None:
        self.provider = provider
        self.validation_config = validation_config or ValidationConfig()
        self.prompt_builder = prompt_builder or PromptBuilder(
            allowed_function=self.validation_config.allowed_function
        )

    def mutate(
        self, parent: CandidateProgram, *, benchmark_feedback: str
    ) -> CandidateProgram:
        prompt = self.prompt_builder.build_mutation_prompt(
            parent_code=parent.code,
            benchmark_feedback=benchmark_feedback,
        )
        child_code = self.provider.generate(prompt)
        validation = validate_candidate_code(child_code, self.validation_config)
        failure_reason = None
        if validation.failure_reason is not None:
            failure_reason = str(validation.failure_reason)
        return CandidateProgram.create(
            code=child_code,
            prompt=prompt,
            parent_id=parent.program_id,
            generation=parent.generation + 1,
            failure_reason=failure_reason,
        )
