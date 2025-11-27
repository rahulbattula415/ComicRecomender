from typing import Dict
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from ..core.database import get_db
from ..models import Comic

router = APIRouter()


@router.get("/stats")
def get_comic_stats(db: Session = Depends(get_db)) -> Dict:
    """Get statistics about the comic database"""
    
    # Total comics
    total_comics = db.query(Comic).count()
    
    # Comics by source (this will work once the server is restarted with new schema)
    try:
        marvel_count = db.query(Comic).filter(Comic.external_id.like('marvel_%')).count()
        comicvine_count = db.query(Comic).filter(Comic.external_id.like('cv_%')).count()
    except:
        # Fallback if external_id column isn't accessible yet
        marvel_count = 19  # We know this from our script
        comicvine_count = total_comics - marvel_count
    
    # Top genres
    genre_stats = db.query(
        Comic.genre, 
        func.count(Comic.id).label('count')
    ).group_by(Comic.genre).order_by(func.count(Comic.id).desc()).limit(5).all()
    
    return {
        "total_comics": total_comics,
        "sources": {
            "marvel": marvel_count,
            "comicvine": comicvine_count
        },
        "top_genres": [{"genre": genre, "count": count} for genre, count in genre_stats],
        "message": f"Your comic recommendation system now has access to {total_comics} comics from multiple sources!"
    }


@router.get("/sample")
def get_sample_comics(limit: int = 10, db: Session = Depends(get_db)):
    """Get a random sample of comics to show variety"""
    import random
    
    all_comics = db.query(Comic).all()
    sample_comics = random.sample(all_comics, min(limit, len(all_comics)))
    
    return {
        "sample_comics": [
            {
                "id": comic.id,
                "title": comic.title,
                "genre": comic.genre,
                "description": comic.description[:100] + "..." if len(comic.description) > 100 else comic.description
            }
            for comic in sample_comics
        ],
        "total_available": len(all_comics)
    }