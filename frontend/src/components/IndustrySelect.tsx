'use client';

import { useState, useRef, useCallback } from 'react';
import { ChevronDown, Sparkles } from 'lucide-react';
import { INDUSTRY_CATEGORIES } from '@/lib/api';
import { cn } from '@/lib/utils';
import { useClickOutside } from '@/hooks/useClickOutside';

interface IndustrySelectProps {
  value: string;
  onChange: (value: string) => void;
  disabled?: boolean;
}

export const IndustrySelect = ({ value, onChange, disabled }: IndustrySelectProps) => {
  const [isOpen, setIsOpen] = useState(false);
  const containerRef = useRef<HTMLDivElement>(null);
  const closeDropdown = useCallback(() => setIsOpen(false), []);
  useClickOutside(containerRef, closeDropdown);

  const selectedCategory = INDUSTRY_CATEGORIES.find((c) => c.value === value);

  return (
    <div ref={containerRef} className="relative">
      <button
        type="button"
        id="industry-select"
        role="combobox"
        aria-expanded={isOpen}
        aria-haspopup="listbox"
        aria-controls="industry-listbox"
        aria-label="Select industry"
        onClick={() => !disabled && setIsOpen(!isOpen)}
        disabled={disabled}
        className={cn(
          'flex h-14 w-full items-center justify-between rounded-lg border bg-card px-4 text-left transition-all',
          'text-base focus:outline-none focus:ring-2 focus:ring-foreground/20',
          isOpen && 'ring-2 ring-foreground/20',
          disabled && 'cursor-not-allowed opacity-50',
          !value && 'text-muted-foreground',
        )}
      >
        <span className="truncate">
          {selectedCategory ? selectedCategory.label : 'Select industry...'}
        </span>
        <ChevronDown className={cn(
          'ml-2 h-4 w-4 shrink-0 text-muted-foreground transition-transform',
          isOpen && 'rotate-180',
        )} />
      </button>

      {isOpen && (
        <div id="industry-listbox" role="listbox" aria-label="Industry options" className="absolute z-50 mt-2 w-full rounded-lg border bg-card shadow-lg animate-fade-in">
          <div className="max-h-80 overflow-y-auto py-1">
            {INDUSTRY_CATEGORIES.map((category) => (
              <button
                key={category.value}
                type="button"
                role="option"
                aria-selected={category.value === value}
                onClick={() => {
                  onChange(category.value);
                  setIsOpen(false);
                }}
                className={cn(
                  'flex w-full items-start gap-3 px-4 py-3 text-left transition-colors hover:bg-muted/50',
                  category.value === value && 'bg-muted',
                  category.value === 'auto' && 'border-b',
                )}
              >
                {category.value === 'auto' && (
                  <Sparkles className="mt-0.5 h-4 w-4 shrink-0 text-muted-foreground" />
                )}
                <div className={category.value !== 'auto' ? 'pl-7' : ''}>
                  <div className={cn(
                    'text-sm font-medium',
                    category.value === 'auto' && 'font-semibold',
                  )}>
                    {category.label}
                  </div>
                  <div className="text-xs text-muted-foreground">
                    {category.description}
                  </div>
                </div>
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};
