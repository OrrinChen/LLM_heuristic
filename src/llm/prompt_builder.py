from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class PromptBuilder:
    allowed_function: str = "score_candidate"

    def build_mutation_prompt(
        self, *, parent_code: str, benchmark_feedback: str
    ) -> str:
        signature = f"def {self.allowed_function}(state, candidate):"
        return "\n".join(
            [
                "You are mutating one heuristic scoring function.",
                "Return only Python code.",
                f"The returned code must define exactly this function: {signature}",
                "Do not define helper functions.",
                "Do not import modules.",
                "Do not read files, use network access, spawn processes, "
                "or inspect globals.",
                "Lower scores are better.",
                "",
                "Parent program:",
                "```python",
                parent_code.strip(),
                "```",
                "",
                "Benchmark feedback:",
                benchmark_feedback.strip(),
                "",
                "Return the complete replacement function now.",
            ]
        )
