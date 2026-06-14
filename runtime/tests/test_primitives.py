from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

from context_skills.metering import TokenCounter, get_usage_sink
from context_skills.metering.tokens import heuristic_count_tokens
from context_skills.paths import find_repo_root
from context_skills.primitives import (
    budget_context,
    compact_session,
    disclose_skill,
    mask_observation,
    optimize_format,
    run_context_pipeline,
)
from context_skills.primitives.budgeter import ContextComponent
from context_skills.primitives.disclosure import DisclosureTier
from context_skills.primitives.service import run_primitive

BENCHMARK_DIR = find_repo_root() / "researcher" / "benchmarks" / "context-savings"
sys.path.insert(0, str(BENCHMARK_DIR))

import benchmark_context_savings as bench  # noqa: E402

TOLERANCE_PCT = 8.0


def assert_savings_close(actual_pct: float, expected_pct: float) -> None:
    assert abs(actual_pct - expected_pct) <= TOLERANCE_PCT, (
        f"savings {actual_pct:.1f}% vs benchmark {expected_pct:.1f}%"
    )


@pytest.fixture(scope="session")
def repo_root() -> Path:
    return find_repo_root()


@pytest.fixture(autouse=True)
def clear_usage() -> None:
    get_usage_sink().clear()
    yield
    get_usage_sink().clear()


def test_token_counter_heuristic_matches_benchmark() -> None:
    counter = TokenCounter(prefer_heuristic=True)
    sample = "hello world " * 100
    assert counter.count(sample) == heuristic_count_tokens(sample)


def test_observation_masking_matches_benchmark() -> None:
    expected = bench.benchmark_observation_masking()
    raw = json.loads((BENCHMARK_DIR / "test_fixtures" / "sample_tool_output.json").read_text())
    result = run_primitive(mask_observation, tool_name="database_query", content=raw)
    assert_savings_close(result.metrics.savings_pct, expected.savings_pct)
    assert result.metrics.tokens_saved > 0


def test_hierarchical_compaction_matches_benchmark() -> None:
    expected = bench.benchmark_hierarchical_compression()
    messages = json.loads((BENCHMARK_DIR / "test_fixtures" / "sample_conversation.json").read_text())
    result = run_primitive(compact_session, messages=messages, mode="hierarchical")
    assert_savings_close(result.metrics.savings_pct, expected.savings_pct)


def test_handoff_summary_matches_benchmark() -> None:
    expected = bench.benchmark_handoff_summary()
    messages = json.loads((BENCHMARK_DIR / "test_fixtures" / "sample_conversation.json").read_text())
    result = run_primitive(compact_session, messages=messages, mode="handoff_summary")
    assert_savings_close(result.metrics.savings_pct, expected.savings_pct)


def test_selective_retention_matches_benchmark() -> None:
    import inspect
    import re

    expected = bench.benchmark_selective_retention()
    source = inspect.getsource(bench.benchmark_selective_retention)
    match = re.search(r'exploration_session = """([\s\S]*?)"""', source)
    assert match is not None
    exploration_text = match.group(1)
    result = run_primitive(compact_session, text=exploration_text, mode="selective_retention")
    assert_savings_close(result.metrics.savings_pct, expected.savings_pct)


def test_format_optimization_matches_benchmark() -> None:
    expected = bench.benchmark_format_optimization()
    verbose = [
        "I have successfully read the file located at `src/auth/login.py`. The file contains 45 lines of Python code that implement the login functionality including the `login()` function, the `logout()` function, the `create_session()` helper function, and the `record_failed_attempt()` helper function. The file imports from `password_utils`, `models`, and `database` modules.",
        "I have now executed the test suite by running the command `pytest tests/test_auth.py -v`. The results show that all 10 tests have passed successfully. The total execution time was 2.31 seconds. No tests were skipped and no tests failed. The test coverage appears to be adequate for the current functionality.",
        "I have created the new file `auth/middleware.py` which contains 15 lines of code. This file implements the `auth_required` decorator function that checks for a valid Bearer token in the Authorization header of incoming HTTP requests. If the token is not present or is invalid/expired, it returns a 401 Unauthorized response. If the token is valid, it sets `request.current_user` to the authenticated user and allows the request to proceed to the decorated function.",
        "I searched the codebase using the grep tool for all occurrences of the string 'import auth' to find all files that import from the old monolithic auth module. The search returned 12 results across 8 different files. These files will all need to have their import statements updated to use the new modular package structure instead of importing from the single `auth.py` file.",
        "The git diff command shows that we have modified 3 files and created 8 new files in this refactoring session. The total lines added are 235 and the total lines removed are 150, giving us a net change of +85 lines. However, the code is now much better organized across separate modules with clear responsibilities.",
    ]
    result = run_primitive(optimize_format, content=verbose)
    assert_savings_close(result.metrics.savings_pct, expected.savings_pct)


