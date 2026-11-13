import type { RiskFilter } from '../types/flood';

interface TopBarProps {
  riskFilter: RiskFilter;
  onRiskFilterChange: (filter: RiskFilter) => void;
  onFitAll: () => void;
  totalVillages: number;
  filteredCount: number;
}

const FILTER_OPTIONS: RiskFilter[] = ['All', 'Very High', 'High', 'Moderate', 'Low'];

export function TopBar({
  riskFilter,
  onRiskFilterChange,
  onFitAll,
  totalVillages,
  filteredCount,
}: TopBarProps) {
  return (
    <header className="w-full border-b border-[#4cd7f6]/15 bg-[#111A24]/95 px-4 py-2.5 sm:px-6">
      <div className="mx-auto flex max-w-[1600px] flex-wrap items-center justify-between gap-2.5 lg:flex-nowrap lg:gap-8">
        <a
          href="#top"
          className="text-base font-bold tracking-tight text-[#dde2f0] whitespace-nowrap shrink-0 sm:text-lg focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[#4cd7f6]"
        >
          Uttarakhand Flood Watch
        </a>

        <nav
          aria-label="Filter villages by risk level"
          className="order-3 flex w-full items-center justify-between gap-1 overflow-x-auto rounded-md border border-[#3d494c]/60 bg-[#080e17] p-1 lg:order-none lg:w-auto lg:justify-start"
        >
          {FILTER_OPTIONS.map((option) => {
            const isActive = riskFilter === option;
            return (
              <button
                key={option}
                type="button"
                aria-pressed={isActive}
                onClick={() => onRiskFilterChange(option)}
                className={`rounded px-2.5 py-1 text-xs font-medium transition-colors whitespace-nowrap shrink-0 focus-visible:outline-2 focus-visible:outline-offset-1 focus-visible:outline-[#4cd7f6] ${
                  isActive
                    ? 'bg-[#1B2636] text-[#4cd7f6] shadow-xs'
                    : 'text-[#bcc9cd] hover:bg-[#161c25] hover:text-[#dde2f0]'
                }`}
              >
                {option === 'All' ? `All (${totalVillages})` : option}
              </button>
            );
          })}
        </nav>

        <div className="flex items-center gap-3 shrink-0">
          <span className="hidden text-xs font-mono tabular-nums text-[#869397] xl:inline">
            {filteredCount}/{totalVillages} shown
          </span>
          <button
            type="button"
            onClick={onFitAll}
            className="rounded border border-[#06b6d4]/40 bg-[#1B2636]/80 px-3 py-1.5 text-xs font-semibold text-[#4cd7f6] transition-colors hover:border-[#4cd7f6] hover:bg-[#06b6d4]/15 whitespace-nowrap shrink-0 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[#4cd7f6]"
          >
            Fit All Markers
          </button>
        </div>
      </div>
    </header>
  );
}
