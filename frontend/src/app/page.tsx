'use client';

import { useState, useEffect, useRef } from 'react';
import { useRouter } from 'next/navigation';
import { ArrowRight } from 'lucide-react';
import { IndustrySelect } from '@/components/IndustrySelect';
import { createAnalysis } from '@/lib/api';

export default function HomePage() {
  const router = useRouter();
  const [url, setUrl] = useState('');
  const [industryCode, setIndustryCode] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const parallaxRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    let rafId: number;
    const handleScroll = () => {
      cancelAnimationFrame(rafId);
      rafId = requestAnimationFrame(() => {
        if (!parallaxRef.current) {
          return;
        }
        parallaxRef.current.style.transform = `translateY(${window.scrollY * 0.3}px)`;
      });
    };
    window.addEventListener('scroll', handleScroll, { passive: true });
    return () => {
      window.removeEventListener('scroll', handleScroll);
      cancelAnimationFrame(rafId);
    };
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    if (!url.trim()) {
      setError('Please enter a company website URL.');
      return;
    }
    if (!industryCode) {
      setError('Please select an industry.');
      return;
    }

    setIsSubmitting(true);
    try {
      const result = await createAnalysis(url.trim(), industryCode);
      router.push(`/analysis/${result.analysis_id}`);
    } catch {
      setError('Failed to start analysis. Please check the URL and try again.');
      setIsSubmitting(false);
    }
  };

  return (
    <div className="relative flex flex-col items-center px-6 pt-[10vh] pb-[50vh]">
      {/* Parallax background */}
      <div ref={parallaxRef} className="parallax-bg">
        <div className="parallax-circle" style={{ width: '600px', height: '600px', top: '-200px', right: '-100px' }} />
        <div className="parallax-circle" style={{ width: '400px', height: '400px', bottom: '-100px', left: '-50px', opacity: 0.5 }} />
      </div>

      {/* Content */}
      <div className="relative z-10 w-full max-w-xl">
        {/* Hero typography */}
        <div className="mb-16 animate-fade-up text-center">
          <h1 className="text-[clamp(3rem,8vw,6.5rem)] font-bold leading-[0.9] tracking-[-0.04em]">
            <span className="block">FTSE ESG</span>
            <span className="block text-muted-foreground/30">ANALYZER</span>
          </h1>
          <p className="mt-6 max-w-md text-base leading-relaxed text-muted-foreground">
            Analyse any company website against FTSE Russell ESG indicators
            and IFRS S1/S2 sustainability standards.
          </p>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="space-y-4 animate-fade-up-d2">
          <div>
            <label htmlFor="url" className="mb-2 block text-xs font-medium uppercase tracking-[0.1em] text-muted-foreground">
              Company Website
            </label>
            <input
              id="url"
              type="url"
              placeholder="https://www.company.com"
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              disabled={isSubmitting}
              className="flex h-14 w-full rounded-lg border bg-card px-4 text-base transition-all placeholder:text-muted-foreground/50 focus:outline-none focus:ring-2 focus:ring-foreground/20 disabled:cursor-not-allowed disabled:opacity-50"
            />
          </div>

          <div>
            <label htmlFor="industry-select" className="mb-2 block text-xs font-medium uppercase tracking-[0.1em] text-muted-foreground">
              Industry
            </label>
            <IndustrySelect
              value={industryCode}
              onChange={setIndustryCode}
              disabled={isSubmitting}
            />
          </div>

          {error && (
            <div role="alert" aria-live="polite" className="rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
              {error}
            </div>
          )}

          <button
            type="submit"
            disabled={isSubmitting}
            className="flex h-14 w-full items-center justify-center gap-2 rounded-lg bg-foreground text-base font-medium text-background transition-all hover:opacity-90 active:scale-[0.99] disabled:cursor-not-allowed disabled:opacity-50"
          >
            {isSubmitting ? (
              <span>Analysing...</span>
            ) : (
              <>
                <span>Analyse</span>
                <ArrowRight className="h-4 w-4" />
              </>
            )}
          </button>
        </form>
      </div>
    </div>
  );
}
