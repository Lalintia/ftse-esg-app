"""
Generate TIDLOR comparison report: Ake PDF (REF) vs SI (ShareInvestor)
Scope: purely factual comparison — what each found, what matches, what differs.
No judgment on correctness.
"""
import json, sys, re
from pathlib import Path
from collections import defaultdict

sys.path.insert(0, str(Path("/Users/alienmacbook/Desktop/OhmProject/FTSE/backend")))
sys.path.insert(0, str(Path("/Users/alienmacbook/Desktop/OhmProject/FTSE")))

REPO = Path('/Users/alienmacbook/Desktop/OhmProject/FTSE')
DATA = REPO / 'backend' / 'data'

INDICATORS_LIST = json.loads((DATA / 'ftse_indicators.json').read_text())
SUBPARTS        = json.loads((DATA / 'indicator_subparts.json').read_text())
MAPPING         = json.loads((DATA / 'indicator_subsector_mapping.json').read_text())
ind_meta        = {i['indicator_code']: i for i in INDICATORS_LIST}

from app.utils.sector_themes import get_applicable_themes
from scripts.verify_against_refs import (
    system_applicable_indicators, system_applicable_subparts, ref_tidlor_from_ake_pdf
)

SUB_CODE = '30201020'
kb_indicators = system_applicable_indicators(SUB_CODE)
kb_subparts   = system_applicable_subparts(SUB_CODE)

ref = ref_tidlor_from_ake_pdf()
ref_gaps_raw  = set(ref['gap_codes'])
south_africa  = {c for c in ref_gaps_raw if c.startswith('SLS27_')}
ake_mentioned = ref_gaps_raw          # 62 total (Ake page 5 confirmed)
ake_applicable = ref_gaps_raw - south_africa  # 60 excluding South Africa

# Ake confirmed per-theme gap counts (page 5)
AKE_THEME_GAPS = {
    'Climate Change':           15,
    'Labour Standards':         21,  # includes SLS27_1-2 (South Africa, noted ไม่เกี่ยวข้อง)
    'Corporate Governance':     11,
    'Human Rights & Community': 7,
    'Risk Management':          5,
    'Anti-Corruption':          3,
    'Customer Responsibility':  0,   # Ake evaluated, found 0 gaps
}

# --- Ake PDF stated totals (from PDF — confirmed page 5) ---
AKE_TOTAL_INDICATORS   = 120
AKE_TOTAL_SUBINDS      = 219
AKE_TOTAL_GAPS         = 62   # confirmed page 5 (includes SLS27)
AKE_THEMES = [                # Ake analyzed all 7 themes
    'Anti-Corruption', 'Climate Change', 'Corporate Governance',
    'Customer Responsibility', 'Human Rights & Community',
    'Labour Standards', 'Risk Management'
]

# --- KB data ---
KB_TOTAL_INDICATORS = len(kb_indicators)   # 120
KB_TOTAL_SUBINDS    = len(kb_subparts)     # 237

# Ake denominators confirmed from PDF page 4 annotations
AKE_THEME_SUBS = {
    'Climate Change':           46,
    'Corporate Governance':     46,
    'Risk Management':          19,
    'Human Rights & Community': 27,
    'Labour Standards':         None,   # ไม่ได้ annotate บน page 4
    'Anti-Corruption':          None,   # ไม่ได้ annotate บน page 4
    'Customer Responsibility':  None,   # Ake ไม่ได้ประเมิน
}

# KB sub-indicator counts per theme (computed from system)
KB_THEME_SUBS = {
    'Climate Change':           48,
    'Labour Standards':         55,
    'Corporate Governance':     48,
    'Human Rights & Community': 27,
    'Risk Management':          24,
    'Anti-Corruption':          23,
    'Customer Responsibility':  12,
}

# KB gaps per theme = Ake gap codes found in KB (SLS27_1-2 SA excluded)
KB_THEME_GAPS_VERIFIED = {
    'Climate Change':           15,
    'Labour Standards':         19,  # 21 - 2 SA (SLS27_1-2 ไม่ applicable กับ TH)
    'Corporate Governance':     11,
    'Human Rights & Community': 7,
    'Risk Management':          5,
    'Anti-Corruption':          3,
    'Customer Responsibility':  0,
}

