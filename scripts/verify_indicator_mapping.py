"""
Verify indicator_subsector_mapping.json against the official FTSE PDF.

Steps:
1. Parse ftse-russell-esg-data-model-indicators-rc11-2024-2025-thai.pdf
   using dynamic-header heuristic:
   - Indicator codes: left column (x0 ∈ [55, 90])
   - Subsector codes: detected relative to the "Subsector" column header per page
     (header x varies 362-415 across pages — must be x ≥ 300 to skip legend mentions)
2. Convert old ICB codes (3-4 digit) → new 8-digit codes via icb-legacy-to-new-mapping.xlsx
3. Diff fresh extraction vs existing JSON → print discrepancy report

Usage:
    cd /Users/alienmacbook/Desktop/OhmProject/FTSE
    python3 scripts/verify_indicator_mapping.py
"""

import json
import re
from collections import defaultdict
from pathlib import Path

import openpyxl
import pdfplumber

# ── Paths ─────────────────────────────────────────────────────────────────────
ROOT = Path(__file__).parent.parent
PDF_PATH = Path("/Users/alienmacbook/Desktop/OhmProject/ESG Knowledge") / \
    "ftse-russell-esg-data-model-indicators-rc11-2024-2025-thai.pdf"
XLSX_PATH = Path("/Users/alienmacbook/Desktop/OhmProject/ESG Knowledge") / \
    "icb-legacy-to-new-mapping.xlsx"
JSON_PATH = ROOT / "backend/data/indicator_subsector_mapping.json"

# ── Constants ─────────────────────────────────────────────────────────────────
INDICATOR_X_MIN = 55.0
INDICATOR_X_MAX = 90.0
# "Subsector" header must be in the table column (x ≥ 300), not in description text
SUBSECTOR_HEADER_X_MIN = 300.0
# Old ICB codes (3-4 digit) are within ±20px left of header and ±80px right
SUBSECTOR_OFFSET_LEFT = 20.0
SUBSECTOR_OFFSET_RIGHT = 80.0

INDICATOR_RE = re.compile(r"^[A-Z]{2,4}\d{2,3}$")
OLD_CODE_RE = re.compile(r"^\d{3,4}$")  # old ICB codes: 3-4 digits


def load_old_to_new_mapping(xlsx_path: Path) -> dict[str, str]:
    """Load old ICB code (str) → new 8-digit ICB code (str) from xlsx Sheet 2."""
    wb = openpyxl.load_workbook(str(xlsx_path), read_only=True, data_only=True)
    ws = wb.worksheets[1]  # 'Current to New Programmable Map'
    mapping: dict[str, str] = {}
    for row in ws.iter_rows(values_only=True):
        if len(row) < 4:
            continue
        old_code, _, _, new_code = row[:4]
        if old_code is None or new_code is None:
            continue
        old_str = str(old_code).strip()
        new_str = str(new_code).strip()
        if new_str.isdigit() and len(new_str) == 8:
            mapping[old_str] = new_str
            # Also key without leading zeros (PDF sometimes omits them)
            stripped = old_str.lstrip("0") or "0"
            if stripped != old_str:
                mapping[stripped] = new_str
    return mapping


def _find_subsector_column_x(words: list[dict]) -> float | None:
    """Find the x-position of the 'Subsector' table column header on a page."""
    for w in words:
        if w["text"] == "Subsector" and w["x0"] >= SUBSECTOR_HEADER_X_MIN:
            return float(w["x0"])
    return None


def extract_from_pdf(pdf_path: Path) -> dict[str, set[str]]:
    """
    Parse all pages and extract indicator → set of OLD ICB codes.

    Per-page:
    1. Find the 'Subsector' column header (x ≥ 300) → subsector_x
    2. Scan words top→bottom; indicator codes at left column,
       old ICB codes at [subsector_x-20, subsector_x+80]
    3. Each old ICB code is attributed to the most recently seen indicator.
    """
    indicator_to_old: dict[str, set[str]] = defaultdict(set)
    current_indicator: str | None = None

    with pdfplumber.open(str(pdf_path)) as pdf:
        for page in pdf.pages:
            words = page.extract_words(x_tolerance=3, y_tolerance=3)
            words.sort(key=lambda w: (round(w["top"] / 2) * 2, w["x0"]))

            subsector_x = _find_subsector_column_x(words)
            if subsector_x is None:
                # No subsector column on this page (legend/intro pages) — still scan for codes
                sub_x_min = SUBSECTOR_HEADER_X_MIN
                sub_x_max = 500.0
            else:
                sub_x_min = subsector_x - SUBSECTOR_OFFSET_LEFT
                sub_x_max = subsector_x + SUBSECTOR_OFFSET_RIGHT

            for word in words:
                text = word["text"].strip()
                x0 = word["x0"]

                if INDICATOR_X_MIN <= x0 <= INDICATOR_X_MAX and INDICATOR_RE.match(text):
                    current_indicator = text
                    if current_indicator not in indicator_to_old:
                        indicator_to_old[current_indicator] = set()

                elif sub_x_min <= x0 <= sub_x_max and OLD_CODE_RE.match(text):
                    if current_indicator:
                        indicator_to_old[current_indicator].add(text)

    return dict(indicator_to_old)


