"use client";

import React, { useState } from "react";
import Link from "next/link";
import {
  GlassCard,
  GlassPanel,
  GlassNav,
  SegmentedControl,
  RiskChip,
  SimBadge,
  Stat,
  Sheet,
  CommandPalette,
  Toast,
  Skeleton,
  Tooltip,
  Switch,
  Slider,
} from "@/components/ui";
import {
  ArrowLeft,
  Sun,
  Moon,
  Shield,
  Waves,
  Activity,
  Search,
  Sparkles,
  Zap,
  Info,
  BellRing,
  Layers,
} from "lucide-react";

export default function DesignSystemPage() {
  const [isDarkMode, setIsDarkMode] = useState(true);
  const [riskAtmosphere, setRiskAtmosphere] = useState<"low" | "high" | "veryhigh">("low");
  const [navTab, setNavTab] = useState("primitives");
  const [timeHorizon, setTimeHorizon] = useState(3);
  const [switchActive, setSwitchActive] = useState(true);
  const [isSheetOpen, setIsSheetOpen] = useState(false);
  const [isCommandOpen, setIsCommandOpen] = useState(false);
  const [toasts, setToasts] = useState<
    Array<{ id: string; title: string; message: string; type: "warning" | "success" | "info" | "danger" }>
  >([]);

  const addToast = (type: "warning" | "success" | "info" | "danger") => {
    const id = Math.random().toString();
    const newToast = {
      id,
      type,
      title:
        type === "danger"
          ? "Critical Flash-Flood Surge"
          : type === "warning"
          ? "Precipitation Threshold Exceeded"
          : type === "success"
          ? "Sensor Recalibrated"
          : "Telemetry Synchronized",
      message:
        type === "danger"
          ? "River stage rising at 0.85m/h in Upper Mandakini catchment."
          : "Antecedent saturation index updated to 88% capacity.",
    };
    setToasts((prev) => [...prev, newToast]);
  };

  const removeToast = (id: string) => {
    setToasts((prev) => prev.filter((t) => t.id !== id));
  };

  const atmosphereClass =
    riskAtmosphere === "veryhigh"
      ? "mesh-risk-veryhigh"
      : riskAtmosphere === "high"
      ? "mesh-risk-high"
      : "mesh-risk-low";

  return (
    <div className={isDarkMode ? "dark" : "light"}>
      <div className={`min-h-screen relative text-foreground transition-colors duration-300 ${atmosphereClass}`}>
        {/* Atmosphere: Animated Gradient Mesh Background */}
        <div className="mesh-gradient-container" aria-hidden="true">
          <div className="mesh-orb-1" />
          <div className="mesh-orb-2" />
          <div className="mesh-orb-3" />
        </div>

        {/* Top Header / Sticky Nav */}
        <header className="sticky top-0 z-40 p-4 flex justify-between items-center max-w-7xl mx-auto">
          <div className="flex items-center gap-3">
            <Link
              href="/"
              className="p-2 rounded-full glass-surface-2 hover:glass-surface-3 text-muted-foreground hover:text-foreground transition flex items-center gap-1.5 text-scale-12 font-semibold"
            >
              <ArrowLeft className="w-4 h-4" />
              <span>Back to Live Map</span>
            </Link>

            <span className="hidden sm:inline-block px-2.5 py-1 rounded-full text-scale-12 font-bold bg-risk-teal/15 text-risk-teal border border-risk-teal/30">
              visionOS Design System
            </span>
          </div>

          <div className="flex items-center gap-3">
            <button
              onClick={() => setIsCommandOpen(true)}
              className="px-3 py-1.5 rounded-full glass-surface-2 hover:glass-surface-3 text-scale-12 font-medium flex items-center gap-2 transition"
            >
              <Search className="w-3.5 h-3.5 text-muted-foreground" />
              <span>Command Palette</span>
              <kbd className="text-[10px] px-1.5 py-0.5 rounded bg-black/10 dark:bg-white/10 font-mono">⌘K</kbd>
            </button>

            {/* Dark / Light Toggle */}
            <button
              onClick={() => setIsDarkMode(!isDarkMode)}
              className="p-2 rounded-full glass-surface-2 hover:glass-surface-3 transition"
              aria-label={isDarkMode ? "Switch to light theme" : "Switch to dark theme"}
            >
              {isDarkMode ? <Sun className="w-4 h-4 text-amber-400" /> : <Moon className="w-4 h-4 text-sky-600" />}
            </button>
          </div>
        </header>

        {/* Main Showcase Container */}
        <main className="max-w-7xl mx-auto px-4 py-8 space-y-12">
          {/* Hero Section */}
          <section className="space-y-4">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full glass-surface-1 border border-white/15 text-scale-12 font-medium text-risk-teal">
              <Sparkles className="w-3.5 h-3.5" />
              <span>Apple visionOS & macOS Sequoia Tokens + Primitives</span>
            </div>
            <h1 className="text-scale-64 font-black tracking-tight text-foreground">
              Design System
            </h1>
            <p className="text-scale-20 text-muted-foreground max-w-2xl leading-relaxed">
              Layered translucency, precise typography, spring easing physics, accessible color-blind-safe risk states, and ambient atmospheric backgrounds.
            </p>

            {/* Atmosphere Control Bar */}
            <div className="flex items-center gap-3 pt-2">
              <span className="text-scale-12 font-semibold text-muted-foreground uppercase tracking-wider">
                Atmosphere Mode:
              </span>
              <SegmentedControl
                size="sm"
                value={riskAtmosphere}
                onChange={setRiskAtmosphere}
                options={[
                  { value: "low", label: "Calm Teal (Low)" },
                  { value: "high", label: "Amber (Moderate/High)" },
                  { value: "veryhigh", label: "Crimson (Very High)" },
                ]}
              />
            </div>
          </section>

          {/* Section 1: Glass Surfaces (3 Elevations) */}
          <section className="space-y-4">
            <h2 className="text-scale-28 font-bold tracking-tight text-foreground flex items-center gap-2">
              <Layers className="w-5 h-5 text-risk-teal" />
              Glass Surfaces & Elevations
            </h2>
            <p className="text-scale-14 text-muted-foreground">
              3-tier layered depth with blur(24px - 40px), 1px inner hairline border, top highlight sheen, and high-performance shadow drop. Includes solid fallback for reduced transparency.
            </p>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <GlassCard elevation={1} interactive className="p-6">
                <div className="text-scale-12 font-mono text-muted-foreground uppercase tracking-wider">
                  Elevation 1 • Base Card
                </div>
                <div className="text-scale-20 font-bold text-foreground mt-2">
                  Standard Glass Surface
                </div>
                <p className="text-scale-14 text-muted-foreground mt-1">
                  Subtle translucency (bg 6% dark / 60% light) with blur(24px). Perfect for background cards and list rows.
                </p>
                <div className="mt-4 pt-4 border-t border-black/5 dark:border-white/10 flex justify-between text-[11px] font-mono text-muted-foreground">
                  <span>blur(24px)</span>
                  <span>saturate(160%)</span>
                </div>
              </GlassCard>

              <GlassCard elevation={2} interactive className="p-6">
                <div className="text-scale-12 font-mono text-muted-foreground uppercase tracking-wider">
                  Elevation 2 • Map Panel
                </div>
                <div className="text-scale-20 font-bold text-foreground mt-2">
                  Overlay Glass Surface
                </div>
                <p className="text-scale-14 text-muted-foreground mt-1">
                  Elevated translucency (bg 9% dark / 72% light) with blur(32px). Used for map diagnostics and flyout drawers.
                </p>
                <div className="mt-4 pt-4 border-t border-black/5 dark:border-white/10 flex justify-between text-[11px] font-mono text-muted-foreground">
                  <span>blur(32px)</span>
                  <span>saturate(170%)</span>
                </div>
              </GlassCard>

              <GlassCard elevation={3} interactive className="p-6">
                <div className="text-scale-12 font-mono text-muted-foreground uppercase tracking-wider">
                  Elevation 3 • Floating Modal
                </div>
                <div className="text-scale-20 font-bold text-foreground mt-2">
                  Floating Command Surface
                </div>
                <p className="text-scale-14 text-muted-foreground mt-1">
                  High-depth translucency (bg 14% dark / 82% light) with blur(40px). Used for navigation pills and alerts.
                </p>
                <div className="mt-4 pt-4 border-t border-black/5 dark:border-white/10 flex justify-between text-[11px] font-mono text-muted-foreground">
                  <span>blur(40px)</span>
                  <span>saturate(180%)</span>
                </div>
              </GlassCard>
            </div>
          </section>

          {/* Section 2: Floating Nav & Segmented Controls */}
          <section className="space-y-4">
            <h2 className="text-scale-28 font-bold tracking-tight text-foreground">
              Navigation & Segmented Controls
            </h2>

            <div className="flex flex-col md:flex-row gap-6 items-start">
              <div className="w-full md:w-auto">
                <span className="block text-scale-12 font-medium text-muted-foreground mb-2">
                  Floating VisionOS Pill Nav:
                </span>
                <GlassNav
                  items={[
                    { id: "primitives", label: "Primitives" },
                    { id: "telemetry", label: "Telemetry", icon: <Waves className="w-3.5 h-3.5" /> },
                    { id: "authority", label: "Authority", icon: <Shield className="w-3.5 h-3.5" /> },
                  ]}
                  activeId={navTab}
                  onSelect={setNavTab}
                  onOpenSearch={() => setIsCommandOpen(true)}
                  isDarkMode={isDarkMode}
                  onToggleTheme={() => setIsDarkMode(!isDarkMode)}
                />
              </div>

              <div className="w-full md:w-auto">
                <span className="block text-scale-12 font-medium text-muted-foreground mb-2">
                  Segmented Control:
                </span>
                <SegmentedControl
                  value={navTab}
                  onChange={setNavTab}
                  options={[
                    { value: "primitives", label: "Primitives" },
                    { value: "telemetry", label: "Telemetry" },
                    { value: "authority", label: "Command" },
                  ]}
                />
              </div>
            </div>
          </section>

          {/* Section 3: Accessible Color-Blind-Safe Risk Palette */}
          <section className="space-y-4">
            <h2 className="text-scale-28 font-bold tracking-tight text-foreground">
              Accessible Risk Palette & SIM Badges
            </h2>
            <p className="text-scale-14 text-muted-foreground">
              WCAG AA compliant color-blind-safe badges using distinct iconography and pattern markers. Hard Rule 3: Simulated river sensors strictly carry the <code>SIM</code> badge.
            </p>

            <div className="flex flex-wrap gap-4 items-center p-6 rounded-glass-md glass-surface-1">
              <RiskChip level="Low" score={0.14} size="lg" />
              <RiskChip level="Moderate" score={0.42} size="lg" />
              <RiskChip level="High" score={0.68} size="lg" />
              <RiskChip level="Very High" score={0.91} size="lg" />
              <SimBadge size="md" />
            </div>
          </section>

          {/* Section 4: Animated Stats & Tabular Numerics */}
          <section className="space-y-4">
            <h2 className="text-scale-28 font-bold tracking-tight text-foreground">
              Tabular Numeric Stats
            </h2>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
              <Stat
                label="River Stage Height"
                value={4.82}
                decimals={2}
                unit="m"
                delta={0.35}
                deltaLabel="m/h"
                trend="up"
              />
              <Stat
                label="Soil Moisture (0-1cm)"
                value={91}
                unit="%"
                delta={12}
                trend="up"
              />
              <Stat
                label="Safe Elevation Gain"
                value={145}
                unit="m"
                delta={-8}
                trend="down"
                invertTrendColor
              />
              <Stat
                label="Relief Camp Occupancy"
                value={640}
                unit="seats"
                delta={0}
                trend="neutral"
              />
            </div>
          </section>

          {/* Section 5: Sliders, Switches & Tooltips */}
          <section className="space-y-4">
            <h2 className="text-scale-28 font-bold tracking-tight text-foreground">
              Interactive Time Scrubber & Controls
            </h2>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <GlassCard elevation={1} className="p-6 space-y-4">
                <div className="flex justify-between items-center">
                  <span className="text-scale-14 font-semibold text-foreground">
                    Hydrological Forecast Horizon
                  </span>
                  <span className="text-scale-14 font-bold text-risk-teal font-mono">
                    +{timeHorizon} Hours
                  </span>
                </div>

                <Slider
                  min={1}
                  max={24}
                  value={timeHorizon}
                  onChange={setTimeHorizon}
                  labels={[
                    { value: 1, label: "1h (Now)" },
                    { value: 3, label: "3h (Peak)" },
                    { value: 6, label: "6h" },
                    { value: 12, label: "12h" },
                    { value: 24, label: "24h" },
                  ]}
                />
              </GlassCard>

              <GlassCard elevation={1} className="p-6 flex flex-col justify-between">
                <div>
                  <h3 className="text-scale-16 font-bold text-foreground">Toggle Controls & Tooltips</h3>
                  <p className="text-scale-12 text-muted-foreground mt-1">
                    Spring-animated visionOS switches and contextual focus micro-popups.
                  </p>
                </div>

                <div className="flex items-center justify-between pt-4">
                  <Switch
                    checked={switchActive}
                    onChange={setSwitchActive}
                    label="Live Sensor Telemetry Daemon"
                  />

                  <Tooltip content="WCAG AA verified contrast micro-popup" position="top">
                    <button
                      type="button"
                      className="px-3 py-1.5 rounded-full text-scale-12 font-medium glass-surface-2 hover:glass-surface-3 transition flex items-center gap-1.5"
                    >
                      <Info className="w-3.5 h-3.5 text-risk-teal" />
                      <span>Hover for Tooltip</span>
                    </button>
                  </Tooltip>
                </div>
              </GlassCard>
            </div>
          </section>

          {/* Section 6: Skeletons & Shimmer Loaders */}
          <section className="space-y-4">
            <h2 className="text-scale-28 font-bold tracking-tight text-foreground">
              Shimmer Skeleton Loaders
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 p-6 rounded-glass-md glass-surface-1">
              <div className="space-y-3">
                <Skeleton radius="sm" className="h-5 w-2/3" />
                <Skeleton radius="sm" className="h-4 w-full" />
                <Skeleton radius="sm" className="h-4 w-4/5" />
              </div>
              <div className="space-y-3">
                <Skeleton radius="md" className="h-16 w-full" />
                <Skeleton radius="sm" className="h-4 w-1/2" />
              </div>
              <div className="flex items-center gap-3">
                <Skeleton radius="full" className="h-12 w-12 shrink-0" />
                <div className="space-y-2 flex-1">
                  <Skeleton radius="sm" className="h-4 w-3/4" />
                  <Skeleton radius="sm" className="h-3 w-1/2" />
                </div>
              </div>
            </div>
          </section>

          {/* Section 7: Modal Drawers, Toasts & Command Palette */}
          <section className="space-y-4">
            <h2 className="text-scale-28 font-bold tracking-tight text-foreground">
              Overlays, Sheets & Notification Toasts
            </h2>

            <div className="flex flex-wrap gap-3">
              <button
                onClick={() => setIsSheetOpen(true)}
                className="px-4 py-2.5 rounded-glass-sm glass-surface-2 hover:glass-surface-3 text-scale-14 font-semibold text-foreground transition flex items-center gap-2"
              >
                <span>Open Bottom Sheet / Drawer</span>
              </button>

              <button
                onClick={() => setIsCommandOpen(true)}
                className="px-4 py-2.5 rounded-glass-sm glass-surface-2 hover:glass-surface-3 text-scale-14 font-semibold text-foreground transition flex items-center gap-2"
              >
                <Search className="w-4 h-4 text-risk-teal" />
                <span>Open Command Palette (⌘K)</span>
              </button>

              <button
                onClick={() => addToast("danger")}
                className="px-4 py-2.5 rounded-glass-sm bg-red-500/15 hover:bg-red-500/25 border border-red-500/40 text-scale-14 font-semibold text-red-300 transition flex items-center gap-2"
              >
                <BellRing className="w-4 h-4 text-red-400" />
                <span>Trigger Critical Toast</span>
              </button>

              <button
                onClick={() => addToast("success")}
                className="px-4 py-2.5 rounded-glass-sm bg-emerald-500/15 hover:bg-emerald-500/25 border border-emerald-500/40 text-scale-14 font-semibold text-emerald-300 transition flex items-center gap-2"
              >
                <Sparkles className="w-4 h-4 text-emerald-400" />
                <span>Trigger Success Toast</span>
              </button>
            </div>
          </section>
        </main>

        {/* Floating Toast Notification Container */}
        <div className="fixed bottom-6 right-6 z-50 flex flex-col gap-2.5 pointer-events-auto">
          {toasts.map((toast) => (
            <Toast
              key={toast.id}
              id={toast.id}
              type={toast.type}
              title={toast.title}
              message={toast.message}
              onDismiss={removeToast}
              action={{
                label: "View Diagnostic →",
                onClick: () => setIsSheetOpen(true),
              }}
            />
          ))}
        </div>

        {/* Interactive Bottom Sheet */}
        <Sheet
          isOpen={isSheetOpen}
          onClose={() => setIsSheetOpen(false)}
          title="Village Diagnostic & Safe Relief Path"
          description="Alaknanda Catchment • Raini Village • Elevation: 2045m"
        >
          <div className="space-y-4">
            <div className="p-4 rounded-glass-md bg-orange-500/10 border border-orange-500/30 flex items-center justify-between">
              <div>
                <div className="text-[11px] font-semibold text-muted-foreground uppercase">
                  Current Hazard Index
                </div>
                <div className="text-scale-28 font-black text-orange-400">High Risk (68%)</div>
              </div>
              <RiskChip level="High" score={0.68} />
            </div>

            <div className="grid grid-cols-2 gap-3 text-scale-12">
              <div className="p-3 rounded-glass-sm glass-surface-1">
                <span className="text-muted-foreground">Assigned Shelter:</span>
                <div className="font-bold text-foreground mt-0.5">Govt Secondary Helang</div>
              </div>
              <div className="p-3 rounded-glass-sm glass-surface-1">
                <span className="text-muted-foreground">Safe Elevation Gain:</span>
                <div className="font-bold text-emerald-400 mt-0.5">+145m Higher</div>
              </div>
            </div>

            <p className="text-scale-12 text-muted-foreground">
              Official IMD/CWC Advisory: Move all livestock and family members to higher ground. Do not attempt to cross swollen mountain torrents.
            </p>
          </div>
        </Sheet>

        {/* Command Palette */}
        <CommandPalette
          isOpen={isCommandOpen}
          onClose={() => setIsCommandOpen(false)}
        />
      </div>
    </div>
  );
}