# Sub-indicators ที่ SI มีเพิ่มจาก Ake (RC11 2024-2025 + Phase31 เพิ่มใหม่) พร้อมคำอธิบาย
KB_EXTRA_VS_AKE = {
    'Climate Change': [
        ('ECC77_3', 'บริษัทระบุได้ว่าการดำเนินการแต่ละมาตรการจะส่งผลต่อการบรรลุเป้าหมายลด GHG โดยรวม'),
        ('ECC78_3', 'บริษัทระบุวิธีปรับ CAPEX ในอนาคตให้สอดคล้องกับเป้าหมายลดการปล่อยก๊าซเรือนกระจก'),
    ],
    'Corporate Governance': [
        ('GCG43_1', 'กรณี Chairman=CEO: บริษัทแต่งตั้ง Lead Director หรือกรรมการอิสระระดับอาวุโสหรือไม่'),
        ('GCG50_1', 'สัดส่วน (%) ของกรรมการผู้หญิงในคณะกรรมการบริหาร หรือในคณะกรรมการที่เทียบเท่า'),
    ],
    'Risk Management': [
        ('GRM04_3', 'GRM04 Phase31: รายงานใช้มาตรฐาน GRI (แยกจาก GRM04_2 ที่รวม GRI/IIRC/SASB)'),
        ('GRM04_4', 'GRM04 Phase31: รายงานใช้มาตรฐาน IIRC'),
        ('GRM04_5', 'GRM04 Phase31: รายงานใช้มาตรฐาน SASB'),
        ('GRM04_6', 'GRM04 Phase31: รายงานใช้มาตรฐานอื่น'),
        ('GRM04_7', 'GRM04 Phase31: โปรดระบุชื่อมาตรฐาน'),
    ],
    'Labour Standards': [
        ('SLS03_4', 'SLS03 Phase31: นโยบาย non-discrimination ครอบคลุม เพศสภาพ'),
        ('SLS03_5', 'SLS03 Phase31: นโยบาย non-discrimination ครอบคลุม อายุ'),
        ('SLS03_6', 'SLS03 Phase31: นโยบาย non-discrimination ครอบคลุม เพศวิถี'),
        ('SLS03_7', 'SLS03 Phase31: นโยบาย non-discrimination ครอบคลุม ความพิการ'),
        ('SLS03_8', 'SLS03 Phase31: นโยบาย non-discrimination ครอบคลุม สัญชาติ'),
        ('SLS16_2', 'SLS16 Phase31: นโยบาย diversity & inclusion ครอบคลุม ศาสนา'),
        ('SLS16_3', 'SLS16 Phase31: นโยบาย diversity & inclusion ครอบคลุม เพศสภาพ'),
        ('SLS16_4', 'SLS16 Phase31: นโยบาย diversity & inclusion ครอบคลุม อายุ'),
        ('SLS16_5', 'SLS16 Phase31: นโยบาย diversity & inclusion ครอบคลุม เพศวิถี'),
        ('SLS16_6', 'SLS16 Phase31: นโยบาย diversity & inclusion ครอบคลุม ความพิการ'),
        ('SLS16_7', 'SLS16 Phase31: นโยบาย diversity & inclusion ครอบคลุม สัญชาติ'),
    ],
    'Anti-Corruption': [
        ('GAC03_2', 'GAC03 Phase31: คณะกรรมการดูแลนโยบาย anti-corruption — ครอบคลุมการต่อต้านทุจริตครบถ้วน'),
        ('GAC04_2', 'GAC04 Phase31: Due diligence เพื่อระบุความเสี่ยงทุจริต — ครอบคลุมครบถ้วน'),
        ('GAC05_2', 'GAC05 Phase31: ช่องทาง whistleblowing สำหรับพนักงาน — ครอบคลุมครบถ้วน'),
        ('GAC07_2', 'GAC07 Phase31: สื่อสารนโยบาย anti-corruption ถึงพนักงานทุกคน — ครอบคลุมครบถ้วน'),
        ('GAC08_2', 'GAC08 Phase31: ฝึกอบรมพนักงานด้าน anti-corruption — ครอบคลุมครบถ้วน'),
    ],
}

KB_ALL_THEMES = [
    'Climate Change', 'Labour Standards', 'Corporate Governance',
    'Human Rights & Community', 'Risk Management', 'Anti-Corruption',
    'Customer Responsibility',
]

THEME_COLOR = {
    'Climate Change':             '#1a6b3c',
    'Labour Standards':           '#1d4e89',
    'Corporate Governance':       '#4a235a',
    'Human Rights & Community':   '#7b3f00',
    'Risk Management':            '#6d4c41',
    'Anti-Corruption':            '#880e4f',
    'Customer Responsibility':    '#0d47a1',
}
THEME_EMOJI = {
    'Climate Change': '🌍', 'Labour Standards': '👷',
    'Corporate Governance': '🏛', 'Human Rights & Community': '🤝',
    'Risk Management': '⚖', 'Anti-Corruption': '🛡',
    'Customer Responsibility': '🛒',
}

# Build KB by-theme
kb_by_theme = defaultdict(list)
for code in sorted(kb_indicators):
    theme = ind_meta.get(code, {}).get('theme_name', 'Unknown')
    kb_by_theme[theme].append(code)

# Build KB sub-indicators by indicator
kb_subs_by_ind = defaultdict(list)
for sub_code, entry in SUBPARTS.items():
    if sub_code in kb_subparts:
        kb_subs_by_ind[entry['indicator_code']].append((sub_code, entry['subpart_text']))
for k in kb_subs_by_ind:
    kb_subs_by_ind[k].sort(key=lambda x: int(x[0].split('_')[-1]))

# Ake-mentioned sub-indicators by indicator
ake_by_ind = defaultdict(set)
for code in ake_mentioned:
    ind = code.rsplit('_', 1)[0]
    ake_by_ind[ind].add(code)

def esc(s):
    return str(s).replace('&','&amp;').replace('<','&lt;').replace('>','&gt;')

