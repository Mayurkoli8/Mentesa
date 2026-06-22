import axios from 'axios';

// Backend base URL. Override in production via VITE_API_URL.
const API_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

const api = axios.create({
    baseURL: API_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

// Attach the session id to every request so the backend can authorize
// owner-only actions (bot create/delete, billing, api keys).
api.interceptors.request.use((config) => {
    const sessionId = localStorage.getItem('session_id');
    if (sessionId) {
        config.headers['X-Session-Id'] = sessionId;
    }
    return config;
});

export default api;
export { API_URL };
