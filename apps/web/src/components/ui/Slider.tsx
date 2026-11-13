"use client";

import React from "react";
import { cn } from "@/lib/utils";

export interface SliderProps {
  value: number;
  min?: number;
  max?: number;
  step?: number;
  onChange: (value: number) => void;
  labels?: { value: number; label: string }[];
  className?: string;
}

export const Slider: React.FC<SliderProps> = ({
  value,
  min = 1,
  max = 24,
  step = 1,
  onChange,
  labels,
  className,
}) => {
  const percentage = Math.min(100, Math.max(0, ((value - min) / (max - min)) * 100));

  return (
    <div className={cn("w-full space-y-2 select-none", className)}>
      <div className="relative flex items-center h-6">
        {/* Track Background */}
        <div className="w-full h-2 rounded-full glass-surface-1 border border-black/10 dark:border-white/10 relative overflow-hidden">
          {/* Active Fill */}
          <div
            className="h-full bg-gradient-to-r from-risk-teal to-sky-500 rounded-full transition-all"
            style={{ width: `${percentage}%` }}
          />
        </div>

        {/* Real Native Range Input overlay */}
        <input
          type="range"
          min={min}
          max={max}
          step={step}
          value={value}
          onChange={(e) => onChange(parseFloat(e.target.value))}
          className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
          aria-label="Time horizon slider"
        />

        {/* Visual Glass Thumb */}
        <div
          className="pointer-events-none absolute h-5 w-5 rounded-full bg-white dark:bg-slate-100 shadow-glass-1 border border-black/20 dark:border-white/40 -translate-x-1/2 flex items-center justify-center transition-all"
          style={{ left: `${percentage}%` }}
        >
          <div className="w-2 h-2 rounded-full bg-risk-teal" />
        </div>
      </div>

      {/* Step Notches & Labels */}
      {labels && labels.length > 0 && (
        <div className="flex justify-between items-center text-[11px] text-muted-foreground font-mono">
          {labels.map((item) => (
            <span
              key={item.value}
              onClick={() => onChange(item.value)}
              className={cn(
                "cursor-pointer hover:text-foreground transition",
                value === item.value && "font-bold text-foreground"
              )}
            >
              {item.label}
            </span>
          ))}
        </div>
      )}
    </div>
  );
};