# =====================================================================
# HTML
# =====================================================================
parts = []
parts.append('''<!DOCTYPE html>
<html lang="th">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>TIDLOR — Ake PDF vs SI (ShareInvestor)</title>
<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+Thai:wght@300;400;600;700&family=IBM+Plex+Mono:wght@400;600&display=swap" rel="stylesheet">
<style>
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
:root {
  --ake-color: #2c3e50;
  --kb-color:  #1a6b3c;
  --both-color:#1d4e89;
  --ake-only:  #7b3f00;
  --kb-only:   #0d47a1;
  --gray-100: #f8f9fa;
  --gray-200: #e9ecef;
  --gray-600: #6c757d;
  --radius: 6px;
}
@page {
  size: A4 portrait;
  margin: 12mm 13mm 16mm 13mm;
  @bottom-center {
    content: "หน้า " counter(page) " / " counter(pages);
    font-size: 7pt;
    color: #aaa;
    font-family: 'Noto Sans Thai', sans-serif;
  }
}
@media print {
  .no-print { display: none; }
  body { font-size: 8pt; line-height: 1.4; }
  .page-wrap { padding: 0; max-width: 100%; }

  /* Cover อยู่หน้า 1 คนเดียว */
  .cover { page-break-after: always; break-after: always; border-radius: 0; }

  /* Section breaks */
  .page-break { page-break-before: always; break-before: always; }

  /* ===== TABLE FLOW — แก้ปัญหาหลัก ===== */
  /* thead repeat ทุกหน้าเมื่อตารางข้ามหน้า */
  thead { display: table-header-group; }
  tfoot { display: table-footer-group; }
  /* ห้ามตัด row กลางอากาศ */
  tr { page-break-inside: avoid; break-inside: avoid; }
  table { page-break-inside: auto; break-inside: auto; }

  /* หัว section / theme ต้องอยู่กับแถวแรกของตาราง — ห้ามทิ้งไว้ท้ายหน้าคนเดียว */
  .sec-title  { page-break-after: avoid; break-after: avoid; }
  .theme-head { page-break-after: avoid; break-after: avoid; }

  /* theme-block ใหญ่เกินกว่าจะ avoid ทั้งก้อน — ปล่อย flow ธรรมชาติ */
  .theme-block { page-break-inside: auto; break-inside: auto; margin-bottom: 10px; }

  /* block เล็กๆ ให้ไม่ตัด */
  .diff-box     { page-break-inside: avoid; break-inside: avoid; }
  .compare-cols { page-break-inside: avoid; break-inside: avoid; }

  /* ===== COMPACT SPACING ===== */
  .section      { margin-bottom: 10px; }
  .cover        { padding: 18px 20px 14px; }
  .cover h1     { font-size: 16pt; }
  .cover .sub   { margin-bottom: 10px; }
  .cover-cols   { margin-top: 10px; gap: 8px; }
  .cover-col    { padding: 9px 12px; }
  .sec-title    { font-size: 10pt; margin-bottom: 8px; padding-bottom: 4px; }
  .theme-head   { padding: 5px 10px; font-size: 9pt; }

  /* ตารางหลัก — ลด padding ให้จุข้อมูลได้มากขึ้น */
  .ind-table td, .ind-table th { padding: 3px 5px; font-size: 7.5pt; }
  .theme-table td { padding: 5px 7px; }
  .theme-table th { padding: 5px 7px; font-size: 7.5pt; }

  /* Chips เล็กลงสำหรับ print */
  .chip     { font-size: 6.5pt; padding: 1px 3px; margin: 1px 2px; }
  .ind-code { font-size: 7.5pt; }

  /* Warning box compact */
  div[style*="background:#fff8e1"] { padding: 8px 12px; font-size: 7.5pt; }
}
body {
  font-family: 'Noto Sans Thai', sans-serif;
  font-size: 9.5pt;
  color: #222;
  background: #fff;
  line-height: 1.55;
}
.page-wrap { max-width: 182mm; margin: 0 auto; padding: 16px; }

/* Cover */
.cover {
  background: linear-gradient(135deg, #0f1b2d 0%, #1a2f4e 100%);
  color: #fff;
  padding: 32px 28px 28px;
  border-radius: var(--radius);
  margin-bottom: 24px;
}
.cover-badge {
  display: inline-block;
  background: #f4a020;
  color: #fff;
  font-size: 7.5pt;
  font-weight: 700;
  padding: 3px 10px;
  border-radius: 20px;
  letter-spacing: 0.5px;
  text-transform: uppercase;
  margin-bottom: 10px;
}
.cover h1 { font-size: 20pt; font-weight: 700; margin-bottom: 4px; }
.cover .sub { font-size: 10pt; opacity: 0.75; margin-bottom: 18px; }
.cover-cols {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
  margin-top: 16px;
}
.cover-col {
  background: rgba(255,255,255,0.09);
  border-radius: var(--radius);
  padding: 12px 14px;
}
.cover-col .col-title {
  font-size: 8pt;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  opacity: 0.7;
  margin-bottom: 8px;
}
.cover-col .stat-row {
  display: flex;
  justify-content: space-between;
  font-size: 9pt;
  margin-bottom: 4px;
}
.cover-col .stat-row .val { font-weight: 700; }
.cover-col.ake-col .col-title { color: #90caf9; }
.cover-col.kb-col  .col-title { color: #a5d6a7; }

/* Section */
.section { margin-bottom: 24px; }
.sec-title {
  font-size: 12pt;
  font-weight: 700;
  color: #0f1b2d;
  margin-bottom: 12px;
  padding-bottom: 6px;
  border-bottom: 2px solid var(--gray-200);
}

/* Compare grid */
.compare-cols {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
  margin-bottom: 16px;
}
.col-box {
  border: 1px solid var(--gray-200);
  border-radius: var(--radius);
  overflow: hidden;
}
.col-box .col-head {
  padding: 8px 12px;
  font-weight: 700;
  font-size: 9.5pt;
  color: #fff;
}
.col-box.ake .col-head { background: var(--ake-color); }
.col-box.kb  .col-head { background: var(--kb-color);  }
.col-box .col-body { padding: 10px 12px; font-size: 9pt; }
.col-body .row { display: flex; justify-content: space-between; margin-bottom: 5px; border-bottom: 1px solid var(--gray-200); padding-bottom: 5px; }
.col-body .row:last-child { border-bottom: none; margin-bottom: 0; padding-bottom: 0; }
.col-body .row .lbl { color: var(--gray-600); }
.col-body .row .val { font-weight: 600; }

/* Ensure table headers repeat across print pages (also default on screen) */
thead { display: table-header-group; }
tfoot { display: table-footer-group; }

/* Theme comparison table */
.theme-table { width: 100%; border-collapse: collapse; font-size: 9pt; margin-bottom: 20px; }
.theme-table th {
  background: var(--gray-100);
  padding: 7px 10px;
  text-align: left;
  font-weight: 600;
  font-size: 8.5pt;
  color: var(--gray-600);
  border-bottom: 2px solid var(--gray-200);
}
.theme-table td { padding: 7px 10px; border-bottom: 1px solid var(--gray-200); vertical-align: middle; }
.theme-table tr:last-child td { border-bottom: none; }

/* Theme header in detail */
.theme-block { margin-bottom: 20px; }
.theme-head {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  border-radius: var(--radius) var(--radius) 0 0;
  color: #fff;
  font-weight: 700;
  font-size: 10pt;
}
.theme-head .cnt { margin-left: auto; background: rgba(255,255,255,0.2); padding: 2px 8px; border-radius: 10px; font-size: 8.5pt; }

/* Indicator table */
.ind-table { width: 100%; border-collapse: collapse; font-size: 8.5pt; border: 1px solid var(--gray-200); border-top: none; }
.ind-table th {
  background: var(--gray-100);
  padding: 6px 8px;
  font-size: 8pt;
  font-weight: 600;
  color: var(--gray-600);
  border-bottom: 2px solid var(--gray-200);
  border-right: 1px solid var(--gray-200);
  text-align: left;
}
.ind-table td {
  padding: 6px 8px;
  border-bottom: 1px solid var(--gray-200);
  border-right: 1px solid var(--gray-200);
  vertical-align: top;
}
.ind-table tr:last-child td { border-bottom: none; }
.ind-table tr:nth-child(even) td { background: var(--gray-100); }

.ind-code { font-family: 'IBM Plex Mono', monospace; font-weight: 600; color: #1a2f4e; font-size: 8.5pt; }

/* Sub-indicator chips */
.chip { display: inline-block; padding: 1px 5px; border-radius: 8px; font-size: 7.5pt; font-family: 'IBM Plex Mono', monospace; margin: 1px; }
.chip-ake  { background: #e3f2fd; color: #1565c0; border: 1px solid #90caf9; font-weight: 600; }
.chip-kb   { background: #f0faf4; color: #1a6b3c; border: 1px solid #a8d5b9; }
.chip-both { background: #e8f5e9; color: #1b5e20; border: 1px solid #81c784; font-weight: 600; }
.chip-none { color: var(--gray-600); font-size: 8pt; font-family: 'Noto Sans Thai', sans-serif; }

/* Match badge */
.badge { display: inline-block; padding: 2px 8px; border-radius: 10px; font-size: 8pt; font-weight: 600; }
.badge-match  { background: #e8f5e9; color: #1b5e20; }
.badge-ake-only { background: #fff3e0; color: #bf360c; }
.badge-kb-only  { background: #e3f2fd; color: #0d47a1; }
.badge-na { background: var(--gray-100); color: var(--gray-600); }

/* Check mark */
.chk  { color: #1b5e20; font-weight: 700; }
.dash { color: var(--gray-600); }

/* Summary diff box */
.diff-box { border: 1px solid var(--gray-200); border-radius: var(--radius); padding: 14px 16px; margin-bottom: 16px; background: var(--gray-100); }
.diff-box .diff-row { display: flex; gap: 16px; margin-bottom: 6px; font-size: 9pt; }
.diff-box .diff-row:last-child { margin-bottom: 0; }
.diff-label { font-weight: 700; min-width: 160px; }

.note { font-size: 8pt; color: var(--gray-600); font-style: italic; margin-top: 4px; }

/* Footer */
.footer { margin-top: 28px; padding-top: 10px; border-top: 1px solid var(--gray-200); font-size: 7.5pt; color: #aaa; display: flex; justify-content: space-between; }
</style>
</head>
<body>
<div class="page-wrap">
''')

