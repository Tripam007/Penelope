"use client";

import React, { useEffect, useRef } from "react";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { fetchMapGeoJSON } from "@/lib/api";
import { usePenelopeStore } from "@/lib/store";
import HeroLanding from "@/components/HeroLanding";
import HeaderNav from "@/components/HeaderNav";
import MapLibreFloodMap from "@/components/MapLibreFloodMap";
import VillageRiskDrawer from "@/components/VillageRiskDrawer";
import SensorMonitorPanel from "@/components/SensorMonitorPanel";
import AuthorityDashboardModal from "@/components/AuthorityDashboardModal";
import ModelTransparencyModal from "@/components/ModelTransparencyModal";
import FirebaseAuthModal from "@/components/FirebaseAuthModal";
import LiveAlertToast from "@/components/LiveAlertToast";
import { ChevronDown, ArrowUp } from "lucide-react";

export default function HomePage() {
  const queryClient = useQueryClient();
  const { setActiveAlert, activeNavTab, setActiveNavTab } = usePenelopeStore();
  const mapSectionRef = useRef<HTMLDivElement>(null);

  const { data: geoJsonData, isLoading } = useQuery({
    queryKey: ["map-geojson"],
    queryFn: fetchMapGeoJSON,
    refetchInterval: 15000,
  });

  // Real-time WebSocket connection to backend
  useEffect(() => {
    const wsUrl = process.env.NEXT_PUBLIC_WS_URL || "ws://localhost:8000/api/v1/ws";
    let ws: WebSocket | null = null;

    try {
      ws = new WebSocket(wsUrl);

      ws.onmessage = (event) => {
        try {
          const payload = JSON.parse(event.data);
          if (payload.type === "SENSOR_TELEMETRY") {
            queryClient.invalidateQueries({ queryKey: ["sensors"] });
            queryClient.invalidateQueries({ queryKey: ["map-geojson"] });
          } else if (payload.type === "ALERT_TRIGGERED") {
            queryClient.invalidateQueries({ queryKey: ["active-alerts"] });
            queryClient.invalidateQueries({ queryKey: ["all-alerts"] });
            queryClient.invalidateQueries({ queryKey: ["map-geojson"] });
            setActiveAlert({
              id: payload.data.village_id || "alert-1",
              severity: payload.data.severity,
              title: `Flash Flood ${payload.data.severity} Advisory`,
              message: `Surge alert triggered for ${payload.data.village_name}. Risk score: ${Math.round(
                payload.data.risk_score * 100
              )}%.`,
              timestamp: payload.timestamp,
            });
          }
        } catch (e) {
          console.error("Error parsing WebSocket payload:", e);
        }
      };
    } catch {
      // Graceful fallback
    }

    return () => {
      if (ws) ws.close();
    };
  }, [queryClient, setActiveAlert]);

  const scrollToMap = () => {
    setActiveNavTab("map");
    if (mapSectionRef.current) {
      mapSectionRef.current.scrollIntoView({ behavior: "smooth" });
    }
  };

  const scrollToTop = () => {
    setActiveNavTab("home");
    window.scrollTo({ top: 0, behavior: "smooth" });
  };

  return (
    <div className="relative w-full min-h-screen bg-slate-950 text-slate-100 flex flex-col overflow-x-hidden">
      {/* 1. FRONT LOADING HERO LANDING PAGE */}
      <section className="relative w-full min-h-screen">
        <HeroLanding onExploreClick={scrollToMap} />

        {/* Scroll To Explore Pill */}
        <div className="absolute bottom-3 left-1/2 -translate-x-1/2 z-20 flex flex-col items-center gap-1 opacity-75 hover:opacity-100 transition cursor-pointer" onClick={scrollToMap}>
          <span className="text-[10px] tracking-widest uppercase font-semibold text-slate-400">
            Scroll to live map
          </span>
          <ChevronDown className="w-4 h-4 text-teal-400 animate-bounce" />
        </div>
      </section>

      {/* 2. LIVE INTERACTIVE MAP & TELEMETRY SECTION */}
      <section
        id="live-map"
        ref={mapSectionRef}
        className="relative w-full h-screen flex flex-col bg-slate-950 border-t border-white/10"
      >
        {/* Navigation Bar for Map View */}
        <HeaderNav />

        {/* Fullscreen Map Canvas */}
        <div className="relative flex-1 w-full h-[calc(100vh-4rem)]">
          {isLoading && !geoJsonData ? (
            <div className="absolute inset-0 z-30 flex flex-col items-center justify-center bg-slate-950/80 backdrop-blur">
              <div className="h-10 w-10 border-4 border-teal-500 border-t-transparent rounded-full animate-spin" />
              <p className="mt-3 text-sm font-semibold text-slate-300">
                Connecting to PENELOPE Hydrological Network...
              </p>
              <p className="text-xs text-slate-500 mt-1">Data today. Safer tomorrows.</p>
            </div>
          ) : null}

          <MapLibreFloodMap geoJsonData={geoJsonData} />

          {/* Floating Telemetry & Command Drawers */}
          <VillageRiskDrawer />
          <SensorMonitorPanel />
          <LiveAlertToast />
          <AuthorityDashboardModal />
          <ModelTransparencyModal />

          {/* Back to Hero Button */}
          <button
            onClick={scrollToTop}
            title="Return to Hero"
            className="absolute bottom-5 left-5 z-20 p-2.5 rounded-full bg-slate-950/80 hover:bg-slate-900 border border-white/15 text-slate-400 hover:text-white shadow-xl backdrop-blur transition"
          >
            <ArrowUp className="w-4 h-4" />
          </button>
        </div>
      </section>

      {/* 3. FIREBASE AUTHENTICATION MODAL (Email + Phone OTP) */}
      <FirebaseAuthModal />
    </div>
  );
}
