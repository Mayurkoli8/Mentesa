import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../utils/api';
import { Upload, Check, Globe, FileText, Sparkles, Bot, X, Wand2 } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { useToast } from '../context/ToastContext';

const PERSONALITY_PRESETS = [
    { label: 'Support Agent', text: 'Act as a friendly, patient customer support agent. Give concise, accurate answers based only on the provided knowledge, and offer to escalate when unsure.' },
    { label: 'Sales Assistant', text: 'Act as an enthusiastic sales assistant. Highlight benefits, answer product questions clearly, and gently guide the user toward getting started.' },
    { label: 'Technical Expert', text: 'Act as a precise technical expert. Provide detailed, well-structured answers with examples, and admit when something is outside the provided documentation.' },
    { label: 'Friendly Tutor', text: 'Act as an encouraging tutor. Explain concepts simply, use analogies, and check understanding with short follow-up questions.' },
];

const CreateBot = () => {
    const navigate = useNavigate();
    const { user } = useAuth();
    const toast = useToast();
    const [loading, setLoading] = useState(false);
    const [formData, setFormData] = useState({ name: '', prompt: '', url: '' });
    const [files, setFiles] = useState([]);
    const [error, setError] = useState('');

    const removeFile = (idx) => setFiles(files.filter((_, i) => i !== idx));

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');

        if (!formData.name || !formData.prompt) {
            const msg = "Bot name and personality are required";
            setError(msg);
            toast.error(msg);
            return;
        }
        setLoading(true);

        try {
            const payload = {
                owner_email: user.email,
                name: formData.name,
                prompt: formData.prompt,
                url: formData.url || undefined,
                config: formData.url ? { urls: [formData.url] } : {},
            };

            const res = await api.post('/bots', payload);
            const newBot = res.data.bot;

            if (files.length > 0 && newBot.id) {
                for (let file of files) {
                    const fd = new FormData();
                    fd.append('file', file);
                    await api.post(`/bots/${newBot.id}/upload_file`, fd, {
                        headers: { 'Content-Type': 'multipart/form-data' },
                    });
                }
            }

            toast.success('Bot created! Here are your keys.');
            navigate(`/bot/${newBot.id}`);
        } catch (err) {
            console.error(err);
            const msg = err.response?.data?.detail || "Failed to create bot";
            setError(msg);
            toast.error(msg);
        } finally {
            setLoading(false);
        }
    };

    const hasKnowledge = formData.url || files.length > 0;

    return (
        <div className="p-8 max-w-3xl mx-auto animate-fade-in relative min-h-[calc(100vh-64px)]">
            <div className="flex items-center gap-3 mb-2">
                <div className="logo-mark" style={{ width: 44, height: 44 }}><Bot size={22} /></div>
                <div>
                    <h1 className="text-3xl font-bold">Create New Bot</h1>
                    <p className="text-sm" style={{ color: 'var(--text-muted)' }}>Describe it, feed it knowledge, and launch.</p>
                </div>
            </div>

            {error && (
                <div className="my-6 p-4 rounded-lg bg-red-500/10 border border-red-500/20 text-red-400 text-sm">
                    {error}
                </div>
            )}

            <form onSubmit={handleSubmit} className="space-y-6 mt-8">
                {/* Identity */}
                <div className="card p-6">
                    <div className="flex items-center gap-2 mb-4">
                        <Sparkles size={18} style={{ color: 'var(--accent-cyan)' }} />
                        <h2 className="font-semibold">1. Identity</h2>
                    </div>
                    <label className="block text-sm font-medium mb-2">Bot Name</label>
                    <input
                        type="text"
                        className="input-field"
                        placeholder="Company Knowledge Bot"
                        value={formData.name}
                        onChange={e => setFormData({ ...formData, name: e.target.value })}
                        required
                    />
                </div>

                {/* Knowledge sources */}
                <div className="card p-6">
                    <div className="flex items-center justify-between mb-4">
                        <div className="flex items-center gap-2">
                            <Globe size={18} style={{ color: 'var(--accent-cyan)' }} />
                            <h2 className="font-semibold">2. Knowledge Sources</h2>
                        </div>
                        {hasKnowledge && (
                            <span className="text-xs flex items-center gap-1" style={{ color: 'var(--status-active)' }}>
                                <Check size={14} /> sources added
                            </span>
                        )}
                    </div>
                    <p className="text-sm mb-5" style={{ color: 'var(--text-muted)' }}>
                        Give your bot something to learn from. Add a website, files, or both. Skip to build a personality-only bot.
                    </p>

                    {/* Website URL */}
                    <label className="block text-sm font-medium mb-2 flex items-center gap-2">
                        <Globe size={15} /> Website URL
                    </label>
                    <div className="relative mb-2">
                        <Globe size={18} className="absolute left-3 top-1/2 -translate-y-1/2" style={{ color: 'var(--text-muted)' }} />
                        <input
                            type="url"
                            className="input-field pl-10"
                            placeholder="https://yourcompany.com"
                            value={formData.url}
                            onChange={e => setFormData({ ...formData, url: e.target.value })}
                        />
                    </div>
                    <p className="text-xs mb-5" style={{ color: 'var(--text-muted)' }}>
                        We'll scrape this page so your bot can answer questions about it.
                    </p>

                    {/* Files */}
                    <label className="block text-sm font-medium mb-2 flex items-center gap-2">
                        <FileText size={15} /> Documents
                    </label>
                    <div
                        className="p-6 rounded-lg border-2 border-dashed transition-colors cursor-pointer relative text-center"
                        style={{ background: 'var(--bg-tertiary)', borderColor: 'var(--border-soft)' }}
                    >
                        <input
                            type="file"
                            multiple
                            className="absolute inset-0 opacity-0 cursor-pointer"
                            onChange={e => setFiles(prev => [...prev, ...Array.from(e.target.files)])}
                            accept=".pdf,.docx,.txt"
                        />
                        <Upload size={24} className="mx-auto mb-2" style={{ color: 'var(--accent-cyan)' }} />
                        <span className="text-sm block" style={{ color: 'var(--text-muted)' }}>
                            Click to upload PDF, DOCX, or TXT
                        </span>
                    </div>
                    {files.length > 0 && (
                        <div className="mt-3 space-y-2">
                            {files.map((f, i) => (
                                <div key={i} className="flex items-center justify-between px-3 py-2 rounded-lg text-sm"
                                    style={{ background: 'var(--bg-tertiary)' }}>
                                    <span className="flex items-center gap-2 truncate">
                                        <FileText size={15} style={{ color: 'var(--accent-cyan)' }} /> {f.name}
                                    </span>
                                    <button type="button" onClick={() => removeFile(i)}
                                        className="opacity-60 hover:opacity-100" style={{ color: 'var(--text-muted)' }}>
                                        <X size={16} />
                                    </button>
                                </div>
                            ))}
                        </div>
                    )}
                </div>

                {/* Personality */}
                <div className="card p-6">
                    <div className="flex items-center gap-2 mb-4">
                        <Wand2 size={18} style={{ color: 'var(--accent-cyan)' }} />
                        <h2 className="font-semibold">3. Personality</h2>
                    </div>
                    <div className="flex flex-wrap gap-2 mb-3">
                        {PERSONALITY_PRESETS.map((p) => (
                            <button key={p.label} type="button"
                                onClick={() => setFormData({ ...formData, prompt: p.text })}
                                className="text-xs px-3 py-1.5 rounded-full transition-colors"
                                style={{ background: 'var(--bg-tertiary)', border: '1px solid var(--border-soft)' }}>
                                {p.label}
                            </button>
                        ))}
                    </div>
                    <textarea
                        className="input-field h-32 resize-none"
                        placeholder="Respond as a witty and helpful customer service agent, providing concise and accurate information based on the provided knowledge."
                        value={formData.prompt}
                        onChange={e => setFormData({ ...formData, prompt: e.target.value })}
                        required
                    ></textarea>
                    <p className="text-xs mt-1" style={{ color: 'var(--text-muted)' }}>
                        Tip: tap a preset above to start, then tweak it.
                    </p>
                </div>

                <button type="submit" disabled={loading} className="btn-primary w-full py-3 flex items-center justify-center gap-2">
                    {loading ? <><span className="spin"><Sparkles size={18} /></span> Building your bot...</> : <><Bot size={18} /> Create Bot</>}
                </button>
            </form>

            <div className="text-center text-xs mt-6" style={{ color: 'var(--text-muted)' }}>
                v2.0
            </div>
        </div>
    );
};

export default CreateBot;