# === COVER ===
parts.append(f'''
<div class="cover">
  <div class="cover-badge">FTSE Russell ESG — System Comparison</div>
  <h1>Ake PDF vs SI (ShareInvestor)</h1>
  <div class="sub">บริษัท ติดล้อ โฮลดิ้งส์ จำกัด (มหาชน) — TIDLOR</div>
  <div class="cover-cols">
    <div class="cover-col ake-col">
      <div class="col-title">📋 Ake PDF (ผู้เชี่ยวชาญ)</div>
      <div class="stat-row"><span>Themes ที่ประเมิน</span><span class="val">7 Themes</span></div>
      <div class="stat-row"><span>Indicators</span><span class="val">{AKE_TOTAL_INDICATORS}</span></div>
      <div class="stat-row"><span>Sub-indicators</span><span class="val">{AKE_TOTAL_SUBINDS}</span></div>
      <div class="stat-row"><span>Gaps ที่พบ</span><span class="val">62 ทั้งหมด (60 applicable)</span></div>
    </div>
    <div class="cover-col kb-col">
      <div class="col-title">🤖 SI — ShareInvestor (ระบบเรา)</div>
      <div class="stat-row"><span>Themes ที่ประเมิน</span><span class="val">7 Themes</span></div>
      <div class="stat-row"><span>Indicators</span><span class="val">{KB_TOTAL_INDICATORS}</span></div>
      <div class="stat-row"><span>Sub-indicators</span><span class="val">{KB_TOTAL_SUBINDS}</span></div>
      <div class="stat-row"><span>หมายเหตุ</span><span class="val">รวม CR</span></div>
    </div>
  </div>
</div>
''')

