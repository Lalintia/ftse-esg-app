'use client';

import { useState } from 'react';
import Link from 'next/link';
import { ArrowLeft } from 'lucide-react';

type Lang = 'th' | 'en';

const t = {
  hero: {
    th: 'AI-powered ESG analysis tool ที่วิเคราะห์เว็บไซต์บริษัทตามมาตรฐาน FTSE Russell',
    en: 'AI-powered ESG analysis tool that evaluates company websites against FTSE Russell sustainability standards',
  },
  badge: {
    th: 'Internal Sales Tool \u2022 Version 2.0 \u2022 March 2026',
    en: 'Internal Sales Tool \u2022 Version 2.0 \u2022 March 2026',
  },
  overview: {
    title: { th: 'Project Overview', en: 'Project Overview' },
    what: {
      th: 'เครื่องมือสำหรับ<strong>ทีม Sale</strong> ใช้วิเคราะห์เว็บไซต์ของลูกค้า เพื่อดูว่าบริษัทมีข้อมูล ESG (สิ่งแวดล้อม, สังคม, ธรรมาภิบาล) ครบถ้วนแค่ไหน ตามมาตรฐาน FTSE Russell',
      en: 'A tool for the <strong>Sales team</strong> to analyze client websites and assess how well a company discloses ESG (Environmental, Social, Governance) data against FTSE Russell standards.',
    },
    how: {
      th: 'Sale ใส่ URL เว็บไซต์ลูกค้า \u2192 ระบบวิเคราะห์อัตโนมัติ \u2192 ได้คะแนน ESG พร้อมจุดที่ต้องปรับปรุง \u2192 Sale นำไปเสนอลูกค้า',
      en: 'Sales enters client URL \u2192 system analyzes automatically \u2192 ESG score + improvement areas \u2192 Sales presents to client',
    },
    value: {
      th: 'ช่วย Sale pitch ลูกค้าว่า <strong>\u201Cเว็บไซต์คุณขาดข้อมูล ESG ตรงนี้ เราช่วยทำได้\u201D</strong> เปลี่ยน ESG gap เป็นโอกาสขายบริการ',
      en: 'Helps Sales pitch clients: <strong>\u201CYour website is missing ESG data here \u2014 we can help\u201D</strong> turning ESG gaps into service opportunities',
    },
  },
  flow: {
    title: { th: 'User Flow \u2014 ขั้นตอนการใช้งาน', en: 'User Flow \u2014 How users interact' },
    desc: { th: 'จากมุม Sale team', en: 'From the Sales team perspective' },
    steps: [
      {
        title: { th: '1. กรอก URL + เลือก Industry', en: '1. Enter URL + Select Industry' },
        body: {
          th: 'Sale ใส่ URL เว็บไซต์หลักของลูกค้าเพียง URL เดียว \u2014 ระบบจะค้นหาเว็บที่เกี่ยวข้องเอง เช่น subdomain นักลงทุนสัมพันธ์, ความยั่งยืน, Corporate โดยอัตโนมัติ ไม่ต้องใส่ทีละเว็บ',
          en: 'Sales enters just one main URL \u2014 the system automatically discovers related subdomains (IR, Sustainability, Corporate) without needing to enter each one separately.',
        },
        bodyB: {
          th: '<strong>Industry:</strong> ถ้ารู้หมวดธุรกิจก็เลือกได้เลย ถ้าไม่รู้ก็เลือก <strong>Auto-detect</strong> แล้ว AI จะตรวจจากเนื้อหาเว็บให้',
          en: '<strong>Industry:</strong> Select if known, or choose <strong>Auto-detect</strong> and AI will determine it from the website content.',
        },
        tech: 'esg.ohmai.me',
        active: true,
      },
      {
        title: { th: '2. ระบบ Crawl เว็บไซต์', en: '2. System Crawls Website' },
        body: {
          th: 'AI เข้าไปอ่านเนื้อหาทั้งเว็บไซต์ ทุกหน้าที่เกี่ยวข้องกับ ESG รวมถึง subdomain และดาวน์โหลด PDF (Annual Report, Sustainability Report) อัตโนมัติ',
          en: 'AI reads the entire website \u2014 every ESG-relevant page including subdomains, and automatically downloads PDFs (Annual Report, Sustainability Report).',
        },
        tech: 'Playwright + pdfplumber',
      },
      {
        title: { th: '3. AI วิเคราะห์ ESG Indicators', en: '3. AI Analyzes ESG Indicators' },
        body: {
          th: 'AI วิเคราะห์เนื้อหาเทียบกับ FTSE Russell ESG indicators ที่เกี่ยวข้องกับหมวดธุรกิจนั้นๆ ครอบคลุม themes ด้าน Environment, Social และ Governance',
          en: 'AI analyzes content against FTSE Russell ESG indicators relevant to the company\u2019s industry sector, covering Environmental, Social, and Governance themes.',
        },
        tech: 'OpenAI GPT-4.1-mini',
      },
      {
        title: { th: '4. คำนวณคะแนน ESG', en: '4. Calculate ESG Scores' },
        body: {
          th: 'คิดคะแนน 0-5 ต่อ theme ตาม FTSE methodology แล้วรวมเป็นคะแนน E, S, G และ Overall',
          en: 'Calculates scores 0-5 per theme using FTSE methodology, then aggregates into E, S, G and Overall scores.',
        },
        tech: 'Scoring Engine',
      },
      {
        title: { th: '5. แสดงผล Dashboard + Sitemap', en: '5. Display Dashboard + Sitemap' },
        body: {
          th: 'Sale เห็นคะแนนรวม, คะแนนรายธีม, รายละเอียด indicator ที่เจอ/ไม่เจอ, และคำแนะนำว่าควรสร้างหน้าเว็บอะไรเพิ่ม',
          en: 'Sales sees overall scores, per-theme breakdown, indicator details (found/missing), and recommendations for new web pages to improve scores.',
        },
        tech: 'Dashboard',
        active: true,
      },
    ],
  },
  accuracy: {
    title: { th: 'Accuracy & Calibration \u2014 ความแม่นยำและการปรับจูน', en: 'Accuracy & Calibration' },
    desc: {
      th: 'เทียบผลลัพธ์กับคะแนน FTSE Russell จริง แล้วปรับจูนจนใกล้เคียง',
      en: 'Compared with real FTSE Russell scores and calibrated for accuracy',
    },
    process: {
      th: 'เรานำผลลัพธ์จาก App มาเทียบกับ<strong>คะแนน FTSE Russell จริง</strong>ของบริษัทจดทะเบียน จากนั้น<strong>ปรับจูนระบบทีละขั้น</strong>จนคะแนนใกล้เคียงกับของจริงมากที่สุด เป้าหมายคือเก็บข้อมูลจริงจากบริษัทในทุกกลุ่มอุตสาหกรรม เพื่อให้ระบบ calibrate ได้ครอบคลุมและแม่นยำมากยิ่งขึ้น',
      en: 'We compare our App results against <strong>real FTSE Russell scores</strong> of listed companies, then <strong>fine-tune the system step by step</strong> until scores closely match reality. Our goal is to collect real data from companies across all industry sectors for comprehensive and increasingly accurate calibration.',
    },
    steps: [
      {
        title: 'Indicator Mapping',
        desc: {
          th: 'จับคู่ FTSE indicators ทั้ง 381 ตัว (196 Core, 176 Sector-specific, 6 Performance, 3 Geography \u2014 นับจากเอกสาร FTSE Russell โดยตรง) กับแต่ละหมวดอุตสาหกรรม เมื่อเว็บลูกค้าถูกระบุหมวดธุรกิจแล้ว ระบบจะวัดเฉพาะ indicators ที่เกี่ยวข้องกับหมวดนั้นจริงๆ ตรงตาม FTSE methodology',
          en: 'Maps all 381 FTSE indicators (196 Core, 176 Sector-specific, 6 Performance, 3 Geography \u2014 counted directly from FTSE Russell documents) to each industry subsector. Once the client\u2019s industry is identified, the system measures only the relevant indicators, following exact FTSE methodology.',
        },
      },
      {
        title: 'False Positive Reduction',
        desc: {
          th: 'วิเคราะห์ข้อมูลที่ AI \u201Cคิดว่าเจอ\u201D แต่จริงๆ ไม่ถูกต้อง เช่น บริษัทเอ่ยถึงนโยบาย แต่ไม่มีตัวเลขจริงรองรับ \u2014 แล้วเพิ่มกฎให้ AI แยกแยะได้แม่นขึ้น',
          en: 'Analyzes data that AI \u201Cthinks it found\u201D but is actually incorrect \u2014 e.g., a company mentions a policy but lacks actual numbers. Rules are added to help AI distinguish more accurately.',
        },
      },
      {
        title: 'Cross-Industry Calibration',
        desc: {
          th: 'ยิ่งมีผลลัพธ์จริงจากบริษัทหลากหลายอุตสาหกรรมมากขึ้น ระบบยิ่ง calibrate ได้แม่นขึ้น \u2014 เพราะแต่ละอุตสาหกรรมมี pattern การเปิดเผยข้อมูล ESG ต่างกัน',
          en: 'The more real results we collect from diverse industries, the more accurate calibration becomes \u2014 each industry has different ESG disclosure patterns.',
        },
      },
    ],
    benchmark: {
      th: 'Benchmark ล่าสุด: Indicator mapping ตรง <strong>142/142</strong> (100%) \u2014 คะแนนรวมห่างจากของจริงเพียง <strong>0.1 คะแนน</strong>',
      en: 'Latest benchmark: Indicator mapping matches <strong>142/142</strong> (100%) \u2014 overall score differs from real by only <strong>0.1 points</strong>',
    },
  },
  cost: {
    title: { th: 'Cost & Resources', en: 'Cost & Resources' },
    desc: { th: 'ค่าใช้จ่ายรายเดือนและต่อการใช้งาน', en: 'Monthly costs and per-analysis costs' },
    perRun: { th: 'ต่อการวิเคราะห์ 1 ครั้ง (5-7 นาที)', en: 'per analysis (5-7 minutes)' },
    fixed: { th: 'ค่าใช้จ่ายคงที่ / เดือน', en: 'Monthly Fixed Cost' },
    perAnalysis: { th: 'ค่าใช้จ่ายต่อ Analysis', en: 'Per Analysis Cost' },
    total: { th: 'รวม', en: 'Total' },
    time: { th: 'เวลา', en: 'Time' },
    perRunLabel: { th: 'ต่อครั้ง', en: 'Per run' },
  },
  pipeline: {
    title: { th: 'Analysis Pipeline \u2014 ระบบทำงานอย่างไร', en: 'Analysis Pipeline \u2014 How the system works' },
    desc: { th: '9 ขั้นตอนภายใน backend', en: '9 internal backend processing steps' },
    smartPdfTitle: 'Smart PDF Reading',
    smartPdf: {
      th: 'PDF รายงานประจำปีอาจมี 300+ หน้า แต่ระบบไม่อ่านทุกหน้า \u2014 สแกนสารบัญก่อน แล้วอ่านเฉพาะหน้าที่เกี่ยวข้องกับ ESG ทั้งภาษาไทยและอังกฤษ ประหยัดเวลาและ token',
      en: 'Annual reports can be 300+ pages, but the system doesn\u2019t read everything \u2014 it scans the table of contents first, then reads only ESG-relevant pages in both Thai and English, saving time and tokens.',
    },
    steps: [
      { th: 'ค้นหา Sitemap', en: 'Sitemap Scan', desc: { th: 'อ่านไฟล์ sitemap.xml ของเว็บไซต์ เพื่อค้นหาหน้าทั้งหมดที่เกี่ยวข้องกับ ESG', en: 'Reads the website\u2019s sitemap.xml to find all ESG-relevant pages' } },
      { th: 'อ่านเว็บ', en: 'Web Crawl', desc: { th: 'Crawl เนื้อหาจากหน้าเว็บที่คัดเลือกแล้ว รวมถึง subdomain ที่ค้นพบอัตโนมัติ', en: 'Crawls content from selected pages including auto-discovered subdomains' } },
      { th: 'ค้นหาและอ่าน PDF', en: 'PDF Discovery', desc: { th: 'ค้นหา PDF รายงานสำคัญ (Sustainability Report, Annual Report) แล้วอ่านเฉพาะหน้าที่เกี่ยวข้อง', en: 'Finds key PDFs (Sustainability Report, Annual Report) and reads only relevant pages' } },
      { th: 'ระบุหมวดธุรกิจ', en: 'Detect Industry', desc: { th: 'AI วิเคราะห์เนื้อหาเว็บเพื่อระบุหมวดอุตสาหกรรม (ICB subsector) โดยอัตโนมัติ', en: 'AI analyzes web content to automatically identify the ICB subsector' } },
      { th: 'กรอง Indicators', en: 'Filter Indicators', desc: { th: 'เลือกเฉพาะ FTSE indicators ที่เกี่ยวข้องกับหมวดธุรกิจนั้น จาก 381 ตัวทั้งหมด', en: 'Selects only FTSE indicators relevant to that industry from all 381' } },
      { th: 'วิเคราะห์จากเว็บ (Round 1)', en: 'Analyze Website (Round 1)', desc: { th: 'AI วิเคราะห์ indicators ทั้งหมดจากเนื้อหาเว็บไซต์ก่อน เป็นแหล่งข้อมูลหลัก', en: 'AI analyzes all indicators from website content first as the primary source' } },
      { th: 'เติมข้อมูลจาก PDF (Round 2)', en: 'Fill Gaps from PDF (Round 2)', desc: { th: 'Indicators ที่ยังไม่เจอจากเว็บ นำ PDF มาวิเคราะห์เพิ่มเพื่อหาข้อมูลเชิงปริมาณ', en: 'Indicators not found on web are supplemented with PDF data for quantitative info' } },
      { th: 'คำนวณคะแนน', en: 'Calculate Scores', desc: { th: 'รวมผลลัพธ์ทั้ง 2 รอบ แล้วคำนวณคะแนน 0-5 ต่อ theme ตาม FTSE methodology', en: 'Merges both rounds and calculates 0-5 scores per theme using FTSE methodology' } },
      { th: 'แนะนำ Sitemap', en: 'Recommend Sitemap', desc: { th: 'สร้างคำแนะนำว่าควรเพิ่มหน้าเว็บอะไรบ้าง เพื่อปรับปรุงคะแนน ESG', en: 'Generates recommendations for new web pages to improve ESG scores' } },
    ],
  },
  security: {
    title: { th: 'Security Measures', en: 'Security Measures' },
    desc: { th: 'มาตรการรักษาความปลอดภัยตามมาตรฐาน OWASP', en: 'Security measures following OWASP standards' },
  },
  dev: {
    title: { th: 'Development Process \u2014 สร้างแอปนี้ขึ้นมาอย่างไร', en: 'Development Process \u2014 How this app was built' },
    desc: {
      th: 'Vibe Coding \u2014 ใช้ AI เป็นตัวช่วยหลักในการเขียน code ทั้งหมด',
      en: 'Vibe Coding \u2014 AI as the primary code author',
    },
    vibeCoding: {
      th: 'วิธีการพัฒนาซอฟต์แวร์แบบใหม่ที่ใช้ AI coding agent เป็นผู้เขียน code \u2014 ผู้สร้างทำหน้าที่เป็น \u201Cผู้กำกับ\u201D คอยบอกว่าต้องการอะไร ตรวจสอบผลลัพธ์ และตัดสินใจ โดยไม่ต้องเขียน code เองทุกบรรทัด',
      en: 'A new software development approach using AI coding agents to write code \u2014 the creator acts as a \u201Cdirector\u201D, defining requirements, reviewing results, and making decisions without writing every line of code.',
    },
    skillsIntro: {
      th: 'Skills เสริมที่ช่วยให้ AI Agent เขียน code ได้ดีขึ้น แบ่งเป็น 4 กลุ่มตามหน้าที่ \u2014 Skills ที่ใช้จริงในโปรเจกต์นี้จะมี <strong class="text-orange-700">จุดสีส้ม</strong> กำกับ',
      en: 'Supplementary skills that help AI Agents write better code, organized into 4 groups by function \u2014 Skills actually used in this project are marked with an <strong class="text-orange-700">orange dot</strong>',
    },
    legendUsed: { th: 'ใช้แล้วในโปรเจกต์นี้', en: 'Used in this project' },
    legendReady: { th: 'ติดตั้งแล้ว พร้อมใช้งาน', en: 'Installed, ready to use' },
  },
};

