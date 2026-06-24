import React, { useState, useEffect, useRef } from 'react';
import { useParams } from 'react-router-dom';
import api from '../utils/api';
import { Send } from 'lucide-react';

const Chat = () => {
    const { botId } = useParams();
    const [messages, setMessages] = useState([]);
    const [input, setInput] = useState('');
    const [loading, setLoading] = useState(false);
    const [botName, setBotName] = useState('Bot');
    const [bots, setBots] = useState([]);
    const [selectedBotId, setSelectedBotId] = useState(botId || '');
    const messagesEndRef = useRef(null);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    };

    useEffect(() => {
        loadBots();
    }, []);

    useEffect(() => {
        if (selectedBotId) {
            loadBotAndHistory(selectedBotId);
        }
    }, [selectedBotId]);

    useEffect(() => {
        scrollToBottom();
    }, [messages]);

    const loadBots = async () => {
        try {
            const res = await api.get('/bots');
            setBots(res.data);
            if (!selectedBotId && res.data.length > 0) {
                setSelectedBotId(res.data[0].id);
            }
        } catch (err) {
            console.error("Failed to load bots", err);
        }
    };

    const loadBotAndHistory = async (id) => {
        try {
            const [botRes, historyRes] = await Promise.all([
                api.get(`/bots/${id}`),
                api.get(`/bots/${id}/history`)
            ]);
            setBotName(botRes.data.name);
            if (Array.isArray(historyRes.data)) {
                setMessages(historyRes.data);
            }
        } catch (err) {
            console.error("Failed to load chat", err);
        }
    };

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
                message: input
            });

            const botMsg = { role: 'bot', content: res.data.reply };
            const finalHistory = [...newHistory, botMsg];

            setMessages(finalHistory);
            await api.post(`/bots/${selectedBotId}/history`, { history: finalHistory });

        } catch (err) {
            console.error("Chat error", err);
            setMessages([...newHistory, { role: 'bot', content: "⚠️ Error sending message. Please try again." }]);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="flex flex-col h-[calc(100vh-64px)]">
            <div className="p-6 flex items-center justify-between gap-4 flex-wrap" style={{ borderBottom: '1px solid var(--border-soft)' }}>
                <h1 className="text-2xl font-bold">{botName}</h1>
                {bots.length > 0 && (
                    <select
                        className="input-field"
                        style={{ maxWidth: 240 }}
                        value={selectedBotId}
                        onChange={(e) => { setSelectedBotId(e.target.value); setMessages([]); }}
                    >
                        {bots.map((b) => (
                            <option key={b.id} value={b.id}>{b.name}</option>
                        ))}
                    </select>
                )}
            </div>

            <div className="flex-1 overflow-y-auto p-6 space-y-4">
                {messages.length === 0 && (
                    <div className="text-center mt-20" style={{ color: 'var(--text-muted)' }}>
                        Start a conversation with your bot
                    </div>
                )}

                {messages.map((msg, idx) => (
                    <div key={idx} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                        <div
                            className="max-w-[70%] px-4 py-3 rounded-lg"
                            style={{
                                background: msg.role === 'user' ? 'var(--accent-cyan)' : 'var(--bg-tertiary)',
                                color: msg.role === 'user' ? '#06121f' : 'var(--text-primary)',
                            }}
                        >
                            {msg.content}
                        </div>
                    </div>
                ))}

                {loading && (
                    <div className="flex justify-start">
                        <div className="px-4 py-3 rounded-lg italic" style={{ background: 'var(--bg-tertiary)', color: 'var(--text-muted)' }}>
                            Typing...
                        </div>
                    </div>
                )}
                <div ref={messagesEndRef} />
            </div>

            <div className="p-6" style={{ borderTop: '1px solid var(--border-soft)' }}>
                <form onSubmit={handleSend} className="flex gap-3">
                    <input
                        type="text"
                        className="input-field flex-1"
                        placeholder="Type a message..."
                        value={input}
                        onChange={e => setInput(e.target.value)}
                        disabled={loading || !selectedBotId}
                    />
                    <button
                        type="submit"
                        disabled={loading || !input.trim() || !selectedBotId}
                        className="w-12 h-12 rounded-full flex items-center justify-center transition-all"
                        style={{
                            background: input.trim() && selectedBotId ? 'var(--accent-cyan)' : 'var(--bg-tertiary)',
                            color: input.trim() && selectedBotId ? '#06121f' : 'var(--text-muted)'
                        }}
                    >
                        <Send size={20} />
                    </button>
                </form>
            </div>
        </div>
    );
};

export default Chat;
