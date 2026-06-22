import React, { useEffect, useState } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import api, { API_URL } from '../utils/api';
import { Copy, RefreshCw, Upload, Check, MessageSquare, ArrowLeft, KeyRound } from 'lucide-react';

const ManageBot = () => {
    const { botId } = useParams();
    const navigate = useNavigate();
    const [bot, setBot] = useState(null);
    const [apiKey, setApiKey] = useState('');
    const [maskedKey, setMaskedKey] = useState('');
    const [loading, setLoading] = useState(true);
    const [uploading, setUploading] = useState(false);
    const [copied, setCopied] = useState('');
    const [error, setError] = useState('');

    useEffect(() => {
        load();
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [botId]);

    const load = async () => {
        try {
            const [botRes, keyRes] = await Promise.all([
                api.get(`/bots/${botId}`),
                api.get(`/bots/${botId}/apikey`),
            ]);
            setBot(botRes.data);
            setApiKey(keyRes.data.api_key);
            setMaskedKey(keyRes.data.api_key_masked);
        } catch (err) {
            setError(err.response?.data?.detail || 'Failed to load bot');
        } finally {
            setLoading(false);
        }
    };

    const rotateKey = async () => {
        if (!window.confirm('Rotate the API key? The old key will stop working immediately.')) return;
        try {
            const res = await api.post(`/bots/${botId}/rotate-key`);
            setApiKey(res.data.api_key);
            setMaskedKey(res.data.api_key_masked);
        } catch (err) {
            setError(err.response?.data?.detail || 'Failed to rotate key');
        }
    };

    const handleUpload = async (e) => {
        const file = e.target.files[0];
        if (!file) return;
        setUploading(true);
        setError('');
        try {
            const fd = new FormData();
            fd.append('file', file);
            await api.post(`/bots/${botId}/upload_file`, fd, {
                headers: { 'Content-Type': 'multipart/form-data' },
            });
            await load();
        } catch (err) {
            setError(err.response?.data?.detail || 'Upload failed');
        } finally {
            setUploading(false);
        }
    };

    const embedSnippet = `<script src="${API_URL}/static/embed.js"\n  data-api-key="${apiKey}"\n  data-bot-name="${bot?.name || 'Mentesa Bot'}"\n  data-backend-url="${API_URL}"></script>`;

    const copy = (text, which) => {
        navigator.clipboard.writeText(text);
        setCopied(which);
        setTimeout(() => setCopied(''), 1500);
    };

    if (loading) {
        return <div className="p-8 text-gray-400">Loading bot...</div>;
    }

    if (!bot) {
        return (
            <div className="p-8">
                <div className="text-red-400 mb-4">{error || 'Bot not found'}</div>
                <Link to="/dashboard" className="btn-primary">Back to Dashboard</Link>
            </div>
        );
    }

    return (
        <div className="p-8 max-w-3xl mx-auto animate-fade-in">
            <button onClick={() => navigate('/dashboard')}
                className="flex items-center gap-2 text-gray-400 hover:text-white mb-6 transition-colors">
                <ArrowLeft size={18} /> Back
            </button>

            <div className="flex items-center justify-between mb-2">
                <h1 className="text-3xl font-bold">{bot.name}</h1>
                <Link to={`/chat/${bot.id}`} className="btn-secondary flex items-center gap-2">
                    <MessageSquare size={18} /> Test Chat
                </Link>
            </div>
            <p className="text-gray-400 mb-8">{bot.personality}</p>

            {error && (
                <div className="mb-6 p-4 rounded-lg bg-red-500/10 border border-red-500/20 text-red-400 text-sm">
                    {error}
                </div>
            )}

            {/* API key */}
            <section className="mb-8 p-6 rounded-lg" style={{ background: 'var(--bg-secondary)' }}>
                <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
                    <KeyRound size={20} style={{ color: 'var(--accent-cyan)' }} /> API Key
                </h2>
                <div className="flex items-center gap-3">
                    <code className="flex-1 px-4 py-3 rounded-lg text-sm overflow-x-auto"
                        style={{ background: 'var(--bg-tertiary)' }}>
                        {apiKey}
                    </code>
                    <button onClick={() => copy(apiKey, 'key')}
                        className="btn-secondary p-3" title="Copy">
                        {copied === 'key' ? <Check size={18} className="text-green-400" /> : <Copy size={18} />}
                    </button>
                    <button onClick={rotateKey} className="btn-secondary p-3" title="Rotate">
                        <RefreshCw size={18} />
                    </button>
                </div>
                <p className="text-xs text-gray-500 mt-3">
                    Keep this secret. Anyone with this key can use your bot's message quota.
                </p>
            </section>

            {/* Embed */}
            <section className="mb-8 p-6 rounded-lg" style={{ background: 'var(--bg-secondary)' }}>
                <h2 className="text-lg font-semibold mb-4">Embed on your website</h2>
                <p className="text-sm text-gray-400 mb-4">
                    Paste this snippet before the closing &lt;/body&gt; tag of any page.
                </p>
                <div className="relative">
                    <pre className="px-4 py-3 rounded-lg text-xs overflow-x-auto whitespace-pre-wrap"
                        style={{ background: 'var(--bg-tertiary)' }}>{embedSnippet}</pre>
                    <button onClick={() => copy(embedSnippet, 'embed')}
                        className="btn-secondary p-2 absolute top-2 right-2">
                        {copied === 'embed' ? <Check size={16} className="text-green-400" /> : <Copy size={16} />}
                    </button>
                </div>
            </section>

            {/* Knowledge */}
            <section className="p-6 rounded-lg" style={{ background: 'var(--bg-secondary)' }}>
                <h2 className="text-lg font-semibold mb-4">Knowledge Base</h2>
                <div className="space-y-2 mb-4">
                    {(bot.config?.urls || []).map((u, i) => (
                        <div key={`u-${i}`} className="text-sm text-gray-300 px-3 py-2 rounded"
                            style={{ background: 'var(--bg-tertiary)' }}>🔗 {u}</div>
                    ))}
                    {(bot.file_data || []).map((f, i) => (
                        <div key={`f-${i}`} className="text-sm text-gray-300 px-3 py-2 rounded"
                            style={{ background: 'var(--bg-tertiary)' }}>📄 {f.name}</div>
                    ))}
                    {!(bot.config?.urls || []).length && !(bot.file_data || []).length && (
                        <div className="text-sm text-gray-500">No knowledge sources yet.</div>
                    )}
                </div>
                <label className="btn-secondary inline-flex items-center gap-2 cursor-pointer">
                    {uploading ? <RefreshCw size={18} className="animate-spin" /> : <Upload size={18} />}
                    {uploading ? 'Uploading...' : 'Add file (PDF, DOCX, TXT)'}
                    <input type="file" className="hidden" accept=".pdf,.docx,.txt"
                        onChange={handleUpload} disabled={uploading} />
                </label>
            </section>
        </div>
    );
};

export default ManageBot;
