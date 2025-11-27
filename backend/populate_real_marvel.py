#!/usr/bin/env python3
"""
Script to populate database with real Marvel comics from API
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from app.core.database import SessionLocal
from app.models import Comic
from app.services.marvel_comics import marvel_comics_service

def populate_with_real_marvel_comics():
    """Replace database with real Marvel comics from API"""
    print("🦸‍♂️ Fetching real Marvel comics from API...")
    
    # Fetch real Marvel comics
    marvel_comics = marvel_comics_service.fetch_popular_marvel_comics(limit=20)
    
    if not marvel_comics:
        print("❌ No Marvel comics fetched. Check API keys and connection.")
        return
    
    db = SessionLocal()
    try:
        # Clear existing comics
        existing_count = db.query(Comic).count()
        if existing_count > 0:
            print(f"🗑️  Clearing {existing_count} existing comics...")
            db.query(Comic).delete()
            db.commit()
        
        # Add real Marvel comics
        added_count = 0
        for comic_data in marvel_comics:
            if comic_data.get('image_url'):  # Only add comics with valid images
                comic = Comic(
                    title=comic_data['title'],
                    description=comic_data['description'],
                    characters=comic_data['characters'],
                    genre=comic_data['genre'],
                    image_url=comic_data['image_url']
                )
                db.add(comic)
                added_count += 1
                print(f"✅ Added: {comic_data['title']}")
        
        db.commit()
        print(f"\n🎉 Successfully populated database with {added_count} real Marvel comics!")
        print("📚 Database now contains actual Marvel comic runs with official cover images!")
        
    except Exception as e:
        print(f"❌ Error populating database: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    populate_with_real_marvel_comics()