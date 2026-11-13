import test from 'node:test';
import assert from 'node:assert/strict';
import {
  computeSummaryMetrics,
  countVillagesByRisk,
  filterVillagesByRisk,
  formatUtcTime,
  getRiskVisualConfig,
} from './floodStats';
import type { Alert, Village } from '../types/flood';

const sampleVillages: Village[] = [
  {
    id: 1,
    name: 'Kedarpur',
    lat: 30.3,
    lon: 78.0,
    population: 1200,
    risk: 'Very High',
    score: 0.86,
    rainfall_mm_24h: 148,
    updated: '2026-11-13T10:05:00Z',
  },
  {
    id: 2,
    name: 'Joshimath',
    lat: 30.5506,
    lon: 79.566,
    population: 1850,
    risk: 'High',
    score: 0.68,
    rainfall_mm_24h: 96,
    updated: '2026-11-13T09:58:00Z',
  },
  {
    id: 3,
    name: 'Devprayag',
    lat: 30.1459,
    lon: 78.5993,
    population: 1640,
    risk: 'Moderate',
    score: 0.41,
    rainfall_mm_24h: 54,
    updated: '2026-11-13T09:45:00Z',
  },
  {
    id: 4,
    name: 'Srinagar',
    lat: 30.2247,
    lon: 78.7986,
    population: 3100,
    risk: 'Low',
    score: 0.18,
    rainfall_mm_24h: 19,
    updated: '2026-11-13T09:30:00Z',
  },
];

const sampleAlerts: Alert[] = [
  {
    id: 1,
    village: 'Kedarpur',
    risk: 'Very High',
    message: 'Evacuate low-lying areas immediately',
    time: '2026-11-13T10:05:00Z',
  },
  {
    id: 2,
    village: 'Joshimath',
    risk: 'High',
    message: 'High surface runoff warning',
    time: '2026-11-13T09:58:00Z',
  },
];

test('computeSummaryMetrics counts alerts, High + Very High villages, and sums their population', () => {
  const metrics = computeSummaryMetrics(sampleVillages, sampleAlerts);
  assert.equal(metrics.liveAlertsCount, 2);
  assert.equal(metrics.atRiskVillagesCount, 2);
  assert.equal(metrics.peoplePotentiallyAffected, 3050);
});

test('filterVillagesByRisk returns all or matching risk villages', () => {
  assert.equal(filterVillagesByRisk(sampleVillages, 'All').length, 4);
  assert.deepEqual(
    filterVillagesByRisk(sampleVillages, 'Very High').map((v) => v.name),
    ['Kedarpur']
  );
  assert.deepEqual(
    filterVillagesByRisk(sampleVillages, 'Low').map((v) => v.name),
    ['Srinagar']
  );
});

test('countVillagesByRisk aggregates counts per risk tier', () => {
  assert.deepEqual(countVillagesByRisk(sampleVillages), {
    Low: 1,
    Moderate: 1,
    High: 1,
    'Very High': 1,
  });
});

test('getRiskVisualConfig maps risk levels to green, yellow, orange, red hex codes', () => {
  assert.equal(getRiskVisualConfig('Low').hex, '#10B981');
  assert.equal(getRiskVisualConfig('Moderate').hex, '#F59E0B');
  assert.equal(getRiskVisualConfig('High').hex, '#F97316');
  assert.equal(getRiskVisualConfig('Very High').hex, '#EF4444');
});

test('formatUtcTime formats ISO 8601 UTC timestamps cleanly', () => {
  assert.equal(formatUtcTime('2026-11-13T10:05:00Z'), '2026-11-13 10:05 UTC');
});
