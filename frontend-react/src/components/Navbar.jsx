import React from 'react';
import { useAuth } from '../context/AuthContext';
import { useNavigate } from 'react-router-dom';
import { User as UserIcon, Settings, Search, LogOut } from 'lucide-react';

const Navbar = () => {
    const { user, logout } = useAuth();
    const navigate = useNavigate();

    const handleLogout = async () => {
        await logout();
        navigate('/login');
    };

    if (!user) return null;

    return (
        <div className="h-16 border-b border-white/5 flex items-center justify-end px-6 gap-4" style={{ background: 'var(--bg-secondary)' }}>
            <button className="p-2 hover:bg-white/5 rounded-lg transition-colors">
                <UserIcon size={20} className="text-gray-400" />
            </button>

            <button className="p-2 hover:bg-white/5 rounded-lg transition-colors">
                <Settings size={20} className="text-gray-400" />
            </button>

            <button className="p-2 hover:bg-white/5 rounded-lg transition-colors">
                <Search size={20} className="text-gray-400" />
            </button>

            <button
                onClick={handleLogout}
                className="p-2 hover:bg-red-500/10 rounded-lg transition-colors text-red-400"
                title="Logout"
            >
                <LogOut size={20} />
            </button>
        </div>
    );
};

export default Navbar;
