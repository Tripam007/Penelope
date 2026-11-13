"use client";

import React, { useEffect, useRef, useState } from "react";
import maplibregl, { Map as MapLibreMap, Marker, Popup } from "maplibre-gl";
import "maplibre-gl/dist/maplibre-gl.css";
import { usePenelopeStore } from "@/lib/store";
import { getRiskColorClass } from "@/lib/utils";
import { Compass, Layers, AlertTriangle, ShieldCheck, Waves } from "lucide-react";

interface MapProps {
  geoJsonData: any;
}

export default function MapLibreFloodMap({ geoJsonData }: MapProps) {
  const mapContainerRef = useRef<HTMLDivElement>(null);
  const mapRef = useRef<MapLibreMap | null>(null);
  const markersRef = useRef<Marker[]>([]);
  const { setSelectedVillageId, setSelectedSensorCode, language } = usePenelopeStore();

  const [activeLayer, setActiveLayer] = useState<"all" | "high_risk" | "sensors" | "shelters">("all");

  useEffect(() => {
    if (!mapContainerRef.current) return;

    const defaultLat = parseFloat(process.env.NEXT_PUBLIC_DEFAULT_LAT || "30.3753");
    const defaultLon = parseFloat(process.env.NEXT_PUBLIC_DEFAULT_LON || "79.3242");
    const defaultZoom = parseFloat(process.env.NEXT_PUBLIC_DEFAULT_ZOOM || "8.5");
    const mapStyle = process.env.NEXT_PUBLIC_MAP_STYLE || "https://basemaps.cartocdn.com/gl/dark-matter-gl-style/style.json";

    const map = new maplibregl.Map({
      container: mapContainerRef.current,
      style: mapStyle,
      center: [defaultLon, defaultLat],
      zoom: defaultZoom,
      pitch: 45, // 3D mountain perspective
      bearing: -15,
      attributionControl: false,
    });

    map.addControl(new maplibregl.NavigationControl({ visualizePitch: true }), "top-right");
    mapRef.current = map;

    map.on("load", () => {
      // Add evacuation line source and layer
      if (geoJsonData) {
        renderMapFeatures(map, geoJsonData);
      }
    });

    return () => {
      markersRef.current.forEach((m) => m.remove());
      markersRef.current = [];
      map.remove();
    };
  }, []);

  // Update markers when geoJsonData changes
  useEffect(() => {
    if (mapRef.current && geoJsonData) {
      renderMapFeatures(mapRef.current, geoJsonData);
    }
  }, [geoJsonData, activeLayer, language]);

  const renderMapFeatures = (map: MapLibreMap, data: any) => {
    // Clear old markers
    markersRef.current.forEach((m) => m.remove());
    markersRef.current = [];

    if (!data || !data.features) return;

    data.features.forEach((feature: any) => {
      const { layer_type } = feature.properties;
      const coords = feature.geometry.coordinates;

      if (layer_type === "village") {
        if (activeLayer === "sensors" || activeLayer === "shelters") return;
        if (activeLayer === "high_risk" && !["High", "Very High"].includes(feature.properties.risk_level)) return;

        const riskColor = getRiskColorClass(feature.properties.risk_level);
        const isHighOrVeryHigh = ["High", "Very High"].includes(feature.properties.risk_level);

        // Custom HTML Marker Element
        const el = document.createElement("div");
        el.className = "cursor-pointer group flex flex-col items-center";
        el.innerHTML = `
          <div class="relative flex items-center justify-center">
            ${isHighOrVeryHigh ? `<span class="animate-ping absolute inline-flex h-7 w-7 rounded-full bg-red-400 opacity-75"></span>` : ""}
            <div class="h-5 w-5 rounded-full border-2 border-slate-900 shadow-lg flex items-center justify-center text-[10px] font-bold text-white transition-transform group-hover:scale-125" style="background-color: ${riskColor.hex}">
            </div>
          </div>
          <div class="mt-1 px-1.5 py-0.5 rounded bg-slate-950/85 backdrop-blur border border-slate-800 text-[10px] font-medium text-slate-200 shadow-md whitespace-nowrap pointer-events-none">
            ${language === "hi" && feature.properties.hindi_name ? feature.properties.hindi_name : feature.properties.name}
            <span class="ml-1 text-[9px] font-bold" style="color: ${riskColor.hex}">
              ${Math.round(feature.properties.risk_score * 100)}%
            </span>
          </div>
        `;

        el.addEventListener("click", () => {
          setSelectedVillageId(feature.properties.id);
        });

        const marker = new maplibregl.Marker({ element: el })
          .setLngLat(coords)
          .addTo(map);

        markersRef.current.push(marker);
      } else if (layer_type === "sensor") {
        if (activeLayer === "shelters" || activeLayer === "high_risk") return;

        const isSimulated = feature.properties.is_simulated || feature.properties.source === "simulated";
        const dangerRatio = feature.properties.danger_ratio || 0.4;
        const sensorColor = dangerRatio >= 0.85 ? "#ef4444" : dangerRatio >= 0.65 ? "#f59e0b" : "#38bdf8";

        const el = document.createElement("div");
        el.className = "cursor-pointer group flex flex-col items-center";
        el.innerHTML = `
          <div class="relative flex items-center justify-center">
            <div class="h-6 w-6 rounded-md bg-slate-950 border border-slate-700 shadow-xl flex items-center justify-center transition-transform group-hover:scale-125">
              <svg class="w-3.5 h-3.5" style="color: ${sensorColor}" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M13 10V3L4 14h7v7l9-11h-7z" />
              </svg>
            </div>
            ${isSimulated ? `
              <span class="absolute -top-2 -right-3 bg-amber-500 text-slate-950 font-black text-[8px] px-1 rounded-sm shadow border border-amber-300">
                SIM
              </span>
            ` : ""}
          </div>
          <div class="mt-1 px-1.5 py-0.5 rounded bg-slate-950/90 border border-cyan-900/60 text-[9px] font-mono text-cyan-300 shadow whitespace-nowrap">
            ${feature.properties.water_level_m}m
          </div>
        `;

        const popup = new maplibregl.Popup({ offset: 15 }).setHTML(`
          <div class="p-2 text-slate-900">
            <div class="flex items-center gap-1.5 font-bold text-xs border-b pb-1 mb-1.5">
              <span>${feature.properties.name}</span>
              ${isSimulated ? `<span class="bg-amber-100 text-amber-800 text-[9px] px-1 rounded font-bold">SIMULATED</span>` : ""}
            </div>
            <div class="text-[11px] space-y-0.5">
              <div>River: <b>${feature.properties.river_name}</b></div>
              <div>Water Level: <b class="text-cyan-700">${feature.properties.water_level_m} m</b></div>
              <div>Danger Mark: <b>${feature.properties.danger_level_m} m</b></div>
              <div>Warning Mark: <b>${feature.properties.warning_level_m} m</b></div>
            </div>
          </div>
        `);

        el.addEventListener("click", () => {
          setSelectedSensorCode(feature.properties.sensor_code);
        });

        const marker = new maplibregl.Marker({ element: el })
          .setLngLat(coords)
          .setPopup(popup)
          .addTo(map);

        markersRef.current.push(marker);
      } else if (layer_type === "shelter") {
        if (activeLayer === "sensors" || activeLayer === "high_risk") return;

        const el = document.createElement("div");
        el.className = "cursor-pointer group flex flex-col items-center";
        el.innerHTML = `
          <div class="h-5 w-5 rounded-full bg-emerald-950 border border-emerald-400 shadow flex items-center justify-center transition-transform group-hover:scale-125">
            <span class="text-[9px] font-bold text-emerald-400">⛺</span>
          </div>
        `;

        const popup = new maplibregl.Popup({ offset: 15 }).setHTML(`
          <div class="p-2 text-slate-900">
            <div class="font-bold text-xs border-b pb-1 mb-1 text-emerald-800">
              ${language === "hi" && feature.properties.hindi_name ? feature.properties.hindi_name : feature.properties.name}
            </div>
            <div class="text-[11px] space-y-0.5">
              <div>Type: Safe Relief Evacuation Shelter</div>
              <div>Capacity: <b>${feature.properties.capacity} Persons</b></div>
              <div>Safe Elevation: <b>${feature.properties.elevation_m} m</b></div>
              <div>Contact: <b>${feature.properties.contact_person || "Relief Officer"}</b></div>
            </div>
          </div>
        `);

        const marker = new maplibregl.Marker({ element: el })
          .setLngLat(coords)
          .setPopup(popup)
          .addTo(map);

        markersRef.current.push(marker);
      }
    });

    // Render evacuation LineStrings
    const lineFeatures = data.features.filter((f: any) => f.properties.layer_type === "evacuation_route");
    const lineGeoJson = {
      type: "FeatureCollection",
      features: lineFeatures,
    };

    if (map.getSource("evacuation-routes")) {
      (map.getSource("evacuation-routes") as any).setData(lineGeoJson);
    } else {
      map.addSource("evacuation-routes", {
        type: "geojson",
        data: lineGeoJson as any,
      });

      map.addLayer({
        id: "evacuation-routes-line",
        type: "line",
        source: "evacuation-routes",
        layout: {
          "line-join": "round",
          "line-cap": "round",
        },
        paint: {
          "line-color": "#38bdf8",
          "line-width": 2,
          "line-dasharray": [2, 2],
          "line-opacity": 0.7,
        },
      });
    }
  };

  const focusBasin = (lat: number, lon: number, zoom: number = 10) => {
    mapRef.current?.flyTo({
      center: [lon, lat],
      zoom: zoom,
      pitch: 50,
      duration: 1800,
    });
  };

  return (
    <div className="relative w-full h-full overflow-hidden bg-slate-950">
      {/* MapLibre Canvas Container */}
      <div ref={mapContainerRef} className="w-full h-full" />

      {/* Layer Filter Toolbar */}
      <div className="absolute top-4 left-4 z-10 flex items-center gap-1.5 p-1 rounded-xl bg-slate-950/85 backdrop-blur-md border border-slate-800 shadow-2xl">
        <button
          onClick={() => setActiveLayer("all")}
          className={`px-3 py-1.5 rounded-lg text-xs font-medium transition ${
            activeLayer === "all" ? "bg-sky-500 text-white shadow" : "text-slate-400 hover:text-white"
          }`}
        >
          All Layers
        </button>
        <button
          onClick={() => setActiveLayer("high_risk")}
          className={`px-3 py-1.5 rounded-lg text-xs font-medium transition flex items-center gap-1 ${
            activeLayer === "high_risk" ? "bg-red-500/20 text-red-400 border border-red-500/50" : "text-slate-400 hover:text-white"
          }`}
        >
          <AlertTriangle className="w-3.5 h-3.5" />
          High Risk Only
        </button>
        <button
          onClick={() => setActiveLayer("sensors")}
          className={`px-3 py-1.5 rounded-lg text-xs font-medium transition flex items-center gap-1 ${
            activeLayer === "sensors" ? "bg-cyan-500/20 text-cyan-400 border border-cyan-500/50" : "text-slate-400 hover:text-white"
          }`}
        >
          <Waves className="w-3.5 h-3.5" />
          Sensors
        </button>
        <button
          onClick={() => setActiveLayer("shelters")}
          className={`px-3 py-1.5 rounded-lg text-xs font-medium transition flex items-center gap-1 ${
            activeLayer === "shelters" ? "bg-emerald-500/20 text-emerald-400 border border-emerald-500/50" : "text-slate-400 hover:text-white"
          }`}
        >
          <ShieldCheck className="w-3.5 h-3.5" />
          Shelters
        </button>
      </div>

      {/* Basin Hotspot Quick Jumps */}
      <div className="absolute top-4 right-16 z-10 hidden sm:flex items-center gap-2 p-1 rounded-xl bg-slate-950/80 backdrop-blur border border-slate-800 text-xs">
        <span className="text-[10px] uppercase font-bold text-slate-500 px-2">Basins:</span>
        <button
          onClick={() => focusBasin(30.5543, 79.5442, 9.5)}
          className="px-2 py-1 rounded bg-slate-900 hover:bg-slate-800 text-slate-300 transition"
        >
          Chamoli
        </button>
        <button
          onClick={() => focusBasin(30.45, 79.05, 9.5)}
          className="px-2 py-1 rounded bg-slate-900 hover:bg-slate-800 text-slate-300 transition"
        >
          Mandakini
        </button>
        <button
          onClick={() => focusBasin(11.53, 76.13, 10.5)}
          className="px-2 py-1 rounded bg-slate-900 hover:bg-slate-800 text-slate-300 transition"
        >
          Wayanad Ghats
        </button>
      </div>

      {/* Risk Legend Card */}
      <div className="absolute bottom-6 left-4 z-10 p-3 rounded-xl bg-slate-950/90 backdrop-blur-md border border-slate-800 shadow-2xl text-xs space-y-2 max-w-[210px]">
        <div className="font-semibold text-slate-300 flex items-center justify-between text-[11px] uppercase tracking-wider">
          <span>Flood Hazard Tier</span>
          <span className="text-[9px] text-slate-500">IMD/GloFAS</span>
        </div>
        <div className="space-y-1.5 text-[11px]">
          <div className="flex items-center gap-2">
            <span className="w-2.5 h-2.5 rounded-full bg-emerald-500"></span>
            <span className="text-slate-300">Low Risk (&lt;25%)</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="w-2.5 h-2.5 rounded-full bg-amber-500"></span>
            <span className="text-slate-300">Moderate (25-55%)</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="w-2.5 h-2.5 rounded-full bg-orange-500"></span>
            <span className="text-slate-300">High Risk (55-80%)</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="w-2.5 h-2.5 rounded-full bg-red-500 animate-pulse"></span>
            <span className="text-slate-300 font-bold">Very High (&gt;80%)</span>
          </div>
        </div>
        <div className="pt-1.5 border-t border-slate-800 flex items-center justify-between text-[10px] text-slate-400">
          <span className="flex items-center gap-1">
            <span className="bg-amber-500 text-slate-950 text-[8px] font-black px-1 rounded">SIM</span>
            <span>Simulated Sensor</span>
          </span>
        </div>
      </div>
    </div>
  );
}

