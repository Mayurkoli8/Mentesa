import { createContext, useContext, useState, useCallback } from 'react';
import { CheckCircle, AlertCircle, Info, X } from 'lucide-react';

const ToastContext = createContext();

// eslint-disable-next-line react-refresh/only-export-components
export const useToast = () => useContext(ToastContext);

const ICONS = {
    success: CheckCircle,
    error: AlertCircle,
    info: Info,
};

export const ToastProvider = ({ children }) => {
    const [toasts, setToasts] = useState([]);

    const remove = useCallback((id) => {
        setToasts((t) => t.filter((x) => x.id !== id));
    }, []);

    const push = useCallback((message, type = 'info', timeout = 3500) => {
        const id = Date.now() + Math.random();
        setToasts((t) => [...t, { id, message, type }]);
        if (timeout) setTimeout(() => remove(id), timeout);
    }, [remove]);

    const toast = {
        success: (m) => push(m, 'success'),
        error: (m) => push(m, 'error'),
        info: (m) => push(m, 'info'),
    };

    return (
        <ToastContext.Provider value={toast}>
            {children}
            <div className="toast-stack">
                {toasts.map((t) => {
                    const Icon = ICONS[t.type] || Info;
                    return (
                        <div key={t.id} className={`toast ${t.type}`}>
                            <Icon size={18} />
                            <span className="flex-1 text-sm">{t.message}</span>
                            <button onClick={() => remove(t.id)} className="opacity-60 hover:opacity-100">
                                <X size={16} />
                            </button>
                        </div>
                    );
                })}
            </div>
        </ToastContext.Provider>
    );
};
