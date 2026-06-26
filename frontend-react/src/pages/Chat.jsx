import React, { useState, useEffect, useRef, useCallback } from 'react';
import { useParams } from 'react-router-dom';
import api from '../utils/api';
import { useAuth } from '../context/AuthContext';
import { Send, Bot, ChevronDown, MessageSquare, PlusCircle } from 'lucide-react';
import EmptyState from '../components/EmptyState';

const Chat = () => {
    const { botId } = useParams();
    const { user } = useAuth();
    const [messages, setMessages] = useState([]);
    const [input, setInput] = useState('');
    const [loading, setLoading] = useState(false);
    const [bots, setBots] = useState([]);
    const [selectedBotId, setSelectedBotId] = useState(botId || '');
    const messagesEndRef = useRef(null);

    const selectedBot = bots.find((b) => b.id === selectedBotId);

    const loadBots = useCallback(async () => {
        if (!user?.email) return;
        try {
            const res = await api.get(`/bots?owner_email=${encodeURIComponent(user.email)}`);
            setBots(res.data);
            setSelectedBotId((cur) => cur || (res.data.length > 0 ? res.data[0].id : ''));
        } catch (err) {
            console.error('Failed to load bots', err);
        }
    }, [user]);

    const loadHistory = useCallback(async (id) => {
        try {
            const historyRes = await api.get(`/bots/${id}/history`);
            setMessages(Array.isArray(historyRes.data) ? historyRes.data : []);
        } catch (err) {
            console.error('Failed to load chat', err);
            setMessages([]);
        }
    }, []);

    useEffect(() => { loadBots(); }, [loadBots]);
    useEffect(() => { if (selectedBotId) loadHistory(selectedBotId); }, [selectedBotId, loadHistory]);
    useEffect(() => { messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' }); }, [messages]);

    const handleSend = async (e) => {
        e.preventDefault();
        if (!input.trim() || !selectedBotId) return;

        const userMsg = { role: 'user', content: input };
        const newHistory = [...messages, userMsg];
        setMessages(newHistory);
        setInput('');
        setLoading(true);

        try {
            const res = await api.post('/chat', {
                bot_id: selectedBotId,
                message: input,
                history: messages.slice(-12),
                session_id: `app_${selectedBotId}`,
            });
            const finalHistory = [...newHistory, { role: 'bot', content: res.data.reply }];
            setMessages(finalHistory);
            await api.post(`/bots/${selectedBotId}/history`, { history: finalHistory });
        } catch (err) {
            console.error('Chat error', err);
            setMessages([...newHistory, { role: 'bot', content: '⚠️ Error sending message. Please try again.' }]);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="flex flex-col h-[calc(100vh-64px)]">
            {/* Header with bot selector */}
            <div className="px-6 py-4 flex items-center justify-between gap-4 flex-wrap"
                style={{ borderBottom: '1px solid var(--border-soft)', background: 'var(--bg-secondary)' }}>
                <div className="flex items-center gap-3 min-w-0">
                    <div className="w-10 h-10 flex items-center justify-center flex-shrink-0"
                        style={{ background: 'var(--bg-tertiary)', borderRadius: 'var(--radius-sm)' }}>
                        <Bot size={20} style={{ color: 'var(--accent-cyan)' }} />
                    </div>
                    <div className="min-w-0">
                        <div className="font-bold truncate">{selectedBot?.name || 'Select a bot'}</div>
                        <div className="text-xs truncate" style={{ color: 'var(--text-muted)' }}>
                            {selectedBot?.personality?.slice(0, 50) || 'Choose a bot to start chatting'}
                        </div>
                    </div>
                </div>

                <label className="flex items-center gap-2 text-sm" style={{ color: 'var(--text-muted)' }}>
                    <span className="hidden sm:inline">Chatting with</span>
                    <div className="relative">
                        <select
                            className="input-field appearance-none pr-9"
                            style={{ minWidth: 200 }}
                            aria-label="Select a bot to chat with"
                            value={selectedBotId}
                            onChange={(e) => { setSelectedBotId(e.target.value); setMessages([]); }}
                        >
                            {bots.length === 0 && <option value="">No bots yet</option>}
                            {bots.map((b) => <option key={b.id} value={b.id}>{b.name}</option>)}
                        </select>
                        <ChevronDown size={16} className="absolute right-3 top-1/2 -translate-y-1/2 pointer-events-none"
                            style={{ color: 'var(--text-muted)' }} />
                    </div>
                </label>
            </div>

            {/* Messages */}
            <div className="flex-1 overflow-y-auto p-6 space-y-3">
                {bots.length === 0 ? (
                    <div className="max-w-md mx-auto mt-16">
                        <EmptyState
                            icon={<PlusCircle size={26} />}
                            title="No bots to chat with"
                            description="Create your first bot, then come back here to start a conversation."
                            action={{ label: 'Create a Bot', to: '/create-bot', icon: <PlusCircle size={18} /> }}
                        />
                    </div>
                ) : messages.length === 0 ? (
                    <div className="max-w-md mx-auto mt-16">
                        <EmptyState
                            icon={<MessageSquare size={26} />}
                            title="Start the conversation"
                            description={`Say hello to ${selectedBot?.name || 'your bot'} and ask it anything about its knowledge.`}
                        />
                    </div>
                ) : null}

                {messages.map((msg, idx) => (
                    <div key={idx} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
                        style={{ animation: 'fadeIn var(--dur-base) ease-out' }}>
                        <div
                            className="max-w-[75%] px-4 py-2.5"
                            style={{
                                background: msg.role === 'user' ? 'var(--accent-cyan)' : 'var(--bg-secondary)',
                                color: msg.role === 'user' ? '#06121f' : 'var(--text-primary)',
                                border: msg.role === 'user' ? 'none' : '1px solid var(--border-soft)',
                                borderRadius: 'var(--radius-md)',
                            }}
                        >
                            {msg.content}
                        </div>
                    </div>
                ))}

                {loading && (
                    <div className="flex justify-start">
                        <div className="px-4 py-2.5 italic"
                            style={{ background: 'var(--bg-secondary)', color: 'var(--text-muted)', border: '1px solid var(--border-soft)', borderRadius: 'var(--radius-md)' }}>
                            Typing…
                        </div>
                    </div>
                )}
                <div ref={messagesEndRef} />
            </div>

            {/* Input */}
            <div className="p-4" style={{ borderTop: '1px solid var(--border-soft)', background: 'var(--bg-secondary)' }}>
                <form onSubmit={handleSend} className="flex gap-2">
                    <input
                        type="text"
                        className="input-field flex-1"
                        placeholder={selectedBotId ? 'Type a message…' : 'Select a bot first'}
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        disabled={loading || !selectedBotId}
                    />
                    <button
                        type="submit"
                        disabled={loading || !input.trim() || !selectedBotId}
                        aria-label="Send message"
                        className="px-4 flex items-center justify-center"
                        style={{
                            background: input.trim() && selectedBotId ? 'var(--accent-cyan)' : 'var(--bg-tertiary)',
                            color: input.trim() && selectedBotId ? '#06121f' : 'var(--text-muted)',
                            borderRadius: 'var(--radius-md)',
                            minWidth: 48,
                        }}
                    >
                        <Send size={18} />
                    </button>
                </form>
            </div>
        </div>
    );
};

export default Chat;
