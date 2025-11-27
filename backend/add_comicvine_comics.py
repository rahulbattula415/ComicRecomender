#!/usr/bin/env python3
"""
Script to add ComicVine comics to the database
"""
import os
import sys
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent
sys.path.append(str(backend_dir))

from sqlalchemy import text
from app.core.database import SessionLocal, engine
from app.models import Comic
from app.services.comicvine import ComicVineService


def add_external_id_column():
    """Add external_id column to existing comics table if it doesn't exist"""
    db = SessionLocal()
    try:
        # Check if external_id column exists
        result = db.execute(text("PRAGMA table_info(comics)"))
        columns = [row[1] for row in result.fetchall()]
        
        if 'external_id' not in columns:
            print("Adding external_id column to comics table...")
            db.execute(text("ALTER TABLE comics ADD COLUMN external_id VARCHAR"))
            db.commit()
            print("✅ Successfully added external_id column")
        else:
            print("✅ external_id column already exists")
            
        # Update existing Marvel comics with external_id
        marvel_comics = db.query(Comic).filter(Comic.external_id.is_(None)).all()
        for comic in marvel_comics:
            # Generate a Marvel external ID based on the comic title
            external_id = f"marvel_{comic.id}"
            comic.external_id = external_id
            
        db.commit()
        print(f"✅ Updated {len(marvel_comics)} existing Marvel comics with external_id")
        
    except Exception as e:
        print(f"❌ Error updating database schema: {e}")
        db.rollback()
    finally:
        db.close()


def fetch_comicvine_comics():
    """Fetch trending comics from ComicVine"""
    try:
        service = ComicVineService()
        db = SessionLocal()
        added_count = service.add_trending_comics_to_db(db, limit=100)
        db.close()
        return added_count
    except Exception as e:
        print(f"❌ Error fetching ComicVine comics: {e}")
        return 0


def main():
    print("🚀 Adding ComicVine comics to database...")
    print("=" * 50)
    
    # Step 1: Update database schema
    add_external_id_column()
    
    # Step 2: Fetch ComicVine comics
    print("\n📚 Fetching trending comics from ComicVine...")
    added_count = fetch_comicvine_comics()
    
    if added_count > 0:
        print(f"\n🎉 Successfully added {added_count} new comics from ComicVine!")
        
        # Show total comics count
        db = SessionLocal()
        total_comics = db.query(Comic).count()
        marvel_comics = db.query(Comic).filter(Comic.external_id.like('marvel_%')).count()
        comicvine_comics = db.query(Comic).filter(Comic.external_id.like('cv_%')).count()
        db.close()
        
        print(f"\n📊 Database Summary:")
        print(f"   Total Comics: {total_comics}")
        print(f"   Marvel Comics: {marvel_comics}")
        print(f"   ComicVine Comics: {comicvine_comics}")
        print(f"\n✨ Your comic recommendation system now has access to a much larger catalog!")
    else:
        print("\n⚠️  No new comics were added. Check your ComicVine API key and internet connection.")


if __name__ == "__main__":
    main()