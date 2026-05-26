import React, { useEffect } from 'react';
import { AlertTriangle, X, Info, CheckCircle2 } from 'lucide-react';

export type ToastType = 'error' | 'warning' | 'info' | 'success';

export interface ToastMessage {
  id: string;
  type: ToastType;
  title: string;
  detail?: string;
}

interface Props {
  toasts: ToastMessage[];
  onDismiss: (id: string) => void;
  lang?: 'en' | 'id';
}

const styles: Record<ToastType, string> = {
  error: 'border-red-500/40 bg-red-950/90 text-red-100',
  warning: 'border-amber-500/40 bg-amber-950/90 text-amber-100',
  info: 'border-blue-500/40 bg-slate-900/95 text-slate-200',
  success: 'border-emerald-500/40 bg-emerald-950/90 text-emerald-100',
};

const icons: Record<ToastType, React.ReactNode> = {
  error: <AlertTriangle className="w-4 h-4 text-red-400 shrink-0" />,
  warning: <AlertTriangle className="w-4 h-4 text-amber-400 shrink-0" />,
  info: <Info className="w-4 h-4 text-blue-400 shrink-0" />,
  success: <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />,
};

export default function ErrorToastPanel({ toasts, onDismiss, lang = 'en' }: Props) {
  useEffect(() => {
    if (toasts.length === 0) return;
    const timers = toasts.map((t) =>
      setTimeout(() => onDismiss(t.id), t.type === 'error' ? 12000 : 7000)
    );
    return () => timers.forEach(clearTimeout);
  }, [toasts, onDismiss]);

  if (toasts.length === 0) return null;

  return (
    <div className="fixed bottom-4 right-4 z-[100] flex flex-col gap-2 max-w-md w-full pointer-events-none">
      {toasts.map((t) => (
        <div
          key={t.id}
          className={`pointer-events-auto border rounded-xl p-4 shadow-2xl backdrop-blur ${styles[t.type]}`}
          role="alert"
        >
          <div className="flex items-start gap-3">
            {icons[t.type]}
            <div className="flex-1 min-w-0">
              <p className="text-xs font-bold">{t.title}</p>
              {t.detail && (
                <p className="text-[10px] mt-1 opacity-90 font-mono break-words max-h-24 overflow-y-auto">{t.detail}</p>
              )}
            </div>
            <button
              type="button"
              onClick={() => onDismiss(t.id)}
              className="opacity-60 hover:opacity-100 shrink-0"
              aria-label={lang === 'id' ? 'Tutup' : 'Dismiss'}
            >
              <X className="w-4 h-4" />
            </button>
          </div>
        </div>
      ))}
    </div>
  );
}