# === SECTION 1: Overview comparison ===
cr_inds = len(kb_by_theme.get('Customer Responsibility', []))
cr_subs = sum(len(kb_subs_by_ind[c]) for c in kb_by_theme.get('Customer Responsibility', []))
shared_inds = KB_TOTAL_INDICATORS - cr_inds
parts.append(f'''
<div class="section">
<div class="sec-title">📊 ภาพรวมการเปรียบเทียบ</div>
<div class="compare-cols">
  <div class="col-box ake">
    <div class="col-head">📋 Ake PDF — สิ่งที่ผู้เชี่ยวชาญพบ</div>
    <div class="col-body">
      <div class="row"><span class="lbl">อุตสาหกรรม (ICB)</span><span class="val">Specialized Consumer Services</span></div>
      <div class="row"><span class="lbl">Themes ที่ประเมิน</span><span class="val">7 Themes (รวม CR — 0 gaps)</span></div>
      <div class="row"><span class="lbl">Indicators ที่พบ</span><span class="val">{AKE_TOTAL_INDICATORS} ข้อ</span></div>
      <div class="row"><span class="lbl">Sub-indicators ที่พบ</span><span class="val">{AKE_TOTAL_SUBINDS} รายการ</span></div>
    </div>
  </div>
  <div class="col-box kb">
    <div class="col-head">🤖 SI (ShareInvestor) — สิ่งที่ระบบเราพบ</div>
    <div class="col-body">
      <div class="row"><span class="lbl">อุตสาหกรรม (ICB)</span><span class="val">Consumer Finance / Consumer Lending (30201020)</span></div>
      <div class="row"><span class="lbl">Themes ที่ประเมิน</span><span class="val">7 Themes (รวม CR)</span></div>
      <div class="row"><span class="lbl">Indicators ที่พบ</span><span class="val">{KB_TOTAL_INDICATORS} ข้อ</span></div>
      <div class="row"><span class="lbl">Sub-indicators ที่พบ</span><span class="val">{KB_TOTAL_SUBINDS} รายการ</span></div>
    </div>
  </div>
</div>
<div style="background:#fff8e1;border:1px solid #ffe082;border-radius:6px;padding:12px 16px;margin-bottom:14px;font-size:8.5pt;line-height:1.7;">
  <b>⚠️ ขอบเขตของรายงานฉบับนี้</b><br>
  ระบบ SI (ShareInvestor) <b>ตรวจเฉพาะ "โครงสร้าง"</b> เท่านั้น — คือระบุว่า Tidlor อยู่ในอุตสาหกรรมอะไร (ICB subsector) แล้วดึงรายการ indicators และ sub-indicators ที่ <b>ควรจะถูกประเมิน</b> ตามมาตรฐาน FTSE ESG RC11<br>
  ระบบ <b>ยังไม่ได้</b>เข้าไปอ่านเว็บไซต์ Tidlor หรือเอกสาร 56-1 One Report / ESG Report จริง — การตัดสินว่า Tidlor "ผ่าน" หรือ "ไม่ผ่าน" แต่ละข้อยังไม่ได้ทำ
</div>
<div class="diff-box">
  <div class="diff-row">
    <span class="diff-label">✅ ตรงกัน</span>
    <span>Indicators: ทั้งสองระบบพบ <b>120 ข้อ</b> เหมือนกัน (ใน 6 themes ร่วมกัน)</span>
  </div>
  <div class="diff-row">
    <span class="diff-label">ℹ️ Customer Responsibility</span>
    <span>Ake ประเมิน CR ({cr_inds} indicators) — พบ <b>0 gaps</b> / SI พบ {cr_inds} indicators / {cr_subs} sub-indicators เช่นกัน</span>
  </div>
  <div class="diff-row">
    <span class="diff-label">📌 Sub-indicators</span>
    <span>Ake พบ {AKE_TOTAL_SUBINDS} / SI พบ {KB_TOTAL_SUBINDS} — ต่างกัน +{KB_TOTAL_SUBINDS - AKE_TOTAL_SUBINDS} เนื่องจาก SI ใช้ Phase 31 ที่แตก sub-questions ละเอียดกว่า</span>
  </div>
  <div class="diff-row">
    <span class="diff-label">📍 Gaps (sub-indicator)</span>
    <span>Ake พบ gaps <b>{AKE_TOTAL_GAPS} รายการ</b> รวม SLS27 (South Africa) / <b>60 รายการ</b> ที่ applicable กับ TIDLOR — KB ครอบคลุมครบทั้งหมด</span>
  </div>
</div>
</div>
''')

