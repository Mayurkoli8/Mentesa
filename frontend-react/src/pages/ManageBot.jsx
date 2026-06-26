import React, { useEffect, useState } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import api, { API_URL } from '../utils/api';
import { Copy, RefreshCw, Upload, Check, MessageSquare, ArrowLeft, KeyRound, Globe, FileText, Palette } from 'lucide-react';
import { useToast } from '../context/ToastContext';
import { SkeletonCard } from '../components/Skeleton';
import ErrorState from '../components/ErrorState';

const ManageBot = () => {
    const { botId } = useParams();
    const navigate = useNavigate();
    const toast = useToast();
    const [bot, setBot] = useState(null);
    const [apiKey, setApiKey] = useState('');
    const [loading, setLoading] = useState(true);
    const [uploading, setUploading] = useState(false);
    const [copied, setCopied] = useState('');
    const [error, setError] = useState('');
    const [widget, setWidget] = useState(null);
    const [savingWidget, setSavingWidget] = useState(false);

    useEffect(() => {
        load();
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [botId]);

    const load = async () => {
        setLoading(true);
        setError('');
        try {
            const [botRes, keyRes, widgetRes] = await Promise.all([
                api.get(`/bots/${botId}`),
                api.get(`/bots/${botId}/apikey`),
                api.get(`/bots/${botId}/widget`).catch(() => ({ data: null })),
            ]);
            setBot(botRes.data);
            setApiKey(keyRes.data.api_key);
            setWidget(widgetRes.data);
        } catch (err) {
            setError(err.response?.data?.detail || 'Failed to load bot');
        } finally {
            setLoading(false);
        }
    };

    const saveWidget = async () => {
        setSavingWidget(true);
        try {
            const res = await api.put(`/bots/${botId}/widget`, widget);
            setWidget(res.data);
            toast.success('Widget appearance saved');
        } catch (err) {
            toast.error(err.response?.data?.detail || 'Failed to save widget');
        } finally {
            setSavingWidget(false);
        }
    };

    const rotateKey = async () => {
        if (!window.confirm('Rotate the API key? The old key will stop working immediately.')) return;
        try {
            const res = await api.post(`/bots/${botId}/rotate-key`);
            setApiKey(res.data.api_key);
            toast.success('API key rotated');
        } catch (err) {
            toast.error(err.response?.data?.detail || 'Failed to rotate key');
        }
    };

    const handleUpload = async (e) => {
        const file = e.target.files[0];
        if (!file) return;
        setUploading(true);
        try {
            const fd = new FormData();
            fd.append('file', file);
            await api.post(`/bots/${botId}/upload_file`, fd, { headers: { 'Content-Type': 'multipart/form-data' } });
            await load();
            toast.success('File added to knowledge base');
        } catch (err) {
            toast.error(err.response?.data?.detail || 'Upload failed');
        } finally {
            setUploading(false);
        }
    };

    const embedSnippet = `<script src="${API_URL}/static/embed.js"\n  data-api-key="${apiKey}"\n  data-backend-url="${API_URL}"></script>`;

    const copy = (text, which) => {
        navigator.clipboard.writeText(text);
        setCopied(which);
        toast.success('Copied to clipboard');
        setTimeout(() => setCopied(''), 1500);
    };

    if (loading) {
        return (
            <div className="page animate-fade-in">
                <div className="space-y-4">
                    <SkeletonCard height={70} />
                    <SkeletonCard height={120} />
                    <SkeletonCard height={120} />
                </div>
            </div>
        );
    }

    if (error || !bot) {
        return (
            <div className="page">
                <ErrorState message={error || 'Bot not found.'} onRetry={load} />
                <div className="text-center mt-4">
                    <Link to="/manage" className="btn-secondary inline-flex items-center gap-2">
                        <ArrowLeft size={16} /> Back to Manage
                    </Link>
                </div>
            </div>
        );
    }

    return (
        <div className="page animate-fade-in">
            <button onClick={() => navigate('/manage')}
                className="flex items-center gap-2 mb-6 t-body" style={{ background: 'none', border: 'none', cursor: 'pointer' }}>
                <ArrowLeft size={18} /> Back
            </button>

            <div className="flex items-center justify-between mb-2 flex-wrap gap-3">
                <h1 className="t-page-title">{bot.name}</h1>
                <Link to={`/chat/${bot.id}`} className="btn-secondary flex items-center gap-2">
                    <MessageSquare size={18} /> Test Chat
                </Link>
            </div>
            <p className="t-body mb-8">{bot.personality}</p>

            {/* API key */}
            <section className="card p-6 mb-6">
                <h2 className="t-section mb-4 flex items-center gap-2">
                    <KeyRound size={20} style={{ color: 'var(--accent-cyan)' }} /> API Key
                </h2>
                <div className="flex items-center gap-3">
                    <code className="flex-1 px-4 py-3 text-sm overflow-x-auto"
                        style={{ background: 'var(--bg-tertiary)', borderRadius: 'var(--radius-md)' }}>
                        {apiKey}
                    </code>
                    <button onClick={() => copy(apiKey, 'key')} className="btn-secondary p-3" aria-label="Copy API key" title="Copy">
                        {copied === 'key' ? <Check size={18} className="text-green-400" /> : <Copy size={18} />}
                    </button>
                    <button onClick={rotateKey} className="btn-secondary p-3" aria-label="Rotate API key" title="Rotate">
                        <RefreshCw size={18} />
                    </button>
                </div>
                <p className="t-muted mt-3">Keep this secret. Anyone with this key can use your bot's message quota.</p>
            </section>

            {/* Embed */}
            <section className="card p-6 mb-6">
                <h2 className="t-section mb-4">Embed on your website</h2>
                <p className="t-body mb-4">Paste this snippet before the closing &lt;/body&gt; tag of any page.</p>
                <div className="relative">
                    <pre className="px-4 py-3 text-xs overflow-x-auto whitespace-pre-wrap"
                        style={{ background: 'var(--bg-tertiary)', borderRadius: 'var(--radius-md)' }}>{embedSnippet}</pre>
                    <button onClick={() => copy(embedSnippet, 'embed')} className="btn-secondary p-2 absolute top-2 right-2"
                        aria-label="Copy embed snippet">
                        {copied === 'embed' ? <Check size={16} className="text-green-400" /> : <Copy size={16} />}
                    </button>
                </div>
            </section>

            {/* Widget appearance */}
            {widget && (
                <section className="card p-6 mb-6">
                    <h2 className="t-section mb-1 flex items-center gap-2">
                        <Palette size={20} style={{ color: 'var(--accent-cyan)' }} /> Widget Appearance
                    </h2>
                    <p className="t-muted mb-5">Customize how the chat widget looks on your website.</p>

                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                        <div>
                            <label className="block t-muted mb-1">Accent color</label>
                            <div className="flex items-center gap-2">
                                <input type="color" value={widget.accent || '#00d9d9'}
                                    onChange={(e) => setWidget({ ...widget, accent: e.target.value })}
                                    style={{ width: 44, height: 40, padding: 2, background: 'var(--bg-tertiary)', border: '1px solid var(--border-soft)', borderRadius: 'var(--radius-md)' }}
                                    aria-label="Accent color" />
                                <input className="input-field" value={widget.accent || ''}
                                    onChange={(e) => setWidget({ ...widget, accent: e.target.value })} />
                            </div>
                        </div>

                        <div>
                            <label className="block t-muted mb-1">Launcher position</label>
                            <select className="input-field" value={widget.position || 'right'}
                                onChange={(e) => setWidget({ ...widget, position: e.target.value })}
                                aria-label="Launcher position">
                                <option value="right">Bottom right</option>
                                <option value="left">Bottom left</option>
                            </select>
                        </div>

                        <div>
                            <label className="block t-muted mb-1">Header title</label>
                            <input className="input-field" value={widget.title || ''}
                                placeholder={bot.name}
                                onChange={(e) => setWidget({ ...widget, title: e.target.value })} />
                        </div>

                        <div>
                            <label className="block t-muted mb-1">Launcher icon</label>
                            <input className="input-field" value={widget.launcher_icon || ''}
                                placeholder="💬" maxLength={2}
                                onChange={(e) => setWidget({ ...widget, launcher_icon: e.target.value })} />
                        </div>

                        <div className="sm:col-span-2">
                            <label className="block t-muted mb-1">Welcome message</label>
                            <input className="input-field" value={widget.welcome || ''}
                                placeholder="Hi! 👋 How can I help you today?"
                                onChange={(e) => setWidget({ ...widget, welcome: e.target.value })} />
                        </div>
                    </div>

                    {/* Live preview */}
                    <div className="mt-5 p-4" style={{ background: 'var(--bg-tertiary)', borderRadius: 'var(--radius-md)' }}>
                        <div className="t-muted mb-2">Preview</div>
                        <div style={{ maxWidth: 280, borderRadius: 12, overflow: 'hidden', border: '1px solid var(--border-soft)' }}>
                            <div style={{ background: `linear-gradient(135deg, ${widget.accent || '#00d9d9'}, #0a1320)`, color: '#fff', padding: '12px 14px', display: 'flex', alignItems: 'center', gap: 8 }}>
                                <div style={{ width: 28, height: 28, borderRadius: '50%', background: 'rgba(255,255,255,.2)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontWeight: 700, fontSize: 13 }}>
                                    {(widget.title || bot.name || 'M').charAt(0).toUpperCase()}
                                </div>
                                <span style={{ fontWeight: 700, fontSize: 13 }}>{widget.title || bot.name}</span>
                            </div>
                            <div style={{ background: '#f6f8fb', padding: 12 }}>
                                <div style={{ background: '#fff', border: '1px solid #e6eaf0', borderRadius: 12, padding: '8px 12px', fontSize: 13, color: '#1a2332', display: 'inline-block' }}>
                                    {widget.welcome || 'Hi! 👋 How can I help you today?'}
                                </div>
                            </div>
                        </div>
                    </div>

                    <button onClick={saveWidget} disabled={savingWidget} className="btn-primary mt-5 inline-flex items-center gap-2">
                        {savingWidget ? <RefreshCw size={16} className="spin" /> : <Check size={16} />}
                        {savingWidget ? 'Saving...' : 'Save appearance'}
                    </button>
                </section>
            )}

            {/* Knowledge */}
            <section className="card p-6">
                <h2 className="t-section mb-4">Knowledge Base</h2>
                <div className="space-y-2 mb-4">
                    {(bot.config?.urls || []).map((u, i) => (
                        <div key={`u-${i}`} className="flex items-center gap-2 t-body px-3 py-2"
                            style={{ background: 'var(--bg-tertiary)', borderRadius: 'var(--radius-md)' }}>
                            <Globe size={15} style={{ color: 'var(--accent-cyan)' }} /> {u}
                        </div>
                    ))}
                    {(bot.file_data || []).map((f, i) => (
                        <div key={`f-${i}`} className="flex items-center gap-2 t-body px-3 py-2"
                            style={{ background: 'var(--bg-tertiary)', borderRadius: 'var(--radius-md)' }}>
                            <FileText size={15} style={{ color: 'var(--accent-cyan)' }} /> {f.name}
                        </div>
                    ))}
                    {!(bot.config?.urls || []).length && !(bot.file_data || []).length && (
                        <div className="t-muted">No knowledge sources yet.</div>
                    )}
                </div>
                <label className="btn-secondary inline-flex items-center gap-2 cursor-pointer">
                    {uploading ? <RefreshCw size={18} className="spin" /> : <Upload size={18} />}
                    {uploading ? 'Uploading...' : 'Add file (PDF, DOCX, TXT)'}
                    <input type="file" className="hidden" accept=".pdf,.docx,.txt" onChange={handleUpload} disabled={uploading} />
                </label>
            </section>
        </div>
    );
};

export default ManageBot;
