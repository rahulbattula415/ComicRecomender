import React from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

const Home = () => {
  const { isAuthenticated } = useAuth();

  return (
    <div className="min-h-screen relative">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
        <div className="text-center">
          <h1 className="comic-title text-6xl md:text-8xl mb-6 transform hover:scale-105 transition-transform text-red-600">
            AI Comic Recommender
          </h1>
          <div className="speech-bubble max-w-4xl mx-auto mb-12">
            <p className="comic-text text-xl md:text-2xl">
              Discover your next favorite comic book with the power of artificial intelligence!
              Rate comics, get personalized recommendations, and explore amazing stories from 
              the multiverse of comics! 
              <span className="comic-title text-lg text-red-500 ml-2">KAPOW!</span>
            </p>
          </div>
          
          <div className="flex flex-col sm:flex-row gap-6 justify-center mb-16">
            {isAuthenticated ? (
              <>
                <Link to="/browse" className="comic-button text-xl px-8 py-4 comic-effect">
                  Browse Comics
                </Link>
                <Link to="/recommendations" className="comic-button comic-button-secondary text-xl px-8 py-4">
                  My Recommendations
                </Link>
              </>
            ) : (
              <>
                <Link to="/register" className="comic-button text-xl px-8 py-4 comic-effect">
                  Get Started!
                </Link>
                <Link to="/login" className="comic-button comic-button-secondary text-xl px-8 py-4">
                  Sign In
                </Link>
              </>
            )}
          </div>
        </div>
        
        <div className="grid md:grid-cols-3 gap-8 mt-16">
          <div className="comic-card p-8 text-center comic-effect">
            <h3 className="comic-subtitle text-2xl mb-4 text-blue-600">Browse & Discover</h3>
            <p className="comic-text text-lg">
              Explore our extensive collection of comic books across various genres and discover new favorites from the Marvel and DC universes!
            </p>
          </div>
          
          <div className="comic-card p-8 text-center comic-effect">
            <h3 className="comic-subtitle text-2xl mb-4 text-blue-600">Rate & Review</h3>
            <p className="comic-text text-lg">
              Rate comics you've read and build your personal profile to help our AI understand your superhero preferences!
            </p>
          </div>
          
          <div className="comic-card p-8 text-center comic-effect">
            <h3 className="comic-subtitle text-2xl mb-4 text-blue-600">AI Recommendations</h3>
            <p className="comic-text text-lg">
              Get personalized comic recommendations powered by machine learning algorithms that understand your taste!
            </p>
          </div>
        </div>
        
        {/* Comic book style feature callouts */}
        <div className="mt-20 text-center">
          <div className="comic-panel p-12 max-w-4xl mx-auto">
            <h2 className="comic-title text-4xl mb-6 text-red-500">How It Works!</h2>
            <div className="grid md:grid-cols-3 gap-8">
              <div className="text-center">
                <div className="w-16 h-16 bg-yellow-400 rounded-full flex items-center justify-center mx-auto mb-4 border-4 border-black">
                  <span className="comic-text text-black text-2xl font-bold">1</span>
                </div>
                <p className="comic-text">Sign up and browse our comic collection</p>
              </div>
              <div className="text-center">
                <div className="w-16 h-16 bg-red-400 rounded-full flex items-center justify-center mx-auto mb-4 border-4 border-black">
                  <span className="comic-text text-white text-2xl font-bold">2</span>
                </div>
                <p className="comic-text">Rate comics you love (or hate!)</p>
              </div>
              <div className="text-center">
                <div className="w-16 h-16 bg-blue-400 rounded-full flex items-center justify-center mx-auto mb-4 border-4 border-black">
                  <span className="comic-text text-white text-2xl font-bold">3</span>
                </div>
                <p className="comic-text">Get AI-powered recommendations!</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Home;