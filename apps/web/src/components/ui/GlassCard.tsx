"use client";

import React from "react";
import { motion, HTMLMotionProps } from "framer-motion";
import { cn } from "@/lib/utils";

export interface GlassCardProps extends HTMLMotionProps<"div"> {
  elevation?: 1 | 2 | 3;
  interactive?: boolean;
  sheen?: boolean;
  radius?: "sm" | "md" | "lg" | "full";
  className?: string;
  children: React.ReactNode;
}

export const GlassCard: React.FC<GlassCardProps> = ({
  elevation = 1,
  interactive = false,
  sheen = true,
  radius = "md",
  className,
  children,
  ...props
}) => {
  const elevationClass =
    elevation === 3
      ? "glass-surface-3"
      : elevation === 2
      ? "glass-surface-2"
      : "glass-surface-1";

  const radiusClass =
    radius === "sm"
      ? "rounded-glass-sm"
      : radius === "lg"
      ? "rounded-glass-lg"
      : radius === "full"
      ? "rounded-full"
      : "rounded-glass-md";

  return (
    <motion.div
      whileHover={
        interactive
          ? {
              y: -2,
              scale: 1.008,
              transition: { type: "spring", stiffness: 260, damping: 24 },
            }
          : undefined
      }
      whileTap={
        interactive
          ? {
              scale: 0.985,
              transition: { type: "spring", stiffness: 350, damping: 20 },
            }
          : undefined
      }
      className={cn(
        elevationClass,
        radiusClass,
        sheen && "glass-sheen",
        "relative overflow-hidden transition-colors duration-200",
        interactive && "cursor-pointer select-none",
        className
      )}
      {...props}
    >
      {children}
    </motion.div>
  );
};

