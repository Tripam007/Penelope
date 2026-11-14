"use client";

import React, { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { usePenelopeStore } from "@/lib/store";
import { fetchSensors, triggerSimulatedSurge } from "@/lib/api";
import { Waves, X, RefreshCw, AlertTriangle, Zap, CheckCircle2 } from "lucide-react";

export default function SensorMonitorPanel() {
  const { isSensorPanelOpen, setSensorPanelOpen, setSimulatedSurgeNotice } = usePenelopeStore();
  const queryClient = useQueryClient();

  const { data: sensors, isLoading, refetch } = useQuery({
    queryKey: ["sensors"],
    queryFn: fetchSensors,
    enabled: isSensorPanelOpen,
    refetchInterval: 8000,
  });

  const [activeSurgeSensor, setActiveSurgeSensor] = useState<string | null>(null);

  const surgeMutation = useMutation({
    mutationFn: (sensorCode: string) => triggerSimulatedSurge(sensorCode),
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ["sensors"] });
      queryClient.invalidateQueries({ queryKey: ["map-geojson"] });
      setSimulatedSurgeNotice(`Cloudburst surge simulated on ${data.sensor_code}: ${data.water_level_m}m.`);
      setTimeout(() => setSimulatedSurgeNotice(null), 8000);
    },
  });

  if (!isSensorPanelOpen) return null;

  return (
    <div className="absolute top-20 left-4 z-20 w-full max-w-md apple-glass-panel rounded-2xl shadow-2xl overflow-hidden transition-all duration-300">
      {/* Header */}
      <div className="p-4 border-b border-white/10 bg-white/[0.02] flex items-center justify-between">
        <div className="flex items-center gap-2">
          <div className="p-2 rounded-xl bg-cyan-500/15 text-cyan-400 border border-cyan-500/30">
            <Waves className="w-5 h-5" />
          </div>
          <div>
            <h2 className="text-base font-bold text-white">River Gauge Telemetry</h2>
            <p className="text-xs text-slate-400">Live Stage & IoT Sensor Network</p>
          </div>
        </div>
        <div className="flex items-center gap-1">
          <button
            onClick={() => refetch()}
            className="p-1.5 rounded-full hover:bg-white/10 text-slate-400 hover:text-white transition"
            title="Refresh Readings"
          >
            <RefreshCw className="w-4 h-4" />
          </button>
          <button
            onClick={() => setSensorPanelOpen(false)}
            className="p-1.5 rounded-full hover:bg-white/10 text-slate-400 hover:text-white transition"
          >
            <X className="w-5 h-5" />
          </button>
        </div>
      </div>

      {/* Sensor List */}
      <div className="p-4 space-y-3 max-h-[70vh] overflow-y-auto">
        {isLoading ? (
          <div className="text-center py-8 text-xs text-slate-400">Loading river gauges...</div>
        ) : sensors?.length ? (
          sensors.map((sensor: any) => {
            const isSimulated = sensor.is_simulated || sensor.latest_reading?.source === "simulated";
            const waterLevel = sensor.latest_reading?.water_level_m || 1.8;
            const dangerLevel = sensor.danger_level_m || 5.0;
            const warningLevel = sensor.warning_level_m || 3.5;
            const pct = Math.min(100, Math.round((waterLevel / dangerLevel) * 100));

            const isCritical = waterLevel >= dangerLevel;
            const isWarning = waterLevel >= warningLevel;

            return (
              <div
                key={sensor.id}
                className={`p-3.5 rounded-xl border transition ${
                  isCritical
                    ? "bg-red-950/30 border-red-500/50 backdrop-blur-md"
                    : isWarning
                    ? "bg-amber-950/30 border-amber-500/50 backdrop-blur-md"
                    : "apple-glass-card"
                }`}
              >
                <div className="flex items-start justify-between">
                  <div>
                    <div className="flex items-center gap-2">
                      <span className="font-bold text-sm text-white">{sensor.name}</span>
                      {/* Hard Rule 3: Simulated Sensor Badge */}
                      {isSimulated && (
                        <span className="px-1.5 py-0.5 rounded text-[9px] font-black bg-amber-500 text-slate-950 border border-amber-400 shadow">
                          SIM
                        </span>
                      )}
                    </div>
                    <div className="text-xs text-slate-400 mt-0.5">
                      River: <span className="text-slate-300 font-medium">{sensor.river_name}</span> • Code:{" "}
                      <span className="font-mono text-[11px] text-cyan-400">{sensor.sensor_code}</span>
                    </div>
                  </div>

                  <div className="text-right">
                    <div className="text-lg font-black text-white font-mono">{waterLevel}m</div>
                    <div className="text-[10px] text-slate-400">Danger: {dangerLevel}m</div>
                  </div>
                </div>

                {/* Level Gauge Progress Bar */}
                <div className="mt-3 space-y-1">
                  <div className="flex justify-between text-[10px] text-slate-400">
                    <span>Stage Saturation</span>
                    <span className={isCritical ? "text-red-400 font-bold" : isWarning ? "text-amber-400 font-bold" : "text-slate-300"}>
                      {pct}%
                    </span>
                  </div>
                  <div className="w-full h-2 bg-slate-950 rounded-full overflow-hidden border border-slate-800">
                    <div
                      className={`h-full transition-all duration-500 ${
                        isCritical ? "bg-red-500" : isWarning ? "bg-amber-500" : "bg-cyan-500"
                      }`}
                      style={{ width: `${pct}%` }}
                    />
                  </div>
                </div>

                {/* Simulated Surge Generator Button (for simulated sensors only) */}
                {isSimulated && (
                  <div className="mt-3 pt-2.5 border-t border-slate-800/80 flex items-center justify-between">
                    <span className="text-[10px] text-slate-400 flex items-center gap-1">
                      <Zap className="w-3 h-3 text-amber-400" />
                      Test Alert Scenario
                    </span>
                    <button
                      onClick={() => surgeMutation.mutate(sensor.sensor_code)}
                      disabled={surgeMutation.isPending}
                      className="px-2.5 py-1 rounded-lg text-[11px] font-bold bg-amber-500/10 hover:bg-amber-500/20 text-amber-400 border border-amber-500/30 transition flex items-center gap-1"
                    >
                      {surgeMutation.isPending ? "Simulating..." : "Trigger Mountain Surge"}
                    </button>
                  </div>
                )}
              </div>
            );
          })
        ) : (
          <div className="text-center py-8 text-xs text-slate-400">No sensors registered.</div>
        )}
      </div>
    </div>
  );
}

