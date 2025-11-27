#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(__file__))

from app.core.database import SessionLocal, engine
from app.models import Base, User
from app.core.security import get_password_hash

def test_registration():
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    
    print("Testing password hashing...")
    test_password = "testpass123"
    try:
        hashed = get_password_hash(test_password)
        print(f"✅ Password hashing successful: {hashed[:20]}...")
    except Exception as e:
        print(f"❌ Password hashing failed: {e}")
        return
    
    print("Testing user creation...")
    db = SessionLocal()
    try:
        # Check if user exists
        existing_user = db.query(User).filter(User.email == "test@example.com").first()
        if existing_user:
            print("User already exists, deleting...")
            db.delete(existing_user)
            db.commit()
        
        # Create new user
        new_user = User(email="test@example.com", password_hash=hashed)
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        print(f"✅ User created successfully with ID: {new_user.id}")
        
    except Exception as e:
        print(f"❌ User creation failed: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    test_registration()