"use client";

import React from "react";
import { usePenelopeStore } from "@/lib/store";
import { Shield, Waves, Activity, AlertTriangle, Radio, Globe, Palette, User, UserCheck } from "lucide-react";
import Link from "next/link";

export default function HeaderNav() {
  const {
    language,
    setLanguage,
    currentUser,
    setAuthModalOpen,
    setAuthorityModalOpen,
    setTransparencyModalOpen,
    setSensorPanelOpen,
    isSensorPanelOpen
  } = usePenelopeStore();

  return (
    <header className="h-16 px-4 apple-glass-panel border-b border-white/10 flex items-center justify-between z-20 sticky top-0">
      {/* Brand & Pillars */}
      <div className="flex items-center gap-3">
        <div className="h-10 w-10 rounded-xl bg-gradient-to-tr from-sky-600 to-cyan-400 p-0.5 flex items-center justify-center shadow-lg shadow-sky-500/20">
          <div className="w-full h-full bg-slate-950/80 backdrop-blur rounded-[10px] flex items-center justify-center">
            <span className="text-xl font-black bg-gradient-to-r from-sky-400 to-cyan-200 bg-clip-text text-transparent">
              P
            </span>
          </div>
        </div>
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-lg font-black tracking-wider text-white">PENELOPE</h1>
            <span className="hidden md:inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-semibold bg-sky-500/15 text-sky-400 border border-sky-500/30">
              <span className="w-1.5 h-1.5 rounded-full bg-sky-400 animate-pulse"></span>
              Live Telemetry
            </span>
          </div>
          <p className="text-[11px] text-slate-400 font-medium">
            <span className="text-sky-400">Data today. Safer tomorrows.</span>
            <span className="hidden sm:inline text-slate-600 mx-1.5">•</span>
            <span className="hidden sm:inline text-slate-500">Predict · Prepare · Protect</span>
          </p>
        </div>
      </div>

      {/* Action Buttons */}
      <div className="flex items-center gap-2">
        <button
          onClick={() => setSensorPanelOpen(!isSensorPanelOpen)}
          className={`px-3 py-1.5 rounded-xl text-xs font-semibold flex items-center gap-1.5 transition ${
            isSensorPanelOpen
              ? "bg-cyan-500 text-slate-950 shadow-md shadow-cyan-500/25"
              : "apple-glass-card hover:bg-white/10 text-slate-300"
          }`}
        >
          <Waves className="w-3.5 h-3.5" />
          <span className="hidden sm:inline">River Gauges</span>
        </button>

        <button
          onClick={() => setAuthorityModalOpen(true)}
          className="px-3 py-1.5 rounded-xl text-xs font-semibold apple-glass-card hover:bg-white/10 text-slate-300 flex items-center gap-1.5 transition"
        >
          <Shield className="w-3.5 h-3.5 text-amber-400" />
          <span className="hidden sm:inline">Authority Command</span>
        </button>

        <button
          onClick={() => setTransparencyModalOpen(true)}
          className="px-3 py-1.5 rounded-xl text-xs font-semibold apple-glass-card hover:bg-white/10 text-slate-300 flex items-center gap-1.5 transition"
        >
          <Activity className="w-3.5 h-3.5 text-purple-400" />
          <span className="hidden md:inline">AI Metrics & Honor</span>
        </button>

        <Link
          href="/design"
          className="px-3 py-1.5 rounded-xl text-xs font-semibold apple-glass-card hover:bg-white/10 text-slate-300 flex items-center gap-1.5 transition"
        >
          <Palette className="w-3.5 h-3.5 text-teal-400" />
          <span className="hidden lg:inline">Design System</span>
        </Link>

        {/* Dedicated Admin Portal Link for Tripam Biswas / Admin */}
        <Link
          href="/admin"
          className="px-3 py-1.5 rounded-lg text-xs font-bold bg-gradient-to-r from-red-500/20 via-amber-500/20 to-teal-500/20 hover:from-red-500/30 hover:to-teal-500/30 text-amber-300 border border-amber-500/40 flex items-center gap-1.5 transition shadow-sm"
        >
          <Shield className="w-3.5 h-3.5 text-amber-400" />
          <span>Admin Portal</span>
        </Link>

        {/* Firebase Authentication Button */}
        {currentUser ? (
          <button
            onClick={() => setAuthModalOpen(true)}
            className="px-3 py-1.5 rounded-lg text-xs font-semibold bg-teal-500/10 hover:bg-teal-500/20 text-teal-300 border border-teal-500/30 flex items-center gap-1.5 transition"
          >
            <UserCheck className="w-3.5 h-3.5 text-teal-400" />
            <span className="max-w-[80px] sm:max-w-[120px] truncate">{currentUser.displayName}</span>
            <span className="hidden sm:inline text-[9px] uppercase font-bold px-1.5 py-0.2 rounded bg-teal-500/20 text-teal-300">
              {currentUser.role}
            </span>
          </button>
        ) : (
          <button
            onClick={() => setAuthModalOpen(true)}
            className="px-3 py-1.5 rounded-lg text-xs font-semibold bg-gradient-to-r from-teal-500/20 to-cyan-500/20 hover:from-teal-500/30 hover:to-cyan-500/30 text-teal-200 border border-teal-400/40 flex items-center gap-1.5 transition"
          >
            <User className="w-3.5 h-3.5 text-teal-400" />
            <span className="hidden sm:inline">Sign In</span>
          </button>
        )}

        {/* Language Switcher */}
        <div className="flex items-center p-0.5 rounded-lg bg-slate-900 border border-slate-800 text-xs">
          <button
            onClick={() => setLanguage("en")}
            className={`px-2 py-1 rounded text-[11px] font-bold transition ${
              language === "en" ? "bg-sky-500 text-white" : "text-slate-400 hover:text-white"
            }`}
          >
            EN
          </button>
          <button
            onClick={() => setLanguage("hi")}
            className={`px-2 py-1 rounded text-[11px] font-bold transition ${
              language === "hi" ? "bg-sky-500 text-white" : "text-slate-400 hover:text-white"
            }`}
          >
            हिं
          </button>
        </div>
      </div>
    </header>
  );
}