const securityItems = [
  { severity: 'crit' as const, name: 'SSRF Protection', desc: { th: 'ป้องกันไม่ให้ผู้ใช้กรอก URL ที่ชี้ไปยัง IP ภายใน (127.x, 10.x, 172.16.x, 169.254.x) ซึ่งอาจเข้าถึง AWS metadata หรือระบบภายในได้', en: 'Blocks URLs pointing to private IPs (127.x, 10.x, 172.16.x, 169.254.x) to prevent access to AWS metadata or internal systems' } },
  { severity: 'high' as const, name: 'Rate Limiting', desc: { th: 'จำกัดจำนวน request \u2014 สร้าง analysis ได้ 5 ครั้ง/นาที, API ทั่วไป 30 ครั้ง/นาที ป้องกันการใช้งานเกินควรหรือ DDoS', en: 'Limits requests \u2014 5/min for analysis creation, 30/min for general API to prevent abuse or DDoS' } },
  { severity: 'high' as const, name: 'Non-root Docker', desc: { th: 'Container ทุกตัวรันเป็น user ปกติ (appuser:1001) ไม่ใช่ root \u2014 ลดความเสียหายหากมีช่องโหว่', en: 'All containers run as regular user (appuser:1001), not root \u2014 minimizes damage from vulnerabilities' } },
  { severity: 'high' as const, name: 'Input Validation', desc: { th: 'ตรวจสอบ URL ด้วย Pydantic, sanitize ข้อความก่อนส่ง AI (ลบ null bytes, control chars), จำกัด query สูงสุด 100 records', en: 'Validates URLs with Pydantic, sanitizes text before AI (removes null bytes, control chars), limits queries to 100 records' } },
  { severity: 'med' as const, name: 'Security Headers', desc: { th: 'X-Content-Type-Options (ป้องกัน MIME sniffing), X-Frame-Options DENY (ป้องกัน clickjacking), HSTS (บังคับ HTTPS 1 ปี), X-XSS-Protection', en: 'X-Content-Type-Options (prevent MIME sniffing), X-Frame-Options DENY (prevent clickjacking), HSTS (enforce HTTPS 1 year), X-XSS-Protection' } },
  { severity: 'med' as const, name: 'CORS Restricted', desc: { th: 'อนุญาตเฉพาะ esg.ohmai.me เท่านั้นที่เรียก API ได้ ป้องกันเว็บอื่นขโมยใช้ API \u2014 รับเฉพาะ GET, POST', en: 'Only esg.ohmai.me is allowed to call the API, preventing unauthorized use \u2014 GET, POST methods only' } },
];

