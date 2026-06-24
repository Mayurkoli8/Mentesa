import React, { useEffect, useState } from 'react';
import api from '../utils/api';
import { Check, Zap, Building2, Sparkles } from 'lucide-react';

const PLAN_ICONS = { free: Sparkles, pro: Zap, business: Building2 };

const Billing = () => {
    const [plans, setPlans] = useState([]);
    const [usage, setUsage] = useState(null);
    const [loading, setLoading] = useState(true);
    const [busy, setBusy] = useState('');
    const [error, setError] = useState('');

    useEffect(() => {
        load();
        // Reflect Dodo Payments redirect status
        const params = new URLSearchParams(window.location.search);
        if (params.get('status') === 'success') {
            setTimeout(load, 1500); // give webhook a moment
        }
    }, []);

    const load = async () => {
        try {
            const [plansRes, usageRes] = await Promise.all([
                api.get('/billing/plans'),
                api.get('/billing/usage'),
            ]);
            setPlans(plansRes.data.plans);
            setUsage(usageRes.data);
        } catch (err) {
            setError(err.response?.data?.detail || 'Failed to load billing');
        } finally {
            setLoading(false);
        }
    };

    const subscribe = async (planId) => {
        setBusy(planId);
        setError('');
        try {
            const res = await api.post('/billing/checkout', { plan_id: planId });
            window.location.href = res.data.url;
        } catch (err) {
            setError(err.response?.data?.detail || 'Could not start checkout');
            setBusy('');
        }
    };

    const manage = async () => {
        setBusy('portal');
        try {
            const res = await api.post('/billing/portal');
            window.location.href = res.data.url;
        } catch (err) {
            setError(err.response?.data?.detail || 'Could not open billing portal');
            setBusy('');
        }
    };

    if (loading) return <div className="p-8 text-gray-400">Loading plans...</div>;

    const pct = usage ? Math.min(100, Math.round((usage.message_used / usage.message_limit) * 100)) : 0;

    return (
        <div className="p-8 max-w-5xl mx-auto animate-fade-in">
            <h1 className="text-3xl font-bold mb-2">Plans & Billing</h1>
            <p className="text-gray-400 mb-8">Upgrade to grow your bots and message volume.</p>

            {error && (
                <div className="mb-6 p-4 rounded-lg bg-red-500/10 border border-red-500/20 text-red-400 text-sm">
                    {error}
                </div>
            )}

            {usage && (
                <div className="mb-10 p-6 rounded-lg" style={{ background: 'var(--bg-secondary)' }}>
                    <div className="flex items-center justify-between mb-3">
                        <div>
                            <span className="text-sm text-gray-400">Current plan</span>
                            <div className="text-xl font-bold">{usage.plan_name}</div>
                        </div>
                        {usage.plan_id !== 'free' && (
                            <button onClick={manage} disabled={busy === 'portal'} className="btn-secondary">
                                {busy === 'portal' ? 'Opening...' : 'Manage subscription'}
                            </button>
                        )}
                    </div>
                    <div className="text-sm text-gray-400 mb-2">
                        {usage.message_used.toLocaleString()} / {usage.message_limit.toLocaleString()} messages this month
                    </div>
                    <div className="w-full h-2 rounded-full overflow-hidden" style={{ background: 'var(--bg-tertiary)' }}>
                        <div className="h-full rounded-full transition-all"
                            style={{ width: `${pct}%`, background: pct > 90 ? '#ff5555' : 'var(--accent-cyan)' }} />
                    </div>
                </div>
            )}

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                {plans.map((plan) => {
                    const Icon = PLAN_ICONS[plan.id] || Sparkles;
                    const isCurrent = usage?.plan_id === plan.id;
                    const isFree = plan.id === 'free';
                    return (
                        <div key={plan.id}
                            className="p-6 rounded-lg border transition-all"
                            style={{
                                background: 'var(--bg-secondary)',
                                borderColor: isCurrent ? 'var(--accent-cyan)' : 'rgba(255,255,255,0.1)',
                            }}>
                            <div className="flex items-center gap-2 mb-4">
                                <Icon size={22} style={{ color: 'var(--accent-cyan)' }} />
                                <h3 className="text-xl font-bold">{plan.name}</h3>
                            </div>
                            <div className="mb-6">
                                {plan.price_usd === 0 ? (
                                    <span className="text-3xl font-bold">Free</span>
                                ) : (
                                    <>
                                        <span className="text-3xl font-bold">${plan.price_usd.toFixed(2)}</span>
                                        <span style={{ color: 'var(--text-muted)' }}>/mo</span>
                                    </>
                                )}
                            </div>
                            <ul className="space-y-3 mb-6 text-sm">
                                <li className="flex items-center gap-2">
                                    <Check size={16} className="text-green-400" />
                                    {plan.bot_limit === null ? 'Unlimited bots' : `${plan.bot_limit} bot${plan.bot_limit > 1 ? 's' : ''}`}
                                </li>
                                <li className="flex items-center gap-2">
                                    <Check size={16} className="text-green-400" />
                                    {plan.message_limit.toLocaleString()} messages/mo
                                </li>
                                <li className="flex items-center gap-2">
                                    <Check size={16} className="text-green-400" />
                                    {plan.branding ? 'Mentesa branding' : 'No branding'}
                                </li>
                            </ul>
                            {isCurrent ? (
                                <button disabled className="btn-secondary w-full opacity-60 cursor-default">
                                    Current Plan
                                </button>
                            ) : isFree ? (
                                <button disabled className="btn-secondary w-full opacity-60 cursor-default">
                                    Free Forever
                                </button>
                            ) : (
                                <button onClick={() => subscribe(plan.id)} disabled={busy === plan.id}
                                    className="btn-primary w-full">
                                    {busy === plan.id ? 'Redirecting...' : `Upgrade to ${plan.name}`}
                                </button>
                            )}
                        </div>
                    );
                })}
            </div>
        </div>
    );
};

export default Billing;
