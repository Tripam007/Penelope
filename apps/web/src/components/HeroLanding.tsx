"use client";

import React, { useState } from "react";
import { usePenelopeStore } from "@/lib/store";
import {
  Bell,
  Play,
  ArrowRight,
  Activity,
  UserCheck,
  Lock,
  Sparkles,
} from "lucide-react";
import Link from "next/link";
import FlowingGlassNav, { NavTabItem } from "@/components/FlowingGlassNav";

interface HeroLandingProps {
  onExploreClick: () => void;
  onOpenDemoVideo?: () => void;
}

export default function HeroLanding({ onExploreClick, onOpenDemoVideo }: HeroLandingProps) {
  const {
    currentUser,
    setAuthModalOpen,
    activeNavTab,
    setActiveNavTab,
    setTransparencyModalOpen,
  } = usePenelopeStore();

  const [isDemoPlaying, setIsDemoPlaying] = useState(false);

  return (
    <div className="relative min-h-screen w-full bg-slate-950 text-slate-100 flex flex-col justify-between overflow-hidden select-none">
      {/* =========================================================================
          BACKGROUND: Exact High-Resolution Mountain Dome Image from Reference
      ========================================================================= */}
      <div className="absolute inset-0 z-0 overflow-hidden pointer-events-none">
        {/* Fullscreen background image matching uploaded screenshot */}
        <div
          className="absolute inset-0 bg-cover bg-center bg-no-repeat transition-transform duration-1000 scale-[1.01]"
          style={{ backgroundImage: "url('/hillsafe-hero-bg.jpg')" }}
        />
        {/* Subtle vignette for crisp text contrast */}
        <div className="absolute inset-0 bg-gradient-to-r from-black/60 via-black/30 to-black/50" />
        <div className="absolute inset-0 bg-gradient-to-b from-black/40 via-transparent to-black/70" />
      </div>

      {/* =========================================================================
          TOP NAVIGATION BAR: Hillsafe Brand, Center Capsule Nav, Live Status & Auth
      ========================================================================= */}
      <header className="relative z-20 w-full px-6 py-6 max-w-7xl mx-auto flex items-center justify-between">
        {/* Brand Logo & Name */}
        <div className="flex items-center gap-3">
          {/* Custom Hillsafe Shield Logo */}
          <div className="w-10 h-11 flex items-center justify-center">
            <svg
              className="w-10 h-11 text-teal-400 drop-shadow-[0_0_12px_rgba(45,212,191,0.6)]"
              viewBox="0 0 36 40"
              fill="none"
              xmlns="http://www.w3.org/2000/svg"
            >
              {/* Shield Outline */}
              <path
                d="M18 2 L33 7 V19 C33 28.5 26.5 35 18 38 C9.5 35 3 28.5 3 19 V7 L18 2 Z"
                stroke="currentColor"
                strokeWidth="2.2"
                fill="rgba(45, 212, 191, 0.08)"
              />
              {/* Twin Mountain Peaks */}
              <path
                d="M9 22 L14 14 L19 22"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
              />
              <path
                d="M17 22 L22 16 L27 22"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
              />
              {/* Water Waves at Base */}
              <path
                d="M8 25 Q13 23 18 25 T28 25"
                stroke="currentColor"
                strokeWidth="1.6"
                strokeLinecap="round"
              />
              <path
                d="M10 28 Q14 26.5 18 28 T26 28"
                stroke="currentColor"
                strokeWidth="1.4"
                strokeLinecap="round"
                opacity="0.8"
              />
            </svg>
          </div>

          <div className="flex items-center gap-3">
            <span className="text-xl font-bold tracking-[0.25em] text-white">
              Hillsafe
            </span>
            <span className="text-slate-500 font-light text-lg">|</span>
            <span className="text-[11px] font-mono text-teal-400 tracking-wider hidden sm:inline uppercase">
              PENELOPE
            </span>
          </div>
        </div>

        {/* Center Floating Flowing Glass Capsule Nav */}
        <FlowingGlassNav
          tabs={[
            { id: "home", label: "Home" },
            { id: "about", label: "About", badge: "ML", badgeType: "ai" },
            { id: "features", label: "Features", badge: "AI", badgeType: "ai" },
            { id: "alerts", label: "Live Alerts", badge: "LIVE", badgeType: "live" },
            { id: "contact", label: "Contact" },
          ]}
          activeId={activeNavTab}
          onSelect={(tabId) => {
            setActiveNavTab(tabId);
            if (tabId === "alerts" || tabId === "features") onExploreClick();
            if (tabId === "about") setTransparencyModalOpen(true);
          }}
        />

        {/* Top-Right: Live Status Glass Capsule & Sign In */}
        <div className="flex items-center gap-3">
          {/* Dedicated Admin Portal Link */}
          <Link
            href="/admin"
            className="flex items-center gap-1.5 px-3.5 py-2 rounded-full bg-gradient-to-r from-red-500/20 to-amber-500/20 hover:from-red-500/30 hover:to-amber-500/30 backdrop-blur-2xl border border-amber-500/40 text-xs font-bold text-amber-300 transition shadow-[0_8px_24px_rgba(245,158,11,0.2)]"
          >
            <span className="w-2 h-2 rounded-full bg-amber-400 animate-pulse" />
            <span>Admin Portal</span>
          </Link>

          {/* Live Status Pill with Bell */}
          <button
            onClick={onExploreClick}
            className="flex items-center gap-2 px-4 py-2 rounded-full bg-slate-950/40 hover:bg-slate-900/60 backdrop-blur-2xl border border-white/15 text-xs font-medium text-slate-200 transition shadow-[0_8px_24px_rgba(0,0,0,0.3)]"
          >
            <Bell className="w-3.5 h-3.5 text-slate-300" />
            <span>Live Status</span>
            <span className="w-2 h-2 rounded-full bg-emerald-400 shadow-[0_0_8px_#34d399] animate-pulse ml-0.5" />
          </button>

          {/* User Profile / Firebase Auth Button */}
          {currentUser ? (
            <button
              onClick={() => setAuthModalOpen(true)}
              className="px-4 py-2 rounded-full bg-teal-500/20 hover:bg-teal-500/30 border border-teal-400/40 text-xs font-semibold text-teal-200 flex items-center gap-2 backdrop-blur-xl transition shadow-md"
            >
              <UserCheck className="w-3.5 h-3.5 text-teal-400" />
              <span className="max-w-[100px] truncate">{currentUser.displayName}</span>
              <span className="text-[9px] uppercase font-bold px-1.5 py-0.5 rounded bg-teal-500/30 text-teal-200">
                {currentUser.role}
              </span>
            </button>
          ) : (
            <button
              onClick={() => setAuthModalOpen(true)}
              className="px-4 py-2 rounded-full bg-white/10 hover:bg-white/15 border border-white/20 text-xs font-semibold text-white flex items-center gap-2 backdrop-blur-xl transition shadow-md"
            >
              <Lock className="w-3.5 h-3.5 text-teal-400" />
              <span>Sign In / Phone</span>
            </button>
          )}
        </div>
      </header>

      {/* =========================================================================
          HERO MAIN CONTENT: Headlines, Subtitle & Action Capsule Buttons
      ========================================================================= */}
      <main className="relative z-10 w-full max-w-7xl mx-auto px-6 pt-12 pb-6 flex-1 flex flex-col justify-center">
        <div className="max-w-xl space-y-6">
          {/* Early Warning Capsule Pill */}
          <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-slate-950/40 backdrop-blur-xl border border-white/15 text-xs text-teal-300 font-medium shadow-[0_4px_16px_rgba(0,0,0,0.3)]">
            <Activity className="w-3.5 h-3.5 text-teal-400" />
            <span>Early Warning. Safer Tomorrow.</span>
          </div>

          {/* Giant Display Headline */}
          <h1 className="text-5xl sm:text-6xl md:text-[68px] font-bold tracking-tight leading-[1.08] text-white">
            Detect. Alert.{" "}
            <span className="text-emerald-400 drop-shadow-[0_0_28px_rgba(52,211,153,0.55)]">
              Protect.
            </span>
          </h1>

          {/* Narrative Subtitle */}
          <p className="text-base sm:text-lg text-slate-300 font-normal leading-relaxed max-w-lg">
            An intelligent flood and landslide early warning system for safer communities
            in hilly regions.
          </p>

          {/* Action Capsule Buttons */}
          <div className="flex flex-wrap items-center gap-4 pt-3">
            {/* Explore Project Button */}
            <button
              onClick={onExploreClick}
              className="px-7 py-3.5 rounded-full bg-gradient-to-r from-teal-400/80 via-teal-400 to-cyan-400 text-slate-950 font-bold text-sm shadow-[0_0_35px_rgba(45,212,191,0.55)] hover:shadow-[0_0_45px_rgba(45,212,191,0.7)] hover:scale-[1.02] active:scale-[0.98] transition flex items-center gap-2 group border border-teal-300/40"
            >
              <span>Explore Project</span>
              <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
            </button>

            {/* Watch Demo Button */}
            <button
              onClick={() => {
                if (onOpenDemoVideo) onOpenDemoVideo();
                else setIsDemoPlaying(true);
              }}
              className="px-6 py-3.5 rounded-full bg-white/10 hover:bg-white/15 text-white font-semibold text-sm border border-white/20 backdrop-blur-2xl transition flex items-center gap-3 shadow-[0_8px_24px_rgba(0,0,0,0.3)] hover:border-white/30"
            >
              <div className="w-6 h-6 rounded-full bg-white/20 flex items-center justify-center">
                <Play className="w-3 h-3 text-white fill-white ml-0.5" />
              </div>
              <span>Watch Demo</span>
            </button>
          </div>
        </div>
      </main>

      {/* =========================================================================
          HERO FOOTER: 3-Pillar VisionOS Card (Left) & Telemetry Status Card (Right)
      ========================================================================= */}
      <footer className="relative z-10 w-full max-w-7xl mx-auto px-6 pb-10 pt-4 flex flex-col md:flex-row items-end justify-between gap-6">
        {/* Left: 3-Pillar Frosted Glass Card matching reference */}
        <div className="w-full md:max-w-2xl p-5 rounded-[24px] bg-white/[0.06] backdrop-blur-2xl border border-white/15 shadow-[0_8px_32px_rgba(0,0,0,0.4)]">
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-5 divide-y sm:divide-y-0 sm:divide-x divide-white/10">
            {/* Pillar 1: Flood Detection */}
            <div className="flex flex-col gap-1.5 sm:pr-4 pt-2 sm:pt-0">
              {/* Three wavy lines icon */}
              <div className="w-8 h-8 flex items-center justify-center">
                <svg
                  className="w-7 h-7 text-cyan-400"
                  viewBox="0 0 28 24"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="2.2"
                  strokeLinecap="round"
                >
                  <path d="M2 6 Q7 3 14 6 T26 6" />
                  <path d="M2 12 Q7 9 14 12 T26 12" />
                  <path d="M2 18 Q7 15 14 18 T26 18" />
                </svg>
              </div>
              <h3 className="text-xs font-bold text-white tracking-wide">Flood Detection</h3>
              <p className="text-[11px] text-slate-300 leading-snug">
                Real-time water level monitoring
              </p>
            </div>

            {/* Pillar 2: Landslide Alerts */}
            <div className="flex flex-col gap-1.5 sm:px-4 pt-3 sm:pt-0">
              {/* Twin mountain peaks icon */}
              <div className="w-8 h-8 flex items-center justify-center">
                <svg
                  className="w-7 h-7 text-emerald-400"
                  viewBox="0 0 28 24"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="2.2"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                >
                  <path d="M3 19 L10 7 L17 19 Z" />
                  <path d="M14 19 L19 11 L25 19 Z" />
                </svg>
              </div>
              <h3 className="text-xs font-bold text-white tracking-wide">Landslide Alerts</h3>
              <p className="text-[11px] text-slate-300 leading-snug">
                Predict and prevent landslides
              </p>
            </div>

            {/* Pillar 3: Public Safety */}
            <div className="flex flex-col gap-1.5 sm:pl-4 pt-3 sm:pt-0">
              {/* Community icon */}
              <div className="w-8 h-8 flex items-center justify-center">
                <svg
                  className="w-7 h-7 text-purple-400"
                  viewBox="0 0 28 24"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="2.2"
                  strokeLinecap="round"
                >
                  <circle cx="14" cy="7" r="3" />
                  <circle cx="6" cy="9" r="2.5" />
                  <circle cx="22" cy="9" r="2.5" />
                  <path d="M9 19 C9 15.5 12 14 14 14 C16 14 19 15.5 19 19" />
                  <path d="M2 20 C2 17.5 4 16.5 6 16.5 C7.5 16.5 8.5 17.2 9 18" />
                  <path d="M26 20 C26 17.5 24 16.5 22 16.5 C20.5 16.5 19.5 17.2 19 18" />
                </svg>
              </div>
              <h3 className="text-xs font-bold text-white tracking-wide">Public Safety</h3>
              <p className="text-[11px] text-slate-300 leading-snug">
                Keep communities one step ahead
              </p>
            </div>
          </div>
        </div>

        {/* Right: Telemetry Status Glass Card matching reference */}
        <div className="flex items-center gap-4 self-stretch sm:self-auto justify-between sm:justify-end">
          <div className="p-4 rounded-[20px] bg-white/[0.06] backdrop-blur-2xl border border-white/15 shadow-[0_8px_32px_rgba(0,0,0,0.4)] flex items-center gap-5">
            <div>
              <div className="flex items-center gap-1.5 text-xs font-bold text-white">
                <span className="w-2 h-2 rounded-full bg-emerald-400 shadow-[0_0_8px_#34d399] animate-pulse" />
                <span>System Active</span>
              </div>
              <p className="text-[11px] text-slate-300 mt-0.5">Monitoring the hills...</p>
            </div>

            {/* Glowing Green ECG / Waveform Line */}
            <svg
              className="w-16 h-7 text-emerald-400 drop-shadow-[0_0_8px_rgba(52,211,153,0.7)]"
              viewBox="0 0 64 24"
              fill="none"
              xmlns="http://www.w3.org/2000/svg"
            >
              <path
                d="M2 14 H18 L24 4 L32 20 L40 8 L46 16 H62"
                stroke="currentColor"
                strokeWidth="2.2"
                strokeLinecap="round"
                strokeLinejoin="round"
              />
            </svg>
          </div>
        </div>
      </footer>

      {/* Bottom-Left: Mouse Scroll To Explore indicator matching reference */}
      <div
        onClick={onExploreClick}
        className="absolute bottom-3 left-6 z-20 hidden lg:flex items-center gap-2.5 text-slate-400 hover:text-white transition cursor-pointer"
      >
        <div className="w-4 h-6 rounded-full border border-slate-400/80 flex items-start justify-center p-1">
          <div className="w-1 h-1.5 rounded-full bg-slate-300 animate-bounce" />
        </div>
        <span className="text-[11px] tracking-wide text-slate-300 font-medium">
          Scroll to explore
        </span>
      </div>

      {/* Interactive Demo Walkthrough Modal */}
      {isDemoPlaying && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-lg animate-in fade-in duration-200">
          <div className="relative w-full max-w-2xl glass-surface-3 rounded-3xl p-6 border border-white/20 shadow-2xl">
            <div className="flex items-center justify-between pb-4 border-b border-white/10 mb-4">
              <div className="flex items-center gap-2">
                <Sparkles className="w-5 h-5 text-teal-400" />
                <h3 className="text-base font-bold text-white">
                  PENELOPE / HillSafe Live Walkthrough
                </h3>
              </div>
              <button
                onClick={() => setIsDemoPlaying(false)}
                className="px-3 py-1 rounded-xl bg-white/10 text-xs font-semibold text-slate-300 hover:text-white"
              >
                Close
              </button>
            </div>

            <div className="space-y-4 text-xs text-slate-300 leading-relaxed">
              <div className="p-4 rounded-2xl bg-black/40 border border-white/10 space-y-2">
                <p className="font-semibold text-teal-300">
                  🏔️ Real-Time Mountain Catchment Ingestion:
                </p>
                <p>
                  1. <strong>Open-Meteo Weather API:</strong> Hourly precipitation, surface pressure, and 4-depth soil moisture.
                </p>
                <p>
                  2. <strong>GloFAS Flood API:</strong> River discharge anomaly percentiles and forecast volumes.
                </p>
                <p>
                  3. <strong>IoT River Gauges:</strong> Telemetry rise rates with simulated badges (`[SIM]`).
                </p>
                <p>
                  4. <strong>LightGBM & LSTM ML Models:</strong> 1h, 3h, 6h, and 24h risk probabilities.
                </p>
              </div>

              <div className="flex justify-end gap-3 pt-2">
                <button
                  onClick={() => {
                    setIsDemoPlaying(false);
                    onExploreClick();
                  }}
                  className="px-5 py-2.5 rounded-xl bg-gradient-to-r from-teal-400 to-cyan-400 text-slate-950 font-bold flex items-center gap-2 shadow-lg shadow-teal-500/25"
                >
                  <span>Launch Live Map</span>
                  <ArrowRight className="w-4 h-4" />
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
