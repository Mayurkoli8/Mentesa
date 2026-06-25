import React, { useEffect, useState } from 'react';
import api from '../utils/api';
import { Check, Zap, Building2, Sparkles } from 'lucide-react';
import PageHeader from '../components/PageHeader';
import ErrorState from '../components/ErrorState';
import { SkeletonCard } from '../components/Skeleton';

const PLAN_ICONS = { free: Sparkles, pro: Zap, business: Building2 };

const Billing = () => {
    const [plans, setPlans] = useState([]);
    const [usage, setUsage] = useState(null);
    const [loading, setLoading] = useState(true);
    const [busy, setBusy] = useState('');
    const [error, setError] = useState(false);

    useEffect(() => {
        load();
        const params = new URLSearchParams(window.location.search);
        if (params.get('status') === 'success') {
            syncAfterCheckout();
        }
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, []);

    const syncAfterCheckout = async () => {
        try {
            const res = await api.post('/billing/sync');
            if (res.data?.synced) setUsage(res.data);
            else setTimeout(load, 3000);
        } catch {
            setTimeout(load, 3000);
        }
        window.history.replaceState({}, '', '/billing');
    };

    const load = async () => {
        setLoading(true);
        setError(false);
        try {
            const [plansRes, usageRes] = await Promise.all([
                api.get('/billing/plans'),
                api.get('/billing/usage'),
            ]);
            setPlans(plansRes.data.plans);
            setUsage(usageRes.data);
        } catch (err) {
            console.error(err);
            setError(true);
        } finally {
            setLoading(false);
        }
    };

    const subscribe = async (planId) => {
        setBusy(planId);
        try {
            const res = await api.post('/billing/checkout', { plan_id: planId });
            window.location.href = res.data.url;
        } catch (err) {
            setError(false);
            setBusy('');
            // surface inline; toast not imported here intentionally to keep minimal
            alert(err.response?.data?.detail || 'Could not start checkout');
        }
    };

    const manage = async () => {
        setBusy('portal');
        try {
            const res = await api.post('/billing/portal');
            window.location.href = res.data.url;
        } catch (err) {
            setBusy('');
            alert(err.response?.data?.detail || 'Could not open billing portal');
        }
    };

    const pct = usage ? Math.min(100, Math.round((usage.message_used / usage.message_limit) * 100)) : 0;

    return (
        <div className="page animate-fade-in">
            <PageHeader title="Plans & Billing" subtitle="Upgrade to grow your bots and message volume." icon={<Zap size={22} />} />

            {error ? (
                <ErrorState message="We couldn't load billing details. Please try again." onRetry={load} />
            ) : loading ? (
                <div className="space-y-6">
                    <SkeletonCard height={110} />
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                        {[1, 2, 3].map((i) => <SkeletonCard key={i} height={260} />)}
                    </div>
                </div>
            ) : (
                <>
                    {usage && (
                        <div className="card p-6 mb-10">
                            <div className="flex items-center justify-between mb-3 flex-wrap gap-3">
                                <div>
                                    <span className="t-muted">Current plan</span>
                                    <div className="t-section">{usage.plan_name}</div>
                                </div>
                                {usage.plan_id !== 'free' && (
                                    <button onClick={manage} disabled={busy === 'portal'} className="btn-secondary">
                                        {busy === 'portal' ? 'Opening...' : 'Manage subscription'}
                                    </button>
                                )}
                            </div>
                            <div className="t-body mb-2">
                                {usage.message_used.toLocaleString()} / {usage.message_limit.toLocaleString()} messages this month
                            </div>
                            <div className="w-full h-2 overflow-hidden" style={{ background: 'var(--bg-tertiary)', borderRadius: 'var(--radius-sm)' }}>
                                <div className="h-full transition-all"
                                    style={{ width: `${pct}%`, background: pct > 90 ? '#ff5555' : 'var(--accent-cyan)', borderRadius: 'var(--radius-sm)' }} />
                            </div>
                        </div>
                    )}

                    <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                        {plans.map((plan) => {
                            const Icon = PLAN_ICONS[plan.id] || Sparkles;
                            const isCurrent = usage?.plan_id === plan.id;
                            const isFree = plan.id === 'free';
                            return (
                                <div key={plan.id} className="card p-6"
                                    style={{ borderColor: isCurrent ? 'var(--accent-cyan)' : 'var(--border-soft)' }}>
                                    <div className="flex items-center gap-2 mb-4">
                                        <div className="icon-chip icon-chip--sm"><Icon size={18} /></div>
                                        <h3 className="t-section">{plan.name}</h3>
                                    </div>
                                    <div className="mb-6">
                                        {plan.price_usd === 0 ? (
                                            <span className="text-3xl font-bold">Free</span>
                                        ) : (
                                            <>
                                                <span className="text-3xl font-bold">${plan.price_usd.toFixed(2)}</span>
                                                <span className="t-muted">/mo</span>
                                            </>
                                        )}
                                    </div>
                                    <ul className="space-y-3 mb-6 text-sm">
                                        <li className="flex items-center gap-2">
                                            <Check size={16} style={{ color: 'var(--status-active)' }} />
                                            {plan.bot_limit === null ? 'Unlimited bots' : `${plan.bot_limit} bot${plan.bot_limit > 1 ? 's' : ''}`}
                                        </li>
                                        <li className="flex items-center gap-2">
                                            <Check size={16} style={{ color: 'var(--status-active)' }} />
                                            {plan.message_limit.toLocaleString()} messages/mo
                                        </li>
                                        <li className="flex items-center gap-2">
                                            <Check size={16} style={{ color: 'var(--status-active)' }} />
                                            {plan.branding ? 'Mentesa branding' : 'No branding'}
                                        </li>
                                    </ul>
                                    {isCurrent ? (
                                        <button disabled className="btn-secondary w-full opacity-60 cursor-default">Current Plan</button>
                                    ) : isFree ? (
                                        <button disabled className="btn-secondary w-full opacity-60 cursor-default">Free Forever</button>
                                    ) : (
                                        <button onClick={() => subscribe(plan.id)} disabled={busy === plan.id} className="btn-primary w-full">
                                            {busy === plan.id ? 'Redirecting...' : `Upgrade to ${plan.name}`}
                                        </button>
                                    )}
                                </div>
                            );
                        })}
                    </div>
                </>
            )}
        </div>
    );
};

export default Billing;
