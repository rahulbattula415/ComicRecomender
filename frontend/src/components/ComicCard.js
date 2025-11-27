import React from 'react';
import { Link } from 'react-router-dom';

const ComicCard = ({ comic, userRating, onRate }) => {
  return (
    <Link to={`/comic/${comic.id}`} className="block">
      <div className="comic-card p-4 comic-effect hover:scale-105 transition-transform duration-300 cursor-pointer">
        <div className="relative">
          {comic.image_url ? (
            <img
              src={comic.image_url}
              alt={comic.title}
              className="w-full h-80 object-cover rounded-lg border-4 border-black shadow-lg"
            />
          ) : (
            <div className="w-full h-80 bg-gradient-to-br from-yellow-400 to-red-500 flex items-center justify-center rounded-lg border-4 border-black shadow-lg">
              <span className="text-6xl">📖</span>
            </div>
          )}
          
          {/* Comic book effect overlay */}
          <div className="absolute top-2 right-2 comic-title text-lg text-yellow-400 transform rotate-12 opacity-90 drop-shadow-lg">
            MARVEL
          </div>
          
          {/* Rating overlay if user has rated */}
          {userRating && (
            <div className="absolute top-2 left-2 bg-yellow-400 text-black px-2 py-1 rounded-full border-2 border-black comic-text text-sm">
              ⭐ {userRating}/5
            </div>
          )}
        </div>
        
        <div className="mt-4 text-center">
          <h3 className="comic-name text-lg leading-tight text-blue-600 hover:text-red-500 transition-colors">
            {comic.title}
          </h3>
        </div>
      </div>
    </Link>
  );
};

export default ComicCard;