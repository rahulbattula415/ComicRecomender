#!/usr/bin/env python3
"""
Service to fetch real Marvel comic runs from the Marvel API
"""

import requests
import hashlib
import time
from typing import List, Dict, Optional
from ..core.config import settings

class MarvelComicsService:
    """Service to fetch real Marvel comic runs and series"""
    
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
    
    def fetch_popular_marvel_comics(self, limit: int = 20) -> List[Dict]:
        """
        Fetch popular Marvel comics from different series
        """
        try:
            auth_params = self._generate_marvel_auth_params()
            if not auth_params:
                print("❌ Marvel API authentication failed")
                return []
            
            # Get popular Marvel series/comics
            popular_series = [
                "Amazing Spider-Man",
                "Avengers", 
                "Iron Man",
                "Captain America",
                "Thor",
                "X-Men",
                "Fantastic Four",
                "Daredevil",
                "Hulk",
                "Ms. Marvel",
                "Guardians of the Galaxy",
                "Black Panther",
                "Doctor Strange",
                "Wolverine",
                "Deadpool"
            ]
            
            all_comics = []
            
            for series in popular_series[:10]:  # Limit to avoid API rate limits
                print(f"🔍 Fetching {series} comics...")
                
                search_params = {
                    'titleStartsWith': series,
                    'format': 'comic',
                    'orderBy': '-onsaleDate',  # Most recent first
                    'limit': 3,  # Get a few from each series
                    'noVariants': True,  # Exclude variant covers
                    **auth_params
                }
                
                response = self.session.get(
                    f"{self.marvel_base_url}/comics",
                    params=search_params,
                    timeout=15
                )
                
                if response.status_code == 200:
                    data = response.json()
                    comics = data.get('data', {}).get('results', [])
                    
                    for comic in comics:
                        # Process each comic
                        processed_comic = self._process_marvel_comic(comic)
                        if processed_comic:
                            all_comics.append(processed_comic)
                            
                    print(f"✅ Found {len(comics)} {series} comics")
                else:
                    print(f"❌ Error fetching {series}: {response.status_code}")
                
                # Small delay to respect API rate limits
                time.sleep(0.5)
            
            print(f"🎉 Total Marvel comics fetched: {len(all_comics)}")
            return all_comics[:limit]  # Return only the requested number
            
        except Exception as e:
            print(f"❌ Error fetching Marvel comics: {e}")
            return []
    
    def _process_marvel_comic(self, comic_data: Dict) -> Optional[Dict]:
        """
        Process raw Marvel API comic data into our format
        """
        try:
            # Extract basic info
            title = comic_data.get('title', 'Unknown Title')
            description = comic_data.get('description') or f"A Marvel comic featuring exciting adventures and iconic characters."
            
            # Get thumbnail image
            thumbnail = comic_data.get('thumbnail', {})
            image_url = None
            if thumbnail and thumbnail.get('path') != 'http://i.annihil.us/u/prod/marvel/i/mg/b/40/image_not_available':
                image_url = f"{thumbnail['path']}/portrait_xlarge.{thumbnail['extension']}"
            
            # Extract characters
            characters = []
            character_items = comic_data.get('characters', {}).get('items', [])
            for char in character_items[:5]:  # Limit to 5 main characters
                characters.append(char.get('name', ''))
            
            # Extract creators
            creators = []
            creator_items = comic_data.get('creators', {}).get('items', [])
            for creator in creator_items[:3]:  # Limit to 3 main creators
                role = creator.get('role', '')
                name = creator.get('name', '')
                if role and name:
                    creators.append(f"{name} ({role})")
            
            # Get issue number and series info
            issue_number = comic_data.get('issueNumber', 0)
            series = comic_data.get('series', {}).get('name', '')
            
            # Create description with more details
            enhanced_description = description
            if creators:
                enhanced_description += f" Created by: {', '.join(creators)}."
            if issue_number and issue_number > 0:
                enhanced_description += f" Issue #{int(issue_number)}."
            
            return {
                'title': title,
                'description': enhanced_description,
                'characters': characters,
                'genre': 'Superhero',  # All Marvel comics are superhero genre
                'image_url': image_url,
                'marvel_id': comic_data.get('id'),
                'series': series,
                'issue_number': issue_number,
                'creators': creators
            }
            
        except Exception as e:
            print(f"❌ Error processing comic data: {e}")
            return None

# Create singleton instance
marvel_comics_service = MarvelComicsService()