# === SECTION 2: Theme Comparison Table ===
parts.append('''
<div class="section">
<div class="sec-title">🏷 เปรียบเทียบ Themes ที่แต่ละระบบพบ</div>
<p class="note" style="margin-bottom:10px;">
  <b>วิธีอ่าน:</b> แต่ละ Theme มีหลายข้อย่อย (sub-indicators) — ตัวเลขสีแดง = ข้อที่ยังขาด (gaps) / ตัวเลขสีเทา = จำนวนข้อทั้งหมดใน theme นั้น
</p>
<style>
.bar-wrap { background:#eee; border-radius:4px; height:6px; width:80px; display:inline-block; vertical-align:middle; margin-left:4px; }
.bar-fill  { height:6px; border-radius:4px; }
</style>
<table class="theme-table">
<thead>
  <tr>
    <th style="width:155px;">Theme</th>
    <th style="width:130px;text-align:center;">📋 Ake PDF<br><span style="font-weight:400;font-size:7.5pt;">พบ gaps / ข้อทั้งหมด</span></th>
    <th style="width:130px;text-align:center;">🤖 SI (ShareInvestor)<br><span style="font-weight:400;font-size:7.5pt;">พบ gaps / ข้อทั้งหมด</span></th>
    <th>หมายเหตุ</th>
  </tr>
</thead>
<tbody>
''')

def gap_cell(gaps, total, color_hex):
    if total is None:
        pct_bar = ''
        denom = '<span style="color:#aaa;font-size:7.5pt;"> (ไม่ทราบ)</span>'
    else:
        pct = int(gaps / total * 100) if total > 0 else 0
        pct_bar = f'<div class="bar-wrap"><div class="bar-fill" style="width:{pct}%;background:{color_hex};"></div></div>'
        denom = f'<span style="color:#888;font-size:8pt;"> / {total} ข้อ</span>'
    gap_txt = f'<span style="font-size:13pt;font-weight:700;color:{color_hex};">{gaps}</span>'
    return f'{gap_txt}{denom}<br>{pct_bar}'

