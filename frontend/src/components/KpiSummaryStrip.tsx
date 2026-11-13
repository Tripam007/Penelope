import type { SummaryMetrics } from '../types/flood';
import { formatNumber } from '../utils/floodStats';

interface KpiSummaryStripProps {
  metrics: SummaryMetrics;
}

export function KpiSummaryStrip({ metrics }: KpiSummaryStripProps) {
  return (
    <section
      aria-label="Flood risk summary metrics"
      className="grid grid-cols-1 gap-3 sm:grid-cols-3 lg:gap-4"
    >
      <div className="rounded-lg border border-[#4cd7f6]/15 bg-[#111A24]/90 px-4 py-2.5">
        <p className="text-xs font-medium text-[#bcc9cd]">Live Alerts</p>
        <div className="mt-0.5 flex items-baseline justify-between gap-2">
          <p
            data-testid="metric-live-alerts"
            className="font-mono text-2xl font-bold tabular-nums text-[#dde2f0]"
          >
            {formatNumber(metrics.liveAlertsCount)}
          </p>
          <span className="font-mono text-xs text-[#f87171]">Active feed</span>
        </div>
      </div>

      <div className="rounded-lg border border-[#4cd7f6]/15 bg-[#111A24]/90 px-4 py-2.5">
        <p className="text-xs font-medium text-[#bcc9cd]">At-Risk Villages</p>
        <div className="mt-0.5 flex items-baseline justify-between gap-2">
          <p
            data-testid="metric-at-risk-villages"
            className="font-mono text-2xl font-bold tabular-nums text-[#dde2f0]"
          >
            {formatNumber(metrics.atRiskVillagesCount)}
          </p>
          <span className="font-mono text-xs text-[#fb923c]">High &amp; Very High</span>
        </div>
      </div>

      <div className="rounded-lg border border-[#4cd7f6]/15 bg-[#111A24]/90 px-4 py-2.5">
        <p className="text-xs font-medium text-[#bcc9cd]">People Potentially Affected</p>
        <div className="mt-0.5 flex items-baseline justify-between gap-2">
          <p
            data-testid="metric-people-affected"
            className="font-mono text-2xl font-bold tabular-nums text-[#4cd7f6]"
          >
            {formatNumber(metrics.peoplePotentiallyAffected)}
          </p>
          <span className="font-mono text-xs text-[#869397]">Combined population</span>
        </div>
      </div>
    </section>
  );
}
