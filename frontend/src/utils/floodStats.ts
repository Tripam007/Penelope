import type { Alert, RiskFilter, RiskLevel, SummaryMetrics, Village } from '../types/flood';

export interface RiskVisualConfig {
  label: RiskLevel;
  hex: string;
  markerBgClass: string;
  markerRingClass: string;
  badgeClass: string;
  textClass: string;
  symbol: string;
}

const RISK_CONFIG_MAP: Record<RiskLevel, RiskVisualConfig> = {
  Low: {
    label: 'Low',
    hex: '#10B981',
    markerBgClass: 'bg-[#10B981]',
    markerRingClass: 'ring-[#10B981]/35',
    badgeClass: 'bg-[#10B981]/12 text-[#34d399] border border-[#10B981]/40',
    textClass: 'text-[#34d399]',
    symbol: '●',
  },
  Moderate: {
    label: 'Moderate',
    hex: '#F59E0B',
    markerBgClass: 'bg-[#F59E0B]',
    markerRingClass: 'ring-[#F59E0B]/35',
    badgeClass: 'bg-[#F59E0B]/12 text-[#fbbf24] border border-[#F59E0B]/40',
    textClass: 'text-[#fbbf24]',
    symbol: '◆',
  },
  High: {
    label: 'High',
    hex: '#F97316',
    markerBgClass: 'bg-[#F97316]',
    markerRingClass: 'ring-[#F97316]/40',
    badgeClass: 'bg-[#F97316]/12 text-[#fb923c] border border-[#F97316]/45',
    textClass: 'text-[#fb923c]',
    symbol: '▲',
  },
  'Very High': {
    label: 'Very High',
    hex: '#EF4444',
    markerBgClass: 'bg-[#EF4444]',
    markerRingClass: 'ring-[#EF4444]/45',
    badgeClass: 'bg-[#EF4444]/15 text-[#f87171] border border-[#EF4444]/50',
    textClass: 'text-[#f87171]',
    symbol: '■',
  },
};

export function getRiskVisualConfig(risk: RiskLevel): RiskVisualConfig {
  return RISK_CONFIG_MAP[risk];
}

export function isAtRiskLevel(risk: RiskLevel): boolean {
  return risk === 'High' || risk === 'Very High';
}

export function computeSummaryMetrics(villages: Village[], alerts: Alert[]): SummaryMetrics {
  const atRiskVillages = villages.filter((v) => isAtRiskLevel(v.risk));
  const peoplePotentiallyAffected = atRiskVillages.reduce((sum, v) => sum + v.population, 0);

  return {
    liveAlertsCount: alerts.length,
    atRiskVillagesCount: atRiskVillages.length,
    peoplePotentiallyAffected,
  };
}

export function filterVillagesByRisk(villages: Village[], filter: RiskFilter): Village[] {
  if (filter === 'All') {
    return villages;
  }
  return villages.filter((v) => v.risk === filter);
}

export function countVillagesByRisk(villages: Village[]): Record<RiskLevel, number> {
  return villages.reduce<Record<RiskLevel, number>>(
    (acc, village) => {
      acc[village.risk] += 1;
      return acc;
    },
    { Low: 0, Moderate: 0, High: 0, 'Very High': 0 }
  );
}

export function formatUtcTime(isoString: string): string {
  const date = new Date(isoString);
  if (Number.isNaN(date.getTime())) {
    return isoString;
  }
  const yyyy = date.getUTCFullYear();
  const mm = String(date.getUTCMonth() + 1).padStart(2, '0');
  const dd = String(date.getUTCDate()).padStart(2, '0');
  const hh = String(date.getUTCHours()).padStart(2, '0');
  const min = String(date.getUTCMinutes()).padStart(2, '0');
  return `${yyyy}-${mm}-${dd} ${hh}:${min} UTC`;
}

export function formatNumber(value: number): string {
  return new Intl.NumberFormat('en-US').format(value);
}