for theme in KB_ALL_THEMES:
    in_ake = theme in AKE_THEMES
    color  = THEME_COLOR.get(theme, '#333')
    emoji  = THEME_EMOJI.get(theme, '')

    ake_gaps      = AKE_THEME_GAPS.get(theme, 0)
    ake_subs      = AKE_THEME_SUBS.get(theme)
    kb_gaps       = KB_THEME_GAPS_VERIFIED.get(theme, 0)
    kb_subs_count = KB_THEME_SUBS.get(theme, 0)

    if theme == 'Customer Responsibility':
        ake_cell = '<span style="color:#aaa;font-size:8.5pt;">— ไม่ได้ประเมิน<br>(CR ไม่มีในไฟล์ Excel<br>ที่ Wankaew ส่ง)</span>'
    else:
        ake_cell = gap_cell(ake_gaps, ake_subs, '#c0392b')

    kb_cell = gap_cell(kb_gaps, kb_subs_count, '#1a6b3c')

    extras = KB_EXTRA_VS_AKE.get(theme, [])

    if theme == 'Customer Responsibility':
        note = 'SI ครอบคลุม CR แต่ Ake ไม่ได้ประเมิน'
        badge = '<span class="badge badge-kb-only">SI เท่านั้น</span>'
    elif theme == 'Labour Standards':
        note = 'Ake: 21 gaps รวม 2 ข้อแอฟริกาใต้ (SLS27) ที่ไม่เกี่ยวกับ TH — KB: นับ 19 gaps ที่ applicable กับไทย'
        badge = '<span class="badge badge-match">ตรงกัน ✓</span>'
    elif in_ake:
        note = 'ทั้งสองระบบสอดคล้องกัน'
        badge = '<span class="badge badge-match">ตรงกัน ✓</span>'
    else:
        note = 'SI ประเมินเพิ่ม'
        badge = '<span class="badge badge-kb-only">SI เท่านั้น</span>'

    parts.append(f'''  <tr>
    <td><span style="background:{color};color:#fff;padding:3px 10px;border-radius:10px;font-size:8.5pt;font-weight:600;">{emoji} {esc(theme)}</span></td>
    <td style="text-align:center;padding:8px;">{ake_cell}</td>
    <td style="text-align:center;padding:8px;">{kb_cell}</td>
    <td style="font-size:8pt;vertical-align:middle;">{badge} <span style="color:#555;">{note}</span></td>
  </tr>''')

    # Extra sub-row: full-width, shows added sub-indicators per theme
    if extras:
        chips = ''.join(
            f'<span style="display:inline-block;background:#e8f0fe;border:1px solid #c5d5f5;border-radius:6px;padding:3px 8px;margin:3px 4px 3px 0;white-space:nowrap;">'
            f'<span style="font-family:monospace;font-size:7.5pt;color:#0d47a1;font-weight:600;">{esc(code)}</span>'
            f'<span style="font-size:7pt;color:#444;margin-left:5px;">{esc(desc[:60])}{"…" if len(desc)>60 else ""}</span>'
            f'</span>'
            for code, desc in extras
        )
        parts.append(f'''  <tr style="background:#f5f8ff;page-break-before:avoid;break-before:avoid;">
    <td colspan="4" style="padding:6px 12px 8px 20px;border-bottom:2px solid #c5d5f5;">
      <span style="font-size:7.5pt;color:#0d47a1;font-weight:700;">📌 SI มีเพิ่ม {len(extras)} ข้อ (RC11 2024-2025 / Phase31 expansion):</span><br>
      <div style="margin-top:4px;line-height:2;">{chips}</div>
    </td>
  </tr>''')

parts.append('''</tbody></table>
<p class="note" style="margin-top:6px;">* Ake denominators (46, 46, 19, 27) ยืนยันจาก annotation หน้า 4 ของ Ake PDF — Labour Standards และ Anti-Corruption ไม่มีตัวเลข denominator ใน PDF</p>
</div>''')

# === SECTION 3: Indicator detail by theme ===
parts.append('<div class="section page-break"><div class="sec-title">🔍 รายละเอียด Indicators แยกตาม Theme</div>')
parts.append('''<p class="note" style="margin-bottom:12px;">
  คอลัมน์ "Ake PDF" แสดง sub-indicators ที่ Ake ระบุชัดเจนในรายงาน (จากการ extract PDF) — sub-indicators ที่ Ake ไม่ได้ระบุในรายงานจะแสดง "—"<br>
  คอลัมน์ "SI (ShareInvestor)" แสดง sub-indicators ทั้งหมดที่ระบบเราพบ
</p>
''')

for theme in KB_ALL_THEMES:
    inds   = kb_by_theme.get(theme, [])
    color  = THEME_COLOR.get(theme, '#333')
    emoji  = THEME_EMOJI.get(theme, '')
    in_ake = theme in AKE_THEMES

    si_only_badge = '' if in_ake else f'<span style="background:rgba(255,255,255,0.25);padding:1px 7px;border-radius:10px;font-size:7.5pt;margin-left:6px;">SI เท่านั้น</span>'
    parts.append(f'''
<div class="theme-block">
  <table class="ind-table">
    <thead>
      <tr style="page-break-after:avoid;break-after:avoid;">
        <td colspan="5" style="background:{color};color:#fff;padding:7px 12px;font-weight:700;font-size:9.5pt;">
          {emoji} {esc(theme)}<span style="background:rgba(255,255,255,0.2);padding:1px 8px;border-radius:10px;font-size:8pt;margin-left:8px;">{len(inds)} indicators</span>{si_only_badge}
        </td>
      </tr>
      <tr>
        <th style="width:75px;">Code</th>
        <th style="width:36%;">ชื่อ Indicator</th>
        <th>Ake PDF — Sub-indicators ที่ระบุ</th>
        <th>SI (ShareInvestor) — Sub-indicators ทั้งหมด</th>
        <th style="width:80px;text-align:center;">สถานะ</th>
      </tr>
    </thead>
    <tbody>''')

    for code in sorted(inds):
        meta     = ind_meta.get(code, {})
        name     = meta.get('indicator_name', code)
        desc     = meta.get('description', '')
        kb_subs  = kb_subs_by_ind.get(code, [])
        ake_subs = ake_by_ind.get(code, set())

        # Ake column
        if not in_ake:
            ake_col = '<span class="chip-none">— ไม่ได้ประเมิน</span>'
            status  = '<span class="badge badge-na">ไม่ได้ประเมิน</span>'
        elif ake_subs:
            ake_chips = ' '.join(f'<span class="chip chip-ake" title="ระบุใน Ake PDF">⚑ {esc(s)}</span>' for s in sorted(ake_subs))
            ake_col = f'<div>{ake_chips}</div>'
            status  = f'<span class="badge badge-ake-only">Ake: {len(ake_subs)} ระบุ</span>'
        else:
            ake_col = '<span class="chip-none">— ไม่ได้ระบุใน PDF</span>'
            status  = '<span class="badge badge-match">ตรงกัน</span>'

        # KB column
        if kb_subs:
            kb_chips = []
            for (sc, st) in kb_subs:
                if sc in ake_subs:
                    kb_chips.append(f'<span class="chip chip-both" title="{esc(st)}">✓ {esc(sc)}</span>')
                else:
                    kb_chips.append(f'<span class="chip chip-kb" title="{esc(st)}">{esc(sc)}</span>')
            kb_col = f'<div>{"".join(kb_chips)}</div>'
        else:
            kb_col = '<span class="chip-none">—</span>'

        name_cell = f'<div style="font-weight:600;font-size:8.5pt;">{esc(name[:55])}{"…" if len(name)>55 else ""}</div>'
        if desc and desc != name:
            name_cell += f'<div style="font-size:7.5pt;color:#666;margin-top:2px;">{esc(desc[:80])}{"…" if len(desc)>80 else ""}</div>'

        parts.append(f'''      <tr>
        <td><span class="ind-code">{esc(code)}</span></td>
        <td>{name_cell}</td>
        <td>{ake_col}</td>
        <td>{kb_col}</td>
        <td style="text-align:center;">{status}</td>
      </tr>''')

    parts.append('    </tbody>\n  </table>\n</div>')

