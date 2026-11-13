"use client";

import React, { useEffect, useState } from "react";
import { motion, useSpring, useTransform } from "framer-motion";
import { GlassCard } from "./GlassCard";
import { TrendingUp, TrendingDown, Minus } from "lucide-react";
import { cn } from "@/lib/utils";

export interface StatProps {
  label: string;
  value: number;
  unit?: string;
  decimals?: number;
  delta?: number;
  deltaLabel?: string;
  trend?: "up" | "down" | "neutral";
  invertTrendColor?: boolean;
  elevation?: 1 | 2;
  className?: string;
}

export const Stat: React.FC<StatProps> = ({
  label,
  value,
  unit,
  decimals = 0,
  delta,
  deltaLabel,
  trend,
  invertTrendColor = false,
  elevation = 1,
  className,
}) => {
  const springValue = useSpring(0, { stiffness: 120, damping: 20 });
  const displayValue = useTransform(springValue, (current) =>
    current.toFixed(decimals)
  );

  const [formattedText, setFormattedText] = useState(value.toFixed(decimals));

  useEffect(() => {
    springValue.set(value);
  }, [value, springValue]);

  useEffect(() => {
    return displayValue.on("change", (latest) => {
      setFormattedText(latest);
    });
  }, [displayValue]);

  // Determine trend badge color
  let trendClass = "text-muted-foreground bg-black/5 dark:bg-white/5";
  if (trend === "up") {
    trendClass = invertTrendColor
      ? "text-emerald-600 dark:text-emerald-400 bg-emerald-500/10"
      : "text-red-600 dark:text-red-400 bg-red-500/10";
  } else if (trend === "down") {
    trendClass = invertTrendColor
      ? "text-red-600 dark:text-red-400 bg-red-500/10"
      : "text-emerald-600 dark:text-emerald-400 bg-emerald-500/10";
  }

  return (
    <GlassCard elevation={elevation} radius="md" className={cn("p-4", className)}>
      <div className="flex items-center justify-between">
        <span className="text-scale-12 font-medium text-muted-foreground uppercase tracking-wider">
          {label}
        </span>
        {delta !== undefined && (
          <span
            className={cn(
              "inline-flex items-center gap-1 px-1.5 py-0.5 rounded-full text-[11px] font-semibold tabular-nums",
              trendClass
            )}
          >
            {trend === "up" && <TrendingUp className="w-3 h-3" />}
            {trend === "down" && <TrendingDown className="w-3 h-3" />}
            {trend === "neutral" && <Minus className="w-3 h-3" />}
            <span>
              {delta > 0 ? `+${delta}` : delta}
              {deltaLabel ? ` ${deltaLabel}` : "%"}
            </span>
          </span>
        )}
      </div>

      <div className="mt-2 flex items-baseline gap-1.5">
        <span className="text-scale-40 font-bold tracking-tight text-foreground tabular-nums">
          {formattedText}
        </span>
        {unit && (
          <span className="text-scale-16 font-medium text-muted-foreground">
            {unit}
          </span>
        )}
      </div>
    </GlassCard>
  );
};

