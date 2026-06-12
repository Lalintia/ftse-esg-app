'use client';

import { useState, useRef, useCallback, useEffect } from 'react';
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
  const [focusedIndex, setFocusedIndex] = useState<number>(-1);
  const containerRef = useRef<HTMLDivElement>(null);
  const listboxRef = useRef<HTMLDivElement>(null);

  const closeDropdown = useCallback(() => {
    setIsOpen(false);
    setFocusedIndex(-1);
  }, []);
  useClickOutside(containerRef, closeDropdown);

  const selectedCategory = INDUSTRY_CATEGORIES.find((c) => c.value === value);

  // Scroll focused item into view
  useEffect(() => {
    if (!isOpen || focusedIndex < 0) return;
    const list = listboxRef.current;
    if (!list) return;
    const item = list.querySelector<HTMLElement>(`[id="industry-option-${focusedIndex}"]`);
    item?.scrollIntoView({ block: 'nearest' });
  }, [focusedIndex, isOpen]);

  const handleKeyDown = (e: React.KeyboardEvent<HTMLButtonElement>) => {
    if (disabled) return;

    switch (e.key) {
      case 'Enter':
      case ' ':
        e.preventDefault();
        if (!isOpen) {
          setIsOpen(true);
          setFocusedIndex(0);
        } else if (focusedIndex >= 0) {
          onChange(INDUSTRY_CATEGORIES[focusedIndex].value);
          closeDropdown();
        }
        break;
      case 'ArrowDown':
        e.preventDefault();
        if (!isOpen) {
          setIsOpen(true);
          setFocusedIndex(0);
        } else {
          setFocusedIndex((prev) => Math.min(prev + 1, INDUSTRY_CATEGORIES.length - 1));
        }
        break;
      case 'ArrowUp':
        e.preventDefault();
        if (isOpen) {
          setFocusedIndex((prev) => Math.max(prev - 1, 0));
        }
        break;
      case 'Escape':
        e.preventDefault();
        closeDropdown();
        break;
    }
  };

  const activedescendant = isOpen && focusedIndex >= 0
    ? `industry-option-${focusedIndex}`
    : undefined;

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
        aria-activedescendant={activedescendant}
        onClick={() => !disabled && setIsOpen(!isOpen)}
        onKeyDown={handleKeyDown}
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
        <div
          id="industry-listbox"
          role="listbox"
          aria-label="Industry options"
          ref={listboxRef}
          className="absolute z-50 mt-2 w-full rounded-lg border bg-card shadow-lg animate-fade-in"
        >
          <div className="max-h-80 overflow-y-auto py-1">
            {INDUSTRY_CATEGORIES.map((category, index) => (
              <button
                key={category.value}
                id={`industry-option-${index}`}
                type="button"
                role="option"
                aria-selected={category.value === value}
                onClick={() => {
                  onChange(category.value);
                  closeDropdown();
                }}
                className={cn(
                  'flex w-full items-start gap-3 px-4 py-3 text-left transition-colors hover:bg-muted/50',
                  category.value === value && 'bg-muted',
                  category.value === 'auto' && 'border-b',
                  focusedIndex === index && 'outline outline-2 outline-foreground/30',
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
