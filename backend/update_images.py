#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(__file__))

from app.core.database import SessionLocal
from app.core.config import settings
from app.models import Comic
from app.services.comic_images import comic_image_service

def update_comic_images():
    """Update all comics with better matching images using Marvel API"""
    print("🎨 Updating comic book cover images with Marvel API...")
    
    # Check Marvel API status
    if settings.marvel_public_api_key and settings.marvel_private_api_key:
        print("🔑 Marvel API keys detected - using real comic cover images!")
    else:
        print("ℹ️  No Marvel API keys - using fallback images")
    
    db = SessionLocal()
    try:
        comics = db.query(Comic).all()
        updated_count = 0
        
        for comic in comics:
            print(f"📚 Updating image for: {comic.title}")
            
            # Get better image based on title, characters, and genre
            old_image = comic.image_url
            new_image_url = comic_image_service.update_comic_image(
                comic_title=comic.title,
                characters=comic.characters if comic.characters else [],
                genre=comic.genre
            )
            
            # Update the comic's image URL
            comic.image_url = new_image_url
            
            if old_image != new_image_url:
                updated_count += 1
                print(f"   ✅ New image: {new_image_url}")
            else:
                print(f"   ℹ️  Image unchanged")
        
        # Commit all changes
        db.commit()
        print(f"\n🎉 Successfully updated {updated_count} comic book covers!")
        
        if settings.marvel_public_api_key and settings.marvel_private_api_key:
            print("🎯 Real Marvel comic covers have been applied where available!")
        
    except Exception as e:
        print(f"❌ Error updating comic images: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    update_comic_images()