"""Expand performance indicators from 1-entry placeholders to full sub-fields.

Source of truth: FTSE ESG Indicators RC11 2024-2025 (Thai PDF) — public document.
CDD Excel is NOT used as input. Only PDF bullet lists are used to derive sub-fields.

Run: python scripts/expand_performance_subparts.py [--dry-run]
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parents[1] / "backend" / "data"
SUBPARTS_PATH = DATA_DIR / "indicator_subparts.json"

DRY_RUN = "--dry-run" in sys.argv


# ---------------------------------------------------------------------------
# PDF-derived sub-field schemas
# Each entry: (indicator_code, indicator_name, theme_code, theme_name,
#              data_type, exposure_level, type, subsectors, sub_fields)
# sub_fields = list of subpart_text strings (one per sub-field)
# ---------------------------------------------------------------------------

# EWT30 — PDF p.20: 3 year labels + 6 destinations × 3 years = 21
EWT30_DESTINATIONS = [
    "มหาสมุทร",
    "น้ำผิวดิน",
    "น้ำใต้ดิน/บ่อน้ำ",
    "การนำบัดน้ำเสียนอกไซต์งาน",
    "การนำน้ำไปใช้ประโยชน์/การใช้งานอื่น ๆ",
    "ปริมาณรวมทั้งหมด",
]

# EWT31 — PDF p.20: 3 year labels + 8 sources × 3 years = 27
EWT31_SOURCES = [
    "น้ำผิวดินจากแม่น้ำ ทะเลสาบ บ่อน้ำตามธรรมชาติ",
    "น้ำบาดาลจากบ่อน้ำบาดาล หลุมเจาะ",
    "น้ำที่ใช้แล้วในเหมือง ซึ่งเก็บจากในเหมือง",
    "น้ำประปาที่ดื่มได้",
    "น้ำเสียจากแหล่งภายนอก",
    "น้ำจากการกักเก็บน้ำฝน",
    "น้ำทะเล น้ำที่สกัดจากทะเลหรือมหาสมุทร",
    "ปริมาณรวมทั้งหมด",
]

# EPR18/19/21/24/25/26 — PDF p.13: "เชิงปริมาณ เป็นระยะเวลา 3 ปี"
# 3 year labels + 3 values = 6 sub-fields (NO coverage — not in PDF)
EPR_3YEAR_INDICATORS = {
    "EPR18": ("การปล่อยก๊าซไนตรัสออกไซด์ (NOx) (ตัน) เป็นระยะเวลา 3 ปี", "Pollution & Resources", "EPR"),
    "EPR19": ("การปล่อยก๊าซซัลเฟอร์ออกไซด์ (SOx) (ตัน) เป็นระยะเวลา 3 ปี", "Pollution & Resources", "EPR"),
    "EPR21": ("การปล่อยสารประกอบอินทรีย์ระเหยง่าย (VOCs) (กิโลกรัม) เป็นระยะเวลา 3 ปี", "Pollution & Resources", "EPR"),
    "EPR24": ("การเกิดของเสียอันตราย (ตัน) เป็นระยะเวลา 3 ปี", "Pollution & Resources", "EPR"),
    "EPR25": ("การเกิดของเสียที่นำกลับมาใช้ใหม่ไม่ได้ (ตัน) เป็นระยะเวลา 3 ปี", "Pollution & Resources", "EPR"),
    "EPR26": ("การเกิดของเสียที่รีไซเคิลได้ (ตัน) เป็นระยะเวลา 3 ปี", "Pollution & Resources", "EPR"),
}

# EPR27 — PDF p.13: "ต้นทุนรวมจากค่าปรับ...ในปีงบประมาณ" (ปีเดียว ไม่ใช่ 3 ปี)
# Pattern C: year label + monetary value = 2 sub-fields
EPR27_ITEMS = ["ปีงบประมาณ", "มูลค่า (สกุลเงิน)"]

# SHS15/38/40 — PDF p.36: "เชิงปริมาณ เป็นระยะเวลา 3 ปี" ไม่มี a/b
# Pattern A: 3 year labels + 3 values = 6 (coverage/definition/datatype = CDD-only)
SHS_3YEAR_INDICATORS = {
    "SHS15": ("อัตราการบาดเจ็บจากการทำงานถึงขั้นหยุดงานเป็นระยะเวลา 3 ปี", "Health & Safety", "SHS"),
    "SHS38": ("จำนวนการเสียชีวิตของพนักงานจากการทำงานเป็นระยะเวลา 3 ปี", "Health & Safety", "SHS"),
    "SHS40": ("จำนวนการเสียชีวิตของผู้รับเหมาจากการทำงานเป็นระยะเวลา 3 ปี", "Health & Safety", "SHS"),
}

# SLS16 — PDF p.46-47: 7 categories (a-g) เหมือน SLS03 แต่ไม่มี policy header
SLS16_ITEMS = [
    "เชื้อชาติ",
    "ศาสนา",
    "เพศสภาพ",
    "อายุ",
    "เพศวิถี",
    "ความพิการ",
    "สัญชาติ",
]

# EWT32/33 — PDF p.20: "เชิงปริมาณ เป็นระยะเวลา 3 ปี" สำหรับบริษัทที่ไม่เปิดเผยภาพรวม
# Pattern A: 3 year labels + 3 values = 6
EWT_3YEAR_FACILITY = {
    "EWT32": ("การดึงน้ำของสถานประกอบการเป็นระยะเวลา 3 ปี", "Water Security", "EWT"),
    "EWT33": ("การระบายน้ำของสถานประกอบการเป็นระยะเวลา 3 ปี", "Water Security", "EWT"),
}

# EWT34/35 — PDF p.21: เป้าหมายลดการใช้น้ำ มี a/b sub-items ชัดเจน = 2 sub-fields
# (Base Year, Target Year, Percentage, Type = CDD-only structural choices ไม่มีใน PDF)
EWT34_ITEMS = ["เป้าหมายที่ไม่ใช่เชิงปริมาณ (a)", "เป้าหมายเชิงปริมาณ (b)"]
EWT35_ITEMS = ["เป้าหมายที่ไม่ใช่เชิงปริมาณ (a)", "เป้าหมายเชิงปริมาณ (b)"]

# SLS03 — PDF p.46: sub-item a + 7 categories (i-vii) = 8
SLS03_ITEMS = [
    "การจัดการเรื่องการไม่เลือกปฏิบัติ/ความเท่าเทียม",  # sub-item a
    "เชื้อชาติ",
    "ศาสนา",
    "เพศสภาพ",
    "อายุ",
    "เพศวิถี",
    "ความพิการ",
    "สัญชาติ",
]

# EPR28 — PDF p.13: "สัดส่วน (%) ... เช่น ISO14001 หรือ EMAS"
# PDF explicitly mentions % value AND name of system → 2 derivable (Year = CDD-only)
EPR28_ITEMS = [
    "สัดส่วน (%) ของไซต์งานที่ได้รับการรับรอง",
    "ชื่อระบบการจัดการ (ISO14001, EMAS หรืออื่น)",
]

# GRM05 — PDF p.65: a) Code of Conduct/Ethics, b) ESG risks = 2 sub-fields
GRM05_ITEMS = [
    "หลักปฏิบัติ หลักจรรยาบรรณ หรือหลักเกณฑ์อื่นที่เทียบเท่า",
    "ความเสี่ยงด้าน ESG",
]

# GRM04 — PDF p.65: sub-item a + 5 checkboxes from sub-item b + name = 7
GRM04_ITEMS = [
    "บริษัทใช้มาตรฐานการบริหารความเสี่ยง เช่น ISO31000 COSO IRM FERMA BASEL",  # sub-item a
    "รายงานของบริษัทใช้มาตรฐาน GRI/IIRC/SASB",  # sub-item b (grouped)
    "GRI",
    "IIRC",
    "SASB",
    "มาตรฐานอื่น",
    "โปรดระบุชื่อมาตรฐาน",
]


def make_3year_multicat_subfields(indicator_code: str, categories: list[str]) -> list[dict]:
    """Pattern B: 3 year labels + N categories × 3 years."""
    fields = []
    n = 1
    for i in range(1, 4):
        fields.append({"subpart_num": n, "subpart_letter": f"year{i}", "subpart_text": f"ปีที่ {i}"})
        n += 1
    for cat in categories:
        for year in range(1, 4):
            fields.append({"subpart_num": n, "subpart_letter": f"{cat[:6]}_y{year}", "subpart_text": f"{cat} (ปีที่ {year})"})
            n += 1
    return fields


def make_3year_single_subfields() -> list[dict]:
    """Pattern A: 3 year labels + 3 values = 6 (no coverage — not in PDF)."""
    fields = []
    for i in range(1, 4):
        fields.append({"subpart_num": i, "subpart_letter": f"year{i}", "subpart_text": f"ปีที่ {i}"})
    for i in range(1, 4):
        fields.append({"subpart_num": i + 3, "subpart_letter": f"val{i}", "subpart_text": f"ค่า ปีที่ {i}"})
    return fields


def make_checkbox_subfields(items: list[str]) -> list[dict]:
    """Pattern D: explicit list items from PDF."""
    return [{"subpart_num": i + 1, "subpart_letter": chr(ord("a") + i), "subpart_text": item}
            for i, item in enumerate(items)]


def build_entries(ind_code: str, base_meta: dict, subfields: list[dict]) -> dict[str, dict]:
    result = {}
    for sf in subfields:
        code = f"{ind_code}_{sf['subpart_num']}"
        result[code] = {
            "indicator_code": ind_code,
            "subpart_code": code,
            **sf,
            **base_meta,
        }
    return result


def expand(data: dict) -> tuple[dict, dict[str, tuple[int, int]]]:
    """Return updated data dict and summary of changes {indicator: (old, new)}."""
    changes: dict[str, tuple[int, int]] = {}

    def replace(ind_code: str, base_meta: dict, subfields: list[dict]) -> None:
        old_count = sum(1 for k in data if k.startswith(f"{ind_code}_"))
        for k in list(data.keys()):
            if k.startswith(f"{ind_code}_"):
                del data[k]
        new_entries = build_entries(ind_code, base_meta, subfields)
        data.update(new_entries)
        changes[ind_code] = (old_count, len(new_entries))

    # EWT30
    replace("EWT30", {
        "indicator_name": "การระบายน้ำทั้งหมดเป็นระยะเวลา 3 ปี แบ่งตามจุดหมายปลายทาง",
        "theme_code": "EWT", "theme_name": "Water Security",
        "data_type": "quantitative", "exposure_level": "High",
        "is_core": True, "type": "core", "marker": "", "subsectors": [],
    }, make_3year_multicat_subfields("EWT30", EWT30_DESTINATIONS))

    # EWT31
    replace("EWT31", {
        "indicator_name": "การดึงน้ำทั้งหมดเป็นระยะเวลา 3 ปี แบ่งตามแหล่งที่มา",
        "theme_code": "EWT", "theme_name": "Water Security",
        "data_type": "quantitative", "exposure_level": "High",
        "is_core": True, "type": "core", "marker": "", "subsectors": [],
    }, make_3year_multicat_subfields("EWT31", EWT31_SOURCES))

    # EPR 3-year indicators
    for ind_code, (ind_name, theme_name, theme_code) in EPR_3YEAR_INDICATORS.items():
        replace(ind_code, {
            "indicator_name": ind_name,
            "theme_code": theme_code, "theme_name": theme_name,
            "data_type": "quantitative", "exposure_level": "High",
            "is_core": True, "type": "core", "marker": "", "subsectors": [],
        }, make_3year_single_subfields())

    # SLS03
    replace("SLS03", {
        "indicator_name": "การไม่เลือกปฏิบัติ",
        "theme_code": "SLS", "theme_name": "Labour Standards",
        "data_type": "qualitative", "exposure_level": "High",
        "is_core": True, "type": "core", "marker": "", "subsectors": [],
    }, make_checkbox_subfields(SLS03_ITEMS))

    # GRM04
    replace("GRM04", {
        "indicator_name": "การอ้างอิงมาตรฐานต่าง ๆ เพื่อสะท้อนความเป็นระบบในการบริหารความเสี่ยง",
        "theme_code": "GRM", "theme_name": "Risk Management",
        "data_type": "qualitative", "exposure_level": "High",
        "is_core": True, "type": "core", "marker": "", "subsectors": [],
    }, make_checkbox_subfields(GRM04_ITEMS))

    # GRM05 — PDF p.65: a/b explicit = 2 sub-fields
    replace("GRM05", {
        "indicator_name": "คณะกรรมการบริษัทที่มีหน้าที่ดูแล (oversight) เรื่องต่อไปนี้เป็นกรณีเฉพาะ",
        "theme_code": "GRM", "theme_name": "Risk Management",
        "data_type": "qualitative", "exposure_level": "High",
        "is_core": True, "type": "core", "marker": "", "subsectors": [],
    }, make_checkbox_subfields(GRM05_ITEMS))

    # EPR27 — Pattern C: year + monetary value = 2 (not 3-year)
    replace("EPR27", {
        "indicator_name": "ต้นทุนรวมจากค่าปรับและบทลงโทษด้านสิ่งแวดล้อมในปีงบประมาณ",
        "theme_code": "EPR", "theme_name": "Pollution & Resources",
        "data_type": "quantitative", "exposure_level": "High",
        "is_core": True, "type": "core", "marker": "", "subsectors": [],
    }, make_checkbox_subfields(EPR27_ITEMS))

    # SHS 3-year indicators
    for ind_code, (ind_name, theme_name, theme_code) in SHS_3YEAR_INDICATORS.items():
        replace(ind_code, {
            "indicator_name": ind_name,
            "theme_code": theme_code, "theme_name": theme_name,
            "data_type": "quantitative", "exposure_level": "High",
            "is_core": True, "type": "core", "marker": "", "subsectors": [],
        }, make_3year_single_subfields())

    # SLS16
    replace("SLS16", {
        "indicator_name": "การปฏิบัติด้านความหลากหลายและการไม่เลือกปฏิบัติ",
        "theme_code": "SLS", "theme_name": "Labour Standards",
        "data_type": "qualitative", "exposure_level": "High",
        "is_core": True, "type": "core", "marker": "", "subsectors": [],
    }, make_checkbox_subfields(SLS16_ITEMS))

    # EWT32/33 facility-level 3-year
    for ind_code, (ind_name, theme_name, theme_code) in EWT_3YEAR_FACILITY.items():
        replace(ind_code, {
            "indicator_name": ind_name,
            "theme_code": theme_code, "theme_name": theme_name,
            "data_type": "quantitative", "exposure_level": "High",
            "is_core": True, "type": "core", "marker": "", "subsectors": [],
        }, make_3year_single_subfields())

    # EWT34/35 — a/b targets only (Base Year/Target Year/Percentage = CDD-only)
    replace("EWT34", {
        "indicator_name": "เป้าหมายในการลดการใช้น้ำ/การดึงน้ำในระดับบริษัท",
        "theme_code": "EWT", "theme_name": "Water Security",
        "data_type": "qualitative", "exposure_level": "High",
        "is_core": True, "type": "core", "marker": "", "subsectors": [],
    }, make_checkbox_subfields(EWT34_ITEMS))

    replace("EWT35", {
        "indicator_name": "เป้าหมายในการลดการใช้น้ำ/การดึงน้ำที่ได้รับผลกระทบจากความเครียดด้านน้ำ",
        "theme_code": "EWT", "theme_name": "Water Security",
        "data_type": "qualitative", "exposure_level": "High",
        "is_core": True, "type": "core", "marker": "", "subsectors": [],
    }, make_checkbox_subfields(EWT35_ITEMS))

    # EPR28 — PDF p.13: % sites + name of system → 2 derivable (Year = CDD-only)
    replace("EPR28", {
        "indicator_name": "สัดส่วน (%) ของไซต์งานที่มีระบบการจัดการสิ่งแวดล้อมที่ได้รับการยอมรับ",
        "theme_code": "EPR", "theme_name": "Pollution & Resources",
        "data_type": "quantitative", "exposure_level": "High",
        "is_core": True, "type": "core", "marker": "", "subsectors": [],
    }, make_checkbox_subfields(EPR28_ITEMS))

    return data, changes


def main() -> None:
    data = json.loads(SUBPARTS_PATH.read_text())
    before_total = len(data)

    data, changes = expand(data)
    after_total = len(data)

    print("=== Performance Sub-field Expansion ===\n")
    for ind_code, (old, new) in sorted(changes.items()):
        delta = new - old
        print(f"  {ind_code}: {old} → {new}  ({delta:+d})")

    print(f"\nTotal entries: {before_total} → {after_total}  ({after_total - before_total:+d})")

    if DRY_RUN:
        print("\n[DRY RUN — no file written]")
        return

    SUBPARTS_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2))
    print(f"\n✅ Written to {SUBPARTS_PATH}")


if __name__ == "__main__":
    main()
