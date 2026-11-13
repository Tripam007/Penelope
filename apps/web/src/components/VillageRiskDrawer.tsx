"use client";

import React from "react";
import { useQuery } from "@tanstack/react-query";
import { usePenelopeStore } from "@/lib/store";
import { fetchVillageDetail } from "@/lib/api";
import { getRiskColorClass } from "@/lib/utils";
import { X, ShieldAlert, Mountain, Compass, Users, MapPin, ChevronRight, PhoneCall, AlertCircle } from "lucide-react";

export default function VillageRiskDrawer() {
  const { selectedVillageId, setSelectedVillageId, language } = usePenelopeStore();

  const { data: village, isLoading } = useQuery({
    queryKey: ["village", selectedVillageId],
    queryFn: () => (selectedVillageId ? fetchVillageDetail(selectedVillageId) : null),
    enabled: Boolean(selectedVillageId),
  });

  if (!selectedVillageId) return null;

  const riskColor = getRiskColorClass(village?.current_risk_level || "Low");

  return (
    <div className="absolute top-20 right-4 z-20 w-full max-w-md bg-slate-950/95 backdrop-blur-xl border border-slate-800 rounded-2xl shadow-2xl overflow-hidden transition-all duration-300">
      {/* Header */}
      <div className="p-4 border-b border-slate-800/80 flex items-start justify-between">
        <div>
          <div className="flex items-center gap-2">
            <h2 className="text-lg font-bold text-white">
              {language === "hi" && village?.hindi_name ? village.hindi_name : village?.name || "Loading..."}
            </h2>
            {village && (
              <span
                className={`text-xs px-2 py-0.5 rounded-full font-bold border ${riskColor.bg} ${riskColor.text} ${riskColor.border}`}
              >
                {village.current_risk_level} Risk
              </span>
            )}
          </div>
          <p className="text-xs text-slate-400 mt-0.5">
            Mountain Catchment Flash-Flood Diagnostic Profile
          </p>
        </div>
        <button
          onClick={() => setSelectedVillageId(null)}
          className="p-1 rounded-lg hover:bg-slate-800 text-slate-400 hover:text-white transition"
        >
          <X className="w-5 h-5" />
        </button>
      </div>

      {isLoading ? (
        <div className="p-8 text-center text-sm text-slate-400">Loading hydrological telemetry...</div>
      ) : village ? (
        <div className="p-4 space-y-4 max-h-[75vh] overflow-y-auto">
          {/* Main Risk Gauge Banner */}
          <div className={`p-3.5 rounded-xl border ${riskColor.bg} ${riskColor.border} flex items-center justify-between`}>
            <div>
              <div className="text-[11px] font-semibold text-slate-300 uppercase tracking-wider">
                Current Flash-Flood Probability
              </div>
              <div className="text-2xl font-black mt-0.5" style={{ color: riskColor.hex }}>
                {Math.round(village.current_risk_score * 100)}%
              </div>
              <div className="text-[10px] text-slate-400 mt-1">
                Calibrated against IMD & CWC flood trigger criteria
              </div>
            </div>
            <div className="text-right text-xs">
              <div className="text-slate-400">Peak Hazard Window</div>
              <div className="font-bold text-white">Next 1 - 3 Hours</div>
            </div>
          </div>

          {/* Terrain & Catchment Metrics */}
          <div className="grid grid-cols-2 gap-2 text-xs">
            <div className="p-2.5 rounded-xl bg-slate-900/60 border border-slate-800/80">
              <div className="flex items-center gap-1.5 text-slate-400 text-[11px]">
                <Mountain className="w-3.5 h-3.5 text-sky-400" />
                Elevation
              </div>
              <div className="text-base font-bold text-white mt-1">
                {village.elevation_m} <span className="text-xs font-normal text-slate-400">meters</span>
              </div>
            </div>

            <div className="p-2.5 rounded-xl bg-slate-900/60 border border-slate-800/80">
              <div className="flex items-center gap-1.5 text-slate-400 text-[11px]">
                <Compass className="w-3.5 h-3.5 text-amber-400" />
                Terrain Slope
              </div>
              <div className="text-base font-bold text-white mt-1">
                {village.slope_degrees}° <span className="text-xs font-normal text-slate-400">gradient</span>
              </div>
            </div>

            <div className="p-2.5 rounded-xl bg-slate-900/60 border border-slate-800/80">
              <div className="flex items-center gap-1.5 text-slate-400 text-[11px]">
                <MapPin className="w-3.5 h-3.5 text-cyan-400" />
                River Proximity
              </div>
              <div className="text-base font-bold text-white mt-1">
                {village.river_distance_m} <span className="text-xs font-normal text-slate-400">meters</span>
              </div>
            </div>

            <div className="p-2.5 rounded-xl bg-slate-900/60 border border-slate-800/80">
              <div className="flex items-center gap-1.5 text-slate-400 text-[11px]">
                <Users className="w-3.5 h-3.5 text-purple-400" />
                Population
              </div>
              <div className="text-base font-bold text-white mt-1">
                {village.population.toLocaleString()}{" "}
                <span className="text-xs font-normal text-slate-400">residents</span>
              </div>
            </div>
          </div>

          {/* Designated Safe Relief Evacuation Shelter */}
          {village.safe_shelter && (
            <div className="p-3.5 rounded-xl bg-emerald-950/30 border border-emerald-800/40 space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-[11px] font-bold text-emerald-400 uppercase tracking-wider flex items-center gap-1.5">
                  <ShieldAlert className="w-4 h-4" />
                  Designated Safe Evacuation Shelter
                </span>
                <span className="text-[10px] bg-emerald-500/20 text-emerald-300 px-1.5 py-0.5 rounded font-semibold border border-emerald-500/30">
                  +{village.safe_shelter.elevation_gain_m}m Gain
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
                <div className="pt-2 border-t border-emerald-800/40 flex items-center justify-between text-xs">
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
          <div className="p-2.5 rounded-lg bg-slate-900 border border-slate-800 text-[11px] text-slate-400 flex items-start gap-2">
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
