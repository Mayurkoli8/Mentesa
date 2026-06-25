import React from 'react';
import { Link } from 'react-router-dom';

// Designed empty state: accent icon chip, title, description, optional CTA.
const EmptyState = ({ icon, title, description, action }) => {
    const renderAction = () => {
        if (!action) return null;
        if (action.to) {
            return <Link to={action.to} className="btn-primary inline-flex items-center gap-2">{action.icon}{action.label}</Link>;
        }
        return (
            <button onClick={action.onClick} className="btn-primary inline-flex items-center gap-2">
                {action.icon}{action.label}
            </button>
        );
    };

    return (
        <div className="card empty-state">
            {icon && <div className="icon-chip">{icon}</div>}
            <h3 className="t-card-title" style={{ marginBottom: 6 }}>{title}</h3>
            {description && <p className="t-body" style={{ maxWidth: 380, marginBottom: action ? 20 : 0 }}>{description}</p>}
            {renderAction()}
        </div>
    );
};

export default EmptyState;
