"use client";

import React, { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Search, MapPin, Waves, ShieldCheck, Compass, ArrowRight, CornerDownLeft, X } from "lucide-react";
import { cn } from "@/lib/utils";

export interface CommandItem {
  id: string;
  category: "Village" | "Basin" | "Sensor" | "Shelter";
  title: string;
  subtitle: string;
  risk?: string;
  onSelect: () => void;
}

export interface CommandPaletteProps {
  isOpen: boolean;
  onClose: () => void;
  items?: CommandItem[];
}

export const CommandPalette: React.FC<CommandPaletteProps> = ({
  isOpen,
  onClose,
  items = [],
}) => {
  const [query, setQuery] = useState("");
  const [selectedIndex, setSelectedIndex] = useState(0);

  const defaultItems: CommandItem[] = items.length
    ? items
    : [
        {
          id: "1",
          category: "Village",
          title: "Raini (Chamoli)",
          subtitle: "Elevation: 2045m • Slope: 32.5°",
          risk: "High",
          onSelect: () => {},
        },
        {
          id: "2",
          category: "Village",
          title: "Joshimath Town",
          subtitle: "Population: 16,700 • Elevation: 1875m",
          risk: "Moderate",
          onSelect: () => {},
        },
        {
          id: "3",
          category: "Village",
          title: "Chooralmala (Wayanad)",
          subtitle: "Elevation: 860m • River: Iruvanji",
          risk: "Very High",
          onSelect: () => {},
        },
        {
          id: "4",
          category: "Sensor",
          title: "RIV-ALK-01 Vishnuprayag Gauge",
          subtitle: "Alaknanda Basin [SIMULATED]",
          risk: "Low",
          onSelect: () => {},
        },
        {
          id: "5",
          category: "Shelter",
          title: "Helang Higher Secondary School",
          subtitle: "Safe Elevation: 1610m • Capacity: 350",
          onSelect: () => {},
        },
        {
          id: "6",
          category: "Basin",
          title: "Mandakini Basin (Kedarnath / Rudraprayag)",
          subtitle: "Uttarakhand Western Himalayas",
          onSelect: () => {},
        },
      ];

  const filtered = defaultItems.filter(
    (item) =>
      item.title.toLowerCase().includes(query.toLowerCase()) ||
      item.subtitle.toLowerCase().includes(query.toLowerCase()) ||
      item.category.toLowerCase().includes(query.toLowerCase())
  );

  useEffect(() => {
    setSelectedIndex(0);
  }, [query]);

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key === "k") {
        e.preventDefault();
        if (isOpen) onClose();
      }
      if (!isOpen) return;

      if (e.key === "ArrowDown") {
        e.preventDefault();
        setSelectedIndex((prev) => (prev + 1) % Math.max(1, filtered.length));
      } else if (e.key === "ArrowUp") {
        e.preventDefault();
        setSelectedIndex((prev) => (prev - 1 + filtered.length) % Math.max(1, filtered.length));
      } else if (e.key === "Enter" && filtered[selectedIndex]) {
        e.preventDefault();
        filtered[selectedIndex].onSelect();
        onClose();
      } else if (e.key === "Escape") {
        onClose();
      }
    };

    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [isOpen, onClose, filtered, selectedIndex]);

  return (
    <AnimatePresence>
      {isOpen && (
        <div className="fixed inset-0 z-50 flex items-start justify-center pt-20 px-4">
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={onClose}
            className="fixed inset-0 bg-black/50 dark:bg-black/70 backdrop-blur-md"
            aria-hidden="true"
          />

          <motion.div
            initial={{ scale: 0.95, opacity: 0, y: -10 }}
            animate={{ scale: 1, opacity: 1, y: 0 }}
            exit={{ scale: 0.95, opacity: 0, y: -10 }}
            transition={{ type: "spring", stiffness: 300, damping: 25 }}
            role="combobox"
            aria-expanded="true"
            aria-haspopup="listbox"
            className="relative z-10 w-full max-w-xl glass-surface-3 glass-sheen rounded-glass-lg border border-white/20 dark:border-white/15 shadow-glass-3 overflow-hidden"
          >
            {/* Search Input Bar */}
            <div className="flex items-center px-4 py-3.5 border-b border-black/10 dark:border-white/10 gap-3">
              <Search className="w-5 h-5 text-muted-foreground shrink-0" />
              <input
                type="text"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="Search villages, river gauges, shelters, or basins..."
                className="w-full bg-transparent text-scale-16 text-foreground placeholder:text-muted-foreground focus:outline-none"
                autoFocus
              />
              <span className="hidden sm:inline-flex items-center gap-0.5 px-2 py-0.5 rounded text-[11px] font-mono text-muted-foreground bg-black/5 dark:bg-white/10 border border-black/10 dark:border-white/10">
                ESC
              </span>
            </div>

            {/* List */}
            <div role="listbox" className="p-2 max-h-80 overflow-y-auto divide-y divide-black/5 dark:divide-white/5">
              {filtered.length > 0 ? (
                filtered.map((item, idx) => {
                  const isSelected = idx === selectedIndex;
                  return (
                    <div
                      key={item.id}
                      role="option"
                      aria-selected={isSelected}
                      onClick={() => {
                        item.onSelect();
                        onClose();
                      }}
                      onMouseEnter={() => setSelectedIndex(idx)}
                      className={cn(
                        "flex items-center justify-between p-3 rounded-glass-sm cursor-pointer transition-colors",
                        isSelected
                          ? "bg-risk-teal/15 dark:bg-risk-teal/20 text-foreground"
                          : "text-muted-foreground hover:text-foreground"
                      )}
                    >
                      <div className="flex items-center gap-3">
                        <div className="p-2 rounded-lg bg-black/5 dark:bg-white/10 text-foreground">
                          {item.category === "Village" && <MapPin className="w-4 h-4 text-sky-400" />}
                          {item.category === "Sensor" && <Waves className="w-4 h-4 text-amber-400" />}
                          {item.category === "Shelter" && <ShieldCheck className="w-4 h-4 text-emerald-400" />}
                          {item.category === "Basin" && <Compass className="w-4 h-4 text-purple-400" />}
                        </div>
                        <div>
                          <div className="text-scale-14 font-semibold text-foreground">
                            {item.title}
                          </div>
                          <div className="text-scale-12 text-muted-foreground">{item.subtitle}</div>
                        </div>
                      </div>

                      <div className="flex items-center gap-2">
                        {item.risk && (
                          <span className="text-[11px] font-bold px-2 py-0.5 rounded-full bg-black/5 dark:bg-white/10 text-foreground">
                            {item.risk}
                          </span>
                        )}
                        {isSelected && (
                          <CornerDownLeft className="w-3.5 h-3.5 text-risk-teal shrink-0" />
                        )}
                      </div>
                    </div>
                  );
                })
              ) : (
                <div className="py-8 text-center text-scale-14 text-muted-foreground">
                  No matching locations or sensors found.
                </div>
              )}
            </div>
          </motion.div>
        </div>
      )}
    </AnimatePresence>
  );
};

