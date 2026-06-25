import React, { useEffect, useState } from 'react';
import { useAuth } from '../context/AuthContext';
import api from '../utils/api';
import { Trash2, MessageSquare, Settings2, Plus, Bot, Zap, Activity } from 'lucide-react';
import { Link } from 'react-router-dom';
import { useToast } from '../context/ToastContext';
import PageHeader from '../components/PageHeader';
import EmptyState from '../components/EmptyState';
import ErrorState from '../components/ErrorState';
import { SkeletonCard } from '../components/Skeleton';

const Dashboard = () => {
    const { user } = useAuth();
    const toast = useToast();
    const [bots, setBots] = useState([]);
    const [usage, setUsage] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(false);

    useEffect(() => {
        fetchData();
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [user]);

    const fetchData = async () => {
        if (!user?.email) return;
        setLoading(true);
        setError(false);
        try {
            const [botsRes, usageRes] = await Promise.all([
                api.get(`/bots?owner_email=${encodeURIComponent(user.email)}`),
                api.get('/billing/usage').catch(() => ({ data: null })),
            ]);
            setBots(botsRes.data);
            setUsage(usageRes.data);
        } catch (err) {
            console.error('Failed to fetch dashboard', err);
            setError(true);
        } finally {
            setLoading(false);
        }
    };

    const deleteBot = async (botId, name) => {
        if (!window.confirm(`Delete "${name}"? This cannot be undone.`)) return;
        try {
            await api.delete(`/bots/${botId}`);
            setBots(bots.filter((b) => b.id !== botId));
            toast.success(`Deleted ${name}`);
        } catch (e) {
            toast.error(e.response?.data?.detail || 'Failed to delete bot');
        }
    };

    const stats = [
        { icon: Bot, label: 'Bots', value: bots.length, sub: usage?.bot_limit == null ? 'unlimited' : `of ${usage?.bot_limit ?? '—'}` },
        { icon: Zap, label: 'Messages this month', value: usage ? usage.message_used.toLocaleString() : '—', sub: usage ? `of ${usage.message_limit.toLocaleString()}` : '' },
        { icon: Activity, label: 'Plan', value: usage?.plan_name || '—', sub: usage?.status || '' },
    ];

    return (
        <div className="page animate-fade-in">
            <PageHeader
                title={`Welcome back, ${user?.displayName?.split(' ')[0] || 'there'}`}
                subtitle="Manage your AI bots and track usage."
                icon={<Bot size={22} />}
                actions={<Link to="/create-bot" className="btn-primary flex items-center gap-2"><Plus size={18} /> New Bot</Link>}
            />

            {/* Stat tiles */}
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-10">
                {stats.map((s, i) => (
                    <div key={i} className="stat-tile">
                        <div className="flex items-center gap-2 mb-3 t-muted">
                            <s.icon size={18} style={{ color: 'var(--accent-cyan)' }} />
                            <span>{s.label}</span>
                        </div>
                        <div className="stat-value">{loading ? <span className="skeleton inline-block" style={{ width: 64, height: 28 }} /> : s.value}</div>
                        {s.sub && <div className="t-muted mt-1">{s.sub}</div>}
                    </div>
                ))}
            </div>

            <h2 className="t-section mb-4">Your Bots</h2>

            {loading ? (
                <div className="space-y-3">
                    {[1, 2, 3].map((i) => <SkeletonCard key={i} height={72} />)}
                </div>
            ) : error ? (
                <ErrorState message="We couldn't load your bots. Check your connection and try again." onRetry={fetchData} />
            ) : bots.length === 0 ? (
                <EmptyState
                    icon={<Bot size={26} />}
                    title="No bots yet"
                    description="Build your first AI assistant in seconds — describe it, add knowledge, and embed it anywhere."
                    action={{ label: 'Create Your First Bot', to: '/create-bot', icon: <Plus size={18} /> }}
                />
            ) : (
                <div className="space-y-3 stagger">
                    {bots.map((bot) => (
                        <div key={bot.id} className="list-row">
                            <div className="flex items-center gap-4 flex-1 min-w-0">
                                <div className="icon-chip icon-chip--sm"><Bot size={18} /></div>
                                <div className="min-w-0">
                                    <div className="t-card-title truncate">{bot.name}</div>
                                    <div className="t-muted truncate">{bot.personality?.slice(0, 70) || 'AI assistant'}</div>
                                </div>
                            </div>

                            <div className="flex items-center gap-1 flex-shrink-0">
                                <Link to={`/bot/${bot.id}`} className="icon-btn" aria-label={`Manage ${bot.name}`} title="Manage">
                                    <Settings2 size={18} />
                                </Link>
                                <Link to={`/chat/${bot.id}`} className="icon-btn" aria-label={`Chat with ${bot.name}`} title="Chat">
                                    <MessageSquare size={18} />
                                </Link>
                                <button onClick={() => deleteBot(bot.id, bot.name)} className="icon-btn icon-btn--danger"
                                    aria-label={`Delete ${bot.name}`} title="Delete">
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
