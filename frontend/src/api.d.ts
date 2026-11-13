import type { Alert, ApiActionResult, Village } from './types/flood';

export function isMockMode(): boolean;
export function getVillages(): Promise<Village[]>;
export function getAlerts(): Promise<Alert[]>;
export function simulate(village_id: number, rainfall_mm: number): Promise<ApiActionResult<Village>>;
export function reset(): Promise<ApiActionResult<{ status: string }>>;
