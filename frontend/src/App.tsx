import type { ReactNode } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Login from './pages/Login';
import Register from './pages/Register';
import Dashboard from './pages/Dashboard';
import { isAuthenticated } from './api/auth';
import './App.css';

const PrivateRoute = ({ children }: { children: ReactNode }) => {
  return isAuthenticated() ? children : <Navigate to="/login" />;
};

function App() {
  return (
    <Router>
      <div className="app-container">
        <header className="header">
          <div className="logo">
            <span className="logo-ob">OB</span>
            <span className="logo-text">Company</span>
            <span className="logo-sub">Vault</span>
          </div>
        </header>
        <main className="main-content">
          <Routes>
            <Route path="/login" element={<Login />} />
            <Route path="/register" element={<Register />} />
            <Route
              path="/dashboard"
              element={
                <PrivateRoute>
                  <Dashboard />
                </PrivateRoute>
              }
            />
            <Route path="/" element={<Navigate to="/dashboard" />} />
          </Routes>
        </main>
        <footer className="footer">
          <p>&copy; 2026 OB Company Secure Infrastructure. All rights reserved.</p>
        </footer>
      </div>
    </Router>
  );
}

export default App;
