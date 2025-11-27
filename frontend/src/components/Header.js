import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

const Header = () => {
  const { user, logout, isAuthenticated } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <header className="comic-nav relative">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center py-4">
          <div className="flex items-center">
            <Link to="/" className="flex items-center space-x-2">
              <span className="comic-title text-3xl">Comic Recommender</span>
            </Link>
          </div>
          
          <nav className="hidden md:flex space-x-6">
            {isAuthenticated && (
              <>
                <Link
                  to="/browse"
                  className="comic-button px-4 py-2 text-sm hover:scale-105 transition-transform"
                >
                  Browse Comics
                </Link>
                <Link
                  to="/recommendations"
                  className="comic-button comic-button-secondary px-4 py-2 text-sm hover:scale-105 transition-transform"
                >
                  Recommendations
                </Link>
              </>
            )}
          </nav>

          <div className="flex items-center space-x-4">
            {isAuthenticated ? (
              <>
                <div className="speech-bubble hidden lg:block">
                  <span className="comic-text text-sm">Welcome, {user?.email}!</span>
                </div>
                <button
                  onClick={handleLogout}
                  className="comic-button comic-button-danger px-4 py-2 text-sm"
                >
                  Logout
                </button>
              </>
            ) : (
              <>
                <Link to="/login" className="comic-button comic-button-secondary px-4 py-2 text-sm">
                  Login
                </Link>
                <Link to="/register" className="comic-button px-4 py-2 text-sm">
                  Register
                </Link>
              </>
            )}
          </div>
        </div>
      </div>
      
      {/* Comic book style decorative elements */}
      <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-yellow-400 via-red-500 to-blue-500"></div>
    </header>
  );
};

export default Header;