import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { Home, PlusCircle, MessageSquare, CreditCard, Users, Settings2 } from 'lucide-react';
import Logo from './Logo';

const NAV = [
    { to: '/dashboard', label: 'Home', icon: Home, match: (p) => p === '/dashboard' },
    { to: '/create-bot', label: 'Create', icon: PlusCircle, match: (p) => p === '/create-bot' },
    { to: '/chat', label: 'Chat', icon: MessageSquare, match: (p) => p.startsWith('/chat') },
    { to: '/manage', label: 'Manage', icon: Settings2, match: (p) => p === '/manage' || p.startsWith('/bot/') },
    { to: '/billing', label: 'Billing', icon: CreditCard, match: (p) => p === '/billing' },
    { to: '/meet-us', label: 'Meet Us', icon: Users, match: (p) => p === '/meet-us' },
];

const Sidebar = ({ open, onClose }) => {
    const location = useLocation();

    return (
        <div className={`sidebar ${open ? 'sidebar-open' : ''}`}>
            <div className="p-6" style={{ borderBottom: '1px solid var(--border-soft)' }}>
                <Link to="/dashboard" className="flex items-center gap-3" onClick={onClose}>
                    <Logo size={36} />
                    <div>
                        <div className="font-bold text-lg">Mentesa<span className="brand-gradient">.live</span></div>
                        <div className="text-xs" style={{ color: 'var(--text-muted)' }}>Your Personal AI Builder</div>
                    </div>
                </Link>
            </div>

            <nav className="sidebar-nav">
                {NAV.map(({ to, label, icon: Icon, match }) => (
                    <Link
                        key={to}
                        to={to}
                        onClick={onClose}
                        className={`sidebar-link ${match(location.pathname) ? 'active' : ''}`}
                    >
                        <div className="flex items-center gap-3">
                            <Icon size={20} />
                            <span>{label}</span>
                        </div>
                    </Link>
                ))}
            </nav>

            <div className="p-4 text-xs text-right" style={{ borderTop: '1px solid var(--border-soft)', color: 'var(--text-muted)' }}>
                v2.0
            </div>
        </div>
    );
};

export default Sidebar;
