import type { Alert } from '../types/flood';
import { formatUtcTime, getRiskVisualConfig } from '../utils/floodStats';

interface AlertsFeedProps {
  alerts: Alert[];
  selectedVillageName: string | null;
  onSelectAlertVillage: (villageName: string) => void;
}

export function AlertsFeed({
  alerts,
  selectedVillageName,
  onSelectAlertVillage,
}: AlertsFeedProps) {
  return (
    <section
      aria-label="Live flood alerts"
      className="rounded-lg border border-[#4cd7f6]/15 bg-[#111A24]/90 p-3.5"
    >
      <div className="flex items-center justify-between gap-2 border-b border-[#3d494c]/40 pb-2">
        <h2 className="text-sm font-semibold text-[#dde2f0]">Live Alerts</h2>
        <span className="font-mono text-xs tabular-nums text-[#869397]">
          {alerts.length} active · newest first
        </span>
      </div>

      {alerts.length === 0 ? (
        <p className="py-4 text-xs text-[#869397]">No active flood alerts.</p>
      ) : (
        <ul className="divide-y divide-[#3d494c]/35">
          {alerts.map((alert) => {
            const visual = getRiskVisualConfig(alert.risk);
            const isSelected = selectedVillageName === alert.village;
            return (
              <li key={alert.id} className="py-1.5 first:pt-2 last:pb-0.5">
                <button
                  type="button"
                  onClick={() => onSelectAlertVillage(alert.village)}
                  aria-label={`Inspect ${alert.village} alert: ${alert.risk} risk`}
                  className={`w-full rounded-md p-2 text-left transition-colors focus-visible:outline-2 focus-visible:outline-[#4cd7f6] ${
                    isSelected
                      ? 'bg-[#1B2636] ring-1 ring-[#4cd7f6]/40'
                      : 'hover:bg-[#161c25]'
                  }`}
                >
                  <div className="flex items-center justify-between gap-2">
                    <span className="text-sm font-semibold text-[#dde2f0]">{alert.village}</span>
                    <span className={`rounded px-1.5 py-0.5 font-mono text-[11px] font-semibold whitespace-nowrap ${visual.badgeClass}`}>
                      {visual.symbol} {alert.risk}
                    </span>
                  </div>
                  <p className="mt-0.5 text-xs leading-snug text-[#bcc9cd]">{alert.message}</p>
                  <p className="mt-0.5 font-mono text-[11px] tabular-nums text-[#869397]">
                    {formatUtcTime(alert.time)}
                  </p>
                </button>
              </li>
            );
          })}
        </ul>
      )}
    </section>
  );
}
