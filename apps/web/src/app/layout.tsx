import type { Metadata, Viewport } from "next";
import "./globals.css";
import Providers from "./providers";

export const metadata: Metadata = {
  title: "PENELOPE - Flash-Flood Early Warning Platform",
  description: "Data today. Safer tomorrows. AI-powered flash-flood early warning platform for mountain regions (Himalayas & Western Ghats).",
  manifest: "/manifest.json",
};

export const viewport: Viewport = {
  themeColor: "#0284c7",
  width: "device-width",
  initialScale: 1,
  maximumScale: 1,
  userScalable: false,
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark">
      <head>
        <link rel="icon" href="/icon.svg" type="image/svg+xml" />
        <link rel="apple-touch-icon" href="/icon.svg" />
      </head>
      <body className="bg-slate-950 text-slate-100 antialiased overflow-hidden">
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}
