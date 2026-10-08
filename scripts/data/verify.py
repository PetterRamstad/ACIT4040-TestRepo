from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.data.check import validate_registry

NON_FATAL_STATUSES = {"human_required", "needs_user_confirmation", "optional"}


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate configured dataset artifacts")
    parser.add_argument("--json", action="store_true", help="Print full validation report as JSON")
    args = parser.parse_args()

    reports = validate_registry()
    if args.json:
        print(json.dumps(reports, indent=2))
    else:
        for report in reports:
            status = report["status"].upper()
            print(f"{report['name']}: {status} - {report['message']}")

    fatal = [report for report in reports if report["status"] not in {"ok", *NON_FATAL_STATUSES}]
    return 1 if fatal else 0


if __name__ == "__main__":
    raise SystemExit(main())
