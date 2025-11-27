from typing import List, Dict
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sqlalchemy.orm import Session
from ..models import Comic, UserRating
from ..schemas import Recommendation


class RecommendationService:
    def __init__(self, db: Session):
        self.db = db
        self.vectorizer = TfidfVectorizer(stop_words='english', max_features=1000)
        
    def _create_content_features(self, comics: List[Comic]) -> pd.DataFrame:
        """Create content features for comics using TF-IDF"""
        data = []
        for comic in comics:
            # Combine description, characters, and genre for content analysis
            characters_text = ' '.join(comic.characters) if comic.characters else ''
            combined_text = f"{comic.description} {characters_text} {comic.genre}"
            data.append({
                'id': comic.id,
                'title': comic.title,
                'content': combined_text,
                'genre': comic.genre,
                'characters': comic.characters
            })
        return pd.DataFrame(data)
    
    def _get_user_preferences(self, user_id: int) -> List[int]:
        """Get comics that user rated highly (3+ stars)"""
        high_ratings = self.db.query(UserRating).filter(
            UserRating.user_id == user_id,
            UserRating.rating >= 3.0
        ).all()
        return [rating.comic_id for rating in high_ratings]
    
    def get_recommendations(self, user_id: int, num_recommendations: int = 5) -> List[Recommendation]:
        """Generate recommendations using content-based filtering"""
        # Get all comics
        all_comics = self.db.query(Comic).all()
        if len(all_comics) < 2:
            return []
        
        # Get user's highly rated comics
        liked_comic_ids = self._get_user_preferences(user_id)
        if not liked_comic_ids:
            # If user has no high ratings, return popular comics
            return self._get_popular_comics(num_recommendations)
        
        # Create content features
        comics_df = self._create_content_features(all_comics)
        
        # Create TF-IDF matrix
        tfidf_matrix = self.vectorizer.fit_transform(comics_df['content'])
        
        # Calculate similarity scores
        cosine_sim = cosine_similarity(tfidf_matrix)
        
        # Get recommendations for liked comics
        recommendations = {}
        
        for comic_id in liked_comic_ids:
            comic_idx = comics_df[comics_df['id'] == comic_id].index
            if len(comic_idx) == 0:
                continue
            comic_idx = comic_idx[0]
            
            # Get similarity scores for this comic
            sim_scores = list(enumerate(cosine_sim[comic_idx]))
            sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
            
            # Add top similar comics to recommendations
            for idx, score in sim_scores[1:]:  # Skip the comic itself
                comic_id_rec = comics_df.iloc[idx]['id']
                if comic_id_rec not in liked_comic_ids:  # Don't recommend already liked comics
                    if comic_id_rec not in recommendations or recommendations[comic_id_rec]['score'] < score:
                        recommendations[comic_id_rec] = {
                            'score': score,
                            'similar_to': comics_df.iloc[comic_idx]['title']
                        }
        
        # Get user's already rated comics to exclude
        user_ratings = self.db.query(UserRating).filter(UserRating.user_id == user_id).all()
        rated_comic_ids = {rating.comic_id for rating in user_ratings}
        
        # Filter out already rated comics
        recommendations = {k: v for k, v in recommendations.items() if k not in rated_comic_ids}
        
        # Sort by similarity score and get top N
        sorted_recommendations = sorted(
            recommendations.items(), 
            key=lambda x: x[1]['score'], 
            reverse=True
        )[:num_recommendations]
        
        # Convert to Recommendation objects
        result = []
        for comic_id, rec_data in sorted_recommendations:
            # Convert numpy int64 to regular Python int for SQLAlchemy compatibility
            comic_id = int(comic_id)
            
            comic = self.db.query(Comic).filter(Comic.id == comic_id).first()
            
            if comic:
                explanation = f"Recommended because it's similar to '{rec_data['similar_to']}' (similarity: {rec_data['score']:.2f})"
                result.append(Recommendation(
                    comic=comic,
                    similarity_score=rec_data['score'],
                    explanation=explanation
                ))
        
        return result
    
    def _get_popular_comics(self, num_recommendations: int = 5) -> List[Recommendation]:
        """Get popular comics as fallback when user has no ratings"""
        # First try to get comics with ratings, ordered by average rating
        from sqlalchemy import func
        popular_comics_with_ratings = self.db.query(Comic).join(UserRating).group_by(Comic.id).order_by(
            func.avg(UserRating.rating).desc()
        ).limit(num_recommendations).all()
        
        # If we don't have enough comics with ratings, get any comics
        if len(popular_comics_with_ratings) < num_recommendations:
            remaining_needed = num_recommendations - len(popular_comics_with_ratings)
            # Get comics that haven't been rated yet
            rated_comic_ids = [comic.id for comic in popular_comics_with_ratings]
            additional_comics = self.db.query(Comic).filter(
                ~Comic.id.in_(rated_comic_ids)
            ).limit(remaining_needed).all()
            popular_comics_with_ratings.extend(additional_comics)
        
        result = []
        for comic in popular_comics_with_ratings:
            result.append(Recommendation(
                comic=comic,
                similarity_score=0.0,
                explanation="Popular comic - recommended for new users"
            ))
        
        return result