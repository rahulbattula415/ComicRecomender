from sqlalchemy import Column, Integer, String, Float, Text, ForeignKey, DateTime, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..core.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    ratings = relationship("UserRating", back_populates="user")


class Comic(Base):
    __tablename__ = "comics"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False, index=True)
    description = Column(Text, nullable=False)
    characters = Column(JSON, nullable=False)  # Using JSON instead of ARRAY for SQLite compatibility
    genre = Column(String, nullable=False)
    image_url = Column(String, nullable=True)
    external_id = Column(String, nullable=True, unique=True, index=True)  # For tracking comics from different sources (Marvel, ComicVine, etc.)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    ratings = relationship("UserRating", back_populates="comic")


class UserRating(Base):
    __tablename__ = "user_ratings"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    comic_id = Column(Integer, ForeignKey("comics.id"), nullable=False)
    rating = Column(Float, nullable=False)  # 1-5 stars
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="ratings")
    comic = relationship("Comic", back_populates="ratings")