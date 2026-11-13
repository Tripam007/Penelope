"use client";

import React, { useEffect, useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { usePenelopeStore } from "@/lib/store";
import { fetchActiveAlerts } from "@/lib/api";
import { AlertTriangle, Zap, X, ShieldAlert } from "lucide-react";

export default function LiveAlertToast() {
  const { simulatedSurgeNotice, setSimulatedSurgeNotice, setSelectedVillageId } = usePenelopeStore();

  const { data: activeAlerts } = useQuery({
    queryKey: ["active-alerts"],
    queryFn: fetchActiveAlerts,
    refetchInterval: 10000,
  });

  const latestAlert = activeAlerts?.[0];

  return (
    <>
      {/* Simulated Surge Notice Banner */}
      {simulatedSurgeNotice && (
        <div className="absolute top-20 left-1/2 -translate-x-1/2 z-40 max-w-md w-full px-4">
          <div className="p-3.5 rounded-xl bg-amber-500 text-slate-950 shadow-2xl flex items-center justify-between border-2 border-amber-300 animate-bounce">
            <div className="flex items-center gap-2">
              <Zap className="w-5 h-5 fill-slate-950 shrink-0" />
              <div>
                <div className="font-black text-xs uppercase tracking-wider">
                  SIMULATION ACTIVE (SIM BADGE)
                </div>
                <div className="text-xs font-semibold">{simulatedSurgeNotice}</div>
              </div>
            </div>
            <button
              onClick={() => setSimulatedSurgeNotice(null)}
              className="p-1 hover:bg-amber-600 rounded-lg transition"
            >
              <X className="w-4 h-4" />
            </button>
          </div>
        </div>
      )}

      {/* Emergency Flash-Flood Live Banner */}
      {latestAlert && !simulatedSurgeNotice && (
        <div className="absolute bottom-6 right-4 z-20 max-w-sm w-full">
          <div className="p-4 rounded-xl bg-red-950/95 backdrop-blur-xl border border-red-500/80 shadow-2xl text-white space-y-2 animate-pulse">
            <div className="flex items-center justify-between">
              <span className="flex items-center gap-1.5 text-xs font-black uppercase text-red-400">
                <AlertTriangle className="w-4 h-4" />
                {latestAlert.severity} Flash-Flood Alert
              </span>
              <span className="text-[10px] text-slate-400">Active Warning</span>
            </div>

            <div className="text-xs font-bold">{latestAlert.title}</div>
            <div className="text-[11px] text-slate-300 leading-tight line-clamp-2">
              {latestAlert.message}
            </div>

            <div className="pt-2 border-t border-red-900/60 flex items-center justify-between text-[11px]">
              <span className="text-red-300 text-[10px]">Follow IMD/CWC/NDMA warnings</span>
              {latestAlert.village_id && (
                <button
                  onClick={() => setSelectedVillageId(latestAlert.village_id)}
                  className="font-bold text-sky-400 hover:underline"
                >
                  View Evacuation →
                </button>
              )}
            </div>
          </div>
        </div>
      )}
    </>
  );
}

