import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { Home, PlusCircle, MessageSquare, User, Settings, Search, CreditCard } from 'lucide-react';

const Sidebar = () => {
    const location = useLocation();

    const isActive = (path) => location.pathname === path;

    return (
        <div className="sidebar">
            <div className="p-6" style={{ borderBottom: '1px solid var(--border-soft)' }}>
                <div className="flex items-center gap-3">
                    <div className="logo-mark">
                        <span className="text-xl">M</span>
                    </div>
                    <div>
                        <div className="font-bold text-lg">Mentesa<span className="brand-gradient">.live</span></div>
                        <div className="text-xs" style={{ color: 'var(--text-muted)' }}>Your Personal AI Builder</div>
                    </div>
                </div>
            </div>

            <nav className="sidebar-nav">
                <Link
                    to="/dashboard"
                    className={`sidebar-link ${isActive('/dashboard') || isActive('/') ? 'active' : ''}`}
                >
                    <div className="flex items-center gap-3">
                        <Home size={20} />
                        <span>Home</span>
                    </div>
                </Link>

                <Link
                    to="/create-bot"
                    className={`sidebar-link ${isActive('/create-bot') ? 'active' : ''}`}
                >
                    <div className="flex items-center gap-3">
                        <PlusCircle size={20} />
                        <span>Create</span>
                    </div>
                </Link>

                <Link
                    to="/chat"
                    className={`sidebar-link ${location.pathname.startsWith('/chat') ? 'active' : ''}`}
                >
                    <div className="flex items-center gap-3">
                        <MessageSquare size={20} />
                        <span>Chat</span>
                    </div>
                </Link>

                <Link
                    to="/billing"
                    className={`sidebar-link ${isActive('/billing') ? 'active' : ''}`}
                >
                    <div className="flex items-center gap-3">
                        <CreditCard size={20} />
                        <span>Billing</span>
                    </div>
                </Link>
            </nav>

            <div className="p-4 text-xs text-right" style={{ borderTop: '1px solid var(--border-soft)', color: 'var(--text-muted)' }}>
                v2.0
            </div>
        </div>
    );
};

export default Sidebar;
