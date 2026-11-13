import { AlertTriangle, CheckCircle2, X } from 'lucide-react';

export interface ToastState {
  id: number;
  message: string;
  variant: 'warning' | 'success';
}

interface ToastProps {
  toast: ToastState | null;
  onDismiss: () => void;
}

export function Toast({ toast, onDismiss }: ToastProps) {
  if (!toast) {
    return null;
  }

  const isWarning = toast.variant === 'warning';

  return (
    <div
      role="status"
      aria-live="polite"
      data-testid="toast-notification"
      className={`fixed bottom-4 left-1/2 z-[1000] flex w-[calc(100%-2rem)] max-w-md -translate-x-1/2 items-center justify-between gap-3 rounded-lg border px-4 py-2.5 shadow-xl backdrop-blur-md lg:bottom-auto lg:top-[146px] lg:left-[calc((100%-420px)/2)] ${
        isWarning
          ? 'border-[#F59E0B]/60 bg-[#1B2636]/95 text-[#dde2f0]'
          : 'border-[#10B981]/60 bg-[#1B2636]/95 text-[#dde2f0]'
      }`}
    >
      {isWarning ? (
        <AlertTriangle className="h-4 w-4 shrink-0 text-[#fbbf24]" aria-hidden="true" />
      ) : (
        <CheckCircle2 className="h-4 w-4 shrink-0 text-[#34d399]" aria-hidden="true" />
      )}
      <p className="text-xs font-medium text-[#dde2f0] sm:text-sm">{toast.message}</p>
      <button
        type="button"
        onClick={onDismiss}
        aria-label="Dismiss notification"
        className="ml-1 rounded p-1 text-[#869397] transition-colors hover:bg-[#242a34] hover:text-[#dde2f0] focus-visible:outline-2 focus-visible:outline-[#4cd7f6]"
      >
        <X className="h-3.5 w-3.5" aria-hidden="true" />
      </button>
    </div>
  );
}
