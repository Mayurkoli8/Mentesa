import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import ThemeToggle from '../components/ThemeToggle';
import {
    ArrowRight, Globe, FileText, MessageCircle, Code2, Sparkles, Brain,
    Zap, ShieldCheck, Plug, ChevronDown, Github, ExternalLink, Check,
} from 'lucide-react';

const STEPS = [
    { icon: Sparkles, title: 'Describe your bot', text: 'Tell Mentesa what you want in plain language. No code, no config.' },
    { icon: Globe, title: 'Add your knowledge', text: 'Point it at your website and upload documents (PDF, DOCX, TXT).' },
    { icon: MessageCircle, title: 'Embed anywhere', text: 'Copy one script tag and your AI assistant goes live on any site.' },
];

const FEATURES = [
    { icon: Brain, title: 'Natural-language creation', text: 'Build a working chatbot from a sentence. Mentesa designs the personality and behavior for you.' },
    { icon: Globe, title: 'Website-aware', text: 'Scrape any URL so your bot answers questions about your product, docs, or company instantly.' },
    { icon: FileText, title: 'Document training', text: 'Upload PDFs, Word docs, and text files. Your bot learns from your real content.' },
    { icon: Zap, title: 'Smart retrieval (RAG)', text: 'Retrieval-Augmented Generation keeps answers grounded in your data, not hallucinations.' },
    { icon: Plug, title: 'One-line embed', text: 'A single script tag adds a polished chat widget to any website in seconds.' },
    { icon: ShieldCheck, title: 'Secure & metered', text: 'Per-bot API keys, rate limiting, and usage tracking built in from day one.' },
];

const FAQS = [
    { q: 'What is Mentesa?', a: 'Mentesa is a no-code platform that lets anyone build a custom AI chatbot from a plain-language description. You can train it on your website and documents, then embed it on any site with a single line of code.' },
    { q: 'Do I need to know how to code?', a: 'No. You describe what you want in plain English, optionally add a website URL and documents, and Mentesa builds the chatbot for you. Embedding it takes one copy-paste snippet.' },
    { q: 'How does Mentesa keep answers accurate?', a: 'Mentesa uses Retrieval-Augmented Generation (RAG). It splits your website and documents into chunks, embeds them, and retrieves the most relevant context for each question so answers stay grounded in your content.' },
    { q: 'Is there a free plan?', a: 'Yes. The Free plan includes one bot and 100 messages per month at no cost. Paid plans start at $4.99/month for more bots, higher limits, and no Mentesa branding.' },
    { q: 'Where can I embed my chatbot?', a: 'Anywhere you can paste HTML. Mentesa gives you a script tag with your bot’s API key that adds a floating chat widget to any website or web app.' },
];

const TEAM = [
    { name: 'Mayur Koli', role: 'Founder & Lead Developer', initials: 'MK', url: 'https://mayurkoli8.github.io/portfolio/', color: 'from-blue-500 to-purple-600' },
    { name: 'Anirudh Kapurkar', role: 'Frontend Developer', initials: 'AK', url: 'https://github.com/AnirudhaKapurkar', color: 'from-pink-500 to-rose-500' },
    { name: 'Niharika Wagh', role: 'Backend Developer & Research', initials: 'NW', url: 'https://github.com/ByteAlchemist26', color: 'from-amber-400 to-orange-500' },
];

const PRICING = [
    { name: 'Free', price: '$0', period: '', features: ['1 bot', '100 messages/mo', 'Website + document training', 'Embeddable widget'] },
    { name: 'Pro', price: '$4.99', period: '/mo', features: ['10 bots', '5,000 messages/mo', 'No Mentesa branding', 'Priority responses'], featured: true },
    { name: 'Business', price: '$9.99', period: '/mo', features: ['Unlimited bots', '50,000 messages/mo', 'No branding', 'Custom personality presets'] },
];

const FaqItem = ({ q, a }) => {
    const [open, setOpen] = useState(false);
    return (
        <div className="card" style={{ padding: 0 }}>
            <button onClick={() => setOpen(!open)}
                className="w-full flex items-center justify-between gap-4 p-5 text-left">
                <span className="font-semibold">{q}</span>
                <ChevronDown size={20} style={{ transform: open ? 'rotate(180deg)' : 'none', transition: 'transform .2s', color: 'var(--accent-cyan)' }} />
            </button>
            {open && <p className="px-5 pb-5 text-sm" style={{ color: 'var(--text-secondary)' }}>{a}</p>}
        </div>
    );
};

