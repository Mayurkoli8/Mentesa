import React, { useState, useEffect, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import api from '../utils/api';
import { Send } from 'lucide-react';

const Chat = () => {
    const { botId } = useParams();
    const navigate = useNavigate();
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
            <div className="p-6 border-b border-white/5">
                <h1 className="text-2xl font-bold">{botName}</h1>
            </div>

            <div className="flex-1 overflow-y-auto p-6 space-y-4">
                {messages.length === 0 && (
                    <div className="text-center text-gray-500 mt-20">
                        Start a conversation with your bot
                    </div>
                )}

                {messages.map((msg, idx) => (
                    <div key={idx} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                        <div
                            className="max-w-[70%] px-4 py-3 rounded-lg"
                            style={{
                                background: msg.role === 'user' ? '#0088ff' : '#00d9d9',
                                color: msg.role === 'user' ? 'white' : '#1a2332'
                            }}
                        >
                            {msg.content}
                        </div>
                    </div>
                ))}

                {loading && (
                    <div className="flex justify-start">
                        <div className="px-4 py-3 rounded-lg text-gray-400 italic" style={{ background: 'var(--bg-tertiary)' }}>
                            Typing...
                        </div>
                    </div>
                )}
                <div ref={messagesEndRef} />
            </div>

            <div className="p-6 border-t border-white/5">
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
                            color: input.trim() && selectedBotId ? '#1a2332' : '#7a8a9e'
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
