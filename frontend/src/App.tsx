import { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import { getAlerts, getVillages, reset, simulate } from './api';
import { AlertsFeed } from './components/AlertsFeed';
import { FloodMap } from './components/FloodMap';
import { KpiSummaryStrip } from './components/KpiSummaryStrip';
import { SimulateRainPanel } from './components/SimulateRainPanel';
import { Toast, type ToastState } from './components/Toast';
import { TopBar } from './components/TopBar';
import { VillageDetailsCard } from './components/VillageDetailsCard';
import type { Alert, RiskFilter, Village } from './types/flood';
import { computeSummaryMetrics, filterVillagesByRisk } from './utils/floodStats';

export default function App() {
  const [villages, setVillages] = useState<Village[]>([]);
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [loading, setLoading] = useState(true);
  const [loadError, setLoadError] = useState<string | null>(null);

  const [riskFilter, setRiskFilter] = useState<RiskFilter>('All');
  const [selectedVillage, setSelectedVillage] = useState<Village | null>(null);
  const [fitBoundsTrigger, setFitBoundsTrigger] = useState(0);

  const [simulateVillageId, setSimulateVillageId] = useState<number>(1);
  const [rainfallMm, setRainfallMm] = useState<number>(150);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const [toast, setToast] = useState<ToastState | null>(null);
  const toastTimerRef = useRef<number | null>(null);

  const showToast = useCallback((message: string, variant: 'warning' | 'success' = 'warning') => {
    if (toastTimerRef.current !== null) {
      window.clearTimeout(toastTimerRef.current);
    }
    setToast({ id: Date.now(), message, variant });
    toastTimerRef.current = window.setTimeout(() => {
      setToast(null);
      toastTimerRef.current = null;
    }, 4500);
  }, []);

  useEffect(() => {
    return () => {
      if (toastTimerRef.current !== null) {
        window.clearTimeout(toastTimerRef.current);
      }
    };
  }, []);

  const loadDashboardData = useCallback(async () => {
    setLoading(true);
    setLoadError(null);
    try {
      const [villagesData, alertsData] = await Promise.all([getVillages(), getAlerts()]);
      setVillages(villagesData);
      setAlerts(alertsData);
      if (villagesData.length > 0) {
        setSimulateVillageId((prev) =>
          villagesData.some((v) => v.id === prev) ? prev : villagesData[0].id
        );
      }
    } catch (err) {
      setLoadError(err instanceof Error ? err.message : 'Unable to load flood telemetry data.');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void loadDashboardData();
  }, [loadDashboardData]);

  const summaryMetrics = useMemo(
    () => computeSummaryMetrics(villages, alerts),
    [villages, alerts]
  );

  const filteredVillages = useMemo(
    () => filterVillagesByRisk(villages, riskFilter),
    [villages, riskFilter]
  );

  const handleSelectVillage = useCallback((village: Village) => {
    setSelectedVillage(village);
    setSimulateVillageId(village.id);
  }, []);

  const handleSelectAlertVillage = useCallback(
    (villageName: string) => {
      const match = villages.find((v) => v.name === villageName);
      if (match) {
        if (riskFilter !== 'All' && match.risk !== riskFilter) {
          setRiskFilter('All');
        }
        setSelectedVillage(match);
        setSimulateVillageId(match.id);
      }
    },
    [villages, riskFilter]
  );

  const handleRiskFilterChange = useCallback(
    (nextFilter: RiskFilter) => {
      setRiskFilter(nextFilter);
      if (selectedVillage && nextFilter !== 'All' && selectedVillage.risk !== nextFilter) {
        setSelectedVillage(null);
      }
    },
    [selectedVillage]
  );

  const handleSimulate = useCallback(async () => {
    setIsSubmitting(true);
    try {
      const result = await simulate(simulateVillageId, rainfallMm);
      if (!result.ok) {
        showToast(result.message || 'Backend offline: connect backend to simulate', 'warning');
        return;
      }

      const [updatedVillages, updatedAlerts] = await Promise.all([getVillages(), getAlerts()]);
      setVillages(updatedVillages);
      setAlerts(updatedAlerts);

      if (result.data) {
        setSelectedVillage(result.data);
      }
      showToast('Simulation updated from backend.', 'success');
    } finally {
      setIsSubmitting(false);
    }
  }, [simulateVillageId, rainfallMm, showToast]);

  const handleReset = useCallback(async () => {
    setIsSubmitting(true);
    try {
      const result = await reset();
      if (!result.ok) {
        showToast(result.message || 'Backend offline: connect backend to simulate', 'warning');
        return;
      }

      const [updatedVillages, updatedAlerts] = await Promise.all([getVillages(), getAlerts()]);
      setVillages(updatedVillages);
      setAlerts(updatedAlerts);
      setSelectedVillage((prev) =>
        prev ? updatedVillages.find((v) => v.id === prev.id) ?? null : null
      );
      showToast('Simulations cleared and live data restored.', 'success');
    } finally {
      setIsSubmitting(false);
    }
  }, [showToast]);

  return (
    <div id="top" className="min-h-screen bg-[#0e141d] text-[#dde2f0] lg:flex lg:h-screen lg:flex-col lg:overflow-hidden">
      <TopBar
        riskFilter={riskFilter}
        onRiskFilterChange={handleRiskFilterChange}
        onFitAll={() => setFitBoundsTrigger((c) => c + 1)}
        totalVillages={villages.length}
        filteredCount={filteredVillages.length}
      />

      <main className="mx-auto flex w-full max-w-[1600px] flex-1 flex-col gap-2.5 p-3 sm:px-6 lg:min-h-0 lg:overflow-hidden">
        {loadError ? (
          <div
            role="alert"
            className="flex flex-wrap items-center justify-between gap-4 rounded-lg border border-[#EF4444]/40 bg-[#1B2636] p-4"
          >
            <div>
              <h1 className="text-sm font-semibold text-[#f87171]">Telemetry Load Error</h1>
              <p className="mt-1 text-xs text-[#bcc9cd]">{loadError}</p>
            </div>
            <button
              type="button"
              onClick={() => void loadDashboardData()}
              className="rounded bg-[#06b6d4] px-4 py-2 text-xs font-semibold text-[#003640] hover:bg-[#22d3ee]"
            >
              Retry
            </button>
          </div>
        ) : (
          <>
            <KpiSummaryStrip metrics={summaryMetrics} />

            {loading ? (
              <div className="grid flex-1 grid-cols-1 gap-4 lg:grid-cols-[1fr_400px]">
                <div className="h-[45vh] min-h-[340px] animate-pulse rounded-lg border border-[#4cd7f6]/15 bg-[#111A24] lg:h-full" />
                <div className="space-y-3">
                  <div className="h-32 animate-pulse rounded-lg border border-[#4cd7f6]/15 bg-[#111A24]" />
                  <div className="h-56 animate-pulse rounded-lg border border-[#4cd7f6]/15 bg-[#111A24]" />
                  <div className="h-56 animate-pulse rounded-lg border border-[#4cd7f6]/15 bg-[#111A24]" />
                </div>
              </div>
            ) : (
              <div className="grid flex-1 grid-cols-1 gap-3 lg:min-h-0 lg:grid-cols-[1fr_400px] xl:grid-cols-[1fr_420px]">
                <FloodMap
                  villages={filteredVillages}
                  allVillages={villages}
                  selectedVillage={selectedVillage}
                  onSelectVillage={handleSelectVillage}
                  fitBoundsTrigger={fitBoundsTrigger}
                />

                <aside
                  aria-label="Command controls and alerts"
                  className="flex flex-col gap-2.5 lg:min-h-0 lg:overflow-y-auto lg:pr-0.5"
                >
                  <VillageDetailsCard
                    village={selectedVillage}
                    onClearSelection={() => setSelectedVillage(null)}
                  />

                  <SimulateRainPanel
                    villages={villages}
                    selectedVillageId={simulateVillageId}
                    onVillageChange={setSimulateVillageId}
                    rainfallMm={rainfallMm}
                    onRainfallChange={setRainfallMm}
                    onSimulate={() => void handleSimulate()}
                    onReset={() => void handleReset()}
                    isSubmitting={isSubmitting}
                  />

                  <AlertsFeed
                    alerts={alerts}
                    selectedVillageName={selectedVillage?.name ?? null}
                    onSelectAlertVillage={handleSelectAlertVillage}
                  />
                </aside>
              </div>
            )}
          </>
        )}
      </main>

      <Toast toast={toast} onDismiss={() => setToast(null)} />
    </div>
  );
}
