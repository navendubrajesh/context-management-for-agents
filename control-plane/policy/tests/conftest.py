from __future__ import annotations

import sys
from pathlib import Path

POLICY_ROOT = Path(__file__).resolve().parents[1]
if str(POLICY_ROOT) not in sys.path:
    sys.path.insert(0, str(POLICY_ROOT))
