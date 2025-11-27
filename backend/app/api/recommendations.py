from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..core.database import get_db
from ..models import User
from ..schemas import Recommendation
from ..services.recommendation import RecommendationService
from .auth import get_current_user

router = APIRouter()


@router.get("/", response_model=List[Recommendation])
def get_recommendations(
    limit: int = 5,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    recommendation_service = RecommendationService(db)
    recommendations = recommendation_service.get_recommendations(current_user.id, limit)
    return recommendations