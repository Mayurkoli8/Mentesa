import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Upload, Brain, MessageCircle, Globe, Code2, Sparkles, ArrowRight } from 'lucide-react';

const Home = () => {
    const navigate = useNavigate();

    const steps = [
        { icon: Upload, title: 'Upload knowledge', description: 'Add docs, PDFs, or a website URL.' },
        { icon: Brain, title: 'Customize personality', description: 'Describe how your bot should behave.' },
        { icon: MessageCircle, title: 'Chat & embed', description: 'Drop it on any site with one line.' },
    ];

    const features = [
        { icon: Globe, title: 'Website-aware', text: 'Point at any URL and your bot learns it instantly.' },
        { icon: Code2, title: 'One-line embed', text: 'A single script tag adds a chat widget anywhere.' },
        { icon: Sparkles, title: 'Smart retrieval', text: 'RAG pulls only the relevant context per question.' },
    ];

    return (
        <div className="relative overflow-hidden">
            {/* Hero */}
            <section className="flex flex-col items-center justify-center text-center px-8 pt-20 pb-16 relative">
                <div className="blob" style={{ width: 380, height: 380, top: '-80px', left: '10%', background: '#00d9d9' }} />
                <div className="blob" style={{ width: 320, height: 320, top: '40px', right: '8%', background: '#7a5cff' }} />

                <div className="relative z-10 max-w-3xl animate-fade-in">
                    <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full mb-6 text-sm"
                        style={{ background: 'var(--bg-tertiary)', border: '1px solid var(--border-soft)' }}>
                        <Sparkles size={14} style={{ color: 'var(--accent-cyan)' }} />
                        No-code AI chatbots in seconds
                    </div>
                    <h1 className="text-5xl md:text-6xl font-bold mb-6 leading-tight">
                        Build your own <span className="brand-gradient">AI assistant</span><br />without writing code
                    </h1>
                    <p className="text-lg mb-8" style={{ color: 'var(--text-secondary)' }}>
                        Describe it, feed it your knowledge, and embed it anywhere. Mentesa turns plain language into a working chatbot.
                    </p>
                    <div className="flex items-center justify-center gap-4 flex-wrap">
                        <button onClick={() => navigate('/create-bot')} className="btn-primary px-8 py-4 text-lg flex items-center gap-2">
                            Create a Bot <ArrowRight size={20} />
                        </button>
                        <button onClick={() => navigate('/dashboard')} className="btn-secondary px-8 py-4 text-lg">
                            View Dashboard
                        </button>
                    </div>
                </div>
            </section>

            {/* Steps */}
            <section className="px-8 py-12 max-w-5xl mx-auto">
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                    {steps.map((s, i) => (
                        <div key={i} className="card card-hover p-6 text-center animate-fade-in"
                            style={{ animationDelay: `${i * 0.12}s` }}>
                            <div className="w-16 h-16 rounded-full flex items-center justify-center mb-4 mx-auto"
                                style={{ background: 'rgba(0, 217, 217, 0.12)', border: '2px solid var(--accent-cyan)' }}>
                                <s.icon size={28} style={{ color: 'var(--accent-cyan)' }} />
                            </div>
                            <div className="text-sm font-bold mb-1" style={{ color: 'var(--accent-cyan)' }}>Step {i + 1}</div>
                            <h3 className="font-semibold mb-2">{s.title}</h3>
                            <p className="text-sm" style={{ color: 'var(--text-muted)' }}>{s.description}</p>
                        </div>
                    ))}
                </div>
            </section>

            {/* Features */}
            <section className="px-8 py-12 max-w-5xl mx-auto">
                <h2 className="text-2xl font-bold text-center mb-10">Everything you need to ship</h2>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                    {features.map((f, i) => (
                        <div key={i} className="p-6">
                            <f.icon size={24} style={{ color: 'var(--accent-cyan)' }} className="mb-3" />
                            <h3 className="font-semibold mb-2">{f.title}</h3>
                            <p className="text-sm" style={{ color: 'var(--text-muted)' }}>{f.text}</p>
                        </div>
                    ))}
                </div>
            </section>

            {/* CTA */}
            <section className="px-8 py-16 text-center">
                <div className="card max-w-3xl mx-auto p-12"
                    style={{ background: 'linear-gradient(135deg, rgba(0,217,217,0.12), rgba(122,92,255,0.12))' }}>
                    <h2 className="text-3xl font-bold mb-3">Ready to build?</h2>
                    <p className="mb-6" style={{ color: 'var(--text-secondary)' }}>Your first bot is free. No credit card required.</p>
                    <button onClick={() => navigate('/create-bot')} className="btn-primary px-8 py-4 text-lg">
                        Get Started
                    </button>
                </div>
            </section>
        </div>
    );
};

export default Home;
