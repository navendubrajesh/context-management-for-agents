"""LLM-as-judge evaluator — offline heuristic port of examples/llm-as-judge-skills."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Rubric:
    criteria: str
    max_score: int = 10


@dataclass(frozen=True)
class EvaluationResult:
    score: float
    reasoning: str
    passed: bool


class LLMAsJudgeEvaluator:
    """Scores candidate outputs against rubrics without external LLM calls."""

    def evaluate_direct(self, *, rubric: Rubric, candidate_output: str, context: str = "") -> EvaluationResult:
        score = float(rubric.max_score)
        reasons: list[str] = []

        criteria = rubric.criteria.lower()
        output = candidate_output.lower()
        ctx = context.lower()

        if "concise" in criteria and len(candidate_output) > 500:
            score -= 4
            reasons.append("Output exceeds concise length threshold (500 chars).")

        if "factual" in criteria and ctx:
            context_words = [w for w in ctx.split() if len(w) > 4]
            output_words = set(output.split())
            overlap = [w for w in context_words if w in output_words]
            if not overlap:
                score -= 3
                reasons.append("No factual overlap with provided context.")

        if score < 0:
            score = 0.0

        passed = score >= rubric.max_score * 0.7
        reasoning = " ".join(reasons) if reasons else "Met all rubric criteria."
        return EvaluationResult(score=score, reasoning=reasoning, passed=passed)
