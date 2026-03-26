'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { cn } from '@/lib/utils';

export const Navbar = () => {
  const pathname = usePathname();
  const isHome = pathname === '/';

  return (
    <header className="sticky top-0 z-50 w-full border-b border-border/60 bg-background/80 backdrop-blur-md">
      <div className="mx-auto flex h-14 max-w-6xl items-center justify-between px-6">
        <Link href="/" className="flex items-baseline gap-1.5">
          <span className="text-sm font-bold uppercase tracking-[0.2em]">
            FTSE
          </span>
          <span className="text-xs font-normal uppercase tracking-[0.15em] text-muted-foreground">
            ESG
          </span>
        </Link>

        <nav className="flex items-center gap-6">
          <Link
            href="/"
            className={cn(
              'text-xs font-medium uppercase tracking-[0.1em] transition-colors',
              isHome ? 'text-foreground' : 'text-muted-foreground hover:text-foreground',
            )}
          >
            Analyse
          </Link>
          <Link
            href="/history"
            className={cn(
              'text-xs font-medium uppercase tracking-[0.1em] transition-colors',
              pathname === '/history' ? 'text-foreground' : 'text-muted-foreground hover:text-foreground',
            )}
          >
            History
          </Link>
          <Link
            href="/about"
            className={cn(
              'text-xs font-medium uppercase tracking-[0.1em] transition-colors',
              pathname === '/about' ? 'text-foreground' : 'text-muted-foreground hover:text-foreground',
            )}
          >
            About
          </Link>
        </nav>
      </div>
    </header>
  );
};
