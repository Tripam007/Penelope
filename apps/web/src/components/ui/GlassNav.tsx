"use client";

import React from "react";
import { motion } from "framer-motion";
import { Moon, Sun, Waves, Shield, Activity, Search, Globe } from "lucide-react";
import { cn } from "@/lib/utils";

export interface NavItem {
  id: string;
  label: string;
  icon?: React.ReactNode;
  badge?: React.ReactNode;
}

export interface GlassNavProps {
  items: NavItem[];
  activeId: string;
  onSelect: (id: string) => void;
  isDarkMode?: boolean;
  onToggleTheme?: () => void;
  onOpenSearch?: () => void;
  className?: string;
}

export const GlassNav: React.FC<GlassNavProps> = ({
  items,
  activeId,
  onSelect,
  isDarkMode = true,
  onToggleTheme,
  onOpenSearch,
  className,
}) => {
  return (
    <nav
      role="navigation"
      aria-label="Main Navigation"
      className={cn(
        "flex items-center gap-1.5 p-1.5 rounded-full glass-surface-3 glass-sheen border border-white/20 dark:border-white/15 shadow-glass-3 select-none",
        className
      )}
    >
      {/* Brand Icon */}
      <div className="flex items-center gap-2 pl-2 pr-1">
        <div className="h-7 w-7 rounded-full bg-gradient-to-tr from-teal-400 to-sky-500 flex items-center justify-center text-slate-950 font-black text-xs shadow-sm">
          P
        </div>
        <span className="hidden sm:inline font-bold text-scale-14 text-foreground tracking-tight">
          PENELOPE
        </span>
      </div>

      {/* Nav Items */}
      <div className="flex items-center gap-1">
        {items.map((item) => {
          const isActive = item.id === activeId;
          return (
            <button
              key={item.id}
              onClick={() => onSelect(item.id)}
              className={cn(
                "relative z-10 flex items-center gap-1.5 px-3 py-1.5 rounded-full text-scale-12 font-medium transition-colors focus-visible:ring-2 focus-visible:ring-risk-teal",
                isActive
                  ? "text-foreground font-semibold"
                  : "text-muted-foreground hover:text-foreground"
              )}
            >
              {item.icon}
              <span>{item.label}</span>
              {item.badge}

              {isActive && (
                <motion.div
                  layoutId="glass-nav-pill"
                  transition={{ type: "spring", stiffness: 300, damping: 26 }}
                  className="absolute inset-0 z-[-1] rounded-full bg-white/25 dark:bg-white/15 border border-white/30 dark:border-white/20 shadow-sm"
                />
              )}
            </button>
          );
        })}
      </div>

      {/* Search Shortcut */}
      {onOpenSearch && (
        <button
          onClick={onOpenSearch}
          className="p-1.5 rounded-full hover:bg-black/5 dark:hover:bg-white/10 text-muted-foreground hover:text-foreground transition flex items-center gap-1.5 px-2.5 text-scale-12"
          title="Search (Cmd+K)"
          aria-label="Open command palette"
        >
          <Search className="w-3.5 h-3.5" />
          <span className="hidden md:inline text-[11px] font-mono text-muted-foreground">⌘K</span>
        </button>
      )}

      {/* Theme Toggle */}
      {onToggleTheme && (
        <button
          onClick={onToggleTheme}
          className="p-2 rounded-full hover:bg-black/5 dark:hover:bg-white/10 text-muted-foreground hover:text-foreground transition focus-visible:ring-2 focus-visible:ring-risk-teal"
          aria-label={isDarkMode ? "Switch to light mode" : "Switch to dark mode"}
        >
          {isDarkMode ? <Sun className="w-4 h-4 text-amber-400" /> : <Moon className="w-4 h-4 text-sky-600" />}
        </button>
      )}
    </nav>
  );
};

