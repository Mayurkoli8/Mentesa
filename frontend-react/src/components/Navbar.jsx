import React from 'react';
import { useAuth } from '../context/AuthContext';
import { useNavigate } from 'react-router-dom';
import { LogOut } from 'lucide-react';
import ThemeToggle from './ThemeToggle';
import { useToast } from '../context/ToastContext';

const Navbar = () => {
    const { user, logout } = useAuth();
    const navigate = useNavigate();
    const toast = useToast();

    const handleLogout = async () => {
        await logout();
        toast.info('Signed out');
        navigate('/login');
    };

    if (!user) return null;

    const initial = (user.displayName || user.email || '?').charAt(0).toUpperCase();

    return (
        <div className="h-16 flex items-center justify-end px-6 gap-4"
            style={{ background: 'var(--bg-secondary)', borderBottom: '1px solid var(--border-soft)' }}>
            <ThemeToggle />

            <div className="flex items-center gap-3 pl-2">
                <div className="w-9 h-9 rounded-full flex items-center justify-center font-bold"
                    style={{ background: 'var(--accent-cyan)', color: '#06121f' }}>
                    {initial}
                </div>
                <div className="hidden sm:block text-right leading-tight">
                    <div className="text-sm font-semibold">{user.displayName || 'User'}</div>
                    <div className="text-xs" style={{ color: 'var(--text-muted)' }}>{user.email}</div>
                </div>
            </div>

            <button
                onClick={handleLogout}
                className="p-2 rounded-lg transition-colors text-red-400"
                style={{ background: 'transparent' }}
                onMouseEnter={(e) => (e.currentTarget.style.background = 'rgba(255,80,80,0.1)')}
                onMouseLeave={(e) => (e.currentTarget.style.background = 'transparent')}
                title="Logout"
            >
                <LogOut size={20} />
            </button>
        </div>
    );
};

export default Navbar;
