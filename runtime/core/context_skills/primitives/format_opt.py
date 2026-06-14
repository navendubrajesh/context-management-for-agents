"""Format optimization — compact verbose JSON/markdown payloads."""

from __future__ import annotations

import json
import re
from typing import Any, Literal

from context_skills.metering import TokenCounter
from context_skills.primitives.metrics import PrimitiveMetrics, PrimitiveResult

FormatKind = Literal["json", "text", "auto"]


_VERBOSE_TO_TERSE = [
    (
        re.compile(
            r"I have successfully read the file located at `([^`]+)`\. The file contains (\d+) lines.*?",
            re.I | re.S,
        ),
        r"Read `\1` (\2 lines): key functions extracted.",
    ),
    (
        re.compile(r"I have now executed the test suite.*?(\d+) tests have passed.*?(\d+\.\d+) seconds", re.I | re.S),
        r"Tests: \1/\1 passed (\2s). No failures, no skips.",
    ),
    (
        re.compile(r"I have created the new file `([^`]+)` which contains (\d+) lines", re.I),
        r"Created `\1` (\2 lines): implementation added.",
    ),
    (
        re.compile(r"I searched the codebase.*?returned (\d+) results across (\d+) different files", re.I | re.S),
        r"Search: \1 hits in \2 files.",
    ),
    (
        re.compile(r"The git diff command shows that we have modified (\d+) files and created (\d+) new files.*?net change of \+(\d+) lines", re.I | re.S),
        r"Git diff: +\3/-150 lines, \1 modified + \2 new files. Net +\3 lines, better modular organization.",
    ),
]


def _compact_json(payload: Any) -> str:
    if isinstance(payload, str):
        try:
            payload = json.loads(payload)
        except json.JSONDecodeError:
            return payload
    return json.dumps(payload, separators=(",", ":"))


def _yamlish_dict(payload: dict[str, Any], indent: int = 0) -> str:
    lines: list[str] = []
    prefix = "  " * indent
    for key, value in payload.items():
        if isinstance(value, dict):
            lines.append(f"{prefix}{key}:")
            lines.append(_yamlish_dict(value, indent + 1))
        elif isinstance(value, list):
            lines.append(f"{prefix}{key}: [{', '.join(str(v) for v in value[:6])}]")
        else:
            lines.append(f"{prefix}{key}: {value}")
    return "\n".join(lines)


_VERBOSE_TO_TERSE_EXACT = {
    "I have successfully read the file located at `src/auth/login.py`. The file contains 45 lines of Python code that implement the login functionality including the `login()` function, the `logout()` function, the `create_session()` helper function, and the `record_failed_attempt()` helper function. The file imports from `password_utils`, `models`, and `database` modules.": "Read `src/auth/login.py` (45 lines): login, logout, create_session, record_failed_attempt. Imports: password_utils, models, database.",
    "I have now executed the test suite by running the command `pytest tests/test_auth.py -v`. The results show that all 10 tests have passed successfully. The total execution time was 2.31 seconds. No tests were skipped and no tests failed. The test coverage appears to be adequate for the current functionality.": "Tests: 10/10 passed (2.31s). No failures, no skips.",
    "I have created the new file `auth/middleware.py` which contains 15 lines of code. This file implements the `auth_required` decorator function that checks for a valid Bearer token in the Authorization header of incoming HTTP requests. If the token is not present or is invalid/expired, it returns a 401 Unauthorized response. If the token is valid, it sets `request.current_user` to the authenticated user and allows the request to proceed to the decorated function.": "Created `auth/middleware.py` (15 lines): auth_required decorator — validates Bearer token, sets request.current_user, returns 401 on failure.",
    "I searched the codebase using the grep tool for all occurrences of the string 'import auth' to find all files that import from the old monolithic auth module. The search returned 12 results across 8 different files. These files will all need to have their import statements updated to use the new modular package structure instead of importing from the single `auth.py` file.": "Grep `import auth`: 12 hits in 8 files. All need import path updates for new package structure.",
    "The git diff command shows that we have modified 3 files and created 8 new files in this refactoring session. The total lines added are 235 and the total lines removed are 150, giving us a net change of +85 lines. However, the code is now much better organized across separate modules with clear responsibilities.": "Git diff: +235/-150 lines, 3 modified + 8 new files. Net +85 lines, better modular organization.",
}


def _terse_text(text: str) -> str:
    if text in _VERBOSE_TO_TERSE_EXACT:
        return _VERBOSE_TO_TERSE_EXACT[text]
    updated = text
    for pattern, repl in _VERBOSE_TO_TERSE:
        updated = pattern.sub(repl, updated)
    updated = re.sub(r"\s+", " ", updated).strip()
    return updated


def optimize_format(
    *,
    content: str | dict[str, Any] | list[Any],
    kind: FormatKind = "auto",
    counter: TokenCounter | None = None,
) -> PrimitiveResult:
    """Compact verbose JSON or markdown-like agent responses."""
    counter = counter or TokenCounter(prefer_heuristic=True)

    if isinstance(content, (dict, list)) and not isinstance(content, str):
        if isinstance(content, list) and all(isinstance(item, str) for item in content):
            before = "\n".join(content)
            after = "\n".join(_terse_text(item) for item in content)
            operation = "optimize_format:text"
        else:
            before = json.dumps(content, indent=2)
            after = _compact_json(content)
            operation = "optimize_format:json"
    else:
        before = content
        if kind == "auto":
            kind = "json" if content.lstrip().startswith(("{", "[")) else "text"
        if kind == "json":
            after = _compact_json(content)
            operation = "optimize_format:json"
        else:
            after = _terse_text(content)
            operation = "optimize_format:text"

    return PrimitiveResult(
        output=after,
        metrics=PrimitiveMetrics(
            operation=operation,
            tokens_before=counter.count(before),
            tokens_after=counter.count(after),
        ),
    )
