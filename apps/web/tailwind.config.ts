import type { Config } from "tailwindcss";

const config: Config = {
  darkMode: ["class"],
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: [
          "Inter",
          "-apple-system",
          "BlinkMacSystemFont",
          "SF Pro Display",
          "SF Pro Text",
          "Segoe UI",
          "Roboto",
          "sans-serif",
        ],
        mono: [
          "ui-monospace",
          "SFMono-Regular",
          "Menlo",
          "Monaco",
          "Consolas",
          "Liberation Mono",
          "monospace",
        ],
      },
      fontSize: {
        "scale-12": ["12px", { lineHeight: "16px", letterSpacing: "0" }],
        "scale-14": ["14px", { lineHeight: "20px", letterSpacing: "-0.006em" }],
        "scale-16": ["16px", { lineHeight: "24px", letterSpacing: "-0.011em" }],
        "scale-20": ["20px", { lineHeight: "28px", letterSpacing: "-0.017em" }],
        "scale-28": ["28px", { lineHeight: "36px", letterSpacing: "-0.022em" }],
        "scale-40": ["40px", { lineHeight: "48px", letterSpacing: "-0.025em" }],
        "scale-64": ["64px", { lineHeight: "72px", letterSpacing: "-0.03em" }],
      },
      borderRadius: {
        "glass-sm": "12px",
        "glass-md": "20px",
        "glass-lg": "28px",
      },
      colors: {
        background: "hsl(var(--background))",
        foreground: "hsl(var(--foreground))",
        card: {
          DEFAULT: "hsl(var(--card))",
          foreground: "hsl(var(--card-foreground))",
        },
        popover: {
          DEFAULT: "hsl(var(--popover))",
          foreground: "hsl(var(--popover-foreground))",
        },
        primary: {
          DEFAULT: "hsl(var(--primary))",
          foreground: "hsl(var(--primary-foreground))",
        },
        secondary: {
          DEFAULT: "hsl(var(--secondary))",
          foreground: "hsl(var(--secondary-foreground))",
        },
        muted: {
          DEFAULT: "hsl(var(--muted))",
          foreground: "hsl(var(--muted-foreground))",
        },
        accent: {
          DEFAULT: "hsl(var(--accent))",
          foreground: "hsl(var(--accent-foreground))",
        },
        destructive: {
          DEFAULT: "hsl(var(--destructive))",
          foreground: "hsl(var(--destructive-foreground))",
        },
        border: "hsl(var(--border))",
        input: "hsl(var(--input))",
        ring: "hsl(var(--ring))",
        // Apple visionOS Risk Palette (accessible, colour-blind-safe)
        risk: {
          low: "#34C759",
          moderate: "#FFD60A",
          high: "#FF9F0A",
          veryhigh: "#FF453A",
          teal: "#2DD4BF",
        },
      },
      boxShadow: {
        "glass-1": "0 8px 32px 0 rgba(0, 0, 0, 0.25)",
        "glass-2": "0 12px 40px 0 rgba(0, 0, 0, 0.35)",
        "glass-3": "0 16px 48px 0 rgba(0, 0, 0, 0.45)",
        "glass-light-1": "0 8px 32px 0 rgba(0, 0, 0, 0.08)",
        "glass-light-2": "0 12px 40px 0 rgba(0, 0, 0, 0.12)",
        "glass-light-3": "0 16px 48px 0 rgba(0, 0, 0, 0.16)",
      },
      backdropBlur: {
        "glass-1": "24px",
        "glass-2": "32px",
        "glass-3": "40px",
      },
    },
  },
  plugins: [],
};

export default config;
