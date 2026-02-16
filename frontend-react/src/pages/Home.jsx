import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Upload, Brain, MessageCircle } from 'lucide-react';

const Home = () => {
    const navigate = useNavigate();

    const features = [
        {
            icon: Upload,
            title: 'Upload your knowledge',
            description: 'Add documents and data sources'
        },
        {
            icon: Brain,
            title: 'Customize Personality',
            description: 'Define how your bot behaves'
        },
        {
            icon: MessageCircle,
            title: 'Chat Instantly',
            description: 'Start conversations right away'
        }
    ];

    return (
        <div className="flex flex-col items-center justify-center min-h-[calc(100vh-64px)] p-8">
            <div className="text-center mb-16 animate-fade-in">
                <h1 className="text-5xl font-bold mb-4">
                    Mentesa<span style={{ color: 'var(--accent-cyan)' }}>.live</span>
                </h1>
                <p className="text-xl text-gray-400">Your Personal AI Builder</p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-12 mb-16 max-w-4xl">
                {features.map((feature, index) => (
                    <div
                        key={index}
                        className="flex flex-col items-center text-center animate-fade-in"
                        style={{ animationDelay: `${index * 0.2}s` }}
                    >
                        <div
                            className="w-24 h-24 rounded-full flex items-center justify-center mb-4 border-2"
                            style={{
                                borderColor: 'var(--accent-cyan)',
                                background: 'rgba(0, 217, 217, 0.1)'
                            }}
                        >
                            <feature.icon size={40} style={{ color: 'var(--accent-cyan)' }} />
                        </div>
                        <h3 className="text-lg font-semibold mb-2">{feature.title}</h3>
                    </div>
                ))}
            </div>

            <button
                onClick={() => navigate('/create-bot')}
                className="btn-primary px-8 py-4 text-lg animate-fade-in"
                style={{ animationDelay: '0.6s' }}
            >
                Create Bot
            </button>

            <div className="absolute bottom-8 right-8 text-sm text-gray-600">
                v1.0
            </div>
        </div>
    );
};

export default Home;