def convert_to_new_codes(
    indicator_to_old: dict[str, set[str]],
    old_to_new: dict[str, str],
) -> dict[str, set[str]]:
    """Convert old ICB code sets → new 8-digit code sets, logging unmapped codes."""
    result: dict[str, set[str]] = {}
    unmapped: dict[str, set[str]] = defaultdict(set)

    for indicator, old_codes in indicator_to_old.items():
        new_codes: set[str] = set()
        for old in old_codes:
            new = old_to_new.get(old) or old_to_new.get(old.lstrip("0"))
            if new:
                new_codes.add(new)
            else:
                unmapped[indicator].add(old)
        result[indicator] = new_codes

    if unmapped:
        print("\n⚠️  Old ICB codes with NO new-code mapping (may be discontinued):")
        for ind, codes in sorted(unmapped.items()):
            print(f"   {ind}: {sorted(codes)}")

    return result


def diff_mappings(
    fresh: dict[str, set[str]],
    existing_json: dict,
) -> None:
    """Compare fresh extraction vs existing JSON and print a report."""

    all_indicators = sorted(set(fresh) | set(existing_json))

    only_in_fresh: list[str] = []
    only_in_json: list[str] = []
    subsector_diffs: list[tuple[str, set[str], set[str]]] = []
    type_diffs: list[tuple[str, str, str]] = []

    for ind in all_indicators:
        in_fresh = ind in fresh
        in_json = ind in existing_json

        if in_fresh and not in_json:
            only_in_fresh.append(ind)
            continue
        if in_json and not in_fresh:
            only_in_json.append(ind)
            continue

        # Both present — compare subsectors
        fresh_subs = fresh[ind]
        json_subs = set(existing_json[ind].get("subsectors", []))

        fresh_has_subs = bool(fresh_subs)
        json_has_subs = bool(json_subs)

        # Type implied by fresh extraction
        fresh_type = "specific" if fresh_has_subs else "core"
        json_type = existing_json[ind].get("type", "")

        if fresh_type != json_type:
            type_diffs.append((ind, json_type, fresh_type))

        if fresh_subs != json_subs:
            added = fresh_subs - json_subs
            removed = json_subs - fresh_subs
            if added or removed:
                subsector_diffs.append((ind, added, removed))

    # ── Print Report ──────────────────────────────────────────────────────────
    print("\n" + "=" * 70)
    print("INDICATOR MAPPING VERIFICATION REPORT")
    print("Source: ftse-russell-esg-data-model-indicators-rc11-2024-2025-thai.pdf")
    print("=" * 70)

    print(f"\n📊 Summary:")
    print(f"  PDF extracted:    {len(fresh)} indicators")
    print(f"  JSON has:         {len(existing_json)} indicators")
    print(f"  Type conflicts:   {len(type_diffs)}")
    print(f"  Subsector diffs:  {len(subsector_diffs)}")
    print(f"  Only in PDF:      {len(only_in_fresh)}")
    print(f"  Only in JSON:     {len(only_in_json)}")

    if only_in_fresh:
        print(f"\n🆕 Indicators found in PDF but MISSING from JSON ({len(only_in_fresh)}):")
        for ind in only_in_fresh:
            subs = sorted(fresh[ind])
            print(f"   {ind}  →  {subs if subs else '(core/no subsectors)'}")

    if only_in_json:
        print(f"\n❓ Indicators in JSON but NOT found in PDF ({len(only_in_json)}):")
        for ind in only_in_json:
            print(f"   {ind}  (type={existing_json[ind].get('type')}, "
                  f"subsectors={existing_json[ind].get('subsectors', [])})")

    if type_diffs:
        print(f"\n⚡ Type conflicts — JSON says X, PDF implies Y ({len(type_diffs)}):")
        for ind, json_t, fresh_t in sorted(type_diffs):
            print(f"   {ind}: JSON={json_t} → PDF={fresh_t}")

    if subsector_diffs:
        print(f"\n🔍 Subsector differences ({len(subsector_diffs)}):")
        for ind, added, removed in sorted(subsector_diffs, key=lambda x: x[0]):
            if added:
                print(f"   {ind} + PDF has (missing from JSON): {sorted(added)}")
            if removed:
                print(f"   {ind} - JSON has (not in PDF):      {sorted(removed)}")

    if not (only_in_fresh or only_in_json or type_diffs or subsector_diffs):
        print("\n✅ No discrepancies found — JSON matches PDF exactly!")
    else:
        total = len(only_in_fresh) + len(only_in_json) + len(type_diffs) + len(subsector_diffs)
        print(f"\n⚠️  Total issues found: {total}")


def main() -> None:
    print("Loading old→new ICB code mapping...")
    old_to_new = load_old_to_new_mapping(XLSX_PATH)
    print(f"  Loaded {len(old_to_new)} mappings")

    print("Extracting indicators from PDF...")
    indicator_to_old = extract_from_pdf(PDF_PATH)
    print(f"  Found {len(indicator_to_old)} indicators in PDF")

    print("Converting old ICB codes → new 8-digit codes...")
    fresh = convert_to_new_codes(indicator_to_old, old_to_new)

    print("Loading existing JSON...")
    with open(JSON_PATH) as f:
        existing_json = json.load(f)

    diff_mappings(fresh, existing_json)


if __name__ == "__main__":
    main()
