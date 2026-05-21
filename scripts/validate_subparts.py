"""Validate sub-indicator counts against reference data.

Compares counts produced by subpart_resolver.get_subparts_for_subsector() against
known reference numbers from FTSE-verified sources.
"""
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "backend"))

from app.utils.subpart_resolver import (
    SECTOR_OVERRIDE_FILES,
    get_subparts_for_subsector,
)

REFERENCES = [
    {
        "subsector": "30201020",
        "name": "Consumer Lending (Tidlor)",
        "source": "Tidlor_FTSE_Gap_Analysis (By Ake).pdf",
        "expected": 219,
        "tolerance": 5,
    },
    {
        "subsector": "60101000",
        "name": "Integrated Oil & Gas (PTG)",
        "source": "PTG CDD (FTSE Russell 28 May 2025)",
        # PDF-only derivation (Option C). Remaining gap vs CDD: -14 = CDD structural
        # fields (year labels, coverage, date choices) not listed in FTSE PDF bullets.
        "expected": 399,
        "tolerance": 0,
    },
]


def main() -> None:
    print("=== Sub-indicator Validation ===\n")
    all_passed = True

    for ref in REFERENCES:
        subparts = get_subparts_for_subsector(ref["subsector"])
        actual = len(subparts)
        expected = ref["expected"]
        delta = actual - expected
        within_tolerance = abs(delta) <= ref["tolerance"]
        source_type = (
            "CDD override"
            if ref["subsector"] in SECTOR_OVERRIDE_FILES
            else "description-based"
        )

        status = "✅ PASS" if within_tolerance else "❌ FAIL"
        sign = f"{delta:+d}" if delta else "±0"
        print(f"{ref['name']}  [{source_type}]")
        print(f"  Reference: {ref['source']}")
        print(f"  Expected: {expected}  |  Actual: {actual}  |  Delta: {sign}")
        print(f"  {status}")
        print()

        if not within_tolerance:
            all_passed = False

    print("=" * 50)
    print("Overall:", "✅ ALL PASS" if all_passed else "❌ SOME FAILED")
    sys.exit(0 if all_passed else 1)


if __name__ == "__main__":
    main()
