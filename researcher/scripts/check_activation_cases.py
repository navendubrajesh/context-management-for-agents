#!/usr/bin/env python3
"""
check_activation_cases.py

Adversarial regression test fixture checking skill activation boundaries.
Uses content-matching heuristic to verify that queries trigger expected skills
and do NOT trigger inappropriate adjacent skills.
"""

import os
import sys
import json

# Import shared router from runtime/core (single implementation).
SCRIPT_DIR = os.path.dirname(__file__)
RUNTIME_CORE = os.path.abspath(os.path.join(SCRIPT_DIR, "..", "..", "runtime", "core"))
if RUNTIME_CORE not in sys.path:
    sys.path.insert(0, RUNTIME_CORE)

from context_skills.constants import EXPECTED_SKILLS  # noqa: E402
from context_skills.paths import find_repo_root  # noqa: E402
from context_skills.router import load_router_index, score_skill_match  # noqa: E402


def log_error(msg):
    print(f"[-] ERROR: {msg}", file=sys.stderr)


def log_info(msg):
    print(f"[+] INFO: {msg}")


def main():
    base_dir = find_repo_root(os.path.join(SCRIPT_DIR, "..", ".."))
    ac_file = os.path.join(base_dir, "researcher", "benchmarks", "activation-cases.jsonl")

    if not os.path.exists(ac_file):
        log_error(f"Missing activation cases file: {ac_file}")
        sys.exit(1)

    skills_data = load_router_index(base_dir)

    passed_cases = 0
    total_cases = 0
    failed = False

    with open(ac_file, "r", encoding="utf-8") as f:
        for i, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue

            try:
                case = json.loads(line)
            except Exception as e:
                log_error(f"Failed to parse line {i} as JSON: {e}")
                failed = True
                continue

            total_cases += 1
            case_id = case.get("id", f"case-{i}")
            query = case.get("query", "")
            expected = case.get("expected_skill", "")
            not_expected = case.get("not_skill", "")
            rationale = case.get("rationale", "")

            if expected not in skills_data or not_expected not in skills_data:
                log_error(
                    f"Case {case_id}: expected/not_expected skills invalid ({expected} / {not_expected})"
                )
                failed = True
                continue

            expected_score = score_skill_match(query, skills_data[expected])
            not_expected_score = score_skill_match(query, skills_data[not_expected])

            scores = {
                s_name: score_skill_match(query, s_data) for s_name, s_data in skills_data.items()
            }
            best_skill = max(scores, key=scores.get)

            if expected_score > not_expected_score and expected_score > 0:
                log_info(
                    f"Case {case_id} [{query}]: PASSED (Expected: {expected} ({expected_score:.1f}) > "
                    f"Not Expected: {not_expected} ({not_expected_score:.1f}). Best overall: {best_skill})"
                )
                passed_cases += 1
            else:
                log_error(
                    f"Case {case_id} [{query}]: FAILED\n"
                    f"  Expected: '{expected}' score {expected_score:.1f}\n"
                    f"  Not Expected: '{not_expected}' score {not_expected_score:.1f}\n"
                    f"  Rationale: {rationale}\n"
                    f"  Best overall was: '{best_skill}' with score {scores[best_skill]:.1f}"
                )
                failed = True

    print(f"\n[+] Activation cases check summary: {passed_cases}/{total_cases} passed.")
    if failed:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