const tools = [
  { name: 'Claude Code', desc: { th: 'AI coding agent ที่ทำงานใน VS Code terminal เขียน code, debug, deploy ให้ทั้งหมด', en: 'AI coding agent in VS Code terminal \u2014 writes code, debugs, and deploys' } },
  { name: 'Claude Opus 4.6', desc: { th: 'AI model ที่ขับเคลื่อน Claude Code มีความสามารถวิเคราะห์ code ระดับสูง', en: 'AI model powering Claude Code with advanced code analysis capabilities' } },
  { name: 'Playwright MCP', desc: { th: 'เชื่อมต่อ browser เข้ากับ AI Agent ให้ทดสอบเว็บอัตโนมัติระหว่างพัฒนา', en: 'Connects browser to AI Agent for automated web testing during development' } },
  { name: 'GitHub', desc: { th: 'ระบบจัดการ version ของ source code และ collaboration', en: 'Version control and source code collaboration' } },
  { name: 'AWS EC2', desc: { th: 'Cloud server สำหรับ deploy และรัน production ของทั้ง frontend และ backend', en: 'Cloud server for production deployment of frontend and backend' } },
  { name: 'Docker', desc: { th: 'บรรจุแอปทั้งหมดเป็น container เพื่อ deploy ได้ง่ายและเหมือนกันทุกเครื่อง', en: 'Packages the entire app into containers for easy and consistent deployment' } },
];

