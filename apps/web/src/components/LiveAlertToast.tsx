"use client";

import React from "react";
import { usePenelopeStore } from "@/lib/store";
import { Zap, X } from "lucide-react";

export default function LiveAlertToast() {
  const { simulatedSurgeNotice, setSimulatedSurgeNotice } = usePenelopeStore();

  return (
    <>
      {/* Simulated Surge Notice Banner (Top Centered, only during active simulation) */}
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
    </>
  );
}
