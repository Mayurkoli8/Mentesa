import { createContext, useContext, useState, useEffect } from 'react';
import api from '../utils/api';

const AuthContext = createContext();

export const useAuth = () => {
    return useContext(AuthContext);
};

export const AuthProvider = ({ children }) => {
    const [user, setUser] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        checkSession();
    }, []);

    const checkSession = async () => {
        const sessionId = localStorage.getItem('session_id');
        if (sessionId) {
            try {
                const response = await api.get(`/auth/session?session_id=${sessionId}`);
                setUser(response.data.user);
            } catch (error) {
                console.error("Session invalid:", error);
                localStorage.removeItem('session_id');
                setUser(null);
            }
        }
        setLoading(false);
    };

    const login = async (email, password) => {
        try {
            const response = await api.post('/auth/login', { email, password });
            const { session_id, user } = response.data;
            localStorage.setItem('session_id', session_id);
            setUser(user);
            return { success: true };
        } catch (error) {
            console.error("Login failed:", error);
            return {
                success: false,
                message: error.response?.data?.detail || "Login failed"
            };
        }
    };

    const logout = async () => {
        const sessionId = localStorage.getItem('session_id');
        if (sessionId) {
            try {
                await api.post('/auth/logout', { session_id: sessionId });
            } catch (e) {
                console.error("Logout error", e);
            }
        }
        localStorage.removeItem('session_id');
        setUser(null);
    };

    const value = {
        user,
        login,
        logout,
        loading
    };

    return (
        <AuthContext.Provider value={value}>
            {!loading && children}
        </AuthContext.Provider>
    );
};