def test_progressive_disclosure_matches_benchmark(repo_root: Path) -> None:
    expected = bench.benchmark_progressive_disclosure()
    result = run_primitive(disclose_skill, tier=DisclosureTier.INDEX, repo_root=repo_root)
    assert_savings_close(result.metrics.savings_pct, expected.savings_pct)


def test_context_partitioning_matches_benchmark() -> None:
    expected = bench.benchmark_context_partitioning()
    system_prompt = "You are a senior software engineer. You help with Python web development, testing, debugging, and code review. Follow PEP 8, write tests first, and document your changes." * 3
    tool_schemas = json.dumps([
        {"name": "read_file", "params": {"path": "string"}, "desc": "Read file contents"},
        {"name": "write_file", "params": {"path": "string", "content": "string"}, "desc": "Write file"},
    ], indent=2)
    history_turns = []
    for i in range(25):
        history_turns.append(f"[USER] Turn {i+1}: Can you check the implementation of feature_{i}?")
        history_turns.append(f"[ASSISTANT] I'll look at feature_{i}. Let me read the relevant files and run the tests.")
        history_turns.append(
            f"[TOOL:read_file] Contents of feature_{i}.py:\ndef feature_{i}():\n    '''Implementation of feature {i}.'''\n    data = load_data()\n    result = process(data)\n    return format_output(result)\n"
        )
        history_turns.append(f"[TOOL:run_tests] test_feature_{i}.py: 3/3 passed (0.5s)")
        history_turns.append(f"[ASSISTANT] Feature_{i} looks good. The implementation follows the expected pattern. Tests pass.")
    raw_history = "\n".join(history_turns)
    components = [
        ContextComponent(name="system", content=system_prompt, priority=100),
        ContextComponent(name="tools", content=tool_schemas, priority=80),
        ContextComponent(name="history", content=raw_history, priority=70),
        ContextComponent(name="task", content="Now let's work on the authentication refactor.", priority=90),
    ]
    result = run_primitive(budget_context, components=components, token_budget=10_000)
    assert_savings_close(result.metrics.savings_pct, expected.savings_pct)


def test_combined_pipeline_matches_benchmark() -> None:
    expected = bench.benchmark_combined_pipeline()
    session = {
        "system_prompt": "You are a senior software engineer helping with code review and refactoring. You specialize in Python, testing, and clean architecture." * 2,
        "tool_schemas": json.dumps([
            {"name": f"tool_{i}", "description": f"Tool {i} description with detailed parameters and usage examples. This tool is used for various operations including reading, writing, and processing data in the project.", "parameters": {"param1": "string", "param2": "integer"}}
            for i in range(12)
        ], indent=2),
        "retrieved_docs": "# Architecture Guide\n" + "\n".join([f"## Section {i}\nThis section covers the architecture decisions for component {i}. " * 5 for i in range(10)]),
        "conversation_history": "\n".join([
            f"[Turn {i}] User: Review feature_{i}\nAssistant: Looking at feature_{i}...\nTool Output: {json.dumps({'status': 'ok', 'file': f'feature_{i}.py', 'lines': 50, 'issues': []})}\nAssistant: Feature_{i} looks good, no issues found."
            for i in range(15)
        ]),
        "current_task": "Now please review the authentication module and suggest improvements.",
    }
    result = run_primitive(run_context_pipeline, session)
    assert_savings_close(result.metrics.savings_pct, expected.savings_pct)


def test_primitive_emits_usage_record() -> None:
    raw = json.loads((BENCHMARK_DIR / "test_fixtures" / "sample_tool_output.json").read_text())
    run_primitive(mask_observation, tool_name="database_query", content=raw)
    records = get_usage_sink().recent(limit=1)
    assert records
    assert records[0]["operation"] == "mask_observation"
    assert records[0]["tokens_saved"] > 0
    assert records[0]["correlation_id"]
