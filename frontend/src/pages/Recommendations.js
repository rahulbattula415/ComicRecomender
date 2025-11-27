import React, { useState, useEffect } from 'react';
import { recommendationsAPI } from '../services/api';
import ComicCard from '../components/ComicCard';
import LoadingSpinner from '../components/LoadingSpinner';

const Recommendations = () => {
  const [recommendations, setRecommendations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchRecommendations();
  }, []);

  const fetchRecommendations = async () => {
    try {
      const response = await recommendationsAPI.getRecommendations();
      setRecommendations(response.data);
    } catch (err) {
      setError('Failed to fetch recommendations');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="comic-loader mb-4"></div>
          <p className="comic-text text-xl">Finding your perfect comics...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="comic-alert-error p-6 text-center">
          <span className="text-2xl">{error}</span>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 relative">
      {/* Header Section */}
      <div className="text-center mb-12">
        <h1 className="comic-title text-6xl mb-4">AI Recommendations!</h1>
        <div className="speech-bubble max-w-3xl mx-auto">
          <p className="comic-text text-xl">
            Based on your reading history and ratings, here are comics our AI thinks you'll absolutely love! 
            <span className="comic-title text-lg text-purple-500 ml-2">BOOM!</span>
          </p>
        </div>
      </div>

      {recommendations.length === 0 ? (
        <div className="text-center py-12">
          <div className="comic-panel p-12 max-w-2xl mx-auto">
            <h3 className="comic-subtitle text-3xl mb-4">No Recommendations Yet!</h3>
            <div className="speech-bubble mb-6">
              <p className="comic-text text-lg">
                Rate some comics to help our AI learn your superhero preferences and get amazing personalized recommendations!
              </p>
            </div>
            <a
              href="/browse"
              className="comic-button text-xl px-8 py-4 comic-effect"
            >
              Browse Comics Now!
            </a>
          </div>
        </div>
      ) : (
        <div className="space-y-8">
          {recommendations.map((recommendation, index) => (
            <div key={recommendation.comic.id} className="comic-panel p-8 comic-effect">
              <div className="flex items-start space-x-6">
                {/* Recommendation Rank Badge */}
                <div className="flex-shrink-0">
                  <div className="w-16 h-16 bg-gradient-to-br from-yellow-400 to-orange-500 rounded-full flex items-center justify-center border-4 border-black transform rotate-6">
                    <span className="comic-title text-2xl text-black">#{index + 1}</span>
                  </div>
                </div>
                
                <div className="flex-1">
                  <div className="grid md:grid-cols-4 gap-6">
                    {/* Comic Card */}
                    <div className="md:col-span-1">
                      <ComicCard comic={recommendation.comic} />
                    </div>
                    
                    {/* Comic Details */}
                    <div className="md:col-span-3 flex flex-col justify-center">
                      <div className="mb-6">
                        <h3 className="comic-subtitle text-2xl mb-3">
                          {recommendation.comic.title}
                        </h3>
                        <p className="comic-text text-lg mb-4">
                          {recommendation.comic.description}
                        </p>
                        
                        <div className="mb-4">
                          <span className="comic-button text-sm px-4 py-2 transform -rotate-1">
                            {recommendation.comic.genre}
                          </span>
                        </div>
                        
                        {recommendation.comic.characters && recommendation.comic.characters.length > 0 && (
                          <div className="mb-4">
                            <p className="comic-text text-sm mb-2">Heroes in this comic:</p>
                            <div className="flex flex-wrap gap-2">
                              {recommendation.comic.characters.slice(0, 5).map((character, idx) => (
                                <span
                                  key={idx}
                                  className="inline-block bg-gradient-to-r from-blue-400 to-purple-500 text-white text-sm px-3 py-1 rounded-full border-2 border-black"
                                >
                                  {character}
                                </span>
                              ))}
                              {recommendation.comic.characters.length > 5 && (
                                <span className="inline-block bg-gray-400 text-white text-sm px-3 py-1 rounded-full border-2 border-black">
                                  +{recommendation.comic.characters.length - 5} more
                                </span>
                              )}
                            </div>
                          </div>
                        )}
                      </div>
                      
                      {/* AI Explanation Panel */}
                      <div className="comic-card p-6 bg-gradient-to-r from-green-100 to-blue-100">
                        <h4 className="comic-subtitle text-lg mb-3 flex items-center">
                          <span className="text-2xl mr-2">🧠</span>
                          Why our AI recommends this:
                        </h4>
                        <div className="speech-bubble bg-white">
                          <p className="comic-text text-sm">
                            {recommendation.explanation}
                          </p>
                        </div>
                        <div className="mt-3 text-center">
                          <div className="inline-block comic-button comic-button-secondary text-xs px-3 py-1">
                            Match Score: {(recommendation.similarity_score * 100).toFixed(1)}% 
                            <span className="ml-1">⚡</span>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
      
      {/* Comic book visual effects */}
      <div className="fixed bottom-10 left-10 text-4xl transform rotate-12 opacity-20 pointer-events-none">
        <span className="comic-title text-green-400">MATCH!</span>
      </div>
      <div className="fixed top-20 right-10 text-3xl transform -rotate-12 opacity-15 pointer-events-none">
        <span className="comic-title text-purple-400">AI!</span>
      </div>
    </div>
  );
};

export default Recommendations;