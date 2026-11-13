"use client";

import React from "react";
import { motion } from "framer-motion";
import { cn } from "@/lib/utils";

export interface SwitchProps {
  checked: boolean;
  onChange: (checked: boolean) => void;
  disabled?: boolean;
  label?: string;
  className?: string;
}

export const Switch: React.FC<SwitchProps> = ({
  checked,
  onChange,
  disabled = false,
  label,
  className,
}) => {
  return (
    <label
      className={cn(
        "inline-flex items-center gap-2.5 cursor-pointer select-none",
        disabled && "opacity-50 cursor-not-allowed",
        className
      )}
    >
      <button
        type="button"
        role="switch"
        aria-checked={checked}
        disabled={disabled}
        onClick={() => !disabled && onChange(!checked)}
        className={cn(
          "relative inline-flex h-6 w-11 shrink-0 rounded-full border border-black/10 dark:border-white/15 transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-risk-teal",
          checked
            ? "bg-risk-teal"
            : "bg-black/10 dark:bg-white/10"
        )}
      >
        <motion.span
          layout
          transition={{ type: "spring", stiffness: 450, damping: 28 }}
          className={cn(
            "pointer-events-none block h-5 w-5 rounded-full bg-white shadow-md border border-black/10",
            checked ? "translate-x-5" : "translate-x-0.5"
          )}
          style={{ top: "1px" }}
        />
      </button>

      {label && (
        <span className="text-scale-14 font-medium text-foreground">{label}</span>
      )}
    </label>
  );
};

