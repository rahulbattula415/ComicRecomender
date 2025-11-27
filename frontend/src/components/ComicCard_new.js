import React from 'react';
import { Link } from 'react-router-dom';

const ComicCard = ({ comic, userRating, onRate }) => {
  const renderStars = (rating) => {
    const stars = [];
    for (let i = 1; i <= 5; i++) {
      stars.push(
        <button
          key={i}
          onClick={() => onRate && onRate(comic.id, i)}
          className={`text-3xl comic-star transform hover:scale-125 transition-transform ${
            i <= (rating || 0) ? 'text-yellow-400' : 'text-gray-400'
          } hover:text-yellow-400`}
          disabled={!onRate}
        >
          ★
        </button>
      );
    }
    return stars;
  };

  return (
    <div className="comic-card p-6 comic-effect">
      <div className="relative">
        {comic.image_url ? (
          <img
            src={comic.image_url}
            alt={comic.title}
            className="w-full h-48 object-cover rounded-lg border-4 border-black"
          />
        ) : (
          <div className="w-full h-48 bg-gradient-to-br from-yellow-400 to-red-500 flex items-center justify-center rounded-lg border-4 border-black">
            <span className="text-6xl">📖</span>
          </div>
        )}
        
        {/* Comic book effect overlay */}
        <div className="absolute top-2 right-2 comic-title text-2xl text-yellow-400 transform rotate-12 opacity-80">
          NEW!
        </div>
      </div>
      
      <div className="mt-4">
        <h3 className="comic-subtitle text-xl mb-2 text-center">
          {comic.title}
        </h3>
        
        <div className="speech-bubble mb-4">
          <p className="comic-text text-sm line-clamp-3">
            {comic.description}
          </p>
        </div>
        
        <div className="mb-4 text-center">
          <span className="comic-button text-xs px-3 py-1 transform rotate-1">
            {comic.genre}
          </span>
        </div>
        
        {comic.characters && comic.characters.length > 0 && (
          <div className="mb-4">
            <p className="comic-text text-sm mb-2">🦸‍♂️ Heroes:</p>
            <div className="flex flex-wrap gap-1">
              {comic.characters.slice(0, 3).map((character, index) => (
                <span
                  key={index}
                  className="inline-block bg-gradient-to-r from-blue-400 to-purple-500 text-white text-xs px-2 py-1 rounded-full border-2 border-black"
                >
                  {character}
                </span>
              ))}
              {comic.characters.length > 3 && (
                <span className="inline-block bg-gray-400 text-white text-xs px-2 py-1 rounded-full border-2 border-black">
                  +{comic.characters.length - 3} more
                </span>
              )}
            </div>
          </div>
        )}
        
        {onRate && (
          <div className="mb-4">
            <p className="comic-text text-sm mb-2 text-center">Rate this comic:</p>
            <div className="flex justify-center space-x-1">
              {renderStars(userRating)}
            </div>
          </div>
        )}
        
        <Link
          to={`/comic/${comic.id}`}
          className="comic-button comic-button-secondary w-full py-2 text-center block"
        >
          Read More!
        </Link>
      </div>
    </div>
  );
};

export default ComicCard;