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
  sections: {
    overview: { th: 'Project Overview', en: 'Project Overview' },
    overviewDesc: { th: 'โปรเจกต์นี้ทำอะไร ทำเพื่อใคร และทำไมถึงต้องทำ', en: 'What this project does, who it\'s for, and why it exists' },
    purpose: {
      th: 'เครื่องมือสำหรับ <strong>ทีม Sale</strong> ใช้วิเคราะห์เว็บไซต์ของลูกค้า เพื่อดูว่าบริษัทมีข้อมูล ESG (สิ่งแวดล้อม สังคม ธรรมาภิบาล) ครบถ้วนแค่ไหน ตามมาตรฐาน FTSE Russell',
      en: 'A tool for the <strong>Sales team</strong> to analyze client websites and assess how well a company discloses ESG (Environmental, Social, Governance) data against FTSE Russell standards.',
    },
    howTo: {
      th: '<strong>วิธีใช้:</strong> Sale ใส่ URL เว็บไซต์ลูกค้า → ระบบวิเคราะห์อัตโนมัติ → ได้คะแนน ESG + จุดที่ต้องปรับปรุง → Sale นำไปเสนอลูกค้า',
      en: '<strong>How to use:</strong> Sales enters client URL → system analyzes automatically → ESG score + improvement areas → Sales presents to client',
    },
    value: {
      th: '<strong>Business Value:</strong> ช่วย Sale pitch ลูกค้าว่า "เว็บไซต์ของคุณขาดข้อมูล ESG ตรงนี้ เราช่วยทำได้" — เปลี่ยน ESG gap เป็นโอกาสขายบริการ',
      en: '<strong>Business Value:</strong> Helps Sales pitch clients: "Your website is missing ESG data here — we can help" — turning ESG gaps into service opportunities',
    },
    techStack: { th: 'Tech Stack', en: 'Tech Stack' },
    techDesc: { th: 'เทคโนโลยีที่ใช้ในโปรเจกต์', en: 'Technologies used in this project' },
    userFlow: { th: 'User Flow — ผู้ใช้ทำอะไรบ้าง', en: 'User Flow — How users interact' },
    userFlowDesc: { th: 'ขั้นตอนการใช้งานจากมุม Sale team', en: 'Step-by-step from the Sales team perspective' },
    step1: {
      th: 'Sale ใส่ URL เว็บไซต์หลักของลูกค้าเพียง URL เดียว — ระบบจะค้นหาเว็บที่เกี่ยวข้องเอง เช่น subdomain IR, Sustainability, Corporate โดยอัตโนมัติ ไม่ต้องใส่ทีละเว็บ',
      en: 'Sales enters just one main URL — the system automatically discovers related subdomains (IR, Sustainability, Corporate) without needing to enter each one separately.',
    },
    step1b: {
      th: '<strong>Industry:</strong> ถ้ารู้หมวดธุรกิจก็เลือกได้เลย ถ้าไม่รู้ก็เลือก <strong>Auto-detect</strong> แล้ว AI จะตรวจจากเนื้อหาเว็บให้',
      en: '<strong>Industry:</strong> Select if known, or choose <strong>Auto-detect</strong> and AI will determine it from the website content.',
    },
    step2: {
      th: 'AI เข้าไปอ่านเนื้อหาทั้งเว็บไซต์ ทุกหน้าที่เกี่ยวข้องกับ ESG รวมถึง subdomain และดาวน์โหลด PDF (Annual Report, Sustainability Report) อัตโนมัติ',
      en: 'AI reads the entire website — every ESG-relevant page including subdomains, and automatically downloads PDFs (Annual Report, Sustainability Report).',
    },
    step3: {
      th: 'AI วิเคราะห์เนื้อหาเทียบกับ FTSE Russell ESG indicators ที่เกี่ยวข้องกับหมวดธุรกิจนั้นๆ ครอบคลุม themes ด้าน Environment, Social และ Governance',
      en: 'AI analyzes content against FTSE Russell ESG indicators relevant to the company\'s industry sector, covering Environmental, Social, and Governance themes.',
    },
    step4: {
      th: 'คิดคะแนน 0-5 ต่อ theme ตาม FTSE methodology แล้วรวมเป็นคะแนน E, S, G และ Overall',
      en: 'Calculates scores 0-5 per theme using FTSE methodology, then aggregates into E, S, G and Overall scores.',
    },
    step5: {
      th: 'Sale เห็นคะแนนรวม, คะแนนรายธีม, รายละเอียด indicator ที่เจอ/ไม่เจอ, และคำแนะนำว่าควรสร้างหน้าเว็บอะไรเพิ่ม',
      en: 'Sales sees overall scores, per-theme breakdown, indicator details (found/missing), and recommendations for new web pages to improve scores.',
    },
    pipeline: { th: 'Analysis Pipeline — ระบบทำงานอย่างไร', en: 'Analysis Pipeline — How the system works' },
    pipelineDesc: { th: 'ขั้นตอนการทำงานภายในของ backend ทั้งหมด', en: 'Internal backend processing steps' },
    smartPdf: {
      th: 'PDF รายงานประจำปีอาจมี 300+ หน้า แต่ระบบไม่อ่านทุกหน้า — สแกนสารบัญก่อน แล้วอ่านเฉพาะหน้าที่เกี่ยวข้องกับ ESG ทั้งภาษาไทยและอังกฤษ ประหยัดเวลาและ token',
      en: 'Annual reports can be 300+ pages, but the system doesn\'t read everything — it scans the table of contents first, then reads only ESG-relevant pages in both Thai and English, saving time and tokens.',
    },
    accuracy: { th: 'Accuracy — เปรียบเทียบกับ FTSE จริง', en: 'Accuracy — Compared to real FTSE scores' },
    accuracyDesc: { th: 'Calibrate ด้วยข้อมูลจริงจาก FTSE Russell', en: 'Calibrated with real FTSE Russell data' },
    security: { th: 'Security Measures', en: 'Security Measures' },
    securityDesc: { th: 'มาตรการรักษาความปลอดภัยที่ทำไว้', en: 'Security measures implemented' },
    cost: { th: 'Cost & Resources', en: 'Cost & Resources' },
    costDesc: { th: 'ค่าใช้จ่ายรายเดือนและต่อการใช้งาน', en: 'Monthly costs and per-analysis costs' },
    remaining: { th: 'Remaining Work', en: 'Remaining Work' },
    remainingDesc: { th: 'สิ่งที่ต้องทำต่อ', en: 'What still needs to be done' },
    devProcess: { th: 'Development Process — สร้างแอปนี้ขึ้นมาอย่างไร', en: 'Development Process — How this app was built' },
    devProcessDesc: {
      th: 'โปรเจกต์นี้สร้างด้วย Vibe Coding — ใช้ AI เป็นตัวช่วยหลักในการเขียน code ทั้งหมด',
      en: 'This project was built using Vibe Coding — AI as the primary code author',
    },
    vibeCoding: {
      th: 'วิธีการพัฒนาซอฟต์แวร์แบบใหม่ที่ใช้ AI coding agent เป็นผู้เขียน code — ผู้สร้างทำหน้าที่เป็น "ผู้กำกับ" คอยบอกว่าต้องการอะไร ตรวจสอบผลลัพธ์ และตัดสินใจ โดยไม่ต้องเขียน code เองทุกบรรทัด',
      en: 'A new software development approach using AI coding agents to write code — the creator acts as a "director", defining requirements, reviewing results, and making decisions without writing every line of code.',
    },
  },
};

