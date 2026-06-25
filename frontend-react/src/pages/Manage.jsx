import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import api from '../utils/api';
import { Bot, Settings2, Plus, Search } from 'lucide-react';

const Manage = () => {
    const { user } = useAuth();
    const [bots, setBots] = useState([]);
    const [loading, setLoading] = useState(true);
    const [query, setQuery] = useState('');

    useEffect(() => {
        const fetchBots = async () => {
            if (!user?.email) return;
            try {
                const res = await api.get(`/bots?owner_email=${user.email}`);
                setBots(res.data);
            } catch (e) {
                console.error('Failed to load bots', e);
            } finally {
                setLoading(false);
            }
        };
        fetchBots();
    }, [user]);

    const filtered = bots.filter((b) =>
        b.name?.toLowerCase().includes(query.toLowerCase())
    );

    return (
        <div className="p-8 animate-fade-in">
            <div className="flex items-center justify-between mb-2 flex-wrap gap-4">
                <div>
                    <h1 className="text-3xl font-bold">Manage Bots</h1>
                    <p style={{ color: 'var(--text-muted)' }}>Select a bot to edit its knowledge, API key, and embed.</p>
                </div>
                <Link to="/create-bot" className="btn-primary flex items-center gap-2">
                    <Plus size={18} /> New Bot
                </Link>
            </div>

            {/* Search */}
            <div className="relative my-6 max-w-sm">
                <Search size={18} className="absolute left-3 top-1/2 -translate-y-1/2" style={{ color: 'var(--text-muted)' }} />
                <input
                    className="input-field pl-10"
                    placeholder="Search bots..."
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                />
            </div>

            {loading ? (
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
                    {[1, 2, 3].map((i) => <div key={i} className="skeleton" style={{ height: 110 }} />)}
                </div>
            ) : filtered.length === 0 ? (
                <div className="card p-12 text-center">
                    <Bot size={44} className="mx-auto mb-4" style={{ color: 'var(--accent-cyan)' }} />
                    <p className="mb-6" style={{ color: 'var(--text-muted)' }}>
                        {bots.length === 0 ? 'No bots yet. Create your first one.' : 'No bots match your search.'}
                    </p>
                    {bots.length === 0 && (
                        <Link to="/create-bot" className="btn-primary inline-flex items-center gap-2">
                            <Plus size={18} /> Create Bot
                        </Link>
                    )}
                </div>
            ) : (
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
                    {filtered.map((bot) => (
                        <Link key={bot.id} to={`/bot/${bot.id}`} className="card card-hover p-5 block">
                            <div className="flex items-start gap-3 mb-3">
                                <div className="w-10 h-10 flex items-center justify-center flex-shrink-0"
                                    style={{ background: 'var(--bg-tertiary)', borderRadius: 'var(--radius-sm)' }}>
                                    <Bot size={20} style={{ color: 'var(--accent-cyan)' }} />
                                </div>
                                <div className="min-w-0 flex-1">
                                    <div className="font-semibold truncate">{bot.name}</div>
                                    <div className="text-xs truncate" style={{ color: 'var(--text-muted)' }}>
                                        {bot.personality?.slice(0, 60) || 'AI assistant'}
                                    </div>
                                </div>
                            </div>
                            <div className="flex items-center gap-2 text-sm font-medium" style={{ color: 'var(--accent-cyan)' }}>
                                <Settings2 size={15} /> Manage
                            </div>
                        </Link>
                    ))}
                </div>
            )}
        </div>
    );
};

export default Manage;
