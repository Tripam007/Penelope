"use client";

import React, { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { GlassCard } from "./GlassCard";
import { ChevronDown, ChevronUp } from "lucide-react";
import { cn } from "@/lib/utils";

export interface GlassPanelProps {
  title: string;
  subtitle?: string;
  badge?: React.ReactNode;
  collapsible?: boolean;
  defaultCollapsed?: boolean;
  className?: string;
  headerAction?: React.ReactNode;
  children: React.ReactNode;
}

export const GlassPanel: React.FC<GlassPanelProps> = ({
  title,
  subtitle,
  badge,
  collapsible = false,
  defaultCollapsed = false,
  className,
  headerAction,
  children,
}) => {
  const [collapsed, setCollapsed] = useState(defaultCollapsed);

  return (
    <GlassCard
      elevation={2}
      radius="md"
      className={cn("w-full border border-white/10 dark:border-white/15", className)}
    >
      <div
        className={cn(
          "flex items-center justify-between px-4 py-3 border-b border-black/5 dark:border-white/10",
          collapsible && "cursor-pointer select-none"
        )}
        onClick={() => collapsible && setCollapsed(!collapsed)}
      >
        <div className="flex items-center gap-2">
          <div>
            <div className="flex items-center gap-2">
              <h3 className="text-scale-14 font-semibold text-foreground tracking-tight">
                {title}
              </h3>
              {badge}
            </div>
            {subtitle && (
              <p className="text-scale-12 text-muted-foreground mt-0.5">{subtitle}</p>
            )}
          </div>
        </div>

        <div className="flex items-center gap-2">
          {headerAction && (
            <div onClick={(e) => e.stopPropagation()}>{headerAction}</div>
          )}
          {collapsible && (
            <button
              type="button"
              className="p-1 rounded-lg hover:bg-black/5 dark:hover:bg-white/10 text-muted-foreground transition"
              aria-label={collapsed ? "Expand panel" : "Collapse panel"}
            >
              {collapsed ? (
                <ChevronDown className="w-4 h-4" />
              ) : (
                <ChevronUp className="w-4 h-4" />
              )}
            </button>
          )}
        </div>
      </div>

      <AnimatePresence initial={false}>
        {!collapsed && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: "auto", opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ type: "spring", stiffness: 260, damping: 24 }}
            className="p-4 overflow-hidden"
          >
            {children}
          </motion.div>
        )}
      </AnimatePresence>
    </GlassCard>
  );
};