export default function AboutPage() {
  const [lang, setLang] = useState<Lang>('th');
  const s = t.sections;

  return (
    <div className="mx-auto max-w-4xl px-6 py-8">
      {/* Back button */}
      <div className="mb-8">
        <Link href="/" className="inline-flex items-center gap-2 text-xs uppercase tracking-[0.1em] text-muted-foreground hover:text-foreground">
          <ArrowLeft className="h-3 w-3" />
          Back
        </Link>
      </div>

      {/* Floating language toggle */}
      <button
        onClick={() => setLang(lang === 'th' ? 'en' : 'th')}
        className="fixed right-6 top-20 z-50 rounded-full border border-border bg-background/90 px-4 py-1.5 text-xs font-medium uppercase tracking-[0.1em] text-muted-foreground shadow-sm backdrop-blur-sm transition-colors hover:bg-foreground hover:text-background"
      >
        {lang === 'th' ? 'EN' : 'TH'}
      </button>

      {/* Hero */}
      <div className="mb-16 text-center animate-fade-up">
        <h1 className="text-4xl font-bold tracking-[-0.03em] sm:text-5xl">FTSE ESG Analyzer</h1>
        <p className="mx-auto mt-4 max-w-xl text-sm text-muted-foreground">{lang === 'th' ? t.hero.th : t.hero.en}</p>
        <span className="mt-4 inline-block rounded-full bg-muted px-4 py-1.5 text-xs text-muted-foreground">
          {t.badge[lang]}
        </span>
      </div>

      {/* 1. Overview */}
      <Section num={1} title={s.overview[lang]} desc={s.overviewDesc[lang]}>
        <Card>
          <p className="text-sm" dangerouslySetInnerHTML={{ __html: s.purpose[lang] }} />
          <p className="mt-4 text-sm" dangerouslySetInnerHTML={{ __html: s.howTo[lang] }} />
          <p className="mt-4 text-sm" dangerouslySetInnerHTML={{ __html: s.value[lang] }} />
        </Card>
      </Section>

      {/* 2. Tech Stack */}
      <Section num={2} title={s.techStack[lang]} desc={s.techDesc[lang]}>
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
          <StackBox title="Frontend" items={['Next.js 16', 'TypeScript (strict)', 'Tailwind CSS', 'shadcn/ui', 'Recharts']} />
          <StackBox title="Backend" items={['Python FastAPI', 'Playwright (crawler)', 'pdfplumber (PDF)', 'OpenAI GPT-4.1-mini', 'httpx']} />
          <StackBox title="Infrastructure" items={['AWS EC2 (t3.medium)', 'Docker Compose', 'Nginx (reverse proxy)', 'Supabase (PostgreSQL)', 'Cloudflare (DNS+SSL)']} />
        </div>
      </Section>

      {/* 3. User Flow */}
      <Section num={3} title={s.userFlow[lang]} desc={s.userFlowDesc[lang]}>
        <div className="flex flex-col items-center gap-0">
          <FlowStep active label={lang === 'th' ? '1. กรอก URL + เลือก Industry' : '1. Enter URL + Select Industry'} desc={s.step1[lang]} descB={s.step1b[lang]} tech="esg.ohmai.me" />
          <FlowArrow />
          <FlowStep label={lang === 'th' ? '2. ระบบ Crawl เว็บไซต์' : '2. System Crawls Website'} desc={s.step2[lang]} tech="Playwright + pdfplumber" />
          <FlowArrow />
          <FlowStep label={lang === 'th' ? '3. AI วิเคราะห์ ESG Indicators' : '3. AI Analyzes ESG Indicators'} desc={s.step3[lang]} tech="OpenAI GPT-4.1-mini" />
          <FlowArrow />
          <FlowStep label={lang === 'th' ? '4. คำนวณคะแนน ESG' : '4. Calculate ESG Scores'} desc={s.step4[lang]} tech="Scoring Engine" />
          <FlowArrow />
          <FlowStep active label={lang === 'th' ? '5. แสดงผล Dashboard + Sitemap' : '5. Display Dashboard + Sitemap'} desc={s.step5[lang]} tech="Dashboard" />
        </div>
      </Section>

      {/* 4. Pipeline */}
      <Section num={4} title={s.pipeline[lang]} desc={s.pipelineDesc[lang]}>
        <div className="grid grid-cols-3 gap-2 sm:grid-cols-5">
          {(lang === 'th' ? [
            { n: '1', l: 'ค้นหา Sitemap' }, { n: '2', l: 'อ่านเว็บ' }, { n: '3', l: 'ค้นหา PDF' },
            { n: '4', l: 'ระบุหมวดธุรกิจ' }, { n: '5', l: 'กรอง Indicators' }, { n: '6', l: 'วิเคราะห์จากเว็บ' },
            { n: '7', l: 'เติมข้อมูลจาก PDF' }, { n: '8', l: 'คำนวณคะแนน' }, { n: '9', l: 'แนะนำ Sitemap' },
          ] : [
            { n: '1', l: 'Sitemap Scan' }, { n: '2', l: 'Web Crawl' }, { n: '3', l: 'PDF Discovery' },
            { n: '4', l: 'Detect Industry' }, { n: '5', l: 'Filter Indicators' }, { n: '6', l: 'Analyze Website' },
            { n: '7', l: 'Fill Gaps from PDF' }, { n: '8', l: 'Calculate Scores' }, { n: '9', l: 'Recommend Sitemap' },
          ]).map((p) => (
            <div key={p.n} className="rounded-lg border border-border bg-card p-3 text-center text-xs">
              <span className="mb-1 inline-flex h-6 w-6 items-center justify-center rounded-full bg-foreground text-[10px] text-background">{p.n}</span>
              <span className="mt-1 block font-semibold">{p.l}</span>
            </div>
          ))}
        </div>
        <Card className="mt-4">
          <p className="text-xs font-semibold" style={{ color: '#c2410c' }}>Smart PDF Reading</p>
          <p className="mt-1 text-xs text-muted-foreground">{s.smartPdf[lang]}</p>
        </Card>
      </Section>

      {/* 5. Accuracy */}
      <Section num={5} title={s.accuracy[lang]} desc={s.accuracyDesc[lang]}>
        <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
          <ScoreCard label="ESG Overall" value="3.4" target="3.3" />
          <ScoreCard label="Environmental" value="2.0" target="2.3" />
          <ScoreCard label="Social" value="4.3" target="3.3" />
          <ScoreCard label="Governance" value="4.0" target="4.6" />
        </div>
      </Section>

      {/* 6. Security */}
      <Section num={6} title={s.security[lang]} desc={s.securityDesc[lang]}>
        <div className="grid grid-cols-1 gap-2 sm:grid-cols-2">
          <SecurityItem icon="SSRF Protection" desc={lang === 'th' ? 'Block private IPs ป้องกันเข้าถึง AWS metadata' : 'Block private IPs to prevent AWS metadata access'} />
          <SecurityItem icon="Rate Limiting" desc={lang === 'th' ? '5 req/min สำหรับ analysis' : '5 req/min for analysis creation'} />
          <SecurityItem icon="Security Headers" desc="X-Content-Type-Options, X-Frame-Options, HSTS" />
          <SecurityItem icon="Non-root Docker" desc={lang === 'th' ? 'Container รันเป็น appuser ไม่ใช่ root' : 'Container runs as appuser, not root'} />
          <SecurityItem icon="CORS Restricted" desc={lang === 'th' ? 'อนุญาตเฉพาะ esg.ohmai.me' : 'Only esg.ohmai.me allowed'} />
          <SecurityItem icon="Query Limits" desc={lang === 'th' ? 'จำกัด max 100 records' : 'Max 100 records per request'} />
        </div>
      </Section>

      {/* 7. Cost */}
      <Section num={7} title={s.cost[lang]} desc={s.costDesc[lang]}>
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
          <Card>
            <p className="mb-2 text-xs font-semibold">{lang === 'th' ? 'ค่าใช้จ่ายคงที่ / เดือน' : 'Monthly Fixed Cost'}</p>
            <div className="space-y-1 text-xs text-muted-foreground">
              <div className="flex justify-between"><span>AWS EC2 (shared)</span><span>~$30</span></div>
              <div className="flex justify-between"><span>Supabase PRO</span><span>~$25</span></div>
              <div className="flex justify-between border-t pt-1 font-semibold text-foreground"><span>{lang === 'th' ? 'รวม' : 'Total'}</span><span>~$55/mo (~1,925 THB)</span></div>
            </div>
          </Card>
          <Card>
            <p className="mb-2 text-xs font-semibold">{lang === 'th' ? 'ค่าใช้จ่ายต่อ Analysis' : 'Per Analysis Cost'}</p>
            <div className="space-y-1 text-xs text-muted-foreground">
              <div className="flex justify-between"><span>OpenAI tokens</span><span>~$0.096</span></div>
              <div className="flex justify-between"><span>{lang === 'th' ? 'เวลา' : 'Time'}</span><span>5-7 min</span></div>
              <div className="flex justify-between border-t pt-1 font-semibold text-foreground"><span>{lang === 'th' ? 'ต่อครั้ง' : 'Per run'}</span><span>~3.4 THB</span></div>
            </div>
          </Card>
        </div>
      </Section>

      {/* 8. Dev Process */}
      <Section num={8} title={s.devProcess[lang]} desc={s.devProcessDesc[lang]}>
        <Card>
          <p className="text-xs font-semibold" style={{ color: '#c2410c' }}>Vibe Coding</p>
          <p className="mt-1 text-xs text-muted-foreground">{s.vibeCoding[lang]}</p>
        </Card>
        <Card className="mt-4">
          <p className="mb-2 text-xs font-semibold">{lang === 'th' ? 'เครื่องมือหลัก' : 'Main Tools'}</p>
          <div className="space-y-1 text-xs text-muted-foreground">
            <div><strong className="text-foreground">Claude Code (CLI)</strong> — AI coding agent in VS Code terminal</div>
            <div><strong className="text-foreground">Claude Opus 4.6</strong> — AI model powering Claude Code</div>
            <div><strong className="text-foreground">Playwright (MCP)</strong> — Automated browser testing</div>
            <div><strong className="text-foreground">GitHub</strong> — Version control</div>
            <div><strong className="text-foreground">AWS EC2</strong> — Cloud deployment</div>
          </div>
        </Card>
        <Card className="mt-4">
          <p className="mb-2 text-xs font-semibold">Agent Skills (10)</p>
          <div className="space-y-1 text-xs text-muted-foreground">
            <div><strong className="text-foreground">supabase-postgres-best-practices</strong> — {lang === 'th' ? 'เขียน query, RLS, migration ตามแนวทางของ Supabase' : 'Write queries, RLS, migrations following Supabase guidelines'}</div>
            <div><strong className="text-foreground">next-best-practices</strong> — {lang === 'th' ? 'ใช้ App Router, Server Components, data fetching ตามมาตรฐาน Vercel' : 'App Router, Server Components, data fetching per Vercel standards'}</div>
            <div><strong className="text-foreground">shadcn</strong> — {lang === 'th' ? 'ใช้ UI components อย่างถูกวิธี ตาม design system ของ shadcn/ui' : 'Use UI components correctly per shadcn/ui design system'}</div>
            <div><strong className="text-foreground">vercel-react-best-practices</strong> — {lang === 'th' ? 'เขียน React components ที่ปลอดภัย มี performance ดี' : 'Write safe, performant React components'}</div>
            <div><strong className="text-foreground">systematic-debugging</strong> — {lang === 'th' ? 'วิเคราะห์ bug อย่างเป็นขั้นตอน หาสาเหตุที่แท้จริง' : 'Analyze bugs systematically, find root causes'}</div>
            <div><strong className="text-foreground">frontend-design</strong> — {lang === 'th' ? 'ออกแบบ UI/UX ตามหลัก accessibility และ responsive design' : 'Design UI/UX with accessibility and responsive principles'}</div>
            <div><strong className="text-foreground">pdf</strong> — {lang === 'th' ? 'อ่าน สร้าง และจัดการไฟล์ PDF' : 'Read, create, and manage PDF files'}</div>
            <div><strong className="text-foreground">python-error-handling</strong> — {lang === 'th' ? 'จัดการ error, retry, logging ใน Python อย่างถูกต้อง' : 'Handle errors, retries, logging in Python properly'}</div>
            <div><strong className="text-foreground">python-performance-optimization</strong> — {lang === 'th' ? 'ลด memory usage, ใช้ async/await, optimize algorithm' : 'Reduce memory usage, use async/await, optimize algorithms'}</div>
            <div><strong className="text-foreground">agent-browser</strong> — {lang === 'th' ? 'ควบคุม browser อัตโนมัติ เปิดเว็บ กรอกฟอร์ม ตรวจผลลัพธ์' : 'Automate browser — navigate, fill forms, verify results'}</div>
          </div>
        </Card>
        <Card className="mt-4">
          <p className="mb-2 text-xs font-semibold">{lang === 'th' ? 'Review Agents ที่ใช้ตรวจ code' : 'Code Review Agents'}</p>
          <div className="space-y-1 text-xs text-muted-foreground">
            <div><strong className="text-foreground">performance-error-reviewer</strong> — {lang === 'th' ? 'ตรวจ memory leaks, error handling, timeout, algorithm complexity' : 'Checks memory leaks, error handling, timeout, algorithm complexity'}</div>
            <div><strong className="text-foreground">react-typescript-reviewer</strong> — {lang === 'th' ? 'ตรวจ accessibility, type safety, unused imports, re-render issues' : 'Checks accessibility, type safety, unused imports, re-render issues'}</div>
            <div><strong className="text-foreground">security-auditor</strong> — {lang === 'th' ? 'ตรวจ SSRF, XSS, rate limiting, secrets exposure, Docker security' : 'Checks SSRF, XSS, rate limiting, secrets exposure, Docker security'}</div>
          </div>
        </Card>
      </Section>

      {/* Footer */}
      <div className="mt-16 border-t border-border pt-8 text-center text-xs text-muted-foreground">
        <p className="font-semibold text-foreground">FTSE ESG Analyzer</p>
        <p className="mt-1">Built by P&apos;Ohm with Claude Code (Opus 4.6) &bull; March 2026</p>
      </div>
    </div>
  );
}

