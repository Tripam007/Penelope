"use client";

import React from "react";
import { ShieldCheck, AlertCircle, AlertTriangle, AlertOctagon, Radio } from "lucide-react";
import { cn } from "@/lib/utils";

export type RiskLevel = "Low" | "Moderate" | "High" | "Very High";

export interface RiskChipProps {
  level: RiskLevel;
  score?: number;
  showIcon?: boolean;
  showPattern?: boolean;
  size?: "sm" | "md" | "lg";
  className?: string;
}

export const RiskChip: React.FC<RiskChipProps> = ({
  level,
  score,
  showIcon = true,
  showPattern = true,
  size = "md",
  className,
}) => {
  const normalized = level?.toLowerCase();

  let config = {
    label: "Low Risk",
    color: "#34C759",
    bgClass: "bg-emerald-500/15 dark:bg-emerald-500/20 text-emerald-700 dark:text-emerald-300 border-emerald-500/40",
    icon: ShieldCheck,
    pattern: "•",
  };

  if (normalized === "moderate") {
    config = {
      label: "Moderate",
      color: "#FFD60A",
      bgClass: "bg-yellow-500/15 dark:bg-yellow-400/20 text-yellow-800 dark:text-yellow-200 border-yellow-500/40",
      icon: AlertCircle,
      pattern: "••",
    };
  } else if (normalized === "high") {
    config = {
      label: "High Risk",
      color: "#FF9F0A",
      bgClass: "bg-orange-500/15 dark:bg-orange-500/20 text-orange-800 dark:text-orange-200 border-orange-500/50",
      icon: AlertTriangle,
      pattern: "▲",
    };
  } else if (normalized === "very high" || normalized === "veryhigh") {
    config = {
      label: "Very High",
      color: "#FF453A",
      bgClass: "bg-red-500/15 dark:bg-red-500/25 text-red-800 dark:text-red-200 border-red-500/60 animate-pulse",
      icon: AlertOctagon,
      pattern: "▲▲",
    };
  }

  const IconComponent = config.icon;

  const sizeClasses = {
    sm: "text-[11px] px-2 py-0.5 gap-1",
    md: "text-scale-12 px-2.5 py-1 gap-1.5",
    lg: "text-scale-14 px-3.5 py-1.5 gap-2",
  };

  return (
    <span
      className={cn(
        "inline-flex items-center font-bold rounded-full border shadow-sm backdrop-blur-md select-none",
        config.bgClass,
        sizeClasses[size],
        className
      )}
      role="status"
      aria-label={`${config.label} ${score !== undefined ? `${Math.round(score * 100)} percent` : ""}`}
    >
      {showIcon && <IconComponent className="w-3.5 h-3.5 shrink-0" aria-hidden="true" />}
      <span>{config.label}</span>
      {score !== undefined && (
        <span className="font-mono tabular-nums opacity-90 text-[11px]">
          ({Math.round(score * 100)}%)
        </span>
      )}
      {showPattern && (
        <span className="text-[10px] font-mono tracking-tighter opacity-70" aria-hidden="true">
          [{config.pattern}]
        </span>
      )}
    </span>
  );
};

export interface SimBadgeProps {
  size?: "sm" | "md";
  className?: string;
}

export const SimBadge: React.FC<SimBadgeProps> = ({ size = "md", className }) => {
  return (
    <span
      className={cn(
        "inline-flex items-center gap-1 font-black rounded-md uppercase tracking-wider bg-amber-500 text-slate-950 border border-amber-300 shadow-sm select-none",
        size === "sm" ? "text-[9px] px-1 py-0.2" : "text-[10px] px-1.5 py-0.5",
        className
      )}
      title="Simulated sensor reading. Never presented as live hardware."
      role="note"
      aria-label="Simulated sensor value"
    >
      <Radio className="w-2.5 h-2.5" />
      SIM
    </span>
  );
};

