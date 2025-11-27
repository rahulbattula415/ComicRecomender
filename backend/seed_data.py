import asyncio
from sqlalchemy.orm import Session
from app.core.database import SessionLocal, engine
from app.models import Base, Comic

# Sample comic data with Marvel Comics only for MVP
SAMPLE_COMICS = [
    {
        "title": "Amazing Spider-Man",
        "description": "Peter Parker balances his life as a high school student with his secret identity as the web-slinging superhero Spider-Man.",
        "characters": ["Peter Parker", "Spider-Man", "Mary Jane Watson", "Aunt May", "J. Jonah Jameson"],
        "genre": "Superhero",
        "image_url": "https://images.unsplash.com/photo-1608889476561-6242cfdbf622?w=400&h=600&fit=crop&q=80"
    },
    {
        "title": "The Avengers",
        "description": "Earth's Mightiest Heroes unite to face threats too big for any single superhero to handle alone.",
        "characters": ["Iron Man", "Captain America", "Thor", "Hulk", "Black Widow", "Hawkeye"],
        "genre": "Superhero",
        "image_url": "https://images.unsplash.com/photo-1635805737707-575885ab0820?w=400&h=600&fit=crop&q=80"
    },
    {
        "title": "Iron Man",
        "description": "Billionaire genius Tony Stark uses his advanced armor technology to protect the world as Iron Man.",
        "characters": ["Tony Stark", "Iron Man", "Pepper Potts", "Happy Hogan", "James Rhodes"],
        "genre": "Superhero",
        "image_url": "https://images.unsplash.com/photo-1635805737707-575885ab0820?w=400&h=600&fit=crop&q=80"
    },
    {
        "title": "X-Men",
        "description": "A team of mutant superheroes fight to protect a world that fears and hates them, led by Professor Charles Xavier.",
        "characters": ["Wolverine", "Cyclops", "Storm", "Jean Grey", "Professor X"],
        "genre": "Superhero",
        "image_url": "https://images.unsplash.com/photo-1608889825103-eb5ed706fc64?w=400&h=600&fit=crop&q=80"
    },
    {
        "title": "Captain America",
        "description": "Steve Rogers, a super-soldier from World War II, fights for justice and freedom as Captain America.",
        "characters": ["Steve Rogers", "Captain America", "Bucky Barnes", "Peggy Carter", "Sam Wilson"],
        "genre": "Superhero",
        "image_url": "https://images.unsplash.com/photo-1635805737707-575885ab0820?w=400&h=600&fit=crop&q=80"
    },
    {
        "title": "Thor",
        "description": "The Asgardian God of Thunder protects Earth and the Nine Realms with his mystical hammer Mjolnir.",
        "characters": ["Thor", "Loki", "Odin", "Jane Foster", "Heimdall"],
        "genre": "Superhero",
        "image_url": "https://images.unsplash.com/photo-1635805737707-575885ab0820?w=400&h=600&fit=crop&q=80"
    },
    {
        "title": "X-Men: Days of Future Past",
        "description": "A dystopian future where mutants are hunted by Sentinels, and the X-Men must prevent this dark timeline from occurring.",
        "characters": ["Wolverine", "Professor X", "Magneto", "Storm", "Kitty Pryde"],
        "genre": "Superhero",
        "image_url": "https://images.unsplash.com/photo-1608889825103-eb5ed706fc64?w=400&h=600&fit=crop&q=80"
    },
    {
        "title": "The Fantastic Four",
        "description": "Marvel's First Family uses their cosmic powers to explore the unknown and protect Earth from fantastic threats.",
        "characters": ["Mr. Fantastic", "Invisible Woman", "Human Torch", "The Thing", "Doctor Doom"],
        "genre": "Superhero",
        "image_url": "https://images.unsplash.com/photo-1635805737707-575885ab0820?w=400&h=600&fit=crop&q=80"
    },
    {
        "title": "Daredevil",
        "description": "Blind lawyer Matt Murdock fights crime in Hell's Kitchen as the Man Without Fear, using his enhanced senses.",
        "characters": ["Matt Murdock", "Daredevil", "Foggy Nelson", "Karen Page", "The Kingpin"],
        "genre": "Superhero",
        "image_url": "https://images.unsplash.com/photo-1612198188060-c7c2a3b66eae?w=400&h=600&fit=crop&q=80"
    },
    {
        "title": "The Incredible Hulk",
        "description": "Dr. Bruce Banner struggles to control the monster within him while using the Hulk's power to help others.",
        "characters": ["Bruce Banner", "Hulk", "Betty Ross", "General Ross", "Rick Jones"],
        "genre": "Superhero",
        "image_url": "https://images.unsplash.com/photo-1635805737707-575885ab0820?w=400&h=600&fit=crop&q=80"
    },
    {
        "title": "Ms. Marvel",
        "description": "Kamala Khan, a Pakistani-American teenager from Jersey City, discovers she has superpowers and becomes the new Ms. Marvel.",
        "characters": ["Kamala Khan", "Ms. Marvel", "Carol Danvers", "Bruno Carrelli", "Nakia Bahadir"],
        "genre": "Superhero",
        "image_url": "https://images.unsplash.com/photo-1635805737707-575885ab0820?w=400&h=600&fit=crop&q=80"
    },
    {
        "title": "Guardians of the Galaxy",
        "description": "A group of unlikely heroes team up to protect the galaxy from cosmic threats while dealing with their own personal issues.",
        "characters": ["Star-Lord", "Gamora", "Drax", "Rocket Raccoon", "Groot"],
        "genre": "Superhero",
        "image_url": "https://images.unsplash.com/photo-1518709268805-4e9042af2176?w=400&h=600&fit=crop&q=80"
    }
]


def seed_database():
    """Seed the database with sample comic data"""
    # Create tables
    Base.metadata.create_all(bind=engine)
    
    # Create database session
    db = SessionLocal()
    
    try:
        # Check if comics already exist
        existing_comics = db.query(Comic).count()
        if existing_comics > 0:
            print(f"Database already contains {existing_comics} comics. Skipping seed.")
            return
        
        # Add sample comics
        for comic_data in SAMPLE_COMICS:
            comic = Comic(**comic_data)
            db.add(comic)
        
        db.commit()
        print(f"Successfully seeded database with {len(SAMPLE_COMICS)} comics!")
        
    except Exception as e:
        print(f"Error seeding database: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()