const skillGroups = [
  {
    label: { th: 'Design & UI \u2014 ออกแบบหน้าตา', en: 'Design & UI' },
    skills: [
      { name: 'shadcn/ui', used: true, desc: { th: 'ใช้ UI components สำเร็จรูปอย่างถูกวิธีตาม design system', en: 'Use pre-built UI components correctly per design system' } },
      { name: 'frontend-design', used: true, desc: { th: 'ออกแบบ UI/UX ตามหลัก accessibility และ responsive design', en: 'Design UI/UX with accessibility and responsive principles' } },
      { name: 'brand-guidelines', used: false, desc: { th: 'ควบคุมสี, ฟอนต์, โทนให้ตรงตามแบรนด์', en: 'Control colors, fonts, tone to match brand guidelines' } },
      { name: 'canvas-design', used: false, desc: { th: 'สร้างงานกราฟิก เช่น โปสเตอร์ ออกเป็น PNG/PDF', en: 'Create graphics like posters, output as PNG/PDF' } },
      { name: 'theme-factory', used: false, desc: { th: 'ธีมสำเร็จรูป 10 แบบ พร้อมคู่สีและฟอนต์ที่คัดมาแล้ว', en: '10 professional themes with curated color and font pairs' } },
    ],
  },
  {
    label: { th: 'Code Quality \u2014 เขียน code ให้ดี', en: 'Code Quality' },
    skills: [
      { name: 'next-best-practices', used: true, desc: { th: 'เขียน Next.js ตามมาตรฐาน Vercel \u2014 App Router, Server Components', en: 'Write Next.js per Vercel standards \u2014 App Router, Server Components' } },
      { name: 'react-best-practices', used: true, desc: { th: 'เขียน React components ที่ปลอดภัย มี performance ดี', en: 'Write safe, performant React components' } },
      { name: 'supabase-postgres', used: false, desc: { th: 'เขียน query, RLS, migration ตามแนวทางของ Supabase', en: 'Write queries, RLS, migrations per Supabase guidelines' } },
      { name: 'python-error-handling', used: false, desc: { th: 'จัดการ error, retry, logging ใน Python อย่างถูกต้อง', en: 'Handle errors, retries, logging in Python properly' } },
      { name: 'python-performance', used: false, desc: { th: 'ลด memory, ใช้ async/await, optimize algorithm', en: 'Reduce memory, use async/await, optimize algorithms' } },
    ],
  },
  {
    label: { th: 'Debug & Tools \u2014 หาบัคและเครื่องมือ', en: 'Debug & Tools' },
    skills: [
      { name: 'agent-browser', used: true, desc: { th: 'ควบคุม browser อัตโนมัติ \u2014 เปิดเว็บ, กรอกฟอร์ม, ตรวจผลลัพธ์', en: 'Automated browser control \u2014 navigate, fill forms, verify results' } },
      { name: 'pdf', used: true, desc: { th: 'อ่าน, สร้าง, แยก, รวมไฟล์ PDF \u2014 รวมถึง OCR สำหรับ PDF ที่เป็นรูป', en: 'Read, create, split, merge PDFs \u2014 including OCR for scanned PDFs' } },
      { name: 'systematic-debugging', used: false, desc: { th: 'วิเคราะห์ bug อย่างเป็นขั้นตอน หาสาเหตุที่แท้จริง ไม่ใช่แค่แก้อาการ', en: 'Analyze bugs systematically, find root causes instead of just symptoms' } },
    ],
  },
  {
    label: { th: 'Review Agents \u2014 ตรวจ code อัตโนมัติ', en: 'Review Agents' },
    skills: [
      { name: 'security-auditor', used: true, desc: { th: 'ตรวจช่องโหว่ SSRF, XSS, rate limiting, secrets, Docker security', en: 'Audit SSRF, XSS, rate limiting, secrets exposure, Docker security' } },
      { name: 'performance-reviewer', used: true, desc: { th: 'ตรวจ memory leaks, error handling, timeout, algorithm complexity', en: 'Check memory leaks, error handling, timeout, algorithm complexity' } },
      { name: 'react-ts-reviewer', used: true, desc: { th: 'ตรวจ accessibility, type safety, unused imports, re-render issues', en: 'Check accessibility, type safety, unused imports, re-render issues' } },
    ],
  },
];

