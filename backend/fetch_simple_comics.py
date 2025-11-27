#!/usr/bin/env python3
"""
Simplified script to fetch popular Marvel and DC comics
This version uses a simpler, more direct approach
"""
import os
import sys
import time
from pathlib import Path
from datetime import datetime, timedelta

# Add the backend directory to Python path
backend_dir = Path(__file__).parent
sys.path.append(str(backend_dir))

from app.core.database import SessionLocal
from app.models import Comic
from app.services.comicvine import ComicVineService


class SimpleMarvelDCFetcher(ComicVineService):
    def __init__(self):
        super().__init__()
        
    def get_popular_comics(self, limit: int = 100) -> list:
        """Get popular Marvel and DC comics using a simple approach"""
        print(f"🔍 Fetching {limit} popular Marvel and DC comics...")
        
        all_comics = []
        
        # Strategy 1: Get top Marvel volumes and their recent issues
        print("🕷️ Getting Marvel comics...")
        marvel_comics = self._get_publisher_top_issues('Marvel', limit // 2)
        all_comics.extend(marvel_comics)
        
        # Strategy 2: Get top DC volumes and their recent issues  
        print("🦇 Getting DC comics...")
        dc_comics = self._get_publisher_top_issues('DC Comics', limit // 2)
        all_comics.extend(dc_comics)
        
        # Remove duplicates
        seen_ids = set()
        unique_comics = []
        for comic in all_comics:
            if comic['id'] not in seen_ids:
                seen_ids.add(comic['id'])
                unique_comics.append(comic)
                
        return unique_comics[:limit]
        
    def _get_publisher_top_issues(self, publisher_name: str, limit: int) -> list:
        """Get recent issues from top volumes of a publisher"""
        try:
            # First get top volumes from this publisher
            print(f"   Finding top {publisher_name} volumes...")
            volume_params = {
                'field_list': 'id,name,publisher,start_year,count_of_issues',
                'filter': f'publisher.name:{publisher_name}',
                'sort': 'count_of_issues:desc',
                'limit': 20  # Top 20 series by issue count
            }
            
            volume_response = self._make_request('volumes', volume_params)
            if not volume_response or not volume_response.get('results'):
                return []
                
            volumes = volume_response['results']
            print(f"   Found {len(volumes)} {publisher_name} volumes")
            
            all_issues = []
            issues_per_volume = max(1, limit // len(volumes))
            
            for volume in volumes:
                if len(all_issues) >= limit:
                    break
                    
                volume_id = volume['id']
                volume_name = volume.get('name', 'Unknown')
                
                print(f"   Getting issues from: {volume_name}")
                
                # Get recent issues from this volume
                issue_params = {
                    'field_list': 'id,name,issue_number,volume,description,cover_date,image,site_detail_url',
                    'filter': f'volume:{volume_id}',
                    'sort': 'cover_date:desc',
                    'limit': issues_per_volume
                }
                
                issue_response = self._make_request('issues', issue_params)
                if issue_response and issue_response.get('results'):
                    issues = issue_response['results']
                    
                    # Add publisher info to issues
                    for issue in issues:
                        if issue.get('volume'):
                            issue['volume']['publisher'] = volume.get('publisher', {})
                    
                    # Filter for quality
                    for issue in issues:
                        if self.is_good_comic(issue) and len(all_issues) < limit:
                            all_issues.append(issue)
                
                time.sleep(0.2)  # Rate limiting
                
            return all_issues
            
        except Exception as e:
            print(f"   ❌ Error getting {publisher_name} comics: {e}")
            return []
            
    def is_good_comic(self, issue_data: dict) -> bool:
        """Simple quality check"""
        # Must have image
        if not issue_data.get('image'):
            return False
            
        # Must have volume name
        volume = issue_data.get('volume', {})
        if not volume or not volume.get('name'):
            return False
            
        return True
        
    def convert_to_comic_format(self, issue_data: dict) -> dict:
        """Convert issue data to our comic format"""
        volume = issue_data.get('volume', {})
        volume_name = volume.get('name', 'Unknown Series') if volume else 'Unknown Series'
        issue_number = issue_data.get('issue_number', '1')
        issue_name = issue_data.get('name') or f"Issue #{issue_number}"
        
        # Create title
        if issue_name and issue_name.lower() != f"issue #{issue_number}".lower():
            title = f"{volume_name} #{issue_number}: {issue_name}"
        else:
            title = f"{volume_name} #{issue_number}"
            
        # Clean description
        description = issue_data.get('description', '')
        if description:
            import re
            description = re.sub(r'<[^>]+>', '', description)
            description = re.sub(r'\s+', ' ', description).strip()
        else:
            description = f"Issue #{issue_number} of {volume_name}"
            
        # Get image
        image_data = issue_data.get('image', {})
        image_url = None
        if image_data:
            image_url = (image_data.get('medium_url') or 
                        image_data.get('small_url') or 
                        image_data.get('thumb_url'))
        
        # Determine publisher for genre
        publisher = volume.get('publisher', {})
        publisher_name = publisher.get('name', '') if publisher else ''
        
        if 'Marvel' in publisher_name:
            genre = 'Superhero'
        elif 'DC' in publisher_name:
            genre = 'Superhero'
        else:
            genre = 'Action'
        
        return {
            'title': title[:200],  # Limit title length
            'description': description[:500],  # Limit description length
            'image_url': image_url,
            'characters': [],
            'genre': genre,
            'external_id': f"cv_{issue_data['id']}",
            'source': 'comicvine'
        }


def fetch_simple_marvel_dc_comics():
    """Main function to fetch popular Marvel and DC comics"""
    print("🚀 Fetching POPULAR MARVEL & DC COMICS")
    print("=" * 45)
    
    fetcher = SimpleMarvelDCFetcher()
    db = SessionLocal()
    
    try:
        # Clear previous ComicVine comics
        print("🧹 Clearing previous ComicVine comics...")
        prev_cv_comics = db.query(Comic).filter(Comic.external_id.like('cv_%')).all()
        for comic in prev_cv_comics:
            db.delete(comic)
        db.commit()
        print(f"   Removed {len(prev_cv_comics)} previous ComicVine comics")
        
        # Get popular comics
        popular_comics = fetcher.get_popular_comics(100)
        
        print(f"\n📚 Processing {len(popular_comics)} comics...")
        
        added_count = 0
        for issue_data in popular_comics:
            try:
                comic_data = fetcher.convert_to_comic_format(issue_data)
                external_id = comic_data['external_id']
                
                # Check if already exists
                existing = db.query(Comic).filter(Comic.external_id == external_id).first()
                if existing:
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
                    print(f"   ✅ Added {added_count} comics...")
                    
            except Exception as e:
                print(f"   ❌ Error processing comic: {e}")
                continue
        
        db.commit()
        
        # Show results
        total_comics = db.query(Comic).count()
        marvel_comics = db.query(Comic).filter(Comic.external_id.like('marvel_%')).count()
        cv_comics = db.query(Comic).filter(Comic.external_id.like('cv_%')).count()
        
        print(f"\n🎉 SUCCESS! Added {added_count} popular comics!")
        print(f"\n📊 Updated Database Summary:")
        print(f"   Total Comics: {total_comics}")
        print(f"   Marvel Comics: {marvel_comics}")
        print(f"   ComicVine Comics: {cv_comics}")
        
        # Show sample of new comics
        print(f"\n🦸 Sample of new popular comics:")
        new_comics = db.query(Comic).filter(Comic.external_id.like('cv_%')).limit(15).all()
        for i, comic in enumerate(new_comics, 1):
            print(f"   {i}. {comic.title}")
            
        print(f"\n✨ Database now has popular Marvel & DC comics!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    fetch_simple_marvel_dc_comics()