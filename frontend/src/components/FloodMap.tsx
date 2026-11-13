import { useEffect, useMemo, useRef } from 'react';
import L from 'leaflet';
import { MapContainer, Marker, Popup, TileLayer, Tooltip, useMap } from 'react-leaflet';
import type { RiskLevel, Village } from '../types/flood';
import { countVillagesByRisk, formatNumber, formatUtcTime, getRiskVisualConfig } from '../utils/floodStats';

interface FloodMapProps {
  villages: Village[];
  allVillages: Village[];
  selectedVillage: Village | null;
  onSelectVillage: (village: Village) => void;
  fitBoundsTrigger: number;
}

const DEFAULT_CENTER: [number, number] = [30.38, 78.72];
const DEFAULT_ZOOM = 9;
const LEGEND_ORDER: RiskLevel[] = ['Very High', 'High', 'Moderate', 'Low'];

function createRiskMarkerIcon(risk: RiskLevel, isSelected: boolean): L.DivIcon {
  const visual = getRiskVisualConfig(risk);
  const size = isSelected ? 22 : 16;
  const ringShadow = isSelected
    ? `0 0 0 4px rgba(76, 215, 246, 0.35), 0 0 0 2px #0e141d`
    : `0 0 0 3px ${visual.hex}38, 0 2px 6px rgba(0, 0, 0, 0.6)`;

  return L.divIcon({
    className: 'custom-village-marker',
    iconSize: [size, size],
    iconAnchor: [size / 2, size / 2],
    popupAnchor: [0, -size / 2],
    html: `<span style="display:block;width:${size}px;height:${size}px;border-radius:9999px;background:${visual.hex};border:2px solid ${
      isSelected ? '#4cd7f6' : '#0e141d'
    };box-shadow:${ringShadow};"></span>`,
  });
}

interface MapViewportControllerProps {
  villages: Village[];
  selectedVillage: Village | null;
  fitBoundsTrigger: number;
}

function MapViewportController({
  villages,
  selectedVillage,
  fitBoundsTrigger,
}: MapViewportControllerProps) {
  const map = useMap();
  const hasInitialized = useRef(false);

  useEffect(() => {
    if (!hasInitialized.current && villages.length > 0) {
      hasInitialized.current = true;
      const bounds = L.latLngBounds(villages.map((v) => [v.lat, v.lon]));
      map.fitBounds(bounds, { padding: [36, 36], maxZoom: 11 });
    }
  }, [map, villages]);

  useEffect(() => {
    if (fitBoundsTrigger > 0 && villages.length > 0) {
      const bounds = L.latLngBounds(villages.map((v) => [v.lat, v.lon]));
      map.fitBounds(bounds, { padding: [36, 36], maxZoom: 11, animate: true });
    }
  }, [fitBoundsTrigger, map, villages]);

  useEffect(() => {
    if (selectedVillage) {
      map.panTo([selectedVillage.lat, selectedVillage.lon], { animate: true });
    }
  }, [map, selectedVillage]);

  return null;
}

export function FloodMap({
  villages,
  allVillages,
  selectedVillage,
  onSelectVillage,
  fitBoundsTrigger,
}: FloodMapProps) {
  const counts = useMemo(() => countVillagesByRisk(allVillages), [allVillages]);

  return (
    <div
      data-testid="flood-map-container"
      className="relative h-[45vh] min-h-[340px] w-full overflow-hidden rounded-lg border border-[#4cd7f6]/20 bg-[#080e17] lg:h-full lg:min-h-[520px]"
    >
      <MapContainer
        center={DEFAULT_CENTER}
        zoom={DEFAULT_ZOOM}
        scrollWheelZoom
        className="h-full w-full z-0"
      >
        <TileLayer
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          className="tactical-osm-tiles"
        />

        <MapViewportController
          villages={villages}
          selectedVillage={selectedVillage}
          fitBoundsTrigger={fitBoundsTrigger}
        />

        {villages.map((village) => {
          const isSelected = selectedVillage?.id === village.id;
          const visual = getRiskVisualConfig(village.risk);
          return (
            <Marker
              key={village.id}
              position={[village.lat, village.lon]}
              icon={createRiskMarkerIcon(village.risk, isSelected)}
              title={`${village.name} — ${village.risk} risk`}
              alt={`${village.name} (${village.risk} risk)`}
              eventHandlers={{
                click: () => onSelectVillage(village),
              }}
            >
              <Tooltip direction="top" offset={[0, -8]} className="tactical-tooltip">
                <span>
                  {village.name} · {village.risk} ({village.rainfall_mm_24h} mm)
                </span>
              </Tooltip>
              <Popup>
                <div className="min-w-[232px] space-y-2 text-xs text-[#dde2f0]">
                  <div className="flex items-center justify-between gap-2 border-b border-[#3d494c]/50 pb-1.5 pr-5">
                    <span className="truncate text-sm font-semibold text-[#dde2f0]">{village.name}</span>
                    <span className={`shrink-0 rounded px-1.5 py-0.5 font-mono text-[10px] font-semibold whitespace-nowrap ${visual.badgeClass}`}>
                      {visual.symbol} {village.risk}
                    </span>
                  </div>
                  <dl className="grid grid-cols-[auto_1fr] gap-x-4 gap-y-1 font-mono text-[11px] tabular-nums">
                    <dt className="text-[#869397]">Score</dt>
                    <dd className="text-right font-semibold text-[#dde2f0]">{village.score.toFixed(2)}</dd>
                    <dt className="text-[#869397]">Rainfall (24h)</dt>
                    <dd className="text-right font-semibold text-[#4cd7f6]">{village.rainfall_mm_24h} mm</dd>
                    <dt className="text-[#869397]">Population</dt>
                    <dd className="text-right text-[#dde2f0]">{formatNumber(village.population)}</dd>
                    <dt className="text-[#869397]">Updated</dt>
                    <dd className="text-right whitespace-nowrap text-[#bcc9cd]">{formatUtcTime(village.updated)}</dd>
                  </dl>
                </div>
              </Popup>
            </Marker>
          );
        })}
      </MapContainer>

      {/* Risk Color Legend */}
      <div
        aria-label="Village risk marker legend"
        className="pointer-events-auto absolute bottom-2 left-2 z-[400] rounded-lg border border-[#4cd7f6]/20 bg-[#111A24]/92 px-2.5 py-1.5 backdrop-blur-md sm:bottom-3 sm:left-3 sm:px-3 sm:py-2"
      >
        <p className="mb-1 hidden font-mono text-[10px] font-semibold tracking-wider text-[#bcc9cd] sm:block">
          RISK LEGEND
        </p>
        <ul className="grid grid-cols-2 gap-x-3 gap-y-1 text-[11px] sm:flex sm:flex-wrap sm:items-center sm:gap-3 sm:text-xs">
          {LEGEND_ORDER.map((level) => {
            const visual = getRiskVisualConfig(level);
            return (
              <li key={level} className="flex items-center gap-1.5 whitespace-nowrap">
                <span
                  aria-hidden="true"
                  className="inline-block h-2.5 w-2.5 shrink-0 rounded-full"
                  style={{ backgroundColor: visual.hex }}
                />
                <span className="text-[#dde2f0]">{level}</span>
                <span className="font-mono text-[10px] tabular-nums text-[#869397] sm:text-[11px]">
                  ({counts[level]})
                </span>
              </li>
            );
          })}
        </ul>
      </div>
    </div>
  );
}
