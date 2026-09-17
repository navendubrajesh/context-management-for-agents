"""Eval-as-a-service REST endpoints (CM-404)."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

from deps import require_operation
from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, Field

from context_iam.identity import Principal

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from researcher.eval.pipeline import EvalPipeline
from researcher.eval.store import get_eval_store

router = APIRouter(prefix="/eval", tags=["eval"])


class EvalCheck(BaseModel):
    type: str
    skill: str | None = None
    technique: str | None = None
    min_savings_pct: float | None = None


class EvalRunRequest(BaseModel):
    checks: list[EvalCheck] = Field(default_factory=list)
    use_judge: bool = False
    rubric: dict[str, Any] | None = None
    candidate_output: str = ""
    context: str = ""
    metadata: dict[str, Any] | None = None


@router.post("/run")
def eval_run(
    request: Request,
    body: EvalRunRequest,
    _: Principal = Depends(require_operation("eval:run")),
) -> dict[str, Any]:
    repo_root = Path(getattr(request.app.state, "repo_root", REPO_ROOT))
    pipeline = EvalPipeline(repo_root)
    checks = [check.model_dump(exclude_none=True) for check in body.checks]
    result = pipeline.run(
        checks=checks,
        use_judge=body.use_judge,
        rubric=body.rubric,
        candidate_output=body.candidate_output,
        context=body.context,
        metadata=body.metadata,
    )
    status = "pass" if result.passed else "fail"
    return {"status": status, **result.to_dict()}


@router.get("/results")
def eval_results(
    limit: int = 50,
    _: Principal = Depends(require_operation("eval:read")),
) -> dict[str, Any]:
    runs = get_eval_store().list_runs(limit=limit)
    return {"results": [run.to_dict() for run in runs]}


@router.get("/results/{run_id}")
def eval_result(
    run_id: str,
    _: Principal = Depends(require_operation("eval:read")),
) -> dict[str, Any]:
    record = get_eval_store().get(run_id)
    if record is None:
        raise HTTPException(status_code=404, detail="Eval run not found")
    return record.to_dict()
