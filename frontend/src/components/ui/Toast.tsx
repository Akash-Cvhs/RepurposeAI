import { useEffect } from 'react';
import { useToastStore, type ToastItem } from '../../store/toastStore';
import { CheckCircle2, XCircle, AlertTriangle, Info, X } from 'lucide-react';

const ToastItemComponent = ({ toast }: { toast: ToastItem }) => {
  const { removeToast } = useToastStore();

  useEffect(() => {
    const duration = toast.duration || 4000;
    const timer = setTimeout(() => {
      removeToast(toast.id);
    }, duration);
    return () => clearTimeout(timer);
  }, [toast.id, toast.duration, removeToast]);

  const icons = {
    success: <CheckCircle2 className="w-5 h-5 text-green-500" />,
    error: <XCircle className="w-5 h-5 text-red-500" />,
    warning: <AlertTriangle className="w-5 h-5 text-amber-500" />,
    info: <Info className="w-5 h-5 text-[#E85D24]" />
  };

  const borderColors = {
    success: 'border-green-200 dark:border-green-800',
    error: 'border-red-200 dark:border-red-800',
    warning: 'border-amber-200 dark:border-amber-800',
    info: 'border-[#FDDDD0] dark:border-[#4A2E20]'
  };

  return (
    <div className={`pointer-events-auto min-w-[320px] max-w-[400px] bg-white dark:bg-[#1E2130] border ${borderColors[toast.type]} rounded-xl shadow-lg p-4 flex items-start gap-3 animate-in slide-in-from-right fade-in duration-300`}>
      <div className="flex-shrink-0 mt-0.5">{icons[toast.type]}</div>
      <div className="flex-1">
        <div className="text-sm font-semibold text-gray-900 dark:text-gray-100">{toast.title}</div>
        {toast.message && <div className="text-xs text-gray-500 dark:text-gray-400 mt-0.5">{toast.message}</div>}
      </div>
      <button onClick={() => removeToast(toast.id)} className="flex-shrink-0 w-4 h-4 text-gray-400 hover:text-gray-600 dark:hover:text-gray-200 cursor-pointer transition-colors mt-0.5">
        <X className="w-4 h-4" />
      </button>
    </div>
  );
};

export const ToastContainer = () => {
  const { toasts } = useToastStore();
  
  if (toasts.length === 0) return null;
  
  return (
    <div className="fixed top-4 right-4 z-[9999] flex flex-col gap-2 pointer-events-none">
      {toasts.map(toast => (
        <ToastItemComponent key={toast.id} toast={toast} />
      ))}
    </div>
  );
};
