import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { Home, PlusCircle, MessageSquare, User, Settings, Search, CreditCard } from 'lucide-react';

const Sidebar = () => {
    const location = useLocation();

    const isActive = (path) => location.pathname === path;

    return (
        <div className="sidebar">
            <div className="p-6 border-b border-white/5">
                <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-lg flex items-center justify-center" style={{
                        background: 'linear-gradient(135deg, #00d9d9 0%, #00b8b8 100%)'
                    }}>
                        <span className="text-xl font-bold" style={{ color: '#1a2332' }}>M</span>
                    </div>
                    <div>
                        <div className="font-bold text-lg">Mentesa<span style={{ color: '#00d9d9' }}>.live</span></div>
                        <div className="text-xs text-gray-500">Your Personal AI Builder</div>
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

            <div className="p-4 border-t border-white/5 text-xs text-gray-500 text-right">
                v1.0
            </div>
        </div>
    );
};

export default Sidebar;
