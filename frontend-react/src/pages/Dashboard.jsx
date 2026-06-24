import React, { useEffect, useState } from 'react';
import { useAuth } from '../context/AuthContext';
import api from '../utils/api';
import { Trash2, MessageSquare, Settings2, Plus, Bot, Zap, Activity } from 'lucide-react';
import { Link } from 'react-router-dom';
import { useToast } from '../context/ToastContext';

const Dashboard = () => {
    const { user } = useAuth();
    const toast = useToast();
    const [bots, setBots] = useState([]);
    const [usage, setUsage] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        fetchData();
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [user]);

    const fetchData = async () => {
        if (!user?.email) return;
        try {
            const [botsRes, usageRes] = await Promise.all([
                api.get(`/bots?owner_email=${user.email}`),
                api.get('/billing/usage').catch(() => ({ data: null })),
            ]);
            setBots(botsRes.data);
            setUsage(usageRes.data);
        } catch (err) {
            console.error("Failed to fetch dashboard", err);
            toast.error('Could not load your bots');
        } finally {
            setLoading(false);
        }
    };

    const deleteBot = async (botId, name) => {
        if (!window.confirm(`Delete "${name}"? This cannot be undone.`)) return;
        try {
            await api.delete(`/bots/${botId}`);
            setBots(bots.filter(b => b.id !== botId));
            toast.success(`Deleted ${name}`);
        } catch (e) {
            toast.error(e.response?.data?.detail || "Failed to delete bot");
        }
    };

    const stats = [
        { icon: Bot, label: 'Bots', value: bots.length, sub: usage?.bot_limit == null ? 'unlimited' : `of ${usage?.bot_limit ?? '—'}` },
        { icon: Zap, label: 'Messages this month', value: usage ? usage.message_used.toLocaleString() : '—', sub: usage ? `of ${usage.message_limit.toLocaleString()}` : '' },
        { icon: Activity, label: 'Plan', value: usage?.plan_name || '—', sub: usage?.status || '' },
    ];

    return (
        <div className="p-8 animate-fade-in relative min-h-[calc(100vh-64px)]">
            <div className="flex items-center justify-between mb-8 flex-wrap gap-4">
                <div>
                    <h1 className="text-3xl font-bold">Welcome back, {user?.displayName?.split(' ')[0] || 'there'} 👋</h1>
                    <p style={{ color: 'var(--text-muted)' }}>Manage your AI bots and track usage.</p>
                </div>
                <Link to="/create-bot" className="btn-primary flex items-center gap-2">
                    <Plus size={18} /> New Bot
                </Link>
            </div>

            {/* Stat tiles */}
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-10">
                {stats.map((s, i) => (
                    <div key={i} className="stat-tile card-hover">
                        <div className="flex items-center gap-2 mb-3" style={{ color: 'var(--text-muted)' }}>
                            <s.icon size={18} style={{ color: 'var(--accent-cyan)' }} />
                            <span className="text-sm">{s.label}</span>
                        </div>
                        <div className="stat-value">{loading ? <span className="skeleton inline-block w-16 h-7" /> : s.value}</div>
                        {s.sub && <div className="text-xs mt-1" style={{ color: 'var(--text-muted)' }}>{s.sub}</div>}
                    </div>
                ))}
            </div>

            <h2 className="text-xl font-bold mb-4">Your Bots</h2>

            {loading ? (
                <div className="space-y-3">
                    {[1, 2, 3].map(i => <div key={i} className="skeleton h-16 w-full" />)}
                </div>
            ) : bots.length === 0 ? (
                <div className="card p-12 text-center">
                    <Bot size={48} className="mx-auto mb-4" style={{ color: 'var(--accent-cyan)' }} />
                    <p className="mb-6" style={{ color: 'var(--text-muted)' }}>No bots yet. Build your first AI assistant in seconds.</p>
                    <Link to="/create-bot" className="btn-primary inline-flex items-center gap-2">
                        <Plus size={18} /> Create Your First Bot
                    </Link>
                </div>
            ) : (
                <div className="space-y-3">
                    {bots.map((bot) => (
                        <div key={bot.id}
                            className="card card-hover flex items-center justify-between p-4">
                            <div className="flex items-center gap-4 flex-1 min-w-0">
                                <div className="w-10 h-10 rounded-lg flex items-center justify-center flex-shrink-0"
                                    style={{ background: 'var(--bg-tertiary)' }}>
                                    <Bot size={20} style={{ color: 'var(--accent-cyan)' }} />
                                </div>
                                <div className="min-w-0">
                                    <div className="font-semibold truncate">{bot.name}</div>
                                    <div className="text-xs truncate" style={{ color: 'var(--text-muted)' }}>
                                        {bot.personality?.slice(0, 70) || 'AI assistant'}
                                    </div>
                                </div>
                            </div>

                            <div className="flex items-center gap-1 flex-shrink-0">
                                <Link to={`/bot/${bot.id}`} className="p-2 rounded-lg transition-colors hover:opacity-100 opacity-70"
                                    style={{ background: 'var(--hover-soft)' }} title="Manage">
                                    <Settings2 size={18} />
                                </Link>
                                <Link to={`/chat/${bot.id}`} className="p-2 rounded-lg transition-colors hover:opacity-100 opacity-70"
                                    style={{ background: 'var(--hover-soft)' }} title="Chat">
                                    <MessageSquare size={18} />
                                </Link>
                                <button onClick={() => deleteBot(bot.id, bot.name)}
                                    className="p-2 rounded-lg transition-colors text-red-400 opacity-70 hover:opacity-100"
                                    title="Delete">
                                    <Trash2 size={18} />
                                </button>
                            </div>
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
};

export default Dashboard;
