'use client';

import { useState, useMemo, useRef, useEffect } from 'react';
import { Check, ChevronsUpDown, Search } from 'lucide-react';
import { cn } from '@/lib/utils';
import type { SubsectorItem } from '@/lib/types';

interface SubsectorSelectProps {
  subsectors: SubsectorItem[];
  value: string;
  onChange: (code: string) => void;
  disabled?: boolean;
}

export const SubsectorSelect = ({
  subsectors,
  value,
  onChange,
  disabled = false,
}: SubsectorSelectProps) => {
  const [isOpen, setIsOpen] = useState(false);
  const [search, setSearch] = useState('');
  const containerRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  const selectedItem = subsectors.find((s) => s.code === value);

  const filtered = useMemo(() => {
    if (!search.trim()) { return subsectors; }
    const query = search.toLowerCase();
    return subsectors.filter(
      (s) =>
        s.name.toLowerCase().includes(query) ||
        s.code.toLowerCase().includes(query) ||
        s.industry_name.toLowerCase().includes(query) ||
        s.supersector_name.toLowerCase().includes(query),
    );
  }, [subsectors, search]);

  const grouped = useMemo(() => {
    const groups: Record<string, SubsectorItem[]> = {};
    for (const item of filtered) {
      const key = item.industry_name;
      if (!groups[key]) { groups[key] = []; }
      groups[key].push(item);
    }
    return Object.entries(groups).sort(([a], [b]) => a.localeCompare(b));
  }, [filtered]);

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (containerRef.current && !containerRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  useEffect(() => {
    if (isOpen && inputRef.current) {
      inputRef.current.focus();
    }
  }, [isOpen]);

  return (
    <div ref={containerRef} className="relative w-full">
      <button
        type="button"
        role="combobox"
        aria-expanded={isOpen}
        aria-haspopup="listbox"
        aria-controls="subsector-listbox"
        aria-label="Select subsector"
        disabled={disabled}
        onClick={() => setIsOpen(!isOpen)}
        className={cn(
          'flex w-full items-center justify-between rounded-md border bg-background px-3 py-2.5 text-sm',
          'hover:bg-muted/50 focus:outline-none focus:ring-2 focus:ring-ring',
          'disabled:cursor-not-allowed disabled:opacity-50',
          !value && 'text-muted-foreground',
        )}
      >
        <span className="truncate">
          {selectedItem
            ? `${selectedItem.code} - ${selectedItem.name}`
            : 'Select a subsector...'}
        </span>
        <ChevronsUpDown className="ml-2 h-4 w-4 shrink-0 text-muted-foreground" />
      </button>

      {isOpen && (
        <div id="subsector-listbox" role="listbox" aria-label="Subsector options" className="absolute z-50 mt-1 w-full rounded-md border bg-popover shadow-lg">
          <div className="flex items-center gap-2 border-b px-3 py-2">
            <Search className="h-4 w-4 text-muted-foreground" />
            <input
              ref={inputRef}
              type="text"
              aria-label="Search subsectors"
              aria-autocomplete="list"
              aria-controls="subsector-listbox"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Search subsectors..."
              className="flex-1 bg-transparent text-sm outline-none placeholder:text-muted-foreground"
            />
          </div>
          <div className="max-h-64 overflow-y-auto p-1">
            {grouped.length === 0 ? (
              <div className="py-6 text-center text-sm text-muted-foreground">
                No subsectors found.
              </div>
            ) : (
              grouped.map(([industry, items]) => (
                <div key={industry}>
                  <div className="px-2 py-1.5 text-xs font-semibold text-muted-foreground">
                    {industry}
                  </div>
                  {items.map((item) => (
                    <button
                      key={item.code}
                      type="button"
                      onClick={() => {
                        onChange(item.code);
                        setIsOpen(false);
                        setSearch('');
                      }}
                      className={cn(
                        'flex w-full items-center gap-2 rounded-sm px-2 py-1.5 text-sm',
                        'hover:bg-accent hover:text-accent-foreground',
                        value === item.code && 'bg-accent',
                      )}
                    >
                      <Check
                        className={cn(
                          'h-4 w-4 shrink-0',
                          value === item.code ? 'opacity-100' : 'opacity-0',
                        )}
                      />
                      <span className="font-mono text-xs text-muted-foreground">
                        {item.code}
                      </span>
                      <span className="truncate">{item.name}</span>
                    </button>
                  ))}
                </div>
              ))
            )}
          </div>
        </div>
      )}
    </div>
  );
};