function Section({ num, title, desc, children }: { num: number; title: string; desc: string; children: React.ReactNode }) {
  return (
    <div className="mb-16">
      <div className="mb-2 flex items-center gap-3">
        <span className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-foreground text-xs text-background">{num}</span>
        <h2 className="text-lg font-bold tracking-[-0.02em]">{title}</h2>
      </div>
      <p className="mb-6 text-xs text-muted-foreground">{desc}</p>
      {children}
    </div>
  );
}

function Card({ children, className = '' }: { children: React.ReactNode; className?: string }) {
  return <div className={`rounded-xl border border-border bg-card p-6 ${className}`}>{children}</div>;
}

function StackBox({ title, items }: { title: string; items: string[] }) {
  return (
    <div className="rounded-xl border border-border bg-card p-5 text-center">
      <h4 className="mb-3 text-xs font-bold uppercase tracking-[0.1em]" style={{ color: '#c2410c' }}>{title}</h4>
      <ul className="space-y-1 text-xs text-muted-foreground">
        {items.map((item) => <li key={item}>{item}</li>)}
      </ul>
    </div>
  );
}

function FlowStep({ label, desc, descB, tech, active }: { label: string; desc: string; descB?: string; tech: string; active?: boolean }) {
  return (
    <div className={`w-full max-w-xl rounded-xl border-2 p-5 ${active ? 'border-orange-700/30 bg-orange-50/30' : 'border-border bg-card'}`}>
      <p className="text-sm font-bold">{label}</p>
      <p className="mt-1 text-xs text-muted-foreground" dangerouslySetInnerHTML={{ __html: desc }} />
      {descB && <p className="mt-2 text-xs text-muted-foreground" dangerouslySetInnerHTML={{ __html: descB }} />}
      <span className="mt-2 inline-block rounded border border-border bg-muted/50 px-2 py-0.5 text-[10px] text-muted-foreground">{tech}</span>
    </div>
  );
}

function FlowArrow() {
  return <div className="h-6 w-px bg-border" />;
}

function ScoreCard({ label, value, target }: { label: string; value: string; target: string }) {
  return (
    <div className="rounded-xl border border-border bg-card p-4 text-center">
      <p className="text-2xl font-extrabold tracking-tight">{value}</p>
      <p className="text-[10px] text-muted-foreground">target: {target}</p>
      <p className="mt-1 text-[10px] uppercase tracking-[0.1em] text-muted-foreground">{label}</p>
    </div>
  );
}

function SecurityItem({ icon, desc }: { icon: string; desc: string }) {
  return (
    <div className="flex gap-3 rounded-lg border border-border bg-card p-3">
      <div className="shrink-0 text-xs font-bold text-foreground">{icon}</div>
      <div className="text-xs text-muted-foreground">{desc}</div>
    </div>
  );
}
