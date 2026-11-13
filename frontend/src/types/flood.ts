export type RiskLevel = 'Low' | 'Moderate' | 'High' | 'Very High';

export type RiskFilter = 'All' | RiskLevel;

export interface Village {
  id: number;
  name: string;
  lat: number;
  lon: number;
  population: number;
  risk: RiskLevel;
  score: number;
  rainfall_mm_24h: number;
  updated: string;
}

export interface Alert {
  id: number;
  village: string;
  risk: RiskLevel;
  message: string;
  time: string;
}

export interface SummaryMetrics {
  liveAlertsCount: number;
  atRiskVillagesCount: number;
  peoplePotentiallyAffected: number;
}

export interface ApiActionResult<T = unknown> {
  ok: boolean;
  offline?: boolean;
  message?: string;
  data?: T;
}
