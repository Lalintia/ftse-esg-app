"""Validate every indicator name/description in ftse_indicators.json against RC11.

Row-level check: for each code, extract its definition row from RC11 (code
occurrence followed by a type column, ending at the next row-start code) and
require the KB name or description to be contained in that row. Page-level
matching is NOT enough — EWT34's wrong name passed page-level because the
right text happened to be elsewhere on the same page.

Known limitation: ECC22 has no definition row in the Thai RC11 (only a
cross-reference on the Climate Change performance page), so it is reported
separately and not failed.

Usage:
    python3 scripts/validate_kb_against_rc11.py [--threshold 0.80]
"""

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
INDICATORS_PATH = REPO_ROOT / "backend" / "data" / "ftse_indicators.json"

sys.path.insert(0, str(REPO_ROOT / "scripts"))
from fix_kb_names_from_rc11 import containment, extract_rows, norm  # noqa: E402

KNOWN_NO_ROW = {"ECC22"}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--threshold", type=float, default=0.80)
    args = parser.parse_args()

    rows = extract_rows()
    indicators = json.load(open(INDICATORS_PATH, encoding="utf-8"))

    no_row, mismatches = [], []
    for ind in indicators:
        code = ind["indicator_code"]
        if code not in rows:
            if code not in KNOWN_NO_ROW:
                no_row.append(code)
            continue
        hay = norm(rows[code])
        score = max(
            containment(norm(ind["indicator_name"]), hay),
            containment(norm(ind.get("description", "")), hay),
        )
        if score < args.threshold:
            mismatches.append((code, score, ind["indicator_name"][:70]))

    print(f"checked {len(indicators)} indicators against {len(rows)} RC11 rows")
    print(f"known no-row codes (skipped): {sorted(KNOWN_NO_ROW)}")

    print(f"\nunexpected codes with no RC11 row: {len(no_row)}")
    for code in no_row:
        print(f"  {code}")

    print(f"\nname/description below threshold {args.threshold}: {len(mismatches)}")
    for code, score, name in sorted(mismatches, key=lambda x: x[1]):
        print(f"  {code}  score={score:.2f}  {name}")

    if not no_row and not mismatches:
        print("\nall indicator names verified against RC11 rows ✅")
        sys.exit(0)
    sys.exit(1)


if __name__ == "__main__":
    main()
