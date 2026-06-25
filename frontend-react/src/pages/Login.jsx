import React, { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { useNavigate } from 'react-router-dom';
import { Mail, Lock, User } from 'lucide-react';
import api from '../utils/api';
import ThemeToggle from '../components/ThemeToggle';
import Logo from '../components/Logo';
import { useToast } from '../context/ToastContext';

const Login = () => {
    const [isLogin, setIsLogin] = useState(true);
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [name, setName] = useState('');
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);
    const { login } = useAuth();
    const navigate = useNavigate();
    const toast = useToast();

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');
        setLoading(true);

        if (isLogin) {
            const res = await login(email, password);
            if (res.success) {
                toast.success('Welcome back!');
                navigate('/dashboard');
            } else {
                setError(res.message);
            }
        } else {
            try {
                await api.post('/auth/register', { email, password, display_name: name });
                toast.success('Account created. Check your email to verify.');
                const res = await login(email, password);
                if (res.success) {
                    navigate('/dashboard');
                } else {
                    setError("Account created. Please verify your email, then sign in.");
                    setIsLogin(true);
                }
            } catch (err) {
                setError(err.response?.data?.detail || "Registration failed");
            }
        }
        setLoading(false);
    };

    return (
        <div className="min-h-screen flex items-center justify-center p-4 relative overflow-hidden">
            {/* Ambient blobs */}
            <div className="blob" style={{ width: 340, height: 340, top: '-60px', left: '-40px', background: '#00d9d9' }} />
            <div className="blob" style={{ width: 300, height: 300, bottom: '-60px', right: '-30px', background: '#7a5cff' }} />

            <div className="absolute top-5 right-5 z-10">
                <ThemeToggle />
            </div>

            <div className="w-full max-w-md relative z-10">
                <div className="text-center mb-8">
                    <div className="flex justify-center mb-4">
                        <Logo size={56} />
                    </div>
                    <h1 className="text-4xl font-bold mb-2">
                        Mentesa<span className="brand-gradient">.live</span>
                    </h1>
                    <p style={{ color: 'var(--text-muted)' }}>Your Personal AI Builder</p>
                </div>

                <div className="card p-8">
                    <h2 className="text-2xl font-bold mb-6 text-center">
                        {isLogin ? 'Sign In' : 'Create Account'}
                    </h2>

                    {error && (
                        <div className="mb-4 p-3 rounded-lg bg-red-500/10 border border-red-500/20 text-red-400 text-sm">
                            {error}
                        </div>
                    )}

                    <form onSubmit={handleSubmit} className="space-y-4">
                        {!isLogin && (
                            <div className="relative">
                                <User className="absolute left-3 top-1/2 -translate-y-1/2" size={20} style={{ color: 'var(--text-muted)' }} />
                                <input
                                    type="text"
                                    placeholder="Full Name"
                                    className="input-field pl-10"
                                    value={name}
                                    onChange={(e) => setName(e.target.value)}
                                    required
                                />
                            </div>
                        )}

                        <div className="relative">
                            <Mail className="absolute left-3 top-1/2 -translate-y-1/2" size={20} style={{ color: 'var(--text-muted)' }} />
                            <input
                                type="email"
                                placeholder="Email Address"
                                className="input-field pl-10"
                                value={email}
                                onChange={(e) => setEmail(e.target.value)}
                                required
                            />
                        </div>

                        <div className="relative">
                            <Lock className="absolute left-3 top-1/2 -translate-y-1/2" size={20} style={{ color: 'var(--text-muted)' }} />
                            <input
                                type="password"
                                placeholder="Password"
                                className="input-field pl-10"
                                value={password}
                                onChange={(e) => setPassword(e.target.value)}
                                required
                            />
                        </div>

                        <button
                            type="submit"
                            disabled={loading}
                            className="btn-primary w-full py-3"
                        >
                            {loading ? 'Processing...' : (isLogin ? 'Sign In' : 'Create Account')}
                        </button>
                    </form>

                    <div className="mt-6 text-center text-sm" style={{ color: 'var(--text-muted)' }}>
                        {isLogin ? "Don't have an account? " : "Already have an account? "}
                        <button
                            onClick={() => { setIsLogin(!isLogin); setError(''); }}
                            className="font-semibold hover:underline focus:outline-none"
                            style={{ color: 'var(--accent-cyan)' }}
                        >
                            {isLogin ? 'Sign Up' : 'Sign In'}
                        </button>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default Login;