const Landing = () => {
    const { user } = useAuth();
    const startHref = user ? '/dashboard' : '/login';

    return (
        <div className="landing">
            {/* Header */}
            <header className="landing-header">
                <Link to="/" className="flex items-center gap-2">
                    <div className="logo-mark" style={{ width: 38, height: 38 }}><span>M</span></div>
                    <span className="font-bold text-lg">Mentesa<span className="brand-gradient">.live</span></span>
                </Link>
                <nav className="flex items-center gap-2 sm:gap-4">
                    <a href="#features" className="landing-navlink">Features</a>
                    <a href="#pricing" className="landing-navlink">Pricing</a>
                    <a href="#faq" className="landing-navlink">FAQ</a>
                    <ThemeToggle />
                    <Link to={startHref} className="btn-primary px-4 py-2">
                        {user ? 'Dashboard' : 'Get Started'}
                    </Link>
                </nav>
            </header>

            {/* Hero */}
            <section className="relative overflow-hidden px-6 pt-20 pb-16 text-center">
                <div className="blob" style={{ width: 420, height: 420, top: '-100px', left: '8%', background: '#00d9d9' }} />
                <div className="blob" style={{ width: 360, height: 360, top: '20px', right: '6%', background: '#7a5cff' }} />
                <div className="relative z-10 max-w-3xl mx-auto animate-fade-in">
                    <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full mb-6 text-sm"
                        style={{ background: 'var(--bg-tertiary)', border: '1px solid var(--border-soft)' }}>
                        <Sparkles size={14} style={{ color: 'var(--accent-cyan)' }} />
                        No-code AI chatbots, live in minutes
                    </div>
                    <h1 className="text-5xl md:text-6xl font-bold mb-6 leading-tight">
                        Build a custom <span className="brand-gradient">AI chatbot</span><br />without writing code
                    </h1>
                    <p className="text-lg mb-8 max-w-2xl mx-auto" style={{ color: 'var(--text-secondary)' }}>
                        Mentesa turns plain language into a working AI assistant. Train it on your website and documents,
                        then embed it on any site with a single line of code.
                    </p>
                    <div className="flex items-center justify-center gap-4 flex-wrap">
                        <Link to={startHref} className="btn-primary px-8 py-4 text-lg flex items-center gap-2">
                            Start Building Free <ArrowRight size={20} />
                        </Link>
                        <a href="#how" className="btn-secondary px-8 py-4 text-lg">See how it works</a>
                    </div>
                    <p className="text-xs mt-4" style={{ color: 'var(--text-muted)' }}>
                        Free plan included · No credit card required
                    </p>
                </div>
            </section>

            {/* How it works */}
            <section id="how" className="px-6 py-16 max-w-5xl mx-auto">
                <h2 className="text-3xl font-bold text-center mb-3">How Mentesa works</h2>
                <p className="text-center mb-12" style={{ color: 'var(--text-muted)' }}>Three steps from idea to live assistant.</p>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                    {STEPS.map((s, i) => (
                        <div key={i} className="card card-hover p-6 text-center">
                            <div className="w-16 h-16 rounded-full flex items-center justify-center mb-4 mx-auto"
                                style={{ background: 'rgba(0,217,217,0.12)', border: '2px solid var(--accent-cyan)' }}>
                                <s.icon size={26} style={{ color: 'var(--accent-cyan)' }} />
                            </div>
                            <div className="text-sm font-bold mb-1" style={{ color: 'var(--accent-cyan)' }}>Step {i + 1}</div>
                            <h3 className="font-semibold mb-2">{s.title}</h3>
                            <p className="text-sm" style={{ color: 'var(--text-muted)' }}>{s.text}</p>
                        </div>
                    ))}
                </div>
            </section>

            {/* Features */}
            <section id="features" className="px-6 py-16" style={{ background: 'var(--bg-secondary)' }}>
                <div className="max-w-5xl mx-auto">
                    <h2 className="text-3xl font-bold text-center mb-3">Everything you need to ship</h2>
                    <p className="text-center mb-12" style={{ color: 'var(--text-muted)' }}>Powerful AI, zero complexity.</p>
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                        {FEATURES.map((f, i) => (
                            <div key={i} className="card p-6">
                                <f.icon size={24} style={{ color: 'var(--accent-cyan)' }} className="mb-3" />
                                <h3 className="font-semibold mb-2">{f.title}</h3>
                                <p className="text-sm" style={{ color: 'var(--text-muted)' }}>{f.text}</p>
                            </div>
                        ))}
                    </div>
                </div>
            </section>

            {/* Pricing */}
            <section id="pricing" className="px-6 py-16 max-w-5xl mx-auto">
                <h2 className="text-3xl font-bold text-center mb-3">Simple, honest pricing</h2>
                <p className="text-center mb-12" style={{ color: 'var(--text-muted)' }}>Start free. Upgrade when you grow.</p>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                    {PRICING.map((p) => (
                        <div key={p.name} className="card p-6"
                            style={{ borderColor: p.featured ? 'var(--accent-cyan)' : 'var(--border-soft)', position: 'relative' }}>
                            {p.featured && (
                                <span className="absolute -top-3 left-1/2 -translate-x-1/2 text-xs px-3 py-1 rounded-full font-semibold"
                                    style={{ background: 'var(--accent-cyan)', color: '#06121f' }}>Most popular</span>
                            )}
                            <h3 className="text-xl font-bold mb-2">{p.name}</h3>
                            <div className="mb-5">
                                <span className="text-3xl font-bold">{p.price}</span>
                                <span style={{ color: 'var(--text-muted)' }}>{p.period}</span>
                            </div>
                            <ul className="space-y-2 mb-6 text-sm">
                                {p.features.map((f) => (
                                    <li key={f} className="flex items-center gap-2">
                                        <Check size={16} className="text-green-400 flex-shrink-0" /> {f}
                                    </li>
                                ))}
                            </ul>
                            <Link to={startHref} className={`${p.featured ? 'btn-primary' : 'btn-secondary'} w-full block text-center py-2.5`}>
                                {p.name === 'Free' ? 'Start Free' : `Choose ${p.name}`}
                            </Link>
                        </div>
                    ))}
                </div>
            </section>

            {/* FAQ */}
            <section id="faq" className="px-6 py-16" style={{ background: 'var(--bg-secondary)' }}>
                <div className="max-w-3xl mx-auto">
                    <h2 className="text-3xl font-bold text-center mb-3">Frequently asked questions</h2>
                    <p className="text-center mb-12" style={{ color: 'var(--text-muted)' }}>Everything about building AI chatbots with Mentesa.</p>
                    <div className="space-y-3">
                        {FAQS.map((f, i) => <FaqItem key={i} {...f} />)}
                    </div>
                </div>
            </section>

            {/* Team */}
            <section className="px-6 py-16 max-w-5xl mx-auto">
                <h2 className="text-3xl font-bold text-center mb-3">Meet the team</h2>
                <p className="text-center mb-12" style={{ color: 'var(--text-muted)' }}>
                    The minds behind Mentesa.
                    <a href="https://developer.mentesa.live" target="_blank" rel="noreferrer"
                        className="inline-flex items-center gap-1 ml-2" style={{ color: 'var(--accent-cyan)' }}>
                        Learn more <ExternalLink size={13} />
                    </a>
                </p>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                    {TEAM.map((m) => (
                        <a key={m.name} href={m.url} target="_blank" rel="noreferrer" className="card card-hover p-6 text-center">
                            <div className={`w-20 h-20 mx-auto mb-4 rounded-full bg-gradient-to-br ${m.color} p-1`}>
                                <div className="w-full h-full rounded-full flex items-center justify-center text-xl font-bold"
                                    style={{ background: 'var(--bg-tertiary)' }}>{m.initials}</div>
                            </div>
                            <h3 className="font-bold flex items-center justify-center gap-1">{m.name} <Github size={14} style={{ color: 'var(--text-muted)' }} /></h3>
                            <p className="text-sm" style={{ color: 'var(--text-muted)' }}>{m.role}</p>
                        </a>
                    ))}
                </div>
            </section>

            {/* CTA */}
            <section className="px-6 py-16 text-center">
                <div className="card max-w-3xl mx-auto p-12"
                    style={{ background: 'linear-gradient(135deg, rgba(0,217,217,0.12), rgba(122,92,255,0.12))' }}>
                    <h2 className="text-3xl font-bold mb-3">Ready to build your AI assistant?</h2>
                    <p className="mb-6" style={{ color: 'var(--text-secondary)' }}>Join Mentesa and launch your first chatbot in minutes. Free to start.</p>
                    <Link to={startHref} className="btn-primary px-8 py-4 text-lg inline-flex items-center gap-2">
                        Get Started Free <ArrowRight size={20} />
                    </Link>
                </div>
            </section>

            {/* Footer */}
            <footer className="px-6 py-10" style={{ borderTop: '1px solid var(--border-soft)' }}>
                <div className="max-w-5xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-4">
                    <div className="flex items-center gap-2">
                        <div className="logo-mark" style={{ width: 30, height: 30 }}><span className="text-sm">M</span></div>
                        <span className="font-semibold">Mentesa</span>
                        <span className="text-sm" style={{ color: 'var(--text-muted)' }}>© {new Date().getFullYear()}</span>
                    </div>
                    <div className="flex items-center gap-5 text-sm" style={{ color: 'var(--text-muted)' }}>
                        <a href="#features" className="hover:underline">Features</a>
                        <a href="#pricing" className="hover:underline">Pricing</a>
                        <a href="https://developer.mentesa.live" target="_blank" rel="noreferrer" className="hover:underline">Developers</a>
                        <Link to="/login" className="hover:underline">Sign In</Link>
                    </div>
                </div>
            </footer>
        </div>
    );
};

export default Landing;
