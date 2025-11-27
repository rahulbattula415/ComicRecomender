#!/usr/bin/env python3
"""
Script to reset database with Marvel-only comics for MVP
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from app.core.database import SessionLocal
from app.models import Comic

def reset_database_with_marvel_comics():
    """Clear existing comics and reseed with Marvel-only collection"""
    print("🔄 Resetting database with Marvel Comics only...")
    
    db = SessionLocal()
    try:
        # Delete all existing comics
        existing_count = db.query(Comic).count()
        print(f"📊 Found {existing_count} existing comics")
        
        if existing_count > 0:
            db.query(Comic).delete()
            db.commit()
            print(f"🗑️  Deleted {existing_count} existing comics")
        
        # Now run the seed script
        print("🌱 Reseeding with Marvel Comics...")
        from seed_data import seed_database
        seed_database()
        
        print("✅ Database reset complete! Marvel Comics MVP is ready!")
        
    except Exception as e:
        print(f"❌ Error resetting database: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    reset_database_with_marvel_comics()