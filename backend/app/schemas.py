from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import datetime


# User schemas
class UserBase(BaseModel):
    email: EmailStr


class UserCreate(UserBase):
    password: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class User(UserBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


# Comic schemas
class ComicBase(BaseModel):
    title: str
    description: str
    characters: List[str]
    genre: str
    image_url: Optional[str] = None


class ComicCreate(ComicBase):
    pass


class Comic(ComicBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


# Rating schemas
class RatingBase(BaseModel):
    comic_id: int
    rating: float


class RatingCreate(RatingBase):
    pass


class Rating(RatingBase):
    id: int
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True


# Token schemas
class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: Optional[str] = None


# Recommendation schema
class Recommendation(BaseModel):
    comic: Comic
    similarity_score: float
    explanation: str