import os
import requests
import time
import hashlib
from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from ..models import Comic
from ..core.database import SessionLocal
from ..core.config import settings


class ComicVineService:
    def __init__(self):
        self.api_key = settings.comic_vine_api_key
        self.base_url = 'https://comicvine.gamespot.com/api'
        self.headers = {
            'User-Agent': 'Comic Recommender App'
        }
        
    def _make_request(self, endpoint: str, params: Dict = None) -> Optional[Dict]:
        """Make a request to ComicVine API with rate limiting"""
        if not self.api_key:
            raise ValueError("ComicVine API key not found in environment variables")
            
        default_params = {
            'api_key': self.api_key,
            'format': 'json'
        }
        
        if params:
            default_params.update(params)
            
        url = f"{self.base_url}/{endpoint}"
        
        try:
            # ComicVine has rate limiting, so we add a small delay
            time.sleep(1)
            response = requests.get(url, params=default_params, headers=self.headers)
            response.raise_for_status()
            
            data = response.json()
            if data.get('status_code') == 1:  # ComicVine success code
                return data
            else:
                print(f"ComicVine API error: {data.get('error', 'Unknown error')}")
                return None
                
        except requests.exceptions.RequestException as e:
            print(f"Request error: {e}")
            return None
    
    def get_trending_issues(self, limit: int = 100) -> List[Dict]:
        """Get trending comic issues from ComicVine"""
        issues = []
        offset = 0
        per_page = 100  # ComicVine's max per page
        
        while len(issues) < limit:
            remaining = min(per_page, limit - len(issues))
            
            params = {
                'field_list': 'id,name,issue_number,volume,description,cover_date,image,site_detail_url',
                'sort': 'date_added:desc',  # Sort by recently added (trending)
                'limit': remaining,
                'offset': offset
            }
            
            response = self._make_request('issues', params)
            if not response or not response.get('results'):
                break
                
            batch_issues = response['results']
            if not batch_issues:
                break
                
            issues.extend(batch_issues)
            offset += len(batch_issues)
            
            # If we got fewer results than requested, we've reached the end
            if len(batch_issues) < remaining:
                break
                
        return issues[:limit]
    
    def get_popular_volumes(self, limit: int = 50) -> List[Dict]:
        """Get popular comic volumes/series"""
        params = {
            'field_list': 'id,name,description,publisher,start_year,image,site_detail_url,count_of_issues',
            'sort': 'count_of_issues:desc',  # Sort by issue count (popularity indicator)
            'limit': limit
        }
        
        response = self._make_request('volumes', params)
        return response.get('results', []) if response else []
    
    def convert_to_comic_format(self, issue_data: Dict) -> Dict:
        """Convert ComicVine issue data to our Comic model format"""
        volume = issue_data.get('volume', {})
        volume_name = volume.get('name', 'Unknown Series') if volume else 'Unknown Series'
        issue_number = issue_data.get('issue_number', '1')
        issue_name = issue_data.get('name') or f"Issue #{issue_number}"
        
        # Create a title combining volume and issue
        if issue_name and issue_name != f"Issue #{issue_number}":
            title = f"{volume_name}: {issue_name}"
        else:
            title = f"{volume_name} #{issue_number}"
            
        # Extract description
        description = issue_data.get('description', '')
        if description:
            # Remove HTML tags if present
            import re
            description = re.sub(r'<[^>]+>', '', description)
            description = description.strip()
        else:
            description = f"Issue #{issue_number} of {volume_name}"
            
        # Get image URL
        image_data = issue_data.get('image', {})
        image_url = None
        if image_data:
            # ComicVine provides multiple image sizes, let's use medium
            image_url = (image_data.get('medium_url') or 
                        image_data.get('small_url') or 
                        image_data.get('thumb_url'))
        
        # Generate characters list (ComicVine doesn't always provide this in issues)
        characters = []
        
        # Set genre based on volume info or default
        genre = "Action"  # Default genre
        
        return {
            'title': title,
            'description': description,
            'image_url': image_url,
            'characters': characters,
            'genre': genre,
            'external_id': f"cv_{issue_data['id']}",  # ComicVine ID with prefix
            'source': 'comicvine'
        }
    
    def add_trending_comics_to_db(self, db: Session, limit: int = 100) -> int:
        """Fetch trending comics and add them to the database"""
        print(f"Fetching {limit} trending comics from ComicVine...")
        
        # Get trending issues
        trending_issues = self.get_trending_issues(limit)
        
        added_count = 0
        for issue_data in trending_issues:
            try:
                comic_data = self.convert_to_comic_format(issue_data)
                external_id = comic_data['external_id']
                
                # Check if comic already exists
                existing_comic = db.query(Comic).filter(Comic.external_id == external_id).first()
                if existing_comic:
                    continue
                    
                # Create new comic
                new_comic = Comic(
                    title=comic_data['title'],
                    description=comic_data['description'],
                    image_url=comic_data['image_url'],
                    characters=comic_data['characters'],
                    genre=comic_data['genre'],
                    external_id=external_id
                )
                
                db.add(new_comic)
                added_count += 1
                
                if added_count % 10 == 0:
                    print(f"Added {added_count} comics so far...")
                    
            except Exception as e:
                print(f"Error processing comic {issue_data.get('id', 'unknown')}: {e}")
                continue
        
        try:
            db.commit()
            print(f"Successfully added {added_count} new comics from ComicVine!")
            return added_count
        except Exception as e:
            print(f"Error committing to database: {e}")
            db.rollback()
            return 0


def fetch_comicvine_comics(limit: int = 100):
    """Standalone function to fetch ComicVine comics"""
    db = SessionLocal()
    try:
        service = ComicVineService()
        return service.add_trending_comics_to_db(db, limit)
    finally:
        db.close()


if __name__ == "__main__":
    # For testing
    added = fetch_comicvine_comics(20)
    print(f"Added {added} comics from ComicVine")