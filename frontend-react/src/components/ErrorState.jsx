import React from 'react';
import { AlertTriangle, RefreshCw } from 'lucide-react';

// Error state with retry. message describes what failed; onRetry re-runs the fetch.
const ErrorState = ({ message = 'Something went wrong while loading.', onRetry }) => (
    <div className="card empty-state">
        <div className="icon-chip" style={{ background: 'rgba(255,90,90,0.12)', color: '#ff8585' }}>
            <AlertTriangle size={22} />
        </div>
        <h3 className="t-card-title" style={{ marginBottom: 6 }}>Couldn't load this</h3>
        <p className="t-body" style={{ maxWidth: 380, marginBottom: onRetry ? 20 : 0 }}>{message}</p>
        {onRetry && (
            <button onClick={onRetry} className="btn-secondary inline-flex items-center gap-2">
                <RefreshCw size={16} /> Try again
            </button>
        )}
    </div>
);

export default ErrorState;
