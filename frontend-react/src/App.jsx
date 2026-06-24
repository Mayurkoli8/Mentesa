import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { useAuth } from './context/AuthContext';
import Sidebar from './components/Sidebar';
import Navbar from './components/Navbar';
import Login from './pages/Login';
import Landing from './pages/Landing';
import Home from './pages/Home';
import Dashboard from './pages/Dashboard';
import CreateBot from './pages/CreateBot';
import ManageBot from './pages/ManageBot';
import Chat from './pages/Chat';
import MeetUs from './pages/MeetUs';
import Billing from './pages/Billing';

const ProtectedRoute = ({ children }) => {
  const { user, loading } = useAuth();
  if (loading) return <div className="flex items-center justify-center min-h-screen text-gray-400">Loading...</div>;
  if (!user) return <Navigate to="/login" replace />;
  return children;
};

// Shell with sidebar + navbar for authenticated app pages.
const AppShell = ({ children }) => {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  return (
    <div className="app-layout">
      <Sidebar open={sidebarOpen} onClose={() => setSidebarOpen(false)} />
      {sidebarOpen && <div className="sidebar-overlay" onClick={() => setSidebarOpen(false)} />}
      <div className="main-content">
        <Navbar onMenuClick={() => setSidebarOpen(true)} />
        <main>{children}</main>
      </div>
    </div>
  );
};

const Protected = ({ children }) => (
  <ProtectedRoute><AppShell>{children}</AppShell></ProtectedRoute>
);

const App = () => {
  return (
    <Router>
      <Routes>
        {/* Public */}
        <Route path="/" element={<Landing />} />
        <Route path="/login" element={<Login />} />
        <Route path="/meet-us" element={<MeetUs />} />

        {/* Authenticated app */}
        <Route path="/home" element={<Protected><Home /></Protected>} />
        <Route path="/dashboard" element={<Protected><Dashboard /></Protected>} />
        <Route path="/create-bot" element={<Protected><CreateBot /></Protected>} />
        <Route path="/bot/:botId" element={<Protected><ManageBot /></Protected>} />
        <Route path="/chat/:botId?" element={<Protected><Chat /></Protected>} />
        <Route path="/billing" element={<Protected><Billing /></Protected>} />

        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </Router>
  );
};

export default App;
