import React from 'react';
import { ArrowRight } from 'lucide-react';

const MeetUs = () => {
    return (
        <div className="container animate-fade-in py-12">
            <div className="text-center mb-16">
                <h1 className="text-4xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-purple-400 to-pink-600 mb-4">
                    Meet the Mentesa Team
                </h1>
                <p className="t-body max-w-2xl mx-auto text-lg">
                    We are dedicated to democratizing AI. Our mission is to make powerful generative AI accessible, personal, and fun for everyone.
                </p>
            </div>

            <div className="grid md:grid-cols-3 gap-8 mb-16">
                {[
                    { name: "Mayur Koli", role: "Founder & Lead Developer", color: "from-blue-500 to-purple-600" },
                    { name: "Anirudh Kapurkar", role: "Frontend Developer", color: "from-pink-500 to-rose-500" },
                    { name: "Niharika Wagh", role: "Backend Developer & Research", color: "from-amber-400 to-orange-500" }
                ].map((member, i) => (
                    <div key={i} className="card card-hover p-8 text-center">
                        <div className={`w-20 h-20 mx-auto mb-6 bg-gradient-to-br ${member.color} p-0.5`} style={{ borderRadius: 'var(--radius-md)' }}>
                            <div className="w-full h-full flex items-center justify-center text-xl font-bold"
                                style={{ background: 'var(--bg-tertiary)', borderRadius: 'var(--radius-sm)' }}>
                                {member.name.split(' ').map(n => n[0]).join('')}
                            </div>
                        </div>
                        <h3 className="t-card-title mb-1">{member.name}</h3>
                        <p className="t-muted">{member.role}</p>
                    </div>
                ))}
            </div>

            <div className="text-center">
                <a
                    href="https://developer.mentesa.live/"
                    target="_blank"
                    rel="noreferrer"
                    className="btn-primary inline-flex items-center gap-2"
                >
                    Visit Mentesa Developer Portal <ArrowRight size={18} />
                </a>
            </div>
        </div>
    );
};

export default MeetUs;
