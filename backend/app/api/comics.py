from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ..core.database import get_db
from ..models import Comic
from ..schemas import Comic as ComicSchema, ComicCreate
from .auth import get_current_user

router = APIRouter()


@router.get("/", response_model=List[ComicSchema])
def get_comics(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    comics = db.query(Comic).offset(skip).limit(limit).all()
    return comics


@router.get("/{comic_id}", response_model=ComicSchema)
def get_comic(comic_id: int, db: Session = Depends(get_db)):
    comic = db.query(Comic).filter(Comic.id == comic_id).first()
    if comic is None:
        raise HTTPException(status_code=404, detail="Comic not found")
    return comic


@router.post("/", response_model=ComicSchema)
def create_comic(comic: ComicCreate, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    db_comic = Comic(**comic.dict())
    db.add(db_comic)
    db.commit()
    db.refresh(db_comic)
    return db_comic