const severityStyle = {
  crit: 'bg-red-100 text-red-800',
  high: 'bg-orange-100 text-orange-800',
  med: 'bg-yellow-100 text-yellow-800',
};

export default function AboutPage() {
  const [lang, setLang] = useState<Lang>('th');

  return (
    <div className="mx-auto max-w-[920px] px-6 py-8" style={{ wordBreak: 'keep-all', overflowWrap: 'break-word' }}>
      {/* Back */}
      <div className="mb-8">
        <Link href="/" className="inline-flex items-center gap-2 text-xs uppercase tracking-[0.1em] text-muted-foreground hover:text-foreground">
          <ArrowLeft className="h-3 w-3" />
          Back
        </Link>
      </div>

      {/* Lang toggle */}
      <button
        onClick={() => setLang(lang === 'th' ? 'en' : 'th')}
        className="fixed right-6 top-20 z-50 rounded-full border border-border bg-background/90 px-4 py-1.5 text-xs font-medium uppercase tracking-[0.1em] text-muted-foreground shadow-sm backdrop-blur-sm transition-colors hover:bg-foreground hover:text-background"
      >
        {lang === 'th' ? 'EN' : 'TH'}
      </button>

      {/* Hero */}
      <div className="mb-16 text-center">
        <h1 className="text-4xl font-bold tracking-[-0.04em] sm:text-5xl">FTSE ESG Analyzer</h1>
        <p className="mx-auto mt-4 max-w-xl text-[15px] text-muted-foreground">{t.hero[lang]}</p>
        <span className="mt-4 inline-block rounded-full border border-border px-5 py-1.5 text-[11px] uppercase tracking-[0.1em] text-muted-foreground">
          {t.badge[lang]}
        </span>
      </div>

      {/* 1. Overview */}
      <Section num={1} title={t.overview.title[lang]}>
        <div className="grid grid-cols-1 gap-3.5 sm:grid-cols-3">
          {(['what', 'how', 'value'] as const).map((key) => (
            <div key={key} className="rounded-[14px] border border-border bg-card p-6">
              <div className="mb-3 text-[11px] font-semibold uppercase tracking-[0.1em] text-orange-700">{key.toUpperCase()}</div>
              <p className="text-[15px] leading-[1.75] text-muted-foreground" dangerouslySetInnerHTML={{ __html: t.overview[key][lang] }} />
            </div>
          ))}
        </div>
      </Section>

      {/* 2. User Flow */}
      <Section num={2} title={t.flow.title[lang]} desc={t.flow.desc[lang]}>
        <div className="flex flex-col">
          {t.flow.steps.map((step, i) => (
            <div key={i}>
              {i > 0 && <div className="flex justify-center py-1"><div className="h-5 w-px bg-border" /></div>}
              <div className={`rounded-[14px] border-2 p-6 ${step.active ? 'border-orange-700/20 bg-orange-50/30' : 'border-border bg-card'}`}>
                <div className="mb-2 flex items-center gap-3">
                  <span className={`flex h-7 w-7 shrink-0 items-center justify-center rounded-full text-xs font-semibold ${step.active ? 'bg-orange-700 text-white' : 'bg-foreground text-background'}`}>{i + 1}</span>
                  <h4 className="text-[15px] font-semibold">{step.title[lang]}</h4>
                </div>
                <div className="ml-10 text-[14px] leading-[1.75] text-muted-foreground" dangerouslySetInnerHTML={{ __html: step.body[lang] }} />
                {step.bodyB && <div className="ml-10 mt-3 text-[14px] leading-[1.75] text-muted-foreground" dangerouslySetInnerHTML={{ __html: step.bodyB[lang] }} />}
                <span className="ml-10 mt-2 inline-block rounded border border-border bg-muted/50 px-2 py-0.5 text-[10px] text-muted-foreground">{step.tech}</span>
              </div>
            </div>
          ))}
        </div>
      </Section>

      {/* 3. Accuracy — dark full-width */}
      <div className="-mx-6 mb-[72px] bg-[#1a1a1a] px-6 py-[72px] text-[#fafaf8] sm:-mx-6">
        <div className="mx-auto max-w-[920px]">
          <span className="mb-3.5 flex h-7 w-7 items-center justify-center rounded-full bg-orange-700 text-xs font-semibold text-white">3</span>
          <h2 className="mb-1.5 text-[22px] font-bold tracking-[-0.02em]">{t.accuracy.title[lang]}</h2>
          <p className="mb-7 text-[14px] text-[#bbb]">{t.accuracy.desc[lang]}</p>

          <div className="mb-8 grid grid-cols-2 gap-4 sm:grid-cols-4">
            {[
              { label: 'ESG Overall', value: '3.4', target: '3.3' },
              { label: 'Environmental', value: '2.0', target: '2.3' },
              { label: 'Social', value: '4.3', target: '3.3' },
              { label: 'Governance', value: '4.0', target: '4.6' },
            ].map((s) => (
              <div key={s.label} className="rounded-[14px] border border-white/10 bg-white/[0.04] p-7 text-center">
                <div className="text-[42px] font-bold leading-none tracking-[-0.04em]">{s.value}</div>
                <div className="mt-1.5 text-[13px] text-[#bbb]">target <span className="font-semibold text-orange-700">{s.target}</span></div>
                <div className="mt-2.5 text-[10px] uppercase tracking-[0.1em] text-[#bbb]">{s.label}</div>
              </div>
            ))}
          </div>

          <div className="rounded-[14px] border border-white/10 bg-white/[0.03] p-7">
            <h4 className="mb-3.5 text-[16px] font-semibold">{lang === 'th' ? 'กระบวนการ Calibration' : 'Calibration Process'}</h4>
            <p className="mb-3 text-[14px] leading-[1.85] text-[#bbb]" dangerouslySetInnerHTML={{ __html: t.accuracy.process[lang] }} />

            <div className="mt-5 grid grid-cols-1 gap-3 sm:grid-cols-3">
              {t.accuracy.steps.map((step, i) => (
                <div key={i} className="rounded-[10px] border border-white/[0.08] bg-white/[0.02] p-[18px]">
                  <div className="mb-1.5 text-[10px] font-bold text-orange-700">Step {i + 1}</div>
                  <h5 className="mb-1.5 text-[13px] font-semibold text-[#fafaf8]">{step.title}</h5>
                  <p className="text-[12px] leading-[1.7] text-[#bbb]">{step.desc[lang]}</p>
                </div>
              ))}
            </div>

            <p className="mt-5 text-[14px] leading-[1.85] text-[#bbb]" dangerouslySetInnerHTML={{ __html: t.accuracy.benchmark[lang] }} />
          </div>
        </div>
      </div>

      {/* 4. Cost */}
      <Section num={4} title={t.cost.title[lang]} desc={t.cost.desc[lang]}>
        <div className="mb-7 text-center">
          <div className="text-[clamp(48px,8vw,64px)] font-bold leading-none tracking-[-0.04em]">~3.4 &#x0E3F;</div>
          <div className="mt-1.5 text-[14px] text-muted-foreground">{t.cost.perRun[lang]}</div>
        </div>
        <div className="grid grid-cols-1 gap-3.5 sm:grid-cols-2">
          <div className="rounded-[14px] border border-border bg-card p-6">
            <div className="mb-3.5 text-[11px] font-semibold uppercase tracking-[0.08em] text-muted-foreground">{t.cost.fixed[lang]}</div>
            <div className="flex justify-between py-1.5 text-[14px] text-muted-foreground"><span>AWS EC2 (shared)</span><span>~$30</span></div>
            <div className="flex justify-between py-1.5 text-[14px] text-muted-foreground"><span>Supabase PRO</span><span>~$25</span></div>
            <div className="mt-2 flex justify-between border-t border-border pt-2.5 text-[14px] font-semibold"><span>{t.cost.total[lang]}</span><span>~$55/mo (~1,925 &#x0E3F;)</span></div>
          </div>
          <div className="rounded-[14px] border border-border bg-card p-6">
            <div className="mb-3.5 text-[11px] font-semibold uppercase tracking-[0.08em] text-muted-foreground">{t.cost.perAnalysis[lang]}</div>
            <div className="flex justify-between py-1.5 text-[14px] text-muted-foreground"><span>OpenAI tokens</span><span>~$0.096</span></div>
            <div className="flex justify-between py-1.5 text-[14px] text-muted-foreground"><span>{t.cost.time[lang]}</span><span>5-7 {lang === 'th' ? 'นาที' : 'min'}</span></div>
            <div className="mt-2 flex justify-between border-t border-border pt-2.5 text-[14px] font-semibold"><span>{t.cost.perRunLabel[lang]}</span><span>~3.4 &#x0E3F;</span></div>
          </div>
        </div>
      </Section>

      {/* Zone divider */}
      <div className="mb-[72px] flex items-center gap-4">
        <div className="h-px flex-1 bg-border" />
        <span className="text-[10px] uppercase tracking-[0.15em] text-muted-foreground">Deep Dive &mdash; Technical Details</span>
        <div className="h-px flex-1 bg-border" />
      </div>

      {/* 5. Pipeline — vertical timeline */}
      <Section num={5} title={t.pipeline.title[lang]} desc={t.pipeline.desc[lang]}>
        <div className="relative mb-6 pl-10">
          <div className="absolute bottom-0 left-[13px] top-0 w-px bg-gradient-to-b from-border via-orange-700 to-border" />
          {t.pipeline.steps.map((step, i) => (
            <div key={i} className={`relative ${i < t.pipeline.steps.length - 1 ? 'pb-7' : ''}`}>
              <div className="absolute -left-10 top-0.5 z-10 flex h-[26px] w-[26px] items-center justify-center rounded-full border-2 border-border bg-background text-[10px] font-bold text-muted-foreground">
                {i + 1}
              </div>
              <h5 className="text-[14px] font-semibold">{step[lang]}</h5>
              <p className="text-[13px] leading-[1.65] text-muted-foreground">{step.desc[lang]}</p>
            </div>
          ))}
        </div>
        <div className="rounded-xl border border-orange-700/20 bg-orange-700/[0.06] p-5">
          <div className="text-[12px] font-bold text-orange-700">{t.pipeline.smartPdfTitle}</div>
          <p className="mt-1 text-[13px] leading-[1.75] text-muted-foreground">{t.pipeline.smartPdf[lang]}</p>
        </div>
      </Section>

      {/* 6. Tech Stack */}
      <Section num={6} title="Tech Stack" desc={lang === 'th' ? 'เทคโนโลยีที่ใช้ในโปรเจกต์' : 'Technologies used in this project'}>
        <div className="grid grid-cols-1 gap-3.5 sm:grid-cols-3">
          {[
            { title: 'FRONTEND', items: ['Next.js 16 \u2014 React framework', 'React 19 \u2014 UI library', 'TypeScript \u2014 strict mode', 'Tailwind CSS 4 \u2014 styling', 'shadcn/ui \u2014 components', 'Recharts \u2014 charts', 'Lucide React \u2014 icons'] },
            { title: 'BACKEND', items: ['Python 3.11 \u2014 runtime', 'FastAPI \u2014 API framework', 'Playwright \u2014 web crawler', 'pdfplumber \u2014 PDF extraction', 'OpenAI GPT-4.1-mini \u2014 AI engine', 'httpx \u2014 HTTP client', 'Pydantic \u2014 data validation'] },
            { title: 'INFRASTRUCTURE', items: ['AWS EC2 \u2014 t3.medium server', 'Docker Compose \u2014 3 containers', 'Nginx \u2014 reverse proxy', 'Supabase \u2014 PostgreSQL database', 'Cloudflare \u2014 DNS + SSL', "Let's Encrypt \u2014 HTTPS certificate"] },
          ].map((col) => (
            <div key={col.title} className="rounded-xl border border-border bg-card p-5">
              <h4 className="mb-3.5 text-[11px] font-semibold uppercase tracking-[0.08em] text-orange-700">{col.title}</h4>
              <ul className="space-y-0.5">
                {col.items.map((item) => {
                  const [name, desc] = item.split(' \u2014 ');
                  return <li key={item} className="text-[13px] text-muted-foreground"><span className="font-medium text-foreground">{name}</span> &mdash; {desc}</li>;
                })}
              </ul>
            </div>
          ))}
        </div>
      </Section>

      {/* 7. Security */}
      <Section num={7} title={t.security.title[lang]} desc={t.security.desc[lang]}>
        <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
          {securityItems.map((item) => (
            <div key={item.name} className="rounded-xl border border-border bg-card p-[18px]">
              <h5 className="mb-1 flex items-center gap-1.5 text-[13px] font-semibold">
                <span className={`rounded px-1.5 py-px text-[9px] font-semibold uppercase tracking-[0.05em] ${severityStyle[item.severity]}`}>
                  {item.severity === 'crit' ? 'Critical' : item.severity === 'high' ? 'High' : 'Med'}
                </span>
                {item.name}
              </h5>
              <p className="text-[12px] leading-[1.7] text-muted-foreground">{item.desc[lang]}</p>
            </div>
          ))}
        </div>
      </Section>

      {/* 8. Dev Process */}
      <Section num={8} title={t.dev.title[lang]} desc={t.dev.desc[lang]}>
        {/* Vibe quote */}
        <div className="mb-7 rounded-r-[14px] border-l-[3px] border-orange-700 bg-card py-6 pl-7 pr-6">
          <div className="mb-2 text-[18px] font-bold tracking-[-0.02em]">Vibe Coding</div>
          <p className="text-[14px] leading-[1.85] text-muted-foreground">{t.dev.vibeCoding[lang]}</p>
        </div>

        {/* Tools — 2 column table */}
        <div className="mb-7 overflow-hidden rounded-[14px] border border-border bg-card">
          {tools.map((tool, i) => (
            <div key={tool.name} className={`flex gap-4 px-5 py-4 ${i < tools.length - 1 ? 'border-b border-border' : ''} ${i % 2 === 1 ? 'bg-muted/30' : ''}`}>
              <div className="w-[140px] shrink-0 font-mono text-[14px] font-semibold">{tool.name}</div>
              <div className="text-[12px] leading-[1.6] text-muted-foreground">{tool.desc[lang]}</div>
            </div>
          ))}
        </div>

        {/* Skills */}
        <div className="rounded-[14px] border border-border bg-card p-7">
          <h4 className="mb-1.5 text-[14px] font-bold">Agent Skills & Review Agents</h4>
          <p className="mb-6 text-[12px] leading-[1.7] text-muted-foreground" dangerouslySetInnerHTML={{ __html: t.dev.skillsIntro[lang] }} />

          {skillGroups.map((group) => (
            <div key={group.label.en} className="mb-5 last:mb-0">
              <div className="mb-2.5 text-[10px] font-semibold uppercase tracking-[0.08em] text-orange-700">{group.label[lang]}</div>
              <table className="w-full">
                <tbody>
                  {group.skills.map((skill) => (
                    <tr key={skill.name} className="border-b border-border last:border-b-0">
                      <td className={`w-[190px] whitespace-nowrap py-2 pr-4 font-mono text-[12px] font-medium ${skill.used ? 'text-foreground' : 'text-muted-foreground'}`}>
                        {skill.used && <span className="mr-1.5 inline-block h-[5px] w-[5px] rounded-full bg-orange-700 align-middle" />}
                        {skill.name}
                      </td>
                      <td className="py-2 text-[13px] text-muted-foreground">{skill.desc[lang]}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ))}

          <div className="mt-4 flex gap-4 text-[10px] text-muted-foreground">
            <span><span className="mr-1 inline-block h-1.5 w-1.5 rounded-full bg-orange-700 align-middle" /> {t.dev.legendUsed[lang]}</span>
            <span><span className="mr-1 inline-block h-1.5 w-1.5 rounded-full bg-border align-middle" /> {t.dev.legendReady[lang]}</span>
          </div>
        </div>
      </Section>

      {/* Footer */}
      <div className="mt-16 border-t border-border pt-8 text-center text-xs text-muted-foreground">
        <p className="font-semibold text-foreground">FTSE ESG Analyzer</p>
        <p className="mt-1">Built by P&apos;Ohm with Claude Code (Opus 4.6) &bull; March 2026</p>
      </div>
    </div>
  );
}

function Section({ num, title, desc, children }: { num: number; title: string; desc?: string; children: React.ReactNode }) {
  return (
    <div className="mb-[72px]">
      <span className="mb-3.5 flex h-7 w-7 items-center justify-center rounded-full bg-foreground text-xs font-semibold text-background">{num}</span>
      <h2 className="mb-1.5 text-[22px] font-bold tracking-[-0.02em]">{title}</h2>
      {desc && <p className="mb-7 text-[14px] text-muted-foreground">{desc}</p>}
      {!desc && <div className="mb-7" />}
      {children}
    </div>
  );
}
