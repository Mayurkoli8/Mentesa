import React, { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { useNavigate } from 'react-router-dom';
import { Mail, Lock, User } from 'lucide-react';
import api from '../utils/api';

const Login = () => {
    const [isLogin, setIsLogin] = useState(true);
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [name, setName] = useState('');
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);
    const { login } = useAuth();
    const navigate = useNavigate();

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');
        setLoading(true);

        if (isLogin) {
            const res = await login(email, password);
            if (res.success) {
                navigate('/dashboard');
            } else {
                setError(res.message);
            }
        } else {
            try {
                await api.post('/auth/register', { email, password, display_name: name });
                const res = await login(email, password);
                if (res.success) {
                    navigate('/dashboard');
                } else {
                    setError("Account created but login failed. Please check verification email if sent.");
                }
            } catch (err) {
                setError(err.response?.data?.detail || "Registration failed");
            }
        }
        setLoading(false);
    };

    return (
        <div className="min-h-screen flex items-center justify-center p-4">
            <div className="w-full max-w-md">
                <div className="text-center mb-8">
                    <h1 className="text-4xl font-bold mb-2">
                        Mentesa<span style={{ color: 'var(--accent-cyan)' }}>.live</span>
                    </h1>
                    <p className="text-gray-400">Your Personal AI Builder</p>
                </div>

                <div className="p-8 rounded-lg" style={{ background: 'var(--bg-secondary)', border: '1px solid rgba(255, 255, 255, 0.1)' }}>
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
                                <User className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" size={20} />
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
                            <Mail className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" size={20} />
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
                            <Lock className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" size={20} />
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

                    <div className="mt-6 text-center text-sm text-gray-400">
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
