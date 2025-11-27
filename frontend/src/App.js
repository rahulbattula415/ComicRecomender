import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import Header from './components/Header';
import Home from './pages/Home';
import Login from './pages/Login';
import Register from './pages/Register';
import Browse from './pages/Browse';
import ComicDetail from './pages/ComicDetail';
import Recommendations from './pages/Recommendations';
import LoadingSpinner from './components/LoadingSpinner';

// Protected Route Component
const ProtectedRoute = ({ children }) => {
  const { isAuthenticated, loading } = useAuth();
  
  if (loading) {
    return <LoadingSpinner />;
  }
  
  return isAuthenticated ? children : <Navigate to="/login" replace />;
};

// App Content Component (needed to use useAuth hook)
const AppContent = () => {
  const { loading } = useAuth();

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <LoadingSpinner />
      </div>
    );
  }

  return (
    <div className="min-h-screen relative overflow-hidden">
      {/* Comic Book Background Pattern */}
      <div className="fixed inset-0 halftone-bg"></div>
      
      {/* Main App Content */}
      <div className="relative z-10">
        <Header />
        <main className="relative">
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/login" element={<Login />} />
            <Route path="/register" element={<Register />} />
            <Route
              path="/browse"
              element={
                <ProtectedRoute>
                  <Browse />
                </ProtectedRoute>
              }
            />
            <Route
              path="/comic/:id"
              element={
                <ProtectedRoute>
                  <ComicDetail />
                </ProtectedRoute>
              }
            />
            <Route
              path="/recommendations"
              element={
                <ProtectedRoute>
                  <Recommendations />
                </ProtectedRoute>
              }
            />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </main>
      </div>
      
      {/* Comic Book Visual Effects */}
      <div className="fixed top-10 left-10 text-6xl transform rotate-12 opacity-20 pointer-events-none z-0">
        <span className="comic-title text-yellow-400">POW!</span>
      </div>
      <div className="fixed bottom-20 right-20 text-4xl transform -rotate-12 opacity-20 pointer-events-none z-0">
        <span className="comic-title text-red-400">BAM!</span>
      </div>
      <div className="fixed top-1/2 left-5 text-3xl transform rotate-45 opacity-15 pointer-events-none z-0">
        <span className="comic-title text-blue-400">ZAP!</span>
      </div>
    </div>
  );
};

function App() {
  return (
    <Router>
      <AuthProvider>
        <AppContent />
      </AuthProvider>
    </Router>
  );
}

export default App;