from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    database_url: str = "sqlite:///./comic_recommender.db"
    secret_key: str = "your-secret-key-here-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # Marvel API settings
    marvel_public_api_key: Optional[str] = None
    marvel_private_api_key: Optional[str] = None
    marvel_api_base_url: str = "https://gateway.marvel.com/v1/public"
    
    # ComicVine API settings
    comic_vine_api_key: Optional[str] = None
    
    # For demo purposes, we'll use a free comic image API
    comic_image_api_base: str = "https://comicvine.gamespot.com/api"
    
    class Config:
        env_file = ".env"


settings = Settings()