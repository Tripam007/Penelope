"use client";

import React, { useEffect, useState } from "react";
import { GlassCard } from "@/components/ui/GlassCard";
import { Info, History } from "lucide-react";

interface HindcastEvent {
  dataset: string;
  window_type: string;
  location_name: string;
  total_hours_evaluated: number;
  days_evaluated: number;
  cumulative_rain_72h_mm: number;
  max_antecedent_precip_index_7d: number;
  peak_probability_3h: number;
  peak_risk_tier: string;
  flagged: string;
  lead_time: string;
  first_hour_reached_high: string;
  high_or_above_hours: number;
  false_alarm_rate_hours: number;
  alert_episodes: number;
  episodes_per_day: number;
  event_time_ist: string | null;
}

interface QuietControl {
  dataset: string;
  window_type: string;
  location_name: string;
  total_hours_evaluated: number;
  days_evaluated: number;
  cumulative_rain_72h_mm: number;
  max_antecedent_precip_index_7d: number;
  peak_probability_3h: number;
  peak_risk_tier: string;
  flagged: string;
  lead_time: string;
  first_hour_reached_high: string;
  high_or_above_hours: number;
  false_alarm_rate_hours: number;
  alert_episodes: number;
  episodes_per_day: number;
  event_time_ist: string | null;
}

interface ThresholdSweepRow {
  threshold: number;
  dharali_2025_flagged: string;
  dharali_2025_lead_time: string;
  kedarnath_2013_flagged: string;
  kedarnath_2013_lead_time: string;
  kerala_2018_flagged: string;
  kerala_2018_lead_time: string;
  wayanad_2024_flagged: string;
  wayanad_2024_lead_time: string;
  dharali_2025_quiet_episodes_per_day: number;
  kedarnath_2013_quiet_episodes_per_day: number;
  kerala_2018_quiet_episodes_per_day: number;
  wayanad_2024_quiet_episodes_per_day: number;
}

interface HindcastData {
  events: Record<string, HindcastEvent>;
  quiet_controls: Record<string, QuietControl>;
  threshold_sweep: ThresholdSweepRow[];
  limitations: string[];
}

