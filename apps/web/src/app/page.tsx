"use client";

import React, { useEffect } from "react";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { fetchMapGeoJSON } from "@/lib/api";
import { usePenelopeStore } from "@/lib/store";
import HeaderNav from "@/components/HeaderNav";
import MapLibreFloodMap from "@/components/MapLibreFloodMap";
import VillageRiskDrawer from "@/components/VillageRiskDrawer";
import SensorMonitorPanel from "@/components/SensorMonitorPanel";
import AuthorityDashboardModal from "@/components/AuthorityDashboardModal";
import ModelTransparencyModal from "@/components/ModelTransparencyModal";
import LiveAlertToast from "@/components/LiveAlertToast";

export default function HomePage() {
  const queryClient = useQueryClient();
  const { setActiveAlert } = usePenelopeStore();

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
            // Invalidate sensor and map queries to trigger live refresh
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

      ws.onerror = (e) => {
        // Graceful fallback to periodic polling if WebSocket unavailable
      };
    } catch (e) {
      // Graceful degradation
    }

    return () => {
      if (ws) ws.close();
    };
  }, [queryClient, setActiveAlert]);

  return (
    <main className="relative w-screen h-screen flex flex-col bg-slate-950 overflow-hidden select-none">
      {/* Top Navigation */}
      <HeaderNav />

      {/* Main Fullscreen Interactive Map */}
      <div className="relative flex-1 w-full h-[calc(100vh-4rem)]">
        {isLoading && !geoJsonData ? (
          <div className="absolute inset-0 z-30 flex flex-col items-center justify-center bg-slate-950/80 backdrop-blur">
            <div className="h-10 w-10 border-4 border-sky-500 border-t-transparent rounded-full animate-spin"></div>
            <p className="mt-3 text-sm font-semibold text-slate-300">
              Connecting to PENELOPE Hydrological Network...
            </p>
            <p className="text-xs text-slate-500 mt-1">Data today. Safer tomorrows.</p>
          </div>
        ) : null}

        <MapLibreFloodMap geoJsonData={geoJsonData} />

        {/* Floating Components & Drawers */}
        <VillageRiskDrawer />
        <SensorMonitorPanel />
        <LiveAlertToast />
        <AuthorityDashboardModal />
        <ModelTransparencyModal />
      </div>
    </main>
  );
}

