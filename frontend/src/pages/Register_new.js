import React, { useState } from 'react';
import { Link, Navigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

const Register = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { register, isAuthenticated } = useAuth();

  if (isAuthenticated) {
    return <Navigate to="/browse" replace />;
  }

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    if (password !== confirmPassword) {
      setError('Passwords do not match');
      setLoading(false);
      return;
    }

    if (password.length < 6) {
      setError('Password must be at least 6 characters long');
      setLoading(false);
      return;
    }

    const result = await register(email, password);
    
    if (!result.success) {
      setError(result.error);
    }
    
    setLoading(false);
  };

  return (
    <div className="min-h-screen flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8 relative">
      <div className="max-w-md w-full space-y-8">
        <div className="comic-panel p-8">
          <div className="text-center mb-8">
            <div className="text-6xl mb-4">🦸‍♂️</div>
            <h2 className="comic-title text-4xl text-center mb-4">
              Join the Squad!
            </h2>
            <div className="speech-bubble">
              <p className="comic-text text-center">
                Ready to discover amazing comics? Create your superhero account!
              </p>
            </div>
          </div>

          {error && (
            <div className="comic-alert-error p-4 mb-4 text-center">
              <span className="text-lg">❌ {error}</span>
            </div>
          )}

          <form className="space-y-6" onSubmit={handleSubmit}>
            <div>
              <label htmlFor="email" className="comic-text text-lg block mb-2">
                Email Address
              </label>
              <input
                id="email"
                name="email"
                type="email"
                autoComplete="email"
                required
                className="comic-input w-full px-4 py-3 text-lg"
                placeholder="your.email@example.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
              />
            </div>

            <div>
              <label htmlFor="password" className="comic-text text-lg block mb-2">
                Password
              </label>
              <input
                id="password"
                name="password"
                type="password"
                autoComplete="new-password"
                required
                className="comic-input w-full px-4 py-3 text-lg"
                placeholder="Super secret password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
              />
            </div>

            <div>
              <label htmlFor="confirmPassword" className="comic-text text-lg block mb-2">
                Confirm Password
              </label>
              <input
                id="confirmPassword"
                name="confirmPassword"
                type="password"
                autoComplete="new-password"
                required
                className="comic-input w-full px-4 py-3 text-lg"
                placeholder="Confirm your super secret password"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
              />
            </div>

            <div>
              <button
                type="submit"
                disabled={loading}
                className="comic-button w-full py-4 text-xl comic-effect"
              >
                {loading ? (
                  <span className="flex items-center justify-center">
                    <div className="comic-loader mr-2"></div>
                    Creating Account...
                  </span>
                ) : (
                  'Create Account!'
                )}
              </button>
            </div>

            <div className="text-center">
              <p className="comic-text">
                Already have an account?{' '}
                <Link
                  to="/login"
                  className="comic-subtitle text-blue-500 hover:text-blue-700 underline"
                >
                  Sign in here!
                </Link>
              </p>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
};

export default Register;