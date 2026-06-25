import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import api from '../utils/api';
import { Bot, Settings2, Plus, Search } from 'lucide-react';
import PageHeader from '../components/PageHeader';
import EmptyState from '../components/EmptyState';
import ErrorState from '../components/ErrorState';
import { SkeletonCard } from '../components/Skeleton';

const Manage = () => {
    const { user } = useAuth();
    const [bots, setBots] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(false);
    const [query, setQuery] = useState('');

    const fetchBots = async () => {
        if (!user?.email) return;
        setLoading(true);
        setError(false);
        try {
            const res = await api.get(`/bots?owner_email=${encodeURIComponent(user.email)}`);
            setBots(res.data);
        } catch (e) {
            console.error('Failed to load bots', e);
            setError(true);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchBots();
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [user]);

    const filtered = bots.filter((b) => b.name?.toLowerCase().includes(query.toLowerCase()));

    return (
        <div className="page animate-fade-in">
            <PageHeader
                title="Manage Bots"
                subtitle="Select a bot to edit its knowledge, API key, and embed."
                icon={<Settings2 size={22} />}
                actions={<Link to="/create-bot" className="btn-primary flex items-center gap-2"><Plus size={18} /> New Bot</Link>}
            />

            {/* Search */}
            <div className="relative mb-6 max-w-sm">
                <Search size={18} className="absolute left-3 top-1/2 -translate-y-1/2" style={{ color: 'var(--text-muted)' }} />
                <input
                    className="input-field pl-10"
                    placeholder="Search bots..."
                    aria-label="Search bots"
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                />
            </div>

            {loading ? (
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
                    {[1, 2, 3].map((i) => <SkeletonCard key={i} height={110} />)}
                </div>
            ) : error ? (
                <ErrorState message="We couldn't load your bots. Please try again." onRetry={fetchBots} />
            ) : bots.length === 0 ? (
                <EmptyState
                    icon={<Bot size={26} />}
                    title="No bots yet"
                    description="Create your first bot to manage its knowledge, keys, and embed snippet."
                    action={{ label: 'Create Bot', to: '/create-bot', icon: <Plus size={18} /> }}
                />
            ) : filtered.length === 0 ? (
                <EmptyState
                    icon={<Search size={26} />}
                    title="No matches"
                    description={`No bots match "${query}". Try a different search.`}
                />
            ) : (
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 stagger">
                    {filtered.map((bot) => (
                        <Link key={bot.id} to={`/bot/${bot.id}`} className="card card-hover p-5 block">
                            <div className="flex items-start gap-3 mb-3">
                                <div className="icon-chip icon-chip--sm"><Bot size={18} /></div>
                                <div className="min-w-0 flex-1">
                                    <div className="t-card-title truncate">{bot.name}</div>
                                    <div className="t-muted truncate">{bot.personality?.slice(0, 60) || 'AI assistant'}</div>
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
