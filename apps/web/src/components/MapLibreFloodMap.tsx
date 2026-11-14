"use client";

import React, { useEffect, useRef, useState } from "react";
import maplibregl, { Map as MapLibreMap, Marker, Popup } from "maplibre-gl";
import "maplibre-gl/dist/maplibre-gl.css";
import { usePenelopeStore } from "@/lib/store";
import { getRiskColorClass } from "@/lib/utils";
import { INDIA_REGIONS, IndiaRegionView } from "@/lib/mockData";
import { fetchLiveIndiaHydrology, LiveHydrologyTelemetry } from "@/lib/liveOpenMeteo";
import {
  Compass,
  Layers,
  AlertTriangle,
  ShieldCheck,
  Waves,
  Mountain,
  CloudRain,
  Activity,
  MapPin,
  Tent,
  Radio,
  Globe,
  Sparkles,
  Maximize2
} from "lucide-react";

interface MapProps {
  geoJsonData: any;
}

type LayerFilter = "all" | "villages" | "tourist" | "treks_bridges" | "shelters" | "sensors" | "high_risk";

export default function MapLibreFloodMap({ geoJsonData }: MapProps) {
  const mapContainerRef = useRef<HTMLDivElement>(null);
  const mapRef = useRef<MapLibreMap | null>(null);
  const markersRef = useRef<Marker[]>([]);
  const liveClickMarkerRef = useRef<Marker | null>(null);

  const { setSelectedVillageId, setSelectedSensorCode, language } = usePenelopeStore();

  const [activeFilter, setActiveFilter] = useState<LayerFilter>("all");
  const [selectedRegionId, setSelectedRegionId] = useState<string>("all-india");
  const [liveInspectLoading, setLiveInspectLoading] = useState<boolean>(false);
  const [liveTelemetryPoint, setLiveTelemetryPoint] = useState<LiveHydrologyTelemetry | null>(null);

  // Initialize MapLibre with Pan-India Overview
  useEffect(() => {
    if (!mapContainerRef.current) return;

    // Pan-India default center
    const defaultLng = 78.9629;
    const defaultLat = 22.5937;
    const defaultZoom = 4.8;
    const mapStyle =
      process.env.NEXT_PUBLIC_MAP_STYLE ||
      "https://basemaps.cartocdn.com/gl/dark-matter-gl-style/style.json";

    const map = new maplibregl.Map({
      container: mapContainerRef.current,
      style: mapStyle,
      center: [defaultLng, defaultLat],
      zoom: defaultZoom,
      pitch: 28,
      bearing: 0,
      attributionControl: false,
    });

    map.addControl(new maplibregl.NavigationControl({ visualizePitch: true }), "top-right");
    mapRef.current = map;

    map.on("load", () => {
      if (geoJsonData) {
        renderMapFeatures(map, geoJsonData);
      }
    });

    // Real-Time Live Click Inspector anywhere in India
    map.on("click", async (e) => {
      // If clicking directly on a marker, ignore canvas click
      const originalTarget = (e.originalEvent?.target as HTMLElement) || null;
      if (originalTarget && originalTarget.closest(".maplibregl-marker")) {
        return;
      }

      const { lng, lat } = e.lngLat;
      // Restrict within Indian subcontinent coordinates approx [68, 6] to [97, 36]
      if (lng < 67 || lng > 98 || lat < 6 || lat > 38) return;

      setLiveInspectLoading(true);

      if (liveClickMarkerRef.current) {
        liveClickMarkerRef.current.remove();
        liveClickMarkerRef.current = null;
      }

      try {
        const liveData = await fetchLiveIndiaHydrology(lat, lng);
        setLiveTelemetryPoint(liveData);

        const el = document.createElement("div");
        el.className = "cursor-pointer flex flex-col items-center";
        el.innerHTML = `
          <div class="relative flex items-center justify-center">
            <span class="animate-ping absolute inline-flex h-8 w-8 rounded-full bg-teal-400 opacity-75"></span>
            <div class="h-6 w-6 rounded-full bg-teal-500 border-2 border-white shadow-[0_0_15px_#2dd4bf] flex items-center justify-center text-[10px]">
              📡
            </div>
          </div>
        `;

        const riskColor = getRiskColorClass(liveData.risk_level);

        const popup = new maplibregl.Popup({ offset: 15, maxWidth: "340px" }).setHTML(`
          <div class="p-3 text-slate-100 bg-slate-950 rounded-2xl border border-teal-500/50 font-sans shadow-2xl space-y-2">
            <div class="flex items-start justify-between border-b border-slate-800 pb-2">
              <div>
                <div class="flex items-center gap-1.5">
                  <span class="w-2 h-2 rounded-full bg-teal-400 animate-pulse"></span>
                  <h4 class="font-bold text-xs text-teal-300">Live Real-Time Query</h4>
                </div>
                <div class="text-[10px] text-slate-400 font-mono mt-0.5">
                  ${lat.toFixed(4)}°N, ${lng.toFixed(4)}°E
                </div>
              </div>
              <div class="text-right">
                <span class="text-[9px] text-slate-400 block">GROUND ELEVATION</span>
                <span class="text-xs font-black text-amber-300 font-mono">${liveData.elevation_m}m ASL</span>
              </div>
            </div>

            <div class="p-2 rounded-xl bg-slate-900 border border-slate-800/80">
              <div class="flex items-center justify-between text-[10px] text-sky-400 font-bold mb-1">
                <span>🌧️ Live Open-Meteo Rain</span>
                <span class="text-amber-400">Peak: ${liveData.peak_rain_rate_mmh} mm/h</span>
              </div>
              <div class="grid grid-cols-4 gap-1 text-center font-mono">
                <div class="p-1 rounded bg-slate-950 border border-slate-800">
                  <span class="text-[8px] text-slate-400 block">1H</span>
                  <span class="text-[10px] font-bold text-sky-300">${liveData.rain_1h_mm}m</span>
                </div>
                <div class="p-1 rounded bg-slate-950 border border-slate-800">
                  <span class="text-[8px] text-slate-400 block">3H</span>
                  <span class="text-[10px] font-bold text-sky-300">${liveData.rain_3h_mm}m</span>
                </div>
                <div class="p-1 rounded bg-slate-950 border border-slate-800">
                  <span class="text-[8px] text-slate-400 block">6H</span>
                  <span class="text-[10px] font-bold text-sky-300">${liveData.rain_6h_mm}m</span>
                </div>
                <div class="p-1 rounded bg-slate-950 border border-slate-800">
                  <span class="text-[8px] text-slate-400 block">24H</span>
                  <span class="text-[10px] font-bold text-amber-400">${liveData.rain_24h_mm}m</span>
                </div>
              </div>
            </div>

            <div class="grid grid-cols-2 gap-1.5 text-[10px]">
              <div class="p-1.5 rounded-lg bg-slate-900 border border-slate-800">
                <span class="text-slate-400 block text-[9px]">GLOFAS DISCHARGE</span>
                <span class="font-bold text-white font-mono">${liveData.river_discharge_m3s} m³/s</span>
                <span class="text-[8px] text-slate-500 block">Anomaly: ${liveData.river_anomaly_m3s > 0 ? "+" : ""}${liveData.river_anomaly_m3s} m³/s</span>
              </div>
              <div class="p-1.5 rounded-lg bg-slate-900 border border-slate-800">
                <span class="text-slate-400 block text-[9px]">SOIL SATURATION</span>
                <span class="font-bold text-purple-300 font-mono">${Math.round(liveData.soil_ratios.saturation_ratio * 100)}%</span>
                <span class="text-[8px] text-slate-500 block">API: ${liveData.antecedent_index}</span>
              </div>
            </div>

            <div class="p-1.5 rounded-lg border flex items-center justify-between" style="border-color: ${riskColor.hex}50; background: ${riskColor.hex}15">
              <span class="text-[10px] font-bold" style="color: ${riskColor.hex}">
                ${liveData.risk_level} FLASH-FLOOD RISK
              </span>
              <span class="text-xs font-black font-mono" style="color: ${riskColor.hex}">
                ${Math.round(liveData.risk_score * 100)}%
              </span>
            </div>

            <div class="text-[9px] text-slate-500 flex justify-between border-t border-slate-800/80 pt-1">
              <span>Source: Open-Meteo & GloFAS</span>
              <span>Updated: ${liveData.fetched_at} IST</span>
            </div>
          </div>
        `);

        const newMarker = new maplibregl.Marker({ element: el })
          .setLngLat([lng, lat])
          .setPopup(popup)
          .addTo(map);

        liveClickMarkerRef.current = newMarker;
        popup.addTo(map);
      } catch (err) {
        console.error("Failed to query live hydrology:", err);
      } finally {
        setLiveInspectLoading(false);
      }
    });

    return () => {
      markersRef.current.forEach((m) => m.remove());
      markersRef.current = [];
      if (liveClickMarkerRef.current) liveClickMarkerRef.current.remove();
      map.remove();
    };
  }, []);

  // Re-render markers when data or filter changes
  useEffect(() => {
    if (mapRef.current && geoJsonData) {
      renderMapFeatures(mapRef.current, geoJsonData);
    }
  }, [geoJsonData, activeFilter, language]);

  // Handle India Region Selection and Smooth FlyTo
  const handleSelectRegion = (region: IndiaRegionView) => {
    setSelectedRegionId(region.id);
    if (!mapRef.current) return;

    mapRef.current.flyTo({
      center: region.center,
      zoom: region.zoom,
      pitch: region.pitch,
      speed: 1.4,
      curve: 1.2,
      essential: true,
    });
  };

  const renderMapFeatures = (map: MapLibreMap, data: any) => {
    markersRef.current.forEach((m) => m.remove());
    markersRef.current = [];

    if (!data || !data.features) return;

    data.features.forEach((feature: any) => {
      const p = feature.properties || {};
      const coords = feature.geometry?.coordinates;
      if (!coords || !Array.isArray(coords) || coords.length < 2) return;

      const layerType = p.layer_type || p.category || p.type || "village";
      const isHighOrVeryHigh =
        ["High", "Very High", "HIGH", "VERY HIGH"].includes(p.risk_level) ||
        (p.risk_score && p.risk_score >= 0.6);

      // Filtering logic
      if (activeFilter === "high_risk" && !isHighOrVeryHigh) return;
      if (activeFilter === "villages" && !["village", "town"].includes(layerType)) return;
      if (activeFilter === "tourist" && !["landmark", "tourist_spot"].includes(layerType)) return;
      if (activeFilter === "treks_bridges" && !["trek", "bridge"].includes(layerType)) return;
      if (activeFilter === "shelters" && layerType !== "shelter") return;
      if (activeFilter === "sensors" && layerType !== "sensor") return;

      const riskColor = getRiskColorClass(
        p.risk_level || (p.risk_score ? (p.risk_score >= 0.75 ? "Very High" : p.risk_score >= 0.5 ? "High" : "Moderate") : "Low")
      );
      const displayName = language === "hi" && p.hindi_name ? p.hindi_name : p.name;
      const groundHeight = p.ground_height_m || p.elevation_m || 500;
      const stateName = p.state || "India";
      const rain1h = p.rain_1h_mm ?? 14.0;
      const rain3h = p.rain_3h_mm ?? 38.0;
      const rain6h = p.rain_6h_mm ?? 66.0;
      const rain24h = p.rain_24h_mm ?? 98.0;
      const peakRate = p.peak_rain_rate_mmh ?? 22.0;
      const antecedentIdx = p.antecedent_index ?? 32.0;
      const soilSat = p.soil_ratios?.saturation_ratio != null ? Math.round(p.soil_ratios.saturation_ratio * 100) : 82;
      const dischargeM3s = p.river_discharge_m3s ?? p.discharge_m3s ?? 580.0;
      const anomalyM3s = p.river_anomaly_m3s ?? (dischargeM3s - 220.0);

      // SENSORS
      if (layerType === "sensor") {
        const waterLevel = p.water_level_m || 4.5;
        const dangerLevel = p.danger_level_m || 5.0;

        const el = document.createElement("div");
        el.className = "cursor-pointer group flex flex-col items-center";
        el.innerHTML = `
          <div class="relative flex items-center justify-center">
            <div class="h-6 w-6 rounded-md bg-slate-950 border-2 border-cyan-400 shadow-[0_0_12px_#38bdf8] flex items-center justify-center transition-transform group-hover:scale-125">
              <span class="text-[11px]">📡</span>
            </div>
          </div>
          <div class="mt-1 px-1.5 py-0.5 rounded bg-slate-950/90 border border-cyan-500/50 text-[9px] font-mono text-cyan-300 shadow whitespace-nowrap">
            ${p.river_name || "River"} · ${dischargeM3s}m³/s
          </div>
        `;

        const popup = new maplibregl.Popup({ offset: 15, maxWidth: "300px" }).setHTML(`
          <div class="p-3 text-slate-100 bg-slate-950 rounded-xl border border-cyan-500/40 font-sans shadow-xl">
            <div class="flex items-center gap-2 border-b border-cyan-800/60 pb-1.5 mb-2">
              <span class="text-sm">📡</span>
              <div>
                <h4 class="font-bold text-xs text-cyan-300">${p.name}</h4>
                <p class="text-[10px] text-slate-400">${stateName} · River: ${p.river_name}</p>
              </div>
            </div>
            <div class="grid grid-cols-2 gap-2 text-[11px] mb-2 font-mono">
              <div class="p-1.5 rounded bg-slate-900 border border-slate-800">
                <span class="text-slate-400 block text-[9px] font-sans">WATER STAGE</span>
                <span class="font-bold text-cyan-400">${waterLevel} m</span>
              </div>
              <div class="p-1.5 rounded bg-slate-900 border border-slate-800">
                <span class="text-slate-400 block text-[9px] font-sans">DISCHARGE</span>
                <span class="font-bold text-amber-300">${dischargeM3s} m³/s</span>
              </div>
            </div>
            <div class="text-[10px] text-slate-400 flex justify-between border-t border-slate-800 pt-1">
              <span>Danger Mark: <b>${dangerLevel}m</b></span>
              <span class="text-emerald-400 font-semibold">${p.status || "ACTIVE"}</span>
            </div>
          </div>
        `);

        el.addEventListener("click", () => {
          if (p.sensor_code) setSelectedSensorCode(p.sensor_code);
        });

        const marker = new maplibregl.Marker({ element: el })
          .setLngLat(coords as [number, number])
          .setPopup(popup)
          .addTo(map);

        markersRef.current.push(marker);
        return;
      }

      // SHELTERS
      if (layerType === "shelter") {
        const el = document.createElement("div");
        el.className = "cursor-pointer group flex flex-col items-center";
        el.innerHTML = `
          <div class="relative flex items-center justify-center">
            <div class="h-6 w-6 rounded-full bg-emerald-950 border-2 border-emerald-400 shadow-[0_0_12px_#34d399] flex items-center justify-center transition-transform group-hover:scale-125">
              <span class="text-[11px]">⛺</span>
            </div>
          </div>
          <div class="mt-1 px-1.5 py-0.5 rounded bg-slate-950/90 border border-emerald-500/50 text-[9px] font-medium text-emerald-300 shadow whitespace-nowrap">
            ${displayName} (${p.capacity || 400})
          </div>
        `;

        const popup = new maplibregl.Popup({ offset: 15, maxWidth: "320px" }).setHTML(`
          <div class="p-3 text-slate-100 bg-slate-950 rounded-xl border border-emerald-500/40 font-sans shadow-xl">
            <div class="flex items-center gap-2 border-b border-emerald-800/60 pb-1.5 mb-2">
              <span class="text-sm">⛺</span>
              <div>
                <h4 class="font-bold text-xs text-emerald-300">${displayName}</h4>
                <span class="text-[9px] bg-emerald-500/20 text-emerald-400 px-1 rounded border border-emerald-500/30">${stateName} Safe Evacuation Camp</span>
              </div>
            </div>
            <div class="space-y-1.5 text-[11px] text-slate-300 mb-2">
              <div class="flex justify-between"><span>Capacity:</span> <b class="text-white">${p.capacity || 400} Persons</b></div>
              <div class="flex justify-between"><span>Safe Ground Elevation:</span> <b class="text-emerald-400">${groundHeight} meters</b></div>
              <div class="flex justify-between"><span>Relief Contact:</span> <b class="text-white">${p.contact_phone || "+91-1372-252101"}</b></div>
            </div>
          </div>
        `);

        const marker = new maplibregl.Marker({ element: el })
          .setLngLat(coords as [number, number])
          .setPopup(popup)
          .addTo(map);

        markersRef.current.push(marker);
        return;
      }

      // TOWNS, VILLAGES, LANDMARKS, TREKS, BRIDGES
      let icon = "📍";
      let badgeLabel = "Village";
      let borderStyle = "rounded-full";

      if (layerType === "town") {
        icon = "🏛️";
        badgeLabel = "Town";
        borderStyle = "rounded-lg";
      } else if (layerType === "landmark" || p.type === "tourist_spot") {
        icon = "🛕";
        badgeLabel = "Landmark";
        borderStyle = "rounded-full";
      } else if (layerType === "trek") {
        icon = "🥾";
        badgeLabel = "Trek";
        borderStyle = "rounded-md";
      } else if (layerType === "bridge") {
        icon = "🌉";
        badgeLabel = "Bridge";
        borderStyle = "rounded-sm";
      }

      const riskPercent = Math.round((p.risk_score || 0.3) * 100);

      const el = document.createElement("div");
      el.className = "cursor-pointer group flex flex-col items-center";
      el.innerHTML = `
        <div class="relative flex items-center justify-center">
          ${isHighOrVeryHigh ? `<span class="animate-ping absolute inline-flex h-8 w-8 rounded-full bg-red-400 opacity-75"></span>` : ""}
          <div class="h-6 w-6 ${borderStyle} border-2 border-slate-900 shadow-xl flex items-center justify-center transition-transform group-hover:scale-125" style="background-color: ${riskColor.hex}; box-shadow: 0 0 14px ${riskColor.hex}">
            <span class="text-[10px]">${icon}</span>
          </div>
        </div>
        <div class="mt-1 px-1.5 py-0.5 rounded bg-slate-950/90 backdrop-blur border border-slate-800 text-[10px] font-semibold text-slate-200 shadow-md whitespace-nowrap flex items-center gap-1">
          <span>${displayName}</span>
          <span class="text-[9px] font-bold px-1 rounded" style="background: ${riskColor.hex}25; color: ${riskColor.hex}">
            ${riskPercent}%
          </span>
        </div>
      `;

      const popup = new maplibregl.Popup({ offset: 15, maxWidth: "340px" }).setHTML(`
        <div class="p-3 text-slate-100 bg-slate-950 rounded-2xl border border-slate-800 font-sans shadow-2xl space-y-2">
          <div class="flex items-start justify-between border-b border-slate-800 pb-2">
            <div>
              <div class="flex items-center gap-1.5">
                <span class="text-sm">${icon}</span>
                <h4 class="font-bold text-xs text-white">${displayName}</h4>
              </div>
              <div class="flex items-center gap-1.5 mt-0.5">
                <span class="text-[9px] px-1.5 py-0.2 rounded font-bold uppercase tracking-wider bg-slate-800 text-slate-300">
                  ${stateName} · ${badgeLabel}
                </span>
                <span class="text-[9px] px-1.5 py-0.2 rounded font-bold uppercase" style="background-color: ${riskColor.hex}22; color: ${riskColor.hex}">
                  ${p.risk_level || "MODERATE"} RISK (${riskPercent}%)
                </span>
              </div>
            </div>
            <div class="text-right">
              <span class="text-[9px] text-slate-400 block font-sans">ELEVATION</span>
              <span class="text-xs font-black text-amber-300 font-mono">${groundHeight}m</span>
            </div>
          </div>

          <div class="p-2 rounded-xl bg-slate-900/90 border border-slate-800/80">
            <div class="flex items-center justify-between text-[10px] text-sky-400 font-bold mb-1">
              <span>🌧️ Open-Meteo Rain Forecast</span>
              <span class="text-amber-400">Peak: ${peakRate} mm/h</span>
            </div>
            <div class="grid grid-cols-4 gap-1 text-center font-mono">
              <div class="p-1 rounded bg-slate-950 border border-slate-800/60">
                <span class="text-[8px] text-slate-400 block font-sans">1H</span>
                <span class="text-[10px] font-bold text-sky-300">${rain1h}mm</span>
              </div>
              <div class="p-1 rounded bg-slate-950 border border-slate-800/60">
                <span class="text-[8px] text-slate-400 block font-sans">3H</span>
                <span class="text-[10px] font-bold text-sky-300">${rain3h}mm</span>
              </div>
              <div class="p-1 rounded bg-slate-950 border border-slate-800/60">
                <span class="text-[8px] text-slate-400 block font-sans">6H</span>
                <span class="text-[10px] font-bold text-sky-300">${rain6h}mm</span>
              </div>
              <div class="p-1 rounded bg-slate-950 border border-slate-800/60">
                <span class="text-[8px] text-slate-400 block font-sans">24H</span>
                <span class="text-[10px] font-bold text-amber-400">${rain24h}mm</span>
              </div>
            </div>
          </div>

          <div class="grid grid-cols-2 gap-1.5 text-[10px]">
            <div class="p-1.5 rounded-xl bg-slate-900 border border-slate-800">
              <span class="text-slate-400 block text-[9px]">ANTECEDENT INDEX</span>
              <span class="text-xs font-bold text-teal-300 font-mono">${antecedentIdx}</span>
              <span class="text-[8px] text-slate-500 block">7-day memory</span>
            </div>
            <div class="p-1.5 rounded-xl bg-slate-900 border border-slate-800">
              <span class="text-slate-400 block text-[9px]">SOIL SATURATION</span>
              <span class="text-xs font-bold text-purple-300 font-mono">${soilSat}%</span>
              <span class="text-[8px] text-slate-500 block">Root-zone ratio</span>
            </div>
          </div>

          <div class="p-2 rounded-xl bg-slate-900/90 border border-slate-800 flex items-center justify-between text-[11px]">
            <div>
              <span class="text-[9px] text-slate-400 block font-sans">GLOFAS DISCHARGE</span>
              <span class="font-bold text-cyan-300 font-mono">${dischargeM3s} m³/s</span>
            </div>
            <div class="text-right">
              <span class="text-[9px] text-slate-400 block font-sans">SURGE ANOMALY</span>
              <span class="font-bold ${anomalyM3s > 0 ? "text-red-400" : "text-emerald-400"} font-mono">
                ${anomalyM3s > 0 ? `+${anomalyM3s}` : anomalyM3s} m³/s
              </span>
            </div>
          </div>

          <button
            id="btn-inspect-${p.id}"
            class="w-full mt-1 py-1.5 px-3 rounded-lg bg-teal-500/20 hover:bg-teal-500/30 border border-teal-500/40 text-teal-200 text-xs font-bold transition flex items-center justify-center gap-1.5"
          >
            <span>Open Diagnostic Profile</span>
            <span>→</span>
          </button>
        </div>
      `);

      popup.on("open", () => {
        const btn = document.getElementById(`btn-inspect-${p.id}`);
        if (btn) {
          btn.addEventListener("click", () => {
            setSelectedVillageId(p.id);
          });
        }
      });

      el.addEventListener("click", () => {
        setSelectedVillageId(p.id);
      });

      const marker = new maplibregl.Marker({ element: el })
        .setLngLat(coords as [number, number])
        .setPopup(popup)
        .addTo(map);

      markersRef.current.push(marker);
    });
  };

  return (
    <div className="relative w-full h-full">
      {/* 1. Top Real-Time India Region Quick Jump Bar */}
      <div className="absolute top-3 left-4 z-10 flex items-center gap-1.5 p-1 rounded-2xl bg-slate-950/90 backdrop-blur-2xl border border-white/15 shadow-2xl max-w-[calc(100vw-3rem)] overflow-x-auto scrollbar-none">
        <span className="text-[10px] font-bold text-teal-400 uppercase tracking-wider px-2 flex items-center gap-1 shrink-0">
          <Globe className="w-3.5 h-3.5" />
          <span>India Regions:</span>
        </span>

        {INDIA_REGIONS.map((region) => {
          const isSelected = selectedRegionId === region.id;
          return (
            <button
              key={region.id}
              onClick={() => handleSelectRegion(region)}
              className={`px-2.5 py-1 rounded-xl text-xs font-semibold whitespace-nowrap transition flex items-center gap-1.5 shrink-0 ${
                isSelected
                  ? "bg-teal-500 text-slate-950 font-bold shadow-md shadow-teal-500/30"
                  : "text-slate-300 hover:text-white hover:bg-slate-900/80"
              }`}
            >
              <span>{region.id === "all-india" ? "🇮🇳" : "📍"}</span>
              <span>{region.name.split("(")[0].trim()}</span>
              {region.status === "CRITICAL" && (
                <span className="w-1.5 h-1.5 rounded-full bg-red-400 animate-ping ml-0.5" />
              )}
            </button>
          );
        })}
      </div>

      {/* 2. Secondary Filter Bar (All Landmarks, High Risk, Villages, Tourist, Shelters) */}
      <div className="absolute top-14 left-4 z-10 flex flex-wrap items-center gap-1.5 p-1 rounded-xl bg-slate-950/80 backdrop-blur-xl border border-white/10 shadow-xl max-w-[calc(100vw-3rem)] overflow-x-auto">
        <button
          onClick={() => setActiveFilter("all")}
          className={`px-2.5 py-1 rounded-lg text-[11px] font-bold transition flex items-center gap-1 ${
            activeFilter === "all"
              ? "bg-white/20 text-white border border-white/30"
              : "text-slate-400 hover:text-white"
          }`}
        >
          <Layers className="w-3 h-3" />
          <span>All Landmarks ({geoJsonData?.features?.length || 0})</span>
        </button>

        <button
          onClick={() => setActiveFilter("high_risk")}
          className={`px-2.5 py-1 rounded-lg text-[11px] font-bold transition flex items-center gap-1 ${
            activeFilter === "high_risk"
              ? "bg-red-500 text-white shadow-sm"
              : "text-red-400 hover:bg-red-500/10"
          }`}
        >
          <AlertTriangle className="w-3 h-3 text-red-400" />
          <span>High Risk Only</span>
        </button>

        <button
          onClick={() => setActiveFilter("villages")}
          className={`px-2.5 py-1 rounded-lg text-[11px] font-bold transition flex items-center gap-1 ${
            activeFilter === "villages" ? "bg-amber-500 text-slate-950" : "text-slate-400 hover:text-white"
          }`}
        >
          <span>🏛️</span>
          <span>Villages & Towns</span>
        </button>

        <button
          onClick={() => setActiveFilter("tourist")}
          className={`px-2.5 py-1 rounded-lg text-[11px] font-bold transition flex items-center gap-1 ${
            activeFilter === "tourist" ? "bg-purple-500 text-white" : "text-slate-400 hover:text-white"
          }`}
        >
          <span>🛕</span>
          <span>Tourist & Heritage</span>
        </button>

        <button
          onClick={() => setActiveFilter("treks_bridges")}
          className={`px-2.5 py-1 rounded-lg text-[11px] font-bold transition flex items-center gap-1 ${
            activeFilter === "treks_bridges" ? "bg-sky-500 text-slate-950" : "text-slate-400 hover:text-white"
          }`}
        >
          <span>🥾</span>
          <span>Treks & Bridges</span>
        </button>

        <button
          onClick={() => setActiveFilter("shelters")}
          className={`px-2.5 py-1 rounded-lg text-[11px] font-bold transition flex items-center gap-1 ${
            activeFilter === "shelters" ? "bg-emerald-500 text-slate-950" : "text-slate-400 hover:text-white"
          }`}
        >
          <Tent className="w-3 h-3 text-emerald-400" />
          <span>Safe Shelters</span>
        </button>

        <button
          onClick={() => setActiveFilter("sensors")}
          className={`px-2.5 py-1 rounded-lg text-[11px] font-bold transition flex items-center gap-1 ${
            activeFilter === "sensors" ? "bg-cyan-500 text-slate-950" : "text-slate-400 hover:text-white"
          }`}
        >
          <Waves className="w-3 h-3 text-cyan-400" />
          <span>River Gauges</span>
        </button>
      </div>

      {/* 3. Bottom Live Status Indicator & Click Instruction */}
      <div className="absolute bottom-4 left-4 z-10 flex items-center gap-3">
        <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-slate-950/85 backdrop-blur-xl border border-teal-500/30 text-[11px] font-medium text-slate-200 shadow-xl">
          <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse shadow-[0_0_8px_#34d399]" />
          <span className="font-bold text-teal-300">REAL-TIME INDIA NETWORK</span>
          <span className="text-slate-500">|</span>
          <span className="text-slate-400 hidden sm:inline">Click anywhere on India to query real-time Open-Meteo & GloFAS telemetry</span>
        </div>

        {liveInspectLoading && (
          <div className="flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-teal-500/20 backdrop-blur border border-teal-400 text-xs font-bold text-teal-300 animate-pulse">
            <Sparkles className="w-3.5 h-3.5" />
            <span>Fetching Live Satellite Telemetry...</span>
          </div>
        )}
      </div>

      {/* MapLibre Canvas Container */}
      <div ref={mapContainerRef} className="w-full h-full" />
    </div>
  );
}
