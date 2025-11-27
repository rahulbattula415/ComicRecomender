from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ..core.database import get_db
from ..models import Comic
from ..services.comic_images import comic_image_service
from ..schemas import Comic as ComicSchema

router = APIRouter()

@router.post("/refresh-images", response_model=List[ComicSchema])
def refresh_comic_images(db: Session = Depends(get_db)):
    """
    Refresh all comic book cover images with better matching images
    """
    try:
        comics = db.query(Comic).all()
        updated_comics = []
        
        for comic in comics:
            # Get better image based on title, characters, and genre
            new_image_url = comic_image_service.update_comic_image(
                comic_title=comic.title,
                characters=comic.characters if comic.characters else [],
                genre=comic.genre
            )
            
            # Update the comic's image URL
            comic.image_url = new_image_url
            updated_comics.append(comic)
        
        # Commit all changes
        db.commit()
        
        # Refresh objects to get updated data
        for comic in updated_comics:
            db.refresh(comic)
        
        return updated_comics
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to refresh images: {str(e)}")

@router.get("/image-suggestions/{comic_id}")
def get_image_suggestions(comic_id: int, db: Session = Depends(get_db)):
    """
    Get image suggestions for a specific comic
    """
    comic = db.query(Comic).filter(Comic.id == comic_id).first()
    if not comic:
        raise HTTPException(status_code=404, detail="Comic not found")
    
    # Get different image options
    suggestions = {
        "current": comic.image_url,
        "by_title": comic_image_service.get_marvel_comic_image(comic.title, comic.characters),
        "by_genre": comic_image_service.get_comic_image_by_genre(comic.genre),
        "recommended": comic_image_service.update_comic_image(comic.title, comic.characters, comic.genre)
    }
    
    return {
        "comic_id": comic_id,
        "comic_title": comic.title,
        "suggestions": suggestions
    }