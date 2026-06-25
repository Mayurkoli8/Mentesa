import React from 'react';
import { useAuth } from '../context/AuthContext';
import { useNavigate } from 'react-router-dom';
import { LogOut, Menu } from 'lucide-react';
import ThemeToggle from './ThemeToggle';
import { useToast } from '../context/ToastContext';

const Navbar = ({ onMenuClick }) => {
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
        <div className="h-16 flex items-center px-4 sm:px-6 gap-4"
            style={{ background: 'var(--bg-secondary)', borderBottom: '1px solid var(--border-soft)' }}>
            <button onClick={onMenuClick} className="nav-hamburger p-2 rounded-lg" aria-label="Open menu"
                style={{ background: 'var(--hover-soft)' }}>
                <Menu size={20} />
            </button>

            <div className="flex-1" />

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
                className="icon-btn icon-btn--danger"
                aria-label="Log out"
                title="Logout"
            >
                <LogOut size={20} />
            </button>
        </div>
    );
};

export default Navbar;
