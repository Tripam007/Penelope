import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function getRiskColorClass(level: string): { bg: string; text: string; border: string; hex: string } {
  switch (level?.toLowerCase()) {
    case "very high":
    case "veryhigh":
      return { bg: "bg-red-500/15", text: "text-red-400", border: "border-red-500/50", hex: "#ef4444" };
    case "high":
      return { bg: "bg-orange-500/15", text: "text-orange-400", border: "border-orange-500/50", hex: "#f97316" };
    case "moderate":
      return { bg: "bg-amber-500/15", text: "text-amber-400", border: "border-amber-500/50", hex: "#f59e0b" };
    case "low":
    default:
      return { bg: "bg-emerald-500/15", text: "text-emerald-400", border: "border-emerald-500/50", hex: "#10b981" };
  }
}

