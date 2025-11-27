import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { comicsAPI, ratingsAPI } from '../services/api';
import LoadingSpinner from '../components/LoadingSpinner';

const ComicDetail = () => {
  const { id } = useParams();
  const [comic, setComic] = useState(null);
  const [userRating, setUserRating] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchComic();
    fetchUserRating();
  }, [id]);

  const fetchComic = async () => {
    try {
      const response = await comicsAPI.getComic(id);
      setComic(response.data);
    } catch (err) {
      setError('Failed to fetch comic details');
    } finally {
      setLoading(false);
    }
  };

  const fetchUserRating = async () => {
    try {
      const response = await ratingsAPI.getUserRatingForComic(id);
      setUserRating(response.data.rating);
    } catch (err) {
      // User hasn't rated this comic yet
      setUserRating(null);
    }
  };

  const handleRate = async (rating) => {
    try {
      await ratingsAPI.createRating(parseInt(id), rating);
      setUserRating(rating);
    } catch (err) {
      console.error('Failed to rate comic:', err);
    }
  };

  const renderStars = () => {
    const stars = [];
    for (let i = 1; i <= 5; i++) {
      stars.push(
        <button
          key={i}
          onClick={() => handleRate(i)}
          className={`text-4xl comic-star transform hover:scale-125 transition-transform ${
            i <= (userRating || 0) ? 'text-yellow-400' : 'text-gray-400'
          } hover:text-yellow-400`}
        >
          ★
        </button>
      );
    }
    return stars;
  };

  if (loading) {
    return <LoadingSpinner />;
  }

  if (error || !comic) {
    return (
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
          {error || 'Comic not found'}
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="comic-card comic-effect overflow-hidden">
        <div className="md:flex">
          <div className="md:w-1/2 p-3 flex items-center justify-center">
            {comic.image_url ? (
              <img
                src={comic.image_url}
                alt={comic.title}
                className="max-w-full h-full object-contain rounded-lg border-4 border-black shadow-lg"
              />
            ) : (
              <div className="w-full max-w-sm h-full bg-gradient-to-br from-yellow-400 to-red-500 flex items-center justify-center rounded-lg border-4 border-black">
                <span className="text-6xl">📖</span>
              </div>
            )}
          </div>
          
          <div className="md:w-1/2 p-8 flex flex-col justify-center min-h-[500px]">
            <div className="space-y-8">
              <div>
                <h1 className="comic-title text-4xl mb-6 text-red-600">
                  {comic.title}
                </h1>
              </div>
              
              <div>
                <span className="comic-button text-sm px-4 py-2 transform rotate-1">
                  {comic.genre}
                </span>
              </div>
              
              <div className="speech-bubble">
                <p className="comic-text text-lg leading-relaxed">
                  {comic.description}
                </p>
              </div>
              
              {comic.characters && comic.characters.length > 0 && (
                <div>
                  <h3 className="comic-subtitle text-xl mb-4 text-blue-600">Heroes</h3>
                  <div className="flex flex-wrap gap-2">
                    {comic.characters.map((character, index) => (
                      <span
                        key={index}
                        className="inline-block bg-gradient-to-r from-blue-400 to-purple-500 text-white px-3 py-1 rounded-full border-2 border-black comic-text text-sm"
                      >
                        {character}
                      </span>
                    ))}
                  </div>
                </div>
              )}
              
              <div className="comic-panel p-6 border-4 border-black">
                <h3 className="comic-subtitle text-xl mb-4 text-red-600">Rate this comic!</h3>
                <div className="flex items-center justify-center space-x-2 mb-4">
                  {renderStars()}
                </div>
                {userRating && (
                  <p className="comic-text text-center text-yellow-600">
                    POW! You rated this {userRating}/5 stars!
                  </p>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ComicDetail;