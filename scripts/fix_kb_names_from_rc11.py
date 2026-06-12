"""Repair indicator names/descriptions in the KB from RC11 row text.

Row-level validation found ~50 indicators (mostly the SSC theme, plus
EWT/GAC/SCR/SHS stragglers) whose KB names describe a different indicator
than the one RC11 defines for that code — the KB text came from a source
whose numbering does not match RC11, while the subsector mapping was
extracted correctly. The PTG CDD (official, English) agrees with RC11 on
every code we can cross-check, so RC11 is the repair source.

The fix updates TEXT ONLY (indicator_name, description, subpart_text for
a./b./c. subparts). Subpart key sets are never changed, so applicability
counts verified against TIDLOR/PTG references stay intact.

Usage:
    python3 scripts/fix_kb_names_from_rc11.py            # dry run (report)
    python3 scripts/fix_kb_names_from_rc11.py --apply    # write changes
"""

import argparse
import difflib
import json
import re
from pathlib import Path

import fitz

REPO_ROOT = Path(__file__).resolve().parents[1]
INDICATORS_PATH = REPO_ROOT / "backend" / "data" / "ftse_indicators.json"
SUBPARTS_PATH = REPO_ROOT / "backend" / "data" / "indicator_subparts.json"
RC11_PATH = Path(
    "/Users/alienmacbook/Desktop/OhmProject/ESG Knowledge/"
    "ftse-russell-esg-data-model-indicators-rc11-2024-2025-thai.pdf"
)

CODE_RE = re.compile(r"\b[A-Z]{3}\d{2}\b")
_STRIP = re.compile(r"[่-๋ํ\s]+")
# Subsector tail of a row, e.g. " 8355 Banks", " 7577 Water", "3573 Farming"
SUBSECTOR_TAIL_RE = re.compile(r"\s\d{3,4}\s+[A-Z]")
# Page furniture that bleeds into extracted blocks
JUNK_RE = re.compile(r"(FTSE Russell \|.*|ตัวชี้วัด\s*รหัส.*|\s\d{1,2}\s*$)", re.S)
TYPE_RE = re.compile(r"^(เชิงคุณภาพ|เชิงปริมาณ|/|\s)+")
SUBPART_SPLIT_RE = re.compile(r"\b([a-f])\.\s*")

THAI_RANGE = ("ก", "๛")


def is_thai(ch: str) -> bool:
    return THAI_RANGE[0] <= ch <= THAI_RANGE[1]


def clean_thai(text: str) -> str:
    """Rejoin Thai words the PDF broke across lines, keep Latin spacing."""
    tokens = text.split()
    out = ""
    for token in tokens:
        if out and not (is_thai(out[-1]) and is_thai(token[0])):
            out += " "
        out += token
    return out.strip(" .")


def norm(text: str) -> str:
    return _STRIP.sub("", text).replace("ำ", "า").lower()


def containment(needle: str, hay: str) -> float:
    if not needle:
        return 1.0
    if needle in hay:
        return 1.0
    matcher = difflib.SequenceMatcher(None, hay, needle, autojunk=False)
    return sum(b.size for b in matcher.get_matching_blocks()) / len(needle)


def extract_rows() -> dict[str, str]:
    """Definitive RC11 row text per code (occurrence followed by a type column)."""
    doc = fitz.open(RC11_PATH)
    full = "".join(str(page.get_text()) + "\n" for page in doc)

    def is_row_start(pos_end: int) -> bool:
        return "เชิง" in full[pos_end:pos_end + 40]

    rows: dict[str, str] = {}
    for m in CODE_RE.finditer(full):
        code = m.group(0)
        if not is_row_start(m.end()) or code in rows:
            continue
        # End the block at the next code that itself starts a row — codes
        # referenced inside a description (e.g. "SCR16, SCR17 และ SCR18")
        # must not truncate it.
        end = m.end() + 1500
        for nxt in CODE_RE.finditer(full, m.end(), m.end() + 1500):
            if is_row_start(nxt.end()):
                end = nxt.start()
                break
        rows[code] = full[m.end():end]
    return rows


def parse_row(block: str) -> tuple[str, str, dict[str, str]]:
    """Split an RC11 row block into (name, description, {letter: subpart_text})."""
    flat = " ".join(block.split())
    flat = TYPE_RE.sub("", flat)

    tail = SUBSECTOR_TAIL_RE.search(flat)
    if tail:
        flat = flat[: tail.start()]
    flat = flat.split("*เฉพาะ")[0]
    flat = JUNK_RE.sub("", flat)

    parts = SUBPART_SPLIT_RE.split(flat)
    name = clean_thai(parts[0])
    subparts: dict[str, str] = {}
    for letter, text in zip(parts[1::2], parts[2::2]):
        subparts[letter] = clean_thai(text)

    if subparts:
        description = " ".join(f"{k}. {v}" for k, v in subparts.items())
    else:
        description = name
    return name, description, subparts


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--threshold", type=float, default=0.80)
    args = parser.parse_args()

    rows = extract_rows()
    indicators = json.load(open(INDICATORS_PATH, encoding="utf-8"))
    subparts_db = json.load(open(SUBPARTS_PATH, encoding="utf-8"))

    fixed, letter_mismatch, no_row = [], [], []
    for ind in indicators:
        code = ind["indicator_code"]
        if code not in rows:
            no_row.append(code)
            continue
        hay = norm(rows[code])
        score = max(
            containment(norm(ind["indicator_name"]), hay),
            containment(norm(ind.get("description", "")), hay),
        )
        if score >= args.threshold:
            continue

        name, description, letters = parse_row(rows[code])
        print(f"### {code} (score {score:.2f})")
        print(f"  OLD: {ind['indicator_name'][:75]}")
        print(f"  NEW: {name[:75]}")

        if args.apply:
            ind["indicator_name"] = name
            ind["description"] = description

            existing = {
                k: v for k, v in subparts_db.items()
                if v["indicator_code"] == code
            }
            for entry in existing.values():
                entry["indicator_name"] = name
                letter = entry.get("subpart_letter", "")
                if letter in letters:
                    entry["subpart_text"] = letters[letter]
                elif not letters and entry.get("subpart_num") == 1:
                    entry["subpart_text"] = name
            kb_letters = {
                v.get("subpart_letter") for v in existing.values()
            } & set("abcdef")
            if kb_letters != set(letters):
                letter_mismatch.append(
                    (code, sorted(kb_letters), sorted(letters))
                )
        fixed.append(code)

    print(f"\nfixed: {len(fixed)} indicators")
    print(f"no RC11 row (manual): {no_row}")
    if letter_mismatch:
        print("\nsubpart letter sets differing from RC11 (texts updated where "
              "letters matched; key sets unchanged):")
        for code, kb_l, rc_l in letter_mismatch:
            print(f"  {code}: KB={kb_l} RC11={rc_l}")

    if args.apply:
        with open(INDICATORS_PATH, "w", encoding="utf-8") as f:
            json.dump(indicators, f, ensure_ascii=False, indent=2)
        with open(SUBPARTS_PATH, "w", encoding="utf-8") as f:
            json.dump(subparts_db, f, ensure_ascii=False, indent=2)
        print("\nfiles written")


if __name__ == "__main__":
    main()
