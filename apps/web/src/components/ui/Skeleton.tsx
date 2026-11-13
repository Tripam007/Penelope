"use client";

import React from "react";
import { cn } from "@/lib/utils";

export interface SkeletonProps extends React.HTMLAttributes<HTMLDivElement> {
  radius?: "sm" | "md" | "lg" | "full";
  className?: string;
}

export const Skeleton: React.FC<SkeletonProps> = ({
  radius = "md",
  className,
  ...props
}) => {
  const radiusClass =
    radius === "sm"
      ? "rounded-glass-sm"
      : radius === "lg"
      ? "rounded-glass-lg"
      : radius === "full"
      ? "rounded-full"
      : "rounded-glass-md";

  return (
    <div
      className={cn(
        "animate-pulse bg-black/10 dark:bg-white/10 border border-black/5 dark:border-white/5",
        radiusClass,
        className
      )}
      aria-hidden="true"
      {...props}
    />
  );
};