export default function HindcastPanel() {
  const [data, setData] = useState<HindcastData | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<boolean>(false);

  useEffect(() => {
    const apiUrl = `${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/api/v1/ml/hindcast`;
    let isMounted = true;
    setLoading(true);
    setError(false);

    fetch(apiUrl)
      .then((res) => {
        if (!res.ok) throw new Error("Hindcast fetch failed");
        return res.json();
      })
      .then((json) => {
        if (isMounted) {
          setData(json);
          setLoading(false);
        }
      })
      .catch(() => {
        if (isMounted) {
          setError(true);
          setLoading(false);
        }
      });

    return () => {
      isMounted = false;
    };
  }, []);

  if (loading) {
    return (
      <div className="p-4 rounded-xl border border-slate-800 bg-slate-950/60 text-slate-400 text-xs flex items-center justify-center gap-2">
        <div className="w-4 h-4 rounded-full border-2 border-sky-400 border-t-transparent animate-spin" />
        <span>Loading hindcast data...</span>
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="p-4 rounded-xl border border-slate-800 bg-slate-950/60 text-slate-400 text-xs text-center">
        Hindcast results unavailable
      </div>
    );
  }

  const eventsList = Object.values(data.events || {});
  const quietList = Object.values(data.quiet_controls || {});

  return (
    <div className="space-y-4">
      {/* (a) Heading */}
      <h3 className="text-xs font-bold text-slate-300 uppercase tracking-wider flex items-center gap-1.5">
        <History className="w-4 h-4 text-purple-400 shrink-0" />
        Case study on 4 real events, not statistical validation.
      </h3>

      {/* (b) 4 Events Table */}
      <div className="overflow-x-auto rounded-xl border border-slate-800 bg-slate-950">
        <table className="w-full text-left text-xs">
          <thead className="bg-slate-900/80 text-slate-400 border-b border-slate-800 font-semibold">
            <tr>
              <th className="p-3">Location</th>
              <th className="p-3">Event Time</th>
              <th className="p-3">72h Rain</th>
              <th className="p-3">Peak Probability</th>
              <th className="p-3">Flagged</th>
              <th className="p-3">Lead Time</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800 text-slate-200">
            {eventsList.map((ev) => (
              <tr key={ev.dataset}>
                <td className="p-3 font-medium text-slate-200">{ev.location_name}</td>
                <td className="p-3 font-mono text-slate-400">
                  {ev.event_time_ist ? ev.event_time_ist.replace("T", " ") : "N/A"}
                </td>
                <td className="p-3 font-mono text-sky-300">{ev.cumulative_rain_72h_mm} mm</td>
                <td className="p-3 font-mono">{ev.peak_probability_3h}</td>
                <td className="p-3">
                  <span
                    className={
                      ev.flagged === "yes"
                        ? "text-emerald-400 font-semibold capitalize"
                        : "text-slate-400 capitalize"
                    }
                  >
                    {ev.flagged}
                  </span>
                </td>
                <td className="p-3 font-mono text-amber-300">{ev.lead_time}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* (c) Quiet-Window Controls Table */}
      <div className="overflow-x-auto rounded-xl border border-slate-800 bg-slate-950">
        <table className="w-full text-left text-xs">
          <thead className="bg-slate-900/80 text-slate-400 border-b border-slate-800 font-semibold">
            <tr>
              <th className="p-3">Location</th>
              <th className="p-3">Hours Evaluated</th>
              <th className="p-3">High+ Hours</th>
              <th className="p-3">Alert Episodes per Day</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800 text-slate-200">
            {quietList.map((ctrl) => (
              <tr key={ctrl.dataset}>
                <td className="p-3 font-medium text-slate-200">{ctrl.location_name}</td>
                <td className="p-3 font-mono text-slate-300">{ctrl.total_hours_evaluated}</td>
                <td className="p-3 font-mono text-slate-300">{ctrl.high_or_above_hours}</td>
                <td className="p-3 font-mono text-slate-300">{ctrl.episodes_per_day}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* (d) Threshold Sweep Small Table */}
      <div className="overflow-x-auto rounded-xl border border-slate-800 bg-slate-950">
        <table className="w-full text-left text-xs">
          <thead className="bg-slate-900/80 text-slate-400 border-b border-slate-800 font-semibold">
            <tr>
              <th className="p-2.5">Threshold</th>
              <th className="p-2.5">Dharali (2025)</th>
              <th className="p-2.5">Kedarnath (2013)</th>
              <th className="p-2.5">Kerala (2018)</th>
              <th className="p-2.5">Wayanad (2024)</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800 text-slate-200">
            {(data.threshold_sweep || []).map((row) => (
              <tr key={row.threshold}>
                <td className="p-2.5 font-mono font-bold text-sky-400">{row.threshold}</td>
                <td className="p-2.5 font-mono">
                  <span className={row.dharali_2025_flagged === "yes" ? "text-emerald-400" : "text-slate-400"}>
                    {row.dharali_2025_flagged}
                  </span>{" "}
                  <span className="text-slate-400">({row.dharali_2025_lead_time})</span>
                </td>
                <td className="p-2.5 font-mono">
                  <span className={row.kedarnath_2013_flagged === "yes" ? "text-emerald-400" : "text-slate-400"}>
                    {row.kedarnath_2013_flagged}
                  </span>{" "}
                  <span className="text-slate-400">({row.kedarnath_2013_lead_time})</span>
                </td>
                <td className="p-2.5 font-mono">
                  <span className={row.kerala_2018_flagged === "yes" ? "text-emerald-400" : "text-slate-400"}>
                    {row.kerala_2018_flagged}
                  </span>{" "}
                  <span className="text-slate-400">({row.kerala_2018_lead_time})</span>
                </td>
                <td className="p-2.5 font-mono">
                  <span className={row.wayanad_2024_flagged === "yes" ? "text-emerald-400" : "text-slate-400"}>
                    {row.wayanad_2024_flagged}
                  </span>{" "}
                  <span className="text-slate-400">({row.wayanad_2024_lead_time})</span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* (e) Limitations Visible Note Box */}
      <GlassCard elevation={1} className="p-4 bg-amber-500/10 border border-amber-500/30 text-xs space-y-2">
        <div className="font-bold text-amber-300 text-sm flex items-center gap-1.5">
          <Info className="w-4 h-4 text-amber-400 shrink-0" />
          <span>Evaluation Limitations</span>
        </div>
        <ul className="list-disc list-inside space-y-1 text-slate-300">
          {(data.limitations || []).map((lim, idx) => (
            <li key={idx}>{lim}</li>
          ))}
        </ul>
      </GlassCard>
    </div>
  );
}
