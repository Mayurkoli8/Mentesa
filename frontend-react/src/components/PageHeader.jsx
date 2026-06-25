import React from 'react';

// Consistent page title block: optional icon chip, title, subtitle, right-aligned actions.
const PageHeader = ({ title, subtitle, icon, actions }) => (
    <header className="page-header">
        <div className="page-header__main">
            {icon && <div className="icon-chip">{icon}</div>}
            <div className="min-w-0">
                <h1 className="t-page-title truncate">{title}</h1>
                {subtitle && <p className="t-muted">{subtitle}</p>}
            </div>
        </div>
        {actions && <div className="flex items-center gap-2">{actions}</div>}
    </header>
);

export default PageHeader;
