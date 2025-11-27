import requests
import hashlib
import time
from typing import Optional, Dict, List
from ..core.config import settings

class ComicImageService:
    """Service to fetch comic book cover images from Marvel API"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Comic-Recommender-App/1.0'
        })
        self.marvel_public_key = settings.marvel_public_api_key
        self.marvel_private_key = settings.marvel_private_api_key
        self.marvel_base_url = settings.marvel_api_base_url
    
    def _generate_marvel_auth_params(self) -> Dict[str, str]:
        """Generate authentication parameters for Marvel API"""
        if not self.marvel_public_key or not self.marvel_private_key:
            return {}
        
        timestamp = str(int(time.time()))
        public_key = self.marvel_public_key
        private_key = self.marvel_private_key
        
        # Create hash: md5(timestamp + private_key + public_key)
        hash_input = f"{timestamp}{private_key}{public_key}"
        auth_hash = hashlib.md5(hash_input.encode()).hexdigest()
        
        return {
            'ts': timestamp,
            'apikey': public_key,
            'hash': auth_hash
        }
    
    def get_marvel_comic_image(self, title: str, characters: list = None) -> Optional[str]:
        """
        Fetch comic image from Marvel API or use enhanced fallback
        """
        try:
            if not self.marvel_public_key or not self.marvel_private_key:
                print(f"No Marvel API keys provided for {title}, using enhanced fallback")
                return self._get_enhanced_comic_image(title, characters)
            
            # Try Marvel API first
            auth_params = self._generate_marvel_auth_params()
            if not auth_params:
                print(f"Marvel API auth failed for {title}, using enhanced fallback")
                return self._get_enhanced_comic_image(title, characters)
            
            # Search for comics by title
            search_params = {
                'titleStartsWith': title,
                'limit': 10,
                'format': 'comic',
                'orderBy': 'title',
                **auth_params
            }
            
            print(f"🔍 Searching Marvel API for: {title}")
            response = self.session.get(
                f"{self.marvel_base_url}/comics",
                params=search_params,
                timeout=15
            )
            
            if response.status_code == 200:
                data = response.json()
                comics = data.get('data', {}).get('results', [])
                
                print(f"📊 Found {len(comics)} Marvel comics for '{title}'")
                
                for comic in comics:
                    thumbnail = comic.get('thumbnail')
                    if thumbnail and thumbnail.get('path') != 'http://i.annihil.us/u/prod/marvel/i/mg/b/40/image_not_available':
                        # Get high-quality image
                        image_url = f"{thumbnail['path']}/portrait_xlarge.{thumbnail['extension']}"
                        print(f"✅ Found Marvel API image for {title}: {comic.get('title', 'Unknown')}")
                        return image_url
                
                print(f"❌ No valid thumbnails found in Marvel results for {title}")
            else:
                print(f"❌ Marvel API error {response.status_code} for {title}: {response.text[:200]}")
            
            print(f"🔄 Using enhanced fallback for {title}")
            return self._get_enhanced_comic_image(title, characters)
            
        except Exception as e:
            print(f"❌ Error fetching Marvel image for {title}: {e}")
            return self._get_enhanced_comic_image(title, characters)
    
    def get_marvel_character_comics(self, character_name: str) -> List[Dict]:
        """
        Get comics featuring a specific character from Marvel API
        """
        try:
            if not self.marvel_api_key:
                return []
            
            # First, search for the character
            auth_params = self._generate_marvel_auth_params()
            char_params = {
                'name': character_name,
                'limit': 1,
                **auth_params
            }
            
            response = self.session.get(
                f"{self.marvel_base_url}/characters",
                params=char_params,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                characters = data.get('data', {}).get('results', [])
                
                if characters:
                    character_id = characters[0]['id']
                    
                    # Get comics for this character
                    comics_params = {
                        'characters': character_id,
                        'limit': 10,
                        'format': 'comic',
                        **auth_params
                    }
                    
                    comics_response = self.session.get(
                        f"{self.marvel_base_url}/comics",
                        params=comics_params,
                        timeout=10
                    )
                    
                    if comics_response.status_code == 200:
                        comics_data = comics_response.json()
                        return comics_data.get('data', {}).get('results', [])
            
            return []
            
        except Exception as e:
            print(f"Error fetching character comics for {character_name}: {e}")
            return []
    
    def _get_enhanced_comic_image(self, title: str, characters: list = None) -> Optional[str]:
        """
        Enhanced Marvel comic book cover image matching
        """
        
        # Marvel-focused comic image map with high-quality sources
        marvel_comic_map = {
            # Spider-Man Comics
            'amazing spider-man': 'https://images.unsplash.com/photo-1608889476561-6242cfdbf622?w=400&h=600&fit=crop&auto=format',
            'spider-man': 'https://images.unsplash.com/photo-1608889476561-6242cfdbf622?w=400&h=600&fit=crop&auto=format',
            'peter parker': 'https://images.unsplash.com/photo-1608889476561-6242cfdbf622?w=400&h=600&fit=crop&auto=format',
            
            # Avengers & Team Comics
            'avengers': 'https://images.unsplash.com/photo-1635805737707-575885ab0820?w=400&h=600&fit=crop&auto=format',
            'the avengers': 'https://images.unsplash.com/photo-1635805737707-575885ab0820?w=400&h=600&fit=crop&auto=format',
            
            # Iron Man
            'iron man': 'https://images.unsplash.com/photo-1635805737707-575885ab0820?w=400&h=600&fit=crop&auto=format',
            'tony stark': 'https://images.unsplash.com/photo-1635805737707-575885ab0820?w=400&h=600&fit=crop&auto=format',
            
            # Captain America
            'captain america': 'https://images.unsplash.com/photo-1635805737707-575885ab0820?w=400&h=600&fit=crop&auto=format',
            'steve rogers': 'https://images.unsplash.com/photo-1635805737707-575885ab0820?w=400&h=600&fit=crop&auto=format',
            
            # Thor
            'thor': 'https://images.unsplash.com/photo-1635805737707-575885ab0820?w=400&h=600&fit=crop&auto=format',
            'asgard': 'https://images.unsplash.com/photo-1635805737707-575885ab0820?w=400&h=600&fit=crop&auto=format',
            
            # X-Men Universe
            'x-men': 'https://images.unsplash.com/photo-1608889825103-eb5ed706fc64?w=400&h=600&fit=crop&auto=format',
            'wolverine': 'https://images.unsplash.com/photo-1608889825103-eb5ed706fc64?w=400&h=600&fit=crop&auto=format',
            'days of future past': 'https://images.unsplash.com/photo-1608889825103-eb5ed706fc64?w=400&h=600&fit=crop&auto=format',
            'professor x': 'https://images.unsplash.com/photo-1608889825103-eb5ed706fc64?w=400&h=600&fit=crop&auto=format',
            'magneto': 'https://images.unsplash.com/photo-1608889825103-eb5ed706fc64?w=400&h=600&fit=crop&auto=format',
            
            # Fantastic Four
            'fantastic four': 'https://images.unsplash.com/photo-1635805737707-575885ab0820?w=400&h=600&fit=crop&auto=format',
            'mr. fantastic': 'https://images.unsplash.com/photo-1635805737707-575885ab0820?w=400&h=600&fit=crop&auto=format',
            'human torch': 'https://images.unsplash.com/photo-1635805737707-575885ab0820?w=400&h=600&fit=crop&auto=format',
            
            # Street Level Heroes
            'daredevil': 'https://images.unsplash.com/photo-1612198188060-c7c2a3b66eae?w=400&h=600&fit=crop&auto=format',
            'matt murdock': 'https://images.unsplash.com/photo-1612198188060-c7c2a3b66eae?w=400&h=600&fit=crop&auto=format',
            'hell\'s kitchen': 'https://images.unsplash.com/photo-1612198188060-c7c2a3b66eae?w=400&h=600&fit=crop&auto=format',
            
            # Hulk
            'hulk': 'https://images.unsplash.com/photo-1635805737707-575885ab0820?w=400&h=600&fit=crop&auto=format',
            'incredible hulk': 'https://images.unsplash.com/photo-1635805737707-575885ab0820?w=400&h=600&fit=crop&auto=format',
            'bruce banner': 'https://images.unsplash.com/photo-1635805737707-575885ab0820?w=400&h=600&fit=crop&auto=format',
            
            # Ms. Marvel
            'ms. marvel': 'https://images.unsplash.com/photo-1635805737707-575885ab0820?w=400&h=600&fit=crop&auto=format',
            'kamala khan': 'https://images.unsplash.com/photo-1635805737707-575885ab0820?w=400&h=600&fit=crop&auto=format',
            
            # Guardians of the Galaxy
            'guardians of the galaxy': 'https://images.unsplash.com/photo-1518709268805-4e9042af2176?w=400&h=600&fit=crop&auto=format',
            'star-lord': 'https://images.unsplash.com/photo-1518709268805-4e9042af2176?w=400&h=600&fit=crop&auto=format',
            'gamora': 'https://images.unsplash.com/photo-1518709268805-4e9042af2176?w=400&h=600&fit=crop&auto=format',
            'groot': 'https://images.unsplash.com/photo-1518709268805-4e9042af2176?w=400&h=600&fit=crop&auto=format',
        }
        
        # Normalize title for matching
        title_lower = title.lower().strip()
        
        # Try exact match first
        if title_lower in marvel_comic_map:
            print(f"Exact Marvel match found for: {title}")
            return marvel_comic_map[title_lower]
        
        # Try partial matches with scoring
        best_match = None
        best_score = 0
        
        for keyword, image_url in marvel_comic_map.items():
            # Calculate match score
            score = 0
            if keyword in title_lower:
                score = len(keyword) / len(title_lower)  # Longer matches get higher scores
            
            if score > best_score:
                best_score = score
                best_match = image_url
        
        if best_match and best_score > 0.2:  # Lower threshold for Marvel comics
            print(f"Partial Marvel match found for: {title} (score: {best_score:.2f})")
            return best_match
        
        # Check character matches
        if characters:
            for character in characters:
                character_lower = character.lower().strip()
                if character_lower in marvel_comic_map:
                    print(f"Marvel character match found: {character}")
                    return marvel_comic_map[character_lower]
                
                # Partial character matching
                for keyword, image_url in marvel_comic_map.items():
                    if keyword in character_lower or character_lower in keyword:
                        print(f"Partial Marvel character match: {character}")
                        return image_url
        
        # Default Marvel superhero image
        print(f"Using default Marvel superhero image for: {title}")
        return 'https://images.unsplash.com/photo-1635805737707-575885ab0820?w=400&h=600&fit=crop&auto=format'
    
    def _get_demo_comic_image(self, title: str, characters: list = None) -> Optional[str]:
        """Legacy method - redirects to enhanced version"""
        return self._get_enhanced_comic_image(title, characters)
    
    def get_comic_image_by_genre(self, genre: str) -> str:
        """Get a comic image based on genre"""
        genre_images = {
            'superhero': 'https://images.unsplash.com/photo-1635805737707-575885ab0820?w=400&h=600&fit=crop',
            'horror': 'https://images.unsplash.com/photo-1578662996442-48f60103fc96?w=400&h=600&fit=crop',
            'sci-fi': 'https://images.unsplash.com/photo-1518709268805-4e9042af2176?w=400&h=600&fit=crop',
            'fantasy': 'https://images.unsplash.com/photo-1518709268805-4e9042af2176?w=400&h=600&fit=crop',
            'action': 'https://images.unsplash.com/photo-1608889476561-6242cfdbf622?w=400&h=600&fit=crop',
            'adventure': 'https://images.unsplash.com/photo-1608889825103-eb5ed706fc64?w=400&h=600&fit=crop',
            'drama': 'https://images.unsplash.com/photo-1612198188060-c7c2a3b66eae?w=400&h=600&fit=crop',
        }
        
        return genre_images.get(genre.lower(), 'https://images.unsplash.com/photo-1612198188060-c7c2a3b66eae?w=400&h=600&fit=crop')
    
    def update_comic_image(self, comic_title: str, characters: list = None, genre: str = None) -> str:
        """
        Update a comic's image with a better match - now tries Marvel API first
        """
        # Try Marvel API first
        image_url = self.get_marvel_comic_image(comic_title, characters)
        
        # Fallback to genre-based image
        if not image_url and genre:
            image_url = self.get_comic_image_by_genre(genre)
        
        # Final fallback
        if not image_url:
            image_url = 'https://images.unsplash.com/photo-1612198188060-c7c2a3b66eae?w=400&h=600&fit=crop'
        
        return image_url

# Create a singleton instance
comic_image_service = ComicImageService()