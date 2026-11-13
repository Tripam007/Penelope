"use client";

import React from "react";
import { motion } from "framer-motion";
import { cn } from "@/lib/utils";

export interface SegmentOption<T extends string = string> {
  value: T;
  label: React.ReactNode;
  icon?: React.ReactNode;
}

export interface SegmentedControlProps<T extends string = string> {
  options: SegmentOption<T>[];
  value: T;
  onChange: (value: T) => void;
  size?: "sm" | "md";
  className?: string;
  name?: string;
}

export function SegmentedControl<T extends string = string>({
  options,
  value,
  onChange,
  size = "md",
  className,
  name = "segmented-control",
}: SegmentedControlProps<T>) {
  return (
    <div
      role="tablist"
      aria-label={name}
      className={cn(
        "relative flex items-center p-1 rounded-full glass-surface-1 border border-black/5 dark:border-white/10 select-none",
        size === "sm" ? "h-8" : "h-10",
        className
      )}
    >
      {options.map((opt) => {
        const isSelected = opt.value === value;
        return (
          <button
            key={opt.value}
            role="tab"
            aria-selected={isSelected}
            tabIndex={isSelected ? 0 : -1}
            onClick={() => onChange(opt.value)}
            className={cn(
              "relative z-10 flex-1 flex items-center justify-center gap-1.5 px-3 rounded-full font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-risk-teal",
              size === "sm" ? "text-scale-12 h-6" : "text-scale-14 h-8",
              isSelected
                ? "text-foreground font-semibold"
                : "text-muted-foreground hover:text-foreground"
            )}
          >
            {opt.icon && <span className="shrink-0">{opt.icon}</span>}
            <span>{opt.label}</span>

            {isSelected && (
              <motion.div
                layoutId={`segment-pill-${name}`}
                transition={{ type: "spring", stiffness: 300, damping: 26 }}
                className="absolute inset-0 z-[-1] rounded-full bg-white/20 dark:bg-white/15 border border-white/25 dark:border-white/20 shadow-sm"
              />
            )}
          </button>
        );
      })}
    </div>
  );
}

