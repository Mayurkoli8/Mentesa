import React, { useEffect, useState } from 'react';
import { useAuth } from '../context/AuthContext';
import api from '../utils/api';
import { Edit2, Trash2 } from 'lucide-react';
import { Link } from 'react-router-dom';

const Dashboard = () => {
    const { user } = useAuth();
    const [bots, setBots] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        fetchBots();
    }, [user]);

    const fetchBots = async () => {
        if (!user?.email) return;
        try {
            const res = await api.get(`/bots?owner_email=${user.email}`);
            setBots(res.data);
        } catch (err) {
            console.error("Failed to fetch bots", err);
        } finally {
            setLoading(false);
        }
    };

    const deleteBot = async (botId) => {
        if (!window.confirm("Are you sure you want to delete this bot?")) return;
        try {
            await api.delete(`/bots/${botId}`);
            setBots(bots.filter(b => b.id !== botId));
        } catch (e) {
            console.error(e);
            alert("Failed to delete bot");
        }
    }

    const getStatusColor = (index) => {
        const statuses = ['status-active', 'status-live', 'status-training'];
        return statuses[index % 3];
    };

    const getStatusText = (index) => {
        const statuses = ['Active', 'Live', 'Training'];
        return statuses[index % 3];
    };

    return (
        <div className="p-8 animate-fade-in relative min-h-[calc(100vh-64px)]">
            <h1 className="text-3xl font-bold mb-8">Manage Your AI Bots</h1>

            {loading ? (
                <div className="flex items-center justify-center py-20">
                    <div className="text-gray-400">Loading bots...</div>
                </div>
            ) : bots.length === 0 ? (
                <div className="text-center py-20">
                    <p className="text-gray-400 mb-6">No bots created yet.</p>
                    <Link to="/create-bot" className="btn-primary">
                        Create Your First Bot
                    </Link>
                </div>
            ) : (
                <div className="space-y-3">
                    <div className="text-sm font-semibold text-gray-400 mb-4">Bot Name</div>
                    {bots.map((bot, index) => (
                        <div
                            key={bot.id}
                            className="flex items-center justify-between p-4 rounded-lg transition-all hover:bg-white/5"
                            style={{ background: 'var(--bg-tertiary)' }}
                        >
                            <div className="flex items-center gap-4 flex-1">
                                <div className={`status-dot ${getStatusColor(index)}`}></div>
                                <span className="font-medium">{bot.name}</span>
                            </div>

                            <div className="flex items-center gap-6">
                                <div className="flex items-center gap-2">
                                    <div className={`status-dot ${getStatusColor(index)}`}></div>
                                    <span className="text-sm text-gray-400">{getStatusText(index)}</span>
                                </div>

                                <div className="flex items-center gap-2">
                                    <Link
                                        to={`/chat/${bot.id}`}
                                        className="p-2 hover:bg-white/10 rounded-lg transition-colors"
                                        title="Chat"
                                    >
                                        <Edit2 size={18} className="text-gray-400" />
                                    </Link>

                                    <button
                                        onClick={() => deleteBot(bot.id)}
                                        className="p-2 hover:bg-red-500/10 rounded-lg transition-colors"
                                        title="Delete"
                                    >
                                        <Trash2 size={18} className="text-gray-400 hover:text-red-400" />
                                    </button>
                                </div>
                            </div>
                        </div>
                    ))}
                </div>
            )}

            <div className="absolute bottom-8 right-8 text-sm text-gray-600">
                v1.0
            </div>
        </div>
    );
};

export default Dashboard;
