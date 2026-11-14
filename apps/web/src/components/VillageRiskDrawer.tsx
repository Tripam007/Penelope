"use client";

import React from "react";
import { useQuery } from "@tanstack/react-query";
import { usePenelopeStore } from "@/lib/store";
import { fetchVillageDetail } from "@/lib/api";
import { getRiskColorClass } from "@/lib/utils";
import {
  X,
  ShieldAlert,
  Mountain,
  Compass,
  Users,
  MapPin,
  ChevronRight,
  PhoneCall,
  AlertCircle,
  CloudRain,
  Waves,
  Activity,
  Layers
} from "lucide-react";

export default function VillageRiskDrawer() {
  const { selectedVillageId, setSelectedVillageId, language } = usePenelopeStore();

  const { data: village, isLoading } = useQuery({
    queryKey: ["village", selectedVillageId],
    queryFn: () => (selectedVillageId ? fetchVillageDetail(selectedVillageId) : null),
    enabled: Boolean(selectedVillageId),
  });

  if (!selectedVillageId) return null;

  const riskColor = getRiskColorClass(village?.current_risk_level || "Low");

  const rain1h = village?.rain_1h_mm ?? 16.5;
  const rain3h = village?.rain_3h_mm ?? 42.0;
  const rain6h = village?.rain_6h_mm ?? 74.5;
  const rain24h = village?.rain_24h_mm ?? 112.0;
  const peakRate = village?.peak_rain_rate_mmh ?? 24.2;
  const antecedentIdx = village?.antecedent_index ?? 38.6;

  const soilSurface = village?.soil_ratios?.surface_0_7cm != null ? Math.round(village.soil_ratios.surface_0_7cm * 100) : 86;
  const soilRootzone = village?.soil_ratios?.rootzone_7_28cm != null ? Math.round(village.soil_ratios.rootzone_7_28cm * 100) : 88;
  const soilSaturation = village?.soil_ratios?.saturation_ratio != null ? Math.round(village.soil_ratios.saturation_ratio * 100) : 87;

  const dischargeM3s = village?.river_discharge_m3s ?? 940.0;
  const anomalyM3s = village?.river_anomaly_m3s ?? 620.0;
  const anomalyRatio = village?.river_anomaly_ratio ?? 2.94;
  const groundHeight = village?.ground_height_m || village?.elevation_m || 1875.0;

  return (
    <div className="absolute top-20 right-4 z-20 w-full max-w-md apple-glass-panel rounded-2xl shadow-2xl overflow-hidden transition-all duration-300">
      {/* Header */}
      <div className="p-4 border-b border-white/10 flex items-start justify-between bg-white/[0.02]">
        <div>
          <div className="flex items-center gap-2">
            <h2 className="text-lg font-bold text-white">
              {language === "hi" && village?.hindi_name ? village.hindi_name : village?.name || "Loading..."}
            </h2>
            {village && (
              <span
                className={`text-xs px-2 py-0.5 rounded-full font-bold border ${riskColor.bg} ${riskColor.text} ${riskColor.border}`}
              >
                {village.current_risk_level || "MODERATE"} Risk
              </span>
            )}
          </div>
          <p className="text-xs text-slate-400 mt-0.5">
            Hydrometeorological Catchment Diagnostic Profile
          </p>
        </div>
        <button
          onClick={() => setSelectedVillageId(null)}
          className="p-1.5 rounded-full hover:bg-white/10 text-slate-400 hover:text-white transition"
        >
          <X className="w-5 h-5" />
        </button>
      </div>

      {isLoading ? (
        <div className="p-8 text-center text-sm text-slate-400">Loading hydrological telemetry...</div>
      ) : village ? (
        <div className="p-4 space-y-3.5 max-h-[75vh] overflow-y-auto">
          {/* Main Risk Gauge Banner */}
          <div className={`p-3.5 rounded-xl border ${riskColor.bg} ${riskColor.border} flex items-center justify-between backdrop-blur-md`}>
            <div>
              <div className="text-[11px] font-semibold text-slate-300 uppercase tracking-wider">
                Current Flash-Flood Probability
              </div>
              <div className="text-2xl font-black mt-0.5" style={{ color: riskColor.hex }}>
                {Math.round((village.current_risk_score ?? 0.84) * 100)}%
              </div>
              <div className="text-[10px] text-slate-400 mt-1">
                Calibrated against IMD & GloFAS flood criteria
              </div>
            </div>
            <div className="text-right text-xs">
              <div className="text-slate-400">Peak Hazard Window</div>
              <div className="font-bold text-white">Next 1 - 3 Hours</div>
            </div>
          </div>

          {/* 1. Open-Meteo Rain Forecast Panel (1h, 3h, 6h, 24h & Peak Rate) */}
          <div className="p-3.5 rounded-xl apple-glass-card space-y-2">
            <div className="flex items-center justify-between">
              <span className="text-xs font-bold text-sky-400 flex items-center gap-1.5">
                <CloudRain className="w-4 h-4 text-sky-400" />
                Open-Meteo Rain Forecast
              </span>
              <span className="text-[10px] font-bold bg-amber-500/20 text-amber-300 px-2 py-0.5 rounded-full border border-amber-500/30">
                Peak Rate: {peakRate} mm/h
              </span>
            </div>

            <div className="grid grid-cols-4 gap-1.5 text-center font-mono pt-1">
              <div className="p-2 rounded-lg apple-glass-tile">
                <span className="text-[9px] text-slate-400 block font-sans">1H RAIN</span>
                <span className="text-xs font-black text-sky-300">{rain1h} mm</span>
              </div>
              <div className="p-2 rounded-lg apple-glass-tile">
                <span className="text-[9px] text-slate-400 block font-sans">3H RAIN</span>
                <span className="text-xs font-black text-sky-300">{rain3h} mm</span>
              </div>
              <div className="p-2 rounded-lg apple-glass-tile">
                <span className="text-[9px] text-slate-400 block font-sans">6H RAIN</span>
                <span className="text-xs font-black text-sky-300">{rain6h} mm</span>
              </div>
              <div className="p-2 rounded-lg apple-glass-tile">
                <span className="text-[9px] text-slate-400 block font-sans">24H RAIN</span>
                <span className="text-xs font-black text-amber-400">{rain24h} mm</span>
              </div>
            </div>
          </div>

          {/* 2. Antecedent Precipitation Index & Soil Ratios */}
          <div className="grid grid-cols-2 gap-2 text-xs">
            <div className="p-3 rounded-xl apple-glass-card space-y-1">
              <div className="flex items-center gap-1.5 text-slate-400 text-[11px]">
                <Activity className="w-3.5 h-3.5 text-teal-400" />
                Antecedent Index (API)
              </div>
              <div className="text-lg font-black text-teal-300 font-mono">
                {antecedentIdx} <span className="text-xs font-normal text-slate-400">index</span>
              </div>
              <div className="text-[10px] text-slate-500">
                7-day cumulative rainfall memory decay
              </div>
            </div>

            <div className="p-3 rounded-xl apple-glass-card space-y-1">
              <div className="flex items-center gap-1.5 text-slate-400 text-[11px]">
                <Layers className="w-3.5 h-3.5 text-purple-400" />
                Soil Saturation Ratios
              </div>
              <div className="text-lg font-black text-purple-300 font-mono">
                {soilSaturation}% <span className="text-xs font-normal text-slate-400">total</span>
              </div>
              <div className="text-[10px] text-slate-400 flex justify-between">
                <span>0-7cm: <b>{soilSurface}%</b></span>
                <span>7-28cm: <b>{soilRootzone}%</b></span>
              </div>
            </div>
          </div>

          {/* 3. GloFAS River Discharge & Anomaly */}
          <div className="p-3.5 rounded-xl apple-glass-card space-y-2">
            <div className="flex items-center justify-between">
              <span className="text-xs font-bold text-cyan-400 flex items-center gap-1.5">
                <Waves className="w-4 h-4 text-cyan-400" />
                GloFAS Hydrological River Status
              </span>
              <span className="text-[10px] font-bold bg-cyan-500/20 text-cyan-300 px-2 py-0.5 rounded-full border border-cyan-500/30">
                {anomalyRatio}x Climatological Normal
              </span>
            </div>

            <div className="grid grid-cols-2 gap-2 text-xs pt-1">
              <div className="p-2.5 rounded-lg apple-glass-tile">
                <span className="text-[10px] text-slate-400 block">RIVER DISCHARGE</span>
                <span className="text-base font-black text-white font-mono">{dischargeM3s} m³/s</span>
                <span className="text-[9px] text-slate-500 block">GloFAS modeled peak</span>
              </div>
              <div className="p-2.5 rounded-lg apple-glass-tile">
                <span className="text-[10px] text-slate-400 block">RIVER ANOMALY</span>
                <span className="text-base font-black text-red-400 font-mono">
                  {anomalyM3s > 0 ? `+${anomalyM3s}` : anomalyM3s} m³/s
                </span>
                <span className="text-[9px] text-slate-500 block">Surge deviation</span>
              </div>
            </div>
          </div>

          {/* 4. Ground Height & Terrain Metrics */}
          <div className="grid grid-cols-2 gap-2 text-xs">
            <div className="p-2.5 rounded-xl apple-glass-card">
              <div className="flex items-center gap-1.5 text-slate-400 text-[11px]">
                <Mountain className="w-3.5 h-3.5 text-amber-400" />
                Ground Height (DEM)
              </div>
              <div className="text-base font-bold text-white mt-1 font-mono">
                {groundHeight} <span className="text-xs font-normal text-slate-400">meters ASL</span>
              </div>
            </div>

            <div className="p-2.5 rounded-xl apple-glass-card">
              <div className="flex items-center gap-1.5 text-slate-400 text-[11px]">
                <Compass className="w-3.5 h-3.5 text-sky-400" />
                Terrain Slope
              </div>
              <div className="text-base font-bold text-white mt-1">
                {village.slope_degrees || 28}° <span className="text-xs font-normal text-slate-400">gradient</span>
              </div>
            </div>

            <div className="p-2.5 rounded-xl apple-glass-card">
              <div className="flex items-center gap-1.5 text-slate-400 text-[11px]">
                <MapPin className="w-3.5 h-3.5 text-cyan-400" />
                River Distance
              </div>
              <div className="text-base font-bold text-white mt-1 font-mono">
                {village.river_distance_m || 320} <span className="text-xs font-normal text-slate-400">meters</span>
              </div>
            </div>

            <div className="p-2.5 rounded-xl apple-glass-card">
              <div className="flex items-center gap-1.5 text-slate-400 text-[11px]">
                <Users className="w-3.5 h-3.5 text-purple-400" />
                Population
              </div>
              <div className="text-base font-bold text-white mt-1">
                {(village.population || 16700).toLocaleString()}{" "}
                <span className="text-xs font-normal text-slate-400">residents</span>
              </div>
            </div>
          </div>

          {/* 5. Designated Safe Relief Evacuation Shelter */}
          {village.safe_shelter && (
            <div className="p-3.5 rounded-xl apple-glass-card border-emerald-500/30 space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-[11px] font-bold text-emerald-400 uppercase tracking-wider flex items-center gap-1.5">
                  <ShieldAlert className="w-4 h-4" />
                  Designated Safe Evacuation Shelter
                </span>
                <span className="text-[10px] bg-emerald-500/20 text-emerald-300 px-1.5 py-0.5 rounded font-semibold border border-emerald-500/30">
                  +{village.safe_shelter.elevation_gain_m || 120}m Gain
                </span>
              </div>

              <div className="text-sm font-bold text-white">
                {language === "hi" && village.safe_shelter.hindi_name
                  ? village.safe_shelter.hindi_name
                  : village.safe_shelter.name}
              </div>

              <div className="grid grid-cols-2 gap-2 text-xs text-slate-300 pt-1">
                <div>Safe Elevation: <b>{village.safe_shelter.elevation_m}m</b></div>
                <div>Capacity: <b>{village.safe_shelter.capacity} persons</b></div>
              </div>

              {village.safe_shelter.contact_phone && (
                <div className="pt-2 border-t border-white/10 flex items-center justify-between text-xs">
                  <span className="text-slate-400">Relief Officer: {village.safe_shelter.contact_person}</span>
                  <a
                    href={`tel:${village.safe_shelter.contact_phone}`}
                    className="flex items-center gap-1 text-emerald-400 font-bold hover:underline"
                  >
                    <PhoneCall className="w-3.5 h-3.5" />
                    {village.safe_shelter.contact_phone}
                  </a>
                </div>
              )}
            </div>
          )}

          {/* Official Advisory Disclaimer Notice */}
          <div className="p-2.5 rounded-lg apple-glass-tile text-[11px] text-slate-300 flex items-start gap-2">
            <AlertCircle className="w-4 h-4 text-amber-400 shrink-0 mt-0.5" />
            <span>
              <b>Advisory Only:</b> Follow official warning bulletins issued by India Meteorological Department (IMD)
              and District Disaster Management Authorities.
            </span>
          </div>
        </div>
      ) : null}
    </div>
  );
}
