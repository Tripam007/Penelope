"use client";

import React, { useState } from "react";
import { motion } from "framer-motion";

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
  isHighlighted,
}: {
  label: string;
  isHighlighted: boolean;
}) {
  const letters = Array.from(label);

  return (
    <span className="relative inline-flex overflow-hidden h-[20px] items-center pointer-events-none">
      {/* Primary baseline letters (white/slate) */}
      <span className="flex">
        {letters.map((char, i) => (
          <motion.span
            key={i}
            initial={false}
            animate={{
              y: isHighlighted ? "-110%" : "0%",
              opacity: isHighlighted ? 0 : 1,
            }}
            transition={{
              duration: 0.28,
              ease: [0.33, 1, 0.68, 1],
              delay: i * 0.012,
            }}
            className={`inline-block select-none ${
              char === " " ? "w-1" : ""
            } text-slate-300 font-medium tracking-wide`}
          >
            {char === " " ? "\u00A0" : char}
          </motion.span>
        ))}
      </span>

      {/* Rolling highlight letters (flip in from bottom with amber/gold glow) */}
      <span className="flex absolute top-full left-0">
        {letters.map((char, i) => (
          <motion.span
            key={i}
            initial={false}
            animate={{
              y: isHighlighted ? "-100%" : "0%",
              opacity: isHighlighted ? 1 : 0,
            }}
            transition={{
              duration: 0.28,
              ease: [0.33, 1, 0.68, 1],
              delay: i * 0.012,
            }}
            className={`inline-block select-none font-semibold ${
              char === " " ? "w-1" : ""
            } text-amber-300 drop-shadow-[0_0_12px_rgba(251,191,36,0.65)] tracking-wide`}
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

  // The glass box pill is always shown: follows hoveredId if hovering, otherwise follows activeId
  const activeOrHoveredId = hoveredId || activeId;

  return (
    <nav
      onMouseLeave={() => setHoveredId(null)}
      className={`relative hidden md:flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-slate-950/70 backdrop-blur-2xl border border-white/10 shadow-[0_12px_40px_rgba(0,0,0,0.65)] text-xs font-medium ${className}`}
    >
      {tabs.map((tab) => {
        const isCurrentPill = activeOrHoveredId === tab.id;
        const isActive = activeId === tab.id;

        return (
          <button
            key={tab.id}
            onMouseEnter={() => setHoveredId(tab.id)}
            onClick={() => onSelect(tab.id)}
            className="relative px-4 py-2 rounded-full flex items-center justify-center transition-colors duration-200 focus:outline-none"
          >
            {/* 1. Fluid Flowing Glass Box Pill (smooth spring glide) */}
            {isCurrentPill && (
              <motion.div
                layoutId="flowing-glass-pill"
                transition={{
                  type: "spring",
                  stiffness: 420,
                  damping: 32,
                }}
                className="absolute inset-0 rounded-full z-0 bg-gradient-to-b from-white/[0.12] via-white/[0.05] to-transparent backdrop-blur-xl border border-white/15 shadow-[0_4px_24px_rgba(245,158,11,0.22),inset_0_1px_1px_rgba(255,255,255,0.3)]"
              >
                {/* Glowing bottom golden-amber neon streak (matches ok.mp4 / Reellipse) */}
                <span className="absolute bottom-0 left-2.5 right-2.5 h-[2px] rounded-full bg-gradient-to-r from-transparent via-amber-400 to-transparent shadow-[0_0_14px_#fbbf24,0_0_20px_rgba(245,158,11,0.7)]" />
                {/* Subtle glassy top specular reflection */}
                <span className="absolute top-0 left-3 right-3 h-[1px] bg-gradient-to-r from-transparent via-white/35 to-transparent" />
              </motion.div>
            )}

            {/* 2. Rolling Flip Text Animation */}
            <span className="relative z-10 flex items-center gap-1.5">
              <RollingLetterLabel
                label={tab.label}
                isHighlighted={isCurrentPill}
              />
            </span>

            {/* 3. Micro Badges (AI / LIVE / FREE) exactly matching video */}
            {tab.badge && (
              <span
                className={`absolute -top-1.5 -right-1 z-20 text-[9px] font-black px-1.5 py-0.2 rounded-full pointer-events-none transition-transform duration-200 shadow-sm ${
                  isCurrentPill ? "scale-110" : "scale-100"
                } ${
                  tab.badgeType === "live"
                    ? "bg-red-500 text-white shadow-[0_0_8px_rgba(239,68,68,0.6)] flex items-center gap-1"
                    : tab.badgeType === "ai"
                    ? "bg-amber-400 text-slate-950 shadow-[0_0_8px_rgba(245,158,11,0.6)]"
                    : "bg-amber-400 text-slate-950 shadow-[0_0_8px_rgba(245,158,11,0.6)]"
                }`}
              >
                {tab.badgeType === "live" && (
                  <span className="w-1.5 h-1.5 rounded-full bg-white animate-pulse" />
                )}
                {tab.badge}
              </span>
            )}
          </button>
        );
      })}
    </nav>
  );
}