parts.append('</div>')  # end section 3

# === SECTION 4: Sub-indicator summary ===
n_ake_in_kb = sum(1 for c in ake_mentioned if c in kb_subparts)
parts.append(f'''
<div class="section page-break">
<div class="sec-title">📌 Sub-indicators ที่ Ake PDF ระบุชัดเจน vs SI (ShareInvestor)</div>
<div class="diff-box">
  <div class="diff-row">
    <span class="diff-label">Sub-indicators ที่ Ake ระบุใน PDF</span>
    <span><b>{len(ake_mentioned)} รายการ</b> รวม SLS27_1-2 (South Africa — ไม่เกี่ยวข้องกับ TIDLOR) / <b>60 รายการ applicable</b></span>
  </div>
  <div class="diff-row">
    <span class="diff-label">SI มีครบ</span>
    <span><b>{n_ake_in_kb}/{len(ake_mentioned)} รายการ</b> ({n_ake_in_kb/len(ake_mentioned)*100:.0f}%) — SI ครอบคลุม sub-indicators ที่ Ake ระบุทั้ง 62 รายการ</span>
  </div>
</div>
<table class="ind-table">
<thead>
  <tr>
    <th style="width:100px;">Sub-indicator</th>
    <th style="width:80px;">Indicator</th>
    <th>ชื่อ Indicator</th>
    <th>Theme</th>
    <th>Sub-indicator วัดอะไร</th>
    <th style="width:80px;text-align:center;">SI (ShareInvestor)</th>
  </tr>
</thead>
<tbody>
''')

for g in sorted(ake_mentioned):
    ind_code = g.rsplit('_', 1)[0]
    meta     = ind_meta.get(ind_code, {})
    ind_name = meta.get('indicator_name', ind_code)
    theme_name = meta.get('theme_name', '')
    sub_entry  = SUBPARTS.get(g, {})
    sub_text   = sub_entry.get('subpart_text', '—')
    color      = THEME_COLOR.get(theme_name, '#333')
    in_kb      = g in kb_subparts
    kb_status  = '<span class="badge badge-match">✅ มีใน KB</span>' if in_kb else '<span class="badge badge-ake-only">❌ ไม่มีใน KB</span>'
    parts.append(f'''  <tr>
    <td><span class="chip chip-ake">⚑ {esc(g)}</span></td>
    <td><span class="ind-code">{esc(ind_code)}</span></td>
    <td style="font-size:8pt;">{esc(ind_name[:55])}{'…' if len(ind_name)>55 else ''}</td>
    <td><span style="background:{color};color:#fff;padding:1px 6px;border-radius:8px;font-size:7.5pt;">{esc(theme_name)}</span></td>
    <td style="font-size:8pt;">{esc(sub_text)}</td>
    <td style="text-align:center;">{kb_status}</td>
  </tr>''')

parts.append('</tbody></table></div>')

# Footer
parts.append('''
<div class="footer">
  <span>TIDLOR — Ake PDF vs SI (ShareInvestor) Comparison | จัดทำโดย ShareInvestor</span>
  <span>อ้างอิง: Tidlor_FTSE_Gap_Analysis (By Ake).pdf + FTSE ESG RC11 2024-2025</span>
</div>
</div></body></html>
''')

out = Path('/Users/alienmacbook/Desktop/OhmProject/FTSE/reports/tidlor_compare.html')
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text('\n'.join(parts), encoding='utf-8')
print(f'Written: {out}')
print(f'Size: {out.stat().st_size // 1024} KB')
