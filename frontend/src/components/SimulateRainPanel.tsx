import { CloudRain, RotateCcw } from 'lucide-react';
import type { Village } from '../types/flood';

interface SimulateRainPanelProps {
  villages: Village[];
  selectedVillageId: number;
  onVillageChange: (villageId: number) => void;
  rainfallMm: number;
  onRainfallChange: (rainfallMm: number) => void;
  onSimulate: () => void;
  onReset: () => void;
  isSubmitting: boolean;
}

export function SimulateRainPanel({
  villages,
  selectedVillageId,
  onVillageChange,
  rainfallMm,
  onRainfallChange,
  onSimulate,
  onReset,
  isSubmitting,
}: SimulateRainPanelProps) {
  const sliderPercent = Math.min(100, Math.max(0, (rainfallMm / 200) * 100));

  return (
    <section
      aria-label="Simulate Heavy Rain"
      className="rounded-lg border border-[#4cd7f6]/20 bg-[#111A24]/95 p-3.5"
    >
      <div className="flex items-center justify-between gap-2 border-b border-[#3d494c]/40 pb-2">
        <div className="flex items-center gap-2">
          <CloudRain className="h-4 w-4 text-[#4cd7f6]" aria-hidden="true" />
          <h2 className="text-sm font-semibold text-[#dde2f0]">Simulate Heavy Rain</h2>
        </div>
        <span className="font-mono text-xs tabular-nums text-[#869397]">0–200 mm</span>
      </div>

      <form
        className="mt-2.5 space-y-3"
        onSubmit={(e) => {
          e.preventDefault();
          onSimulate();
        }}
      >
        <div>
          <label
            htmlFor="simulate-village-select"
            className="block text-xs font-medium text-[#bcc9cd]"
          >
            Target Village
          </label>
          <select
            id="simulate-village-select"
            value={selectedVillageId}
            onChange={(e) => onVillageChange(Number(e.target.value))}
            className="mt-1 w-full rounded border border-[#3d494c]/80 bg-[#080e17] px-3 py-1.5 text-sm text-[#dde2f0] focus:border-[#06b6d4] focus:outline-none focus:ring-1 focus:ring-[#06b6d4]"
          >
            {villages.map((village) => (
              <option key={village.id} value={village.id}>
                {village.name} ({village.risk} · {village.rainfall_mm_24h} mm)
              </option>
            ))}
          </select>
        </div>

        <div>
          <div className="flex items-center justify-between gap-2">
            <label
              htmlFor="simulate-rainfall-slider"
              className="text-xs font-medium text-[#bcc9cd]"
            >
              Simulated 24h Rainfall
            </label>
            <output
              htmlFor="simulate-rainfall-slider"
              className="font-mono text-sm font-semibold tabular-nums text-[#4cd7f6]"
            >
              {rainfallMm} mm
            </output>
          </div>
          <input
            id="simulate-rainfall-slider"
            type="range"
            min={0}
            max={200}
            step={1}
            value={rainfallMm}
            onChange={(e) => onRainfallChange(Number(e.target.value))}
            style={{
              background: `linear-gradient(to right, #06b6d4 0%, #06b6d4 ${sliderPercent}%, #242a34 ${sliderPercent}%, #242a34 100%)`,
            }}
            className="rainfall-slider mt-2 w-full cursor-pointer"
          />
          <div className="mt-1 flex justify-between font-mono text-[10px] tabular-nums text-[#869397]">
            <span>0 mm</span>
            <span>100 mm</span>
            <span>200 mm</span>
          </div>
        </div>

        <div className="grid grid-cols-2 gap-2.5 pt-0.5">
          <button
            type="submit"
            disabled={isSubmitting || villages.length === 0}
            className="inline-flex items-center justify-center rounded bg-[#06b6d4] px-4 py-2 text-xs font-semibold text-[#003640] transition-colors hover:bg-[#22d3ee] disabled:cursor-not-allowed disabled:opacity-50 whitespace-nowrap focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[#4cd7f6]"
          >
            {isSubmitting ? 'Simulating...' : 'Simulate'}
          </button>

          <button
            type="button"
            disabled={isSubmitting}
            onClick={onReset}
            className="inline-flex items-center justify-center gap-1.5 rounded border border-[#06b6d4]/35 bg-[#1B2636]/75 px-4 py-2 text-xs font-semibold text-[#4cd7f6] transition-colors hover:border-[#4cd7f6] hover:bg-[#1B2636] disabled:cursor-not-allowed disabled:opacity-50 whitespace-nowrap focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[#4cd7f6]"
          >
            <RotateCcw className="h-3.5 w-3.5" aria-hidden="true" />
            Reset
          </button>
        </div>
      </form>
    </section>
  );
}
