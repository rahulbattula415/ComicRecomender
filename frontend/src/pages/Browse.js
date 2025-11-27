import React, { useState, useEffect } from 'react';
import { comicsAPI, ratingsAPI } from '../services/api';
import ComicCard from '../components/ComicCard';
import LoadingSpinner from '../components/LoadingSpinner';

const Browse = () => {
  const [comics, setComics] = useState([]);
  const [userRatings, setUserRatings] = useState({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchComics();
    fetchUserRatings();
  }, []);

  const fetchComics = async () => {
    try {
      const response = await comicsAPI.getComics();
      setComics(response.data);
    } catch (err) {
      setError('Failed to fetch comics');
    }
  };

  const fetchUserRatings = async () => {
    try {
      const response = await ratingsAPI.getUserRatings();
      const ratingsMap = {};
      response.data.forEach(rating => {
        ratingsMap[rating.comic_id] = rating.rating;
      });
      setUserRatings(ratingsMap);
    } catch (err) {
      console.error('Failed to fetch user ratings:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleRate = async (comicId, rating) => {
    try {
      await ratingsAPI.createRating(comicId, rating);
      setUserRatings(prev => ({
        ...prev,
        [comicId]: rating
      }));
    } catch (err) {
      console.error('Failed to rate comic:', err);
    }
  };

  if (loading) {
    return <LoadingSpinner />;
  }

  if (error) {
    return (
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
          {error}
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="mb-8 text-center">
        <h1 className="comic-title text-5xl mb-4 text-red-600">Marvel Comics Collection!</h1>
        <div className="speech-bubble max-w-2xl mx-auto">
          <p className="comic-text text-lg">
            Discover amazing Marvel comic books and rate them to get personalized recommendations! Each comic features authentic Marvel covers from our API!
          </p>
        </div>
      </div>

      {comics.length === 0 ? (
        <div className="text-center py-12">
          <div className="comic-panel p-8 max-w-md mx-auto">
            <h3 className="comic-subtitle text-xl mb-2">No Comics Available!</h3>
            <p className="comic-text">Check back later for new Marvel adventures!</p>
          </div>
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-8">
          {comics.map(comic => (
            <ComicCard
              key={comic.id}
              comic={comic}
              userRating={userRatings[comic.id]}
              onRate={handleRate}
            />
          ))}
        </div>
      )}
    </div>
  );
};

export default Browse;