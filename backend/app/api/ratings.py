from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ..core.database import get_db
from ..models import UserRating, User
from ..schemas import RatingCreate, Rating as RatingSchema
from .auth import get_current_user

router = APIRouter()


@router.post("/", response_model=RatingSchema)
def create_rating(rating: RatingCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    # Check if user already rated this comic
    existing_rating = db.query(UserRating).filter(
        UserRating.user_id == current_user.id,
        UserRating.comic_id == rating.comic_id
    ).first()
    
    if existing_rating:
        # Update existing rating
        existing_rating.rating = rating.rating
        db.commit()
        db.refresh(existing_rating)
        return existing_rating
    else:
        # Create new rating
        db_rating = UserRating(
            user_id=current_user.id,
            comic_id=rating.comic_id,
            rating=rating.rating
        )
        db.add(db_rating)
        db.commit()
        db.refresh(db_rating)
        return db_rating


@router.get("/", response_model=List[RatingSchema])
def get_user_ratings(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    ratings = db.query(UserRating).filter(UserRating.user_id == current_user.id).all()
    return ratings


@router.get("/{comic_id}", response_model=RatingSchema)
def get_user_rating_for_comic(comic_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    rating = db.query(UserRating).filter(
        UserRating.user_id == current_user.id,
        UserRating.comic_id == comic_id
    ).first()
    
    if rating is None:
        raise HTTPException(status_code=404, detail="Rating not found")
    
    return rating