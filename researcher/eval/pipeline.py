"""Eval-as-a-service pipeline — deterministic checks + optional LLM judge."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from researcher.eval.deterministic import run_deterministic_checks
from researcher.eval.judge import LLMAsJudgeEvaluator, Rubric
from researcher.eval.store import EvalStore, get_eval_store


@dataclass(frozen=True)
class EvalResult:
    id: str
    passed: bool
    checks: list[dict[str, Any]]
    judge: dict[str, Any] | None

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "passed": self.passed,
            "checks": self.checks,
            "judge": self.judge,
        }


class EvalPipeline:
    def __init__(self, repo_root: Path, store: EvalStore | None = None) -> None:
        self.repo_root = repo_root
        self.store = store or get_eval_store()
        self.judge = LLMAsJudgeEvaluator()

    def run(
        self,
        *,
        checks: list[dict[str, Any]] | None = None,
        use_judge: bool = False,
        rubric: dict[str, Any] | None = None,
        candidate_output: str = "",
        context: str = "",
        metadata: dict[str, Any] | None = None,
    ) -> EvalResult:
        check_results = run_deterministic_checks(checks or [], self.repo_root)
        judge_result: dict[str, Any] | None = None

        if use_judge and rubric:
            evaluation = self.judge.evaluate_direct(
                rubric=Rubric(
                    criteria=str(rubric.get("criteria", "quality")),
                    max_score=int(rubric.get("max_score", 10)),
                ),
                candidate_output=candidate_output,
                context=context,
            )
            judge_result = {
                "score": evaluation.score,
                "reasoning": evaluation.reasoning,
                "passed": evaluation.passed,
            }

        passed = all(item.get("passed", False) for item in check_results)
        if judge_result is not None:
            passed = passed and judge_result["passed"]

        record = self.store.save(
            passed=passed,
            checks=check_results,
            judge=judge_result,
            metadata=metadata,
        )
        return EvalResult(
            id=record.id,
            passed=passed,
            checks=check_results,
            judge=judge_result,
        )
