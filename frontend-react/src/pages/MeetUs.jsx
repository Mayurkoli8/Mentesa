import React from 'react';
import { ArrowRight } from 'lucide-react';

const MeetUs = () => {
    return (
        <div className="container animate-fade-in py-12">
            <div className="text-center mb-16">
                <h1 className="text-4xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-purple-400 to-pink-600 mb-4">
                    Meet the Mentesa Team
                </h1>
                <p className="text-gray-400 max-w-2xl mx-auto text-lg">
                    We are dedicated to democratizing AI. Our mission is to make powerful generative AI accessible, personal, and fun for everyone.
                </p>
            </div>

            <div className="grid md:grid-cols-3 gap-8 mb-16">
                {[
                    { name: "Mayur Koli", role: "Founder & Lead Developer", color: "from-blue-500 to-purple-600" },
                    { name: "Anirudh Kapurkar", role: "Frontend Developer", color: "from-pink-500 to-rose-500" },
                    { name: "Niharika Wagh", role: "Backend Developer & Research", color: "from-amber-400 to-orange-500" }
                ].map((member, i) => (
                    <div key={i} className="glass p-8 rounded-2xl text-center group hover:-translate-y-2 transition-transform duration-300">
                        <div className={`w-24 h-24 mx-auto mb-6 rounded-full bg-gradient-to-br ${member.color} p-1`}>
                            <div className="w-full h-full bg-slate-900 rounded-full flex items-center justify-center text-2xl font-bold">
                                {member.name.split(' ').map(n => n[0]).join('')}
                            </div>
                        </div>
                        <h3 className="text-xl font-bold text-white mb-2">{member.name}</h3>
                        <p className="text-gray-400">{member.role}</p>
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
