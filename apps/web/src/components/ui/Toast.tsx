"use client";

import React, { useEffect, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { AlertTriangle, CheckCircle, Info, X } from "lucide-react";
import { cn } from "@/lib/utils";

export interface ToastProps {
  id: string;
  type?: "warning" | "success" | "info" | "danger";
  title: string;
  message: string;
  durationMs?: number;
  onDismiss: (id: string) => void;
  action?: {
    label: string;
    onClick: () => void;
  };
}

export const Toast: React.FC<ToastProps> = ({
  id,
  type = "info",
  title,
  message,
  durationMs = 6000,
  onDismiss,
  action,
}) => {
  const [progress, setProgress] = useState(100);

  useEffect(() => {
    const startTime = Date.now();
    const interval = setInterval(() => {
      const elapsed = Date.now() - startTime;
      const remaining = Math.max(0, 100 - (elapsed / durationMs) * 100);
      setProgress(remaining);
      if (remaining === 0) {
        clearInterval(interval);
        onDismiss(id);
      }
    }, 50);

    return () => clearInterval(interval);
  }, [id, durationMs, onDismiss]);

  const icons = {
    warning: <AlertTriangle className="w-5 h-5 text-yellow-400 shrink-0" />,
    success: <CheckCircle className="w-5 h-5 text-emerald-400 shrink-0" />,
    info: <Info className="w-5 h-5 text-sky-400 shrink-0" />,
    danger: <AlertTriangle className="w-5 h-5 text-red-400 shrink-0" />,
  };

  return (
    <motion.div
      layout
      initial={{ opacity: 0, y: 20, scale: 0.95 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      exit={{ opacity: 0, y: 15, scale: 0.9 }}
      transition={{ type: "spring", stiffness: 280, damping: 24 }}
      role="alert"
      className="relative z-50 w-full max-w-sm glass-surface-3 glass-sheen rounded-glass-md border border-white/20 dark:border-white/15 shadow-glass-3 p-4 overflow-hidden"
    >
      <div className="flex items-start gap-3">
        {icons[type]}
        <div className="flex-1 pr-2">
          <div className="text-scale-14 font-bold text-foreground leading-snug">{title}</div>
          <div className="text-scale-12 text-muted-foreground mt-0.5 leading-relaxed">{message}</div>

          {action && (
            <button
              onClick={action.onClick}
              className="mt-2 text-scale-12 font-bold text-risk-teal hover:underline focus-visible:outline-none"
            >
              {action.label}
            </button>
          )}
        </div>

        <button
          onClick={() => onDismiss(id)}
          className="p-1 rounded-full text-muted-foreground hover:text-foreground hover:bg-black/5 dark:hover:bg-white/10 transition"
          aria-label="Dismiss alert"
        >
          <X className="w-4 h-4" />
        </button>
      </div>

      {/* Auto-dismiss progress bar */}
      <div className="absolute bottom-0 left-0 right-0 h-0.5 bg-black/5 dark:bg-white/10">
        <div
          className="h-full bg-risk-teal transition-all ease-linear"
          style={{ width: `${progress}%` }}
        />
      </div>
    </motion.div>
  );
};

