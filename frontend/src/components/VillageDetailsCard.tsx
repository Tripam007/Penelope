import { MapPin, X } from 'lucide-react';
import type { Village } from '../types/flood';
import { formatNumber, formatUtcTime, getRiskVisualConfig } from '../utils/floodStats';

interface VillageDetailsCardProps {
  village: Village | null;
  onClearSelection: () => void;
}

export function VillageDetailsCard({ village, onClearSelection }: VillageDetailsCardProps) {
  if (!village) {
    return (
      <section
        aria-label="Village details"
        className="rounded-lg border border-[#4cd7f6]/15 bg-[#111A24]/90 p-4"
      >
        <div className="flex items-center justify-between gap-2">
          <h2 className="text-sm font-semibold text-[#dde2f0]">Village Details</h2>
        </div>
        <p className="mt-2 text-xs leading-relaxed text-[#869397]">
          Click any village marker on the map or select an alert below to inspect its current risk score, 24h rainfall, population, and coordinates.
        </p>
      </section>
    );
  }

  const visual = getRiskVisualConfig(village.risk);
  const scorePercent = Math.min(100, Math.max(0, Math.round(village.score * 100)));

  return (
    <section
      aria-label={`Details for ${village.name}`}
      data-testid="village-details-card"
      className="rounded-lg border border-[#4cd7f6]/25 bg-[#111A24]/95 p-3.5"
    >
      <div className="flex items-start justify-between gap-3 border-b border-[#3d494c]/40 pb-2.5">
        <div className="min-w-0">
          <div className="flex items-center gap-2">
            <MapPin className="h-4 w-4 shrink-0 text-[#4cd7f6]" aria-hidden="true" />
            <h2 className="truncate text-base font-semibold text-[#dde2f0]">{village.name}</h2>
          </div>
          <p className="mt-0.5 font-mono text-xs tabular-nums text-[#869397]">
            {village.lat.toFixed(4)}° N, {village.lon.toFixed(4)}° E
          </p>
        </div>

        <div className="flex items-center gap-2 shrink-0">
          <span className={`rounded px-2 py-0.5 font-mono text-xs font-semibold whitespace-nowrap ${visual.badgeClass}`}>
            {visual.symbol} {village.risk}
          </span>
          <button
            type="button"
            onClick={onClearSelection}
            aria-label={`Close details for ${village.name}`}
            className="rounded p-1 text-[#869397] transition-colors hover:bg-[#1B2636] hover:text-[#dde2f0] focus-visible:outline-2 focus-visible:outline-[#4cd7f6]"
          >
            <X className="h-4 w-4" aria-hidden="true" />
          </button>
        </div>
      </div>

      <div className="mt-2.5">
        <div className="mb-1 flex items-center justify-between text-xs">
          <span className="text-[#bcc9cd]">Risk Score</span>
          <span className="font-mono font-semibold tabular-nums text-[#dde2f0]">
            {village.score.toFixed(2)} / 1.00
          </span>
        </div>
        <div className="h-1.5 w-full overflow-hidden rounded bg-[#242a34]">
          <div
            className="h-full rounded transition-all duration-200"
            style={{ width: `${scorePercent}%`, backgroundColor: visual.hex }}
          />
        </div>
      </div>

      <dl className="mt-2.5 grid grid-cols-[1fr_1fr_auto] gap-x-3 gap-y-1 border-t border-[#3d494c]/40 pt-2.5">
        <div>
          <dt className="text-[11px] text-[#869397]">24h Rainfall</dt>
          <dd className="mt-0.5 font-mono text-sm font-semibold tabular-nums text-[#4cd7f6]">
            {village.rainfall_mm_24h} mm
          </dd>
        </div>
        <div>
          <dt className="text-[11px] text-[#869397]">Population</dt>
          <dd className="mt-0.5 font-mono text-sm font-semibold tabular-nums text-[#dde2f0]">
            {formatNumber(village.population)}
          </dd>
        </div>
        <div className="text-right">
          <dt className="text-[11px] text-[#869397]">Updated</dt>
          <dd className="mt-0.5 font-mono text-xs tabular-nums whitespace-nowrap text-[#bcc9cd]">
            {formatUtcTime(village.updated)}
          </dd>
        </div>
      </dl>
    </section>
  );
}
