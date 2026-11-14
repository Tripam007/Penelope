"use client";

import React, { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";

export interface NavTabItem {
  id: string;
  label: string;
  badge?: string;
  badgeType?: "ai" | "live" | "free";
}

interface FlowingGlassNavProps {
  tabs: NavTabItem[];
  activeId: string;
  onSelect: (id: string) => void;
  className?: string;
}

function RollingLetterLabel({
  label,
  isHovered,
  isActive,
}: {
  label: string;
  isHovered: boolean;
  isActive: boolean;
}) {
  const letters = Array.from(label);
  const activeOrHovered = isHovered || isActive;

  return (
    <span className="relative inline-flex overflow-hidden h-[18px] items-center pointer-events-none">
      {/* Primary baseline letters */}
      <span className="flex">
        {letters.map((char, i) => (
          <motion.span
            key={i}
            initial={false}
            animate={{
              y: activeOrHovered ? "-100%" : "0%",
              opacity: activeOrHovered ? 0 : 1,
            }}
            transition={{
              duration: 0.26,
              ease: [0.33, 1, 0.68, 1],
              delay: i * 0.012,
            }}
            className={`inline-block select-none ${
              char === " " ? "w-1" : ""
            } ${
              isActive
                ? "text-white font-semibold"
                : "text-slate-300 font-medium"
            }`}
          >
            {char === " " ? "\u00A0" : char}
          </motion.span>
        ))}
      </span>

      {/* Rolling highlight letters (flip from bottom) */}
      <span className="flex absolute top-full left-0">
        {letters.map((char, i) => (
          <motion.span
            key={i}
            initial={false}
            animate={{
              y: activeOrHovered ? "-100%" : "0%",
              opacity: activeOrHovered ? 1 : 0,
            }}
            transition={{
              duration: 0.26,
              ease: [0.33, 1, 0.68, 1],
              delay: i * 0.012,
            }}
            className={`inline-block select-none font-semibold ${
              char === " " ? "w-1" : ""
            } text-amber-200 drop-shadow-[0_0_10px_rgba(251,191,36,0.55)]`}
          >
            {char === " " ? "\u00A0" : char}
          </motion.span>
        ))}
      </span>
    </span>
  );
}

export default function FlowingGlassNav({
  tabs,
  activeId,
  onSelect,
  className = "",
}: FlowingGlassNavProps) {
  const [hoveredId, setHoveredId] = useState<string | null>(null);

  return (
    <nav
      onMouseLeave={() => setHoveredId(null)}
      className={`relative hidden md:flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-slate-950/60 backdrop-blur-2xl border border-white/15 shadow-[0_12px_40px_rgba(0,0,0,0.6)] text-xs font-medium ${className}`}
    >
      {tabs.map((tab) => {
        const isActive = activeId === tab.id;
        const isHovered = hoveredId === tab.id;

        return (
          <button
            key={tab.id}
            onMouseEnter={() => setHoveredId(tab.id)}
            onClick={() => onSelect(tab.id)}
            className="relative px-4 py-2 rounded-full flex items-center justify-center transition-colors duration-200 focus:outline-none"
          >
            {/* 1. Flowing Glass Box Pill (with spring glide animation) */}
            {hoveredId === tab.id && (
              <motion.div
                layoutId="flowing-glass-pill"
                transition={{
                  type: "spring",
                  stiffness: 420,
                  damping: 32,
                }}
                className="absolute inset-0 rounded-full z-0 bg-gradient-to-b from-white/[0.14] via-white/[0.06] to-white/[0.02] backdrop-blur-xl border border-amber-400/40 shadow-[0_0_22px_rgba(245,158,11,0.28),inset_0_1px_2px_rgba(255,255,255,0.35)]"
              >
                {/* Glowing bottom amber/golden neon streak */}
                <span className="absolute bottom-0 left-2.5 right-2.5 h-[2px] rounded-full bg-gradient-to-r from-transparent via-amber-400 to-transparent shadow-[0_0_12px_#fbbf24]" />
                {/* Top edge glassy reflection */}
                <span className="absolute top-0 left-3 right-3 h-[1px] bg-gradient-to-r from-transparent via-white/40 to-transparent" />
              </motion.div>
            )}

            {/* 2. Rolling Flip Text */}
            <span className="relative z-10 flex items-center gap-1.5">
              <RollingLetterLabel
                label={tab.label}
                isHovered={isHovered}
                isActive={isActive}
              />
            </span>

            {/* 3. Micro Badges (AI / Live / Free) */}
            {tab.badge && (
              <span
                className={`absolute -top-2 -right-1 z-20 text-[9px] font-black px-1.5 py-0.2 rounded-full border shadow-sm pointer-events-none transition-transform duration-200 ${
                  isHovered ? "scale-110" : "scale-100"
                } ${
                  tab.badgeType === "live"
                    ? "bg-red-500/25 text-red-300 border-red-500/40 shadow-[0_0_8px_rgba(239,68,68,0.4)] flex items-center gap-0.5"
                    : tab.badgeType === "ai"
                    ? "bg-amber-500/25 text-amber-300 border-amber-400/40 shadow-[0_0_8px_rgba(245,158,11,0.35)]"
                    : "bg-emerald-500/25 text-emerald-300 border-emerald-400/40 shadow-[0_0_8px_rgba(52,211,153,0.35)]"
                }`}
              >
                {tab.badgeType === "live" && (
                  <span className="w-1.5 h-1.5 rounded-full bg-red-400 animate-pulse" />
                )}
                {tab.badge}
              </span>
            )}

            {/* 4. Active Cyan Glow Dot Underneath (from user's original bar) */}
            {isActive && (
              <motion.span
                layoutId="active-cyan-dot"
                transition={{
                  type: "spring",
                  stiffness: 400,
                  damping: 30,
                }}
                className="absolute -bottom-1.5 left-1/2 -translate-x-1/2 w-1.5 h-1.5 rounded-full bg-teal-400 shadow-[0_0_10px_#2dd4bf,0_0_4px_#38bdf8]"
              />
            )}
          </button>
        );
      })}
    </nav>
  );
}
