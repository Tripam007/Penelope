"use client";

import React, { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { usePenelopeStore } from "@/lib/store";
import { fetchAllAlerts, fetchVillages, triggerManualAlert } from "@/lib/api";
import { Shield, X, Send, AlertTriangle, CheckCircle, Clock, Check, AlertCircle } from "lucide-react";

export default function AuthorityDashboardModal() {
  const { isAuthorityModalOpen, setAuthorityModalOpen } = usePenelopeStore();
  const queryClient = useQueryClient();

  const { data: alerts } = useQuery({
    queryKey: ["all-alerts"],
    queryFn: fetchAllAlerts,
    enabled: isAuthorityModalOpen,
  });

  const { data: villages } = useQuery({
    queryKey: ["villages"],
    queryFn: fetchVillages,
    enabled: isAuthorityModalOpen,
  });

  const [severity, setSeverity] = useState<"Moderate" | "High" | "Very High">("High");
  const [title, setTitle] = useState("Flash-Flood Early Warning - Mountain Catchment Surge");
  const [message, setMessage] = useState("Intense convective cloudburst rainfall detected. River stage exceeding danger mark. Evacuate riverbank settlements to designated shelters immediately.");
  const [selectedChannels, setSelectedChannels] = useState<string[]>(["SMS", "Telegram", "Email", "Webhook", "Push"]);
  const [statusNotice, setStatusNotice] = useState<string | null>(null);

  const triggerMutation = useMutation({
    mutationFn: () => {
      const basinId = villages?.[0]?.basin_id || "default";
      return triggerManualAlert({
        basin_id: basinId,
        severity: severity,
        title: title,
        message: message,
        channels: selectedChannels,
      });
    },
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ["all-alerts"] });
      queryClient.invalidateQueries({ queryKey: ["active-alerts"] });
      setStatusNotice("Alert dispatched! Delivery statuses recorded.");
      setTimeout(() => setStatusNotice(null), 6000);
    },
  });

  if (!isAuthorityModalOpen) return null;

  const toggleChannel = (ch: string) => {
    setSelectedChannels((prev) =>
      prev.includes(ch) ? prev.filter((c) => c !== ch) : [...prev, ch]
    );
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-md">
      <div className="w-full max-w-4xl bg-slate-900 border border-slate-800 rounded-2xl shadow-2xl overflow-hidden flex flex-col max-h-[90vh]">
        {/* Header */}
        <div className="p-4 bg-slate-950 border-b border-slate-800 flex items-center justify-between">
          <div className="flex items-center gap-2.5">
            <div className="p-2 rounded-xl bg-amber-500/10 border border-amber-500/30 text-amber-400">
              <Shield className="w-5 h-5" />
            </div>
            <div>
              <h2 className="text-base font-bold text-white">Disaster Authority Command Center</h2>
              <p className="text-xs text-slate-400">NDRF / SDRF / DDMA Emergency Alert Dispatch Engine</p>
            </div>
          </div>
          <button
            onClick={() => setAuthorityModalOpen(false)}
            className="p-1.5 rounded-lg hover:bg-slate-800 text-slate-400 hover:text-white transition"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content Body: Left Form, Right Audit Log */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-0 divide-y md:divide-y-0 md:divide-x divide-slate-800 overflow-y-auto">
          {/* Left: Dispatch Form */}
          <div className="p-5 space-y-4">
            <h3 className="text-sm font-bold text-slate-200 flex items-center gap-1.5">
              <Send className="w-4 h-4 text-sky-400" />
              Issue Multi-Channel Alert
            </h3>

            {statusNotice && (
              <div className="p-3 rounded-lg bg-emerald-500/15 border border-emerald-500/40 text-emerald-300 text-xs flex items-center gap-2">
                <Check className="w-4 h-4" />
                {statusNotice}
              </div>
            )}

            <div>
              <label className="block text-xs font-semibold text-slate-400 mb-1.5">Alert Severity</label>
              <div className="grid grid-cols-3 gap-2">
                {(["Moderate", "High", "Very High"] as const).map((sev) => (
                  <button
                    key={sev}
                    type="button"
                    onClick={() => setSeverity(sev)}
                    className={`py-2 rounded-lg text-xs font-bold border transition ${
                      severity === sev
                        ? sev === "Very High"
                          ? "bg-red-500/20 text-red-400 border-red-500"
                          : sev === "High"
                          ? "bg-orange-500/20 text-orange-400 border-orange-500"
                          : "bg-amber-500/20 text-amber-400 border-amber-500"
                        : "bg-slate-950 text-slate-400 border-slate-800"
                    }`}
                  >
                    {sev}
                  </button>
                ))}
              </div>
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-400 mb-1.5">Alert Title</label>
              <input
                type="text"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                className="w-full px-3 py-2 rounded-lg bg-slate-950 border border-slate-800 text-xs text-white focus:outline-none focus:border-sky-500"
              />
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-400 mb-1.5">Emergency Message</label>
              <textarea
                rows={3}
                value={message}
                onChange={(e) => setMessage(e.target.value)}
                className="w-full px-3 py-2 rounded-lg bg-slate-950 border border-slate-800 text-xs text-white focus:outline-none focus:border-sky-500"
              />
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-400 mb-1.5">Dispatch Channels</label>
              <div className="flex flex-wrap gap-2 text-xs">
                {["SMS", "Telegram", "Email", "Webhook", "Push"].map((ch) => {
                  const isChecked = selectedChannels.includes(ch);
                  return (
                    <button
                      key={ch}
                      type="button"
                      onClick={() => toggleChannel(ch)}
                      className={`px-3 py-1.5 rounded-lg border font-medium transition ${
                        isChecked
                          ? "bg-sky-500/20 text-sky-300 border-sky-500/50"
                          : "bg-slate-950 text-slate-500 border-slate-800"
                      }`}
                    >
                      {ch}
                    </button>
                  );
                })}
              </div>
              <p className="text-[10px] text-slate-500 mt-1">
                Unconfigured providers degrade gracefully and record status as <code>skipped_unconfigured</code>.
              </p>
            </div>

            <button
              onClick={() => triggerMutation.mutate()}
              disabled={triggerMutation.isPending}
              className="w-full py-2.5 rounded-xl font-bold text-xs bg-gradient-to-r from-red-600 to-amber-600 hover:from-red-500 hover:to-amber-500 text-white shadow-lg transition disabled:opacity-50"
            >
              {triggerMutation.isPending ? "Broadcasting..." : "Broadcast Immediate Early Warning"}
            </button>
          </div>

          {/* Right: Live Delivery Audit Trail (Hard Rule 4 & 8) */}
          <div className="p-5 space-y-3 bg-slate-950/40">
            <h3 className="text-sm font-bold text-slate-200 flex items-center justify-between">
              <span>Incident & Delivery Audit Log</span>
              <span className="text-[10px] text-slate-500 font-mono">Real Delivery Status</span>
            </h3>

            <div className="space-y-2.5 max-h-[50vh] overflow-y-auto pr-1">
              {alerts?.length ? (
                alerts.map((al: any) => (
                  <div key={al.id} className="p-3 rounded-xl bg-slate-950 border border-slate-800 text-xs space-y-2">
                    <div className="flex items-center justify-between">
                      <span className="font-bold text-slate-200">{al.title}</span>
                      <span className="text-[10px] font-bold px-1.5 py-0.5 rounded bg-red-500/20 text-red-400 border border-red-500/30">
                        {al.severity}
                      </span>
                    </div>

                    <p className="text-[11px] text-slate-400 line-clamp-2">{al.message}</p>

                    {/* Channel delivery statuses */}
                    <div className="pt-2 border-t border-slate-800/80 flex flex-wrap gap-1.5">
                      {al.deliveries?.map((del: any) => {
                        const isDelivered = del.status === "delivered";
                        const isSkipped = del.status === "skipped_unconfigured";
                        return (
                          <span
                            key={del.id}
                            className={`px-2 py-0.5 rounded text-[10px] font-mono flex items-center gap-1 ${
                              isDelivered
                                ? "bg-emerald-500/15 text-emerald-400 border border-emerald-500/30"
                                : isSkipped
                                ? "bg-slate-800 text-slate-400 border border-slate-700"
                                : "bg-red-500/15 text-red-400 border border-red-500/30"
                            }`}
                          >
                            <span>{del.channel}:</span>
                            <b>{del.status}</b>
                          </span>
                        );
                      })}
                    </div>
                  </div>
                ))
              ) : (
                <div className="text-center py-10 text-xs text-slate-500">No alert logs recorded yet.</div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

