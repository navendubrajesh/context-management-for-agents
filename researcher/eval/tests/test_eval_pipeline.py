from __future__ import annotations

from pathlib import Path

import pytest

from researcher.eval.judge import LLMAsJudgeEvaluator, Rubric
from researcher.eval.pipeline import EvalPipeline
from researcher.eval.store import get_eval_store

REPO_ROOT = Path(__file__).resolve().parents[3]


@pytest.fixture(autouse=True)
def clear_store() -> None:
    get_eval_store().clear()


def test_llm_judge_passes_concise_output() -> None:
    judge = LLMAsJudgeEvaluator()
    result = judge.evaluate_direct(
        rubric=Rubric(criteria="concise factual answer", max_score=10),
        candidate_output="Short answer with shared context tokens.",
        context="shared context tokens from source document",
    )
    assert result.passed is True


def test_llm_judge_fails_verbose_output() -> None:
    judge = LLMAsJudgeEvaluator()
    result = judge.evaluate_direct(
        rubric=Rubric(criteria="concise factual answer", max_score=10),
        candidate_output="word " * 200,
        context="",
    )
    assert result.passed is False


def test_eval_pipeline_benchmark_gate() -> None:
    pipeline = EvalPipeline(REPO_ROOT)
    result = pipeline.run(
        checks=[{"type": "benchmark_threshold", "technique": "Observation Masking", "min_savings_pct": 90}],
    )
    assert result.passed is True
    assert result.id
    stored = get_eval_store().get(result.id)
    assert stored is not None


def test_eval_pipeline_with_judge() -> None:
    pipeline = EvalPipeline(REPO_ROOT)
    result = pipeline.run(
        checks=[],
        use_judge=True,
        rubric={"criteria": "concise", "max_score": 10},
        candidate_output="ok",
    )
    assert result.judge is not None
    assert result.passed is True
