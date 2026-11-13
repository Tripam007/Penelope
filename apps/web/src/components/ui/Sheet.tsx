"use client";

import React, { useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { X } from "lucide-react";
import { cn } from "@/lib/utils";

export interface SheetProps {
  isOpen: boolean;
  onClose: () => void;
  title: string;
  description?: string;
  position?: "bottom" | "right";
  className?: string;
  children: React.ReactNode;
}

export const Sheet: React.FC<SheetProps> = ({
  isOpen,
  onClose,
  title,
  description,
  position = "bottom",
  className,
  children,
}) => {
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === "Escape" && isOpen) {
        onClose();
      }
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [isOpen, onClose]);

  const isBottom = position === "bottom";

  return (
    <AnimatePresence>
      {isOpen && (
        <div className="fixed inset-0 z-50 flex justify-center items-end sm:items-center">
          {/* Backdrop */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={onClose}
            className="fixed inset-0 bg-black/40 dark:bg-black/60 backdrop-blur-sm"
            aria-hidden="true"
          />

          {/* Sheet Surface */}
          <motion.div
            initial={isBottom ? { y: "100%" } : { x: "100%" }}
            animate={isBottom ? { y: 0 } : { x: 0 }}
            exit={isBottom ? { y: "100%" } : { x: "100%" }}
            transition={{ type: "spring", stiffness: 260, damping: 24 }}
            role="dialog"
            aria-modal="true"
            aria-labelledby="sheet-title"
            className={cn(
              "relative z-10 w-full max-h-[85vh] overflow-hidden glass-surface-3 glass-sheen border border-white/20 dark:border-white/15 shadow-glass-3",
              isBottom
                ? "rounded-t-glass-lg sm:rounded-glass-lg sm:max-w-xl sm:mb-8"
                : "sm:max-w-md sm:h-full sm:right-0 sm:fixed",
              className
            )}
          >
            {/* Grab Handle for Mobile */}
            {isBottom && (
              <div className="w-12 h-1.5 bg-black/20 dark:bg-white/20 rounded-full mx-auto mt-3 mb-1" />
            )}

            {/* Header */}
            <div className="flex items-center justify-between px-6 py-4 border-b border-black/5 dark:border-white/10">
              <div>
                <h2 id="sheet-title" className="text-scale-16 font-bold text-foreground tracking-tight">
                  {title}
                </h2>
                {description && (
                  <p className="text-scale-12 text-muted-foreground mt-0.5">{description}</p>
                )}
              </div>
              <button
                type="button"
                onClick={onClose}
                className="p-1.5 rounded-full hover:bg-black/5 dark:hover:bg-white/10 text-muted-foreground hover:text-foreground transition focus-visible:ring-2 focus-visible:ring-risk-teal"
                aria-label="Close sheet"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* Body */}
            <div className="p-6 overflow-y-auto max-h-[70vh]">{children}</div>
          </motion.div>
        </div>
      )}
    </AnimatePresence>
  );
};

