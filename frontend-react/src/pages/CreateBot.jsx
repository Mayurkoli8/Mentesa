import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../utils/api';
import { Upload, Check } from 'lucide-react';
import { useAuth } from '../context/AuthContext';

const CreateBot = () => {
    const navigate = useNavigate();
    const { user } = useAuth();
    const [loading, setLoading] = useState(false);
    const [formData, setFormData] = useState({
        name: '',
        prompt: '',
        url: '',
    });
    const [files, setFiles] = useState([]);
    const [error, setError] = useState('');

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        setError('');

        if (!formData.name || !formData.prompt) {
            setError("Bot name and personality are required");
            setLoading(false);
            return;
        }

        try {
            const payload = {
                owner_email: user.email,
                name: formData.name,
                prompt: formData.prompt,
                url: formData.url || undefined,
                config: formData.url ? { urls: [formData.url] } : {}
            };

            const res = await api.post('/bots', payload);
            const newBot = res.data.bot;

            if (files.length > 0 && newBot.id) {
                for (let file of files) {
                    const fd = new FormData();
                    fd.append('file', file);
                    await api.post(`/bots/${newBot.id}/upload_file`, fd, {
                        headers: { 'Content-Type': 'multipart/form-data' }
                    });
                }
            }

            navigate(`/bot/${newBot.id}`);

        } catch (err) {
            console.error(err);
            setError(err.response?.data?.detail || "Failed to create bot");
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="p-8 max-w-3xl mx-auto animate-fade-in relative min-h-[calc(100vh-64px)]">
            <h1 className="text-3xl font-bold mb-8">Create New Bot</h1>

            {error && (
                <div className="mb-6 p-4 rounded-lg bg-red-500/10 border border-red-500/20 text-red-400 text-sm">
                    {error}
                </div>
            )}

            <form onSubmit={handleSubmit} className="space-y-6">
                <div>
                    <label className="block text-sm font-semibold mb-2">Bot Name</label>
                    <input
                        type="text"
                        className="input-field"
                        placeholder="Company Knowledge Bot"
                        value={formData.name}
                        onChange={e => setFormData({ ...formData, name: e.target.value })}
                        required
                    />
                </div>

                <div>
                    <label className="block text-sm font-semibold mb-2 flex items-center gap-2">
                        Upload Chat File
                        {files.length > 0 && <Check size={16} className="text-green-400" />}
                    </label>
                    <div
                        className="p-6 rounded-lg border-2 border-dashed border-gray-600 hover:border-cyan-500 transition-colors cursor-pointer relative"
                        style={{ background: 'var(--bg-tertiary)' }}
                    >
                        <input
                            type="file"
                            multiple
                            className="absolute inset-0 opacity-0 cursor-pointer"
                            onChange={e => setFiles(Array.from(e.target.files))}
                            accept=".pdf,.docx,.txt"
                        />
                        <div className="flex items-center gap-3">
                            {files.length > 0 ? (
                                <>
                                    <Check size={20} className="text-green-400" />
                                    <span className="text-sm">{files.map(f => f.name).join(', ')}</span>
                                </>
                            ) : (
                                <>
                                    <Upload size={20} className="text-gray-400" />
                                    <span className="text-sm text-gray-400">Click to upload files (PDF, DOCX, TXT)</span>
                                </>
                            )}
                        </div>
                    </div>
                </div>

                <div>
                    <label className="block text-sm font-semibold mb-2">Customize Bot Personality</label>
                    <textarea
                        className="input-field h-32 resize-none"
                        placeholder="Respond as a witty and helpful customer service agent, providing concise and accurate information based on uploaded documents."
                        value={formData.prompt}
                        onChange={e => setFormData({ ...formData, prompt: e.target.value })}
                        required
                    ></textarea>
                </div>

                <button
                    type="submit"
                    disabled={loading}
                    className="btn-primary w-full py-3"
                >
                    {loading ? 'Creating Bot...' : 'Create Bot'}
                </button>
            </form>

            <div className="absolute bottom-8 right-8 text-sm text-gray-600">
                v1.0
            </div>
        </div>
    );
};

export default CreateBot;
