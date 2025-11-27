#!/usr/bin/env python3
"""
Enhanced script to fetch comics from targeted series with flexible matching
"""
import os
import sys
import csv
import time
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent
sys.path.append(str(backend_dir))

from app.core.database import SessionLocal
from app.models import Comic
from app.services.comicvine import ComicVineService


class FlexibleComicsFetcher(ComicVineService):
    def __init__(self, series_file_path: str):
        super().__init__()
        self.series_list = self.load_series_from_file(series_file_path)
        
        # Fallback popular series that are more likely to exist
        self.fallback_series = [
            {'title': 'Batman', 'publisher': 'DC', 'type': 'Ongoing'},
            {'title': 'Superman', 'publisher': 'DC', 'type': 'Ongoing'},
            {'title': 'Wonder Woman', 'publisher': 'DC', 'type': 'Ongoing'},
            {'title': 'Justice League', 'publisher': 'DC', 'type': 'Ongoing'},
            {'title': 'The Flash', 'publisher': 'DC', 'type': 'Ongoing'},
            {'title': 'Green Lantern', 'publisher': 'DC', 'type': 'Ongoing'},
            {'title': 'Aquaman', 'publisher': 'DC', 'type': 'Ongoing'},
            {'title': 'Teen Titans', 'publisher': 'DC', 'type': 'Ongoing'},
            {'title': 'Nightwing', 'publisher': 'DC', 'type': 'Ongoing'},
            {'title': 'Spider-Man', 'publisher': 'Marvel', 'type': 'Ongoing'},
            {'title': 'X-Men', 'publisher': 'Marvel', 'type': 'Ongoing'},
            {'title': 'Avengers', 'publisher': 'Marvel', 'type': 'Ongoing'},
            {'title': 'Captain America', 'publisher': 'Marvel', 'type': 'Ongoing'},
            {'title': 'Iron Man', 'publisher': 'Marvel', 'type': 'Ongoing'},
            {'title': 'Thor', 'publisher': 'Marvel', 'type': 'Ongoing'},
            {'title': 'Hulk', 'publisher': 'Marvel', 'type': 'Ongoing'},
            {'title': 'Fantastic Four', 'publisher': 'Marvel', 'type': 'Ongoing'},
            {'title': 'Wolverine', 'publisher': 'Marvel', 'type': 'Ongoing'},
            {'title': 'Deadpool', 'publisher': 'Marvel', 'type': 'Ongoing'}
        ]
        
    def load_series_from_file(self, file_path: str) -> list:
        """Load series list from CSV file"""
        series_list = []
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    # Normalize publisher names
                    publisher = row['Publisher'].strip()
                    if 'Marvel' in publisher:
                        publisher = 'Marvel'
                    elif 'DC' in publisher:
                        publisher = 'DC'
                    
                    series_list.append({
                        'title': row['Title'].strip(),
                        'publisher': publisher,
                        'type': row['Series Type'].strip()
                    })
            print(f"📋 Loaded {len(series_list)} series from file")
            return series_list
        except Exception as e:
            print(f"❌ Error loading series file: {e}")
            return []
    
    def fetch_flexible_comics(self, issues_per_series: int = 2) -> list:
        """Fetch comics with flexible matching"""
        print(f"🎯 Fetching comics with flexible matching...")
        
        all_comics = []
        found_series = []
        
        # First, try the user's targeted series
        print(f"\n📋 Trying user's targeted series ({len(self.series_list)} series)...")
        for series in self.series_list:
            series_comics = self.search_series_flexible(series['title'], series['publisher'], issues_per_series)
            if series_comics:
                all_comics.extend(series_comics)
                found_series.append(series['title'])
                print(f"   ✅ {series['title']}: Found {len(series_comics)} issues")
            time.sleep(0.2)
        
        # If we didn't find enough, try fallback series
        if len(all_comics) < 20:
            print(f"\n🔄 Found only {len(all_comics)} comics, trying fallback popular series...")
            for series in self.fallback_series:
                if len(all_comics) >= 50:  # Reasonable limit
                    break
                if series['title'] not in found_series:  # Avoid duplicates
                    series_comics = self.search_series_flexible(series['title'], series['publisher'], issues_per_series)
                    if series_comics:
                        all_comics.extend(series_comics)
                        found_series.append(series['title'])
                        print(f"   ✅ {series['title']}: Found {len(series_comics)} issues")
                    time.sleep(0.2)
        
        print(f"\n🎯 Total found: {len(all_comics)} comics from {len(found_series)} series")
        return all_comics
    
    def search_series_flexible(self, series_name: str, publisher_name: str, limit: int) -> list:
        """Flexible search for series"""
        try:
            # Try multiple search strategies
            
            # Strategy 1: Exact publisher match
            comics = self.search_with_publisher(series_name, publisher_name, limit)
            if comics:
                return comics
            
            # Strategy 2: Broader search without strict publisher matching
            comics = self.search_broad(series_name, limit)
            if comics:
                return comics
            
            return []
            
        except Exception as e:
            print(f"      ❌ Error searching {series_name}: {e}")
            return []
    
    def search_with_publisher(self, series_name: str, publisher_name: str, limit: int) -> list:
        """Search with specific publisher"""
        # Normalize publisher names for search
        if publisher_name == 'Marvel':
            publisher_search = 'Marvel'
        elif publisher_name == 'DC':
            publisher_search = 'DC Comics'
        else:
            publisher_search = publisher_name
        
        volume_params = {
            'field_list': 'id,name,publisher,start_year,count_of_issues',
            'filter': f'publisher.name:{publisher_search}',
            'limit': 30
        }
        
        volume_response = self._make_request('volumes', volume_params)
        if not volume_response or not volume_response.get('results'):
            return []
        
        # Find matching volumes
        matching_volumes = []
        for volume in volume_response['results']:
            vol_name = volume.get('name', '').lower()
            series_lower = series_name.lower()
            
            # Check for matches
            if (series_lower in vol_name or 
                any(word in vol_name for word in series_lower.split()) or
                vol_name.startswith(series_lower.split()[0])):  # First word match
                matching_volumes.append(volume)
        
        if not matching_volumes:
            return []
        
        # Get the best volume (most recent with most issues)
        best_volume = max(matching_volumes, key=lambda v: (
            int(v.get('start_year', 0)) if v.get('start_year', '').isdigit() else 0,
            v.get('count_of_issues', 0)
        ))
        
        return self.get_issues_from_volume(best_volume, limit)
    
    def search_broad(self, series_name: str, limit: int) -> list:
        """Broader search without publisher restriction"""
        # Search for volumes with series name
        volume_params = {
            'field_list': 'id,name,publisher,start_year,count_of_issues',
            'filter': f'name:{series_name.split()[0]}',  # Use first word
            'limit': 20
        }
        
        volume_response = self._make_request('volumes', volume_params)
        if not volume_response or not volume_response.get('results'):
            return []
        
        # Find best match
        best_volume = None
        best_score = 0
        
        for volume in volume_response['results']:
            vol_name = volume.get('name', '').lower()
            series_lower = series_name.lower()
            
            score = 0
            if series_lower in vol_name:
                score = 100
            elif vol_name.startswith(series_lower.split()[0]):
                score = 50
            
            # Prefer Marvel/DC
            publisher = volume.get('publisher', {})
            publisher_name = publisher.get('name', '') if publisher else ''
            if any(pub in publisher_name for pub in ['Marvel', 'DC']):
                score += 25
            
            if score > best_score:
                best_score = score
                best_volume = volume
        
        if best_volume and best_score > 40:  # Minimum threshold
            return self.get_issues_from_volume(best_volume, limit)
        
        return []
    
    def get_issues_from_volume(self, volume: dict, limit: int) -> list:
        """Get recent issues from a volume"""
        volume_id = volume['id']
        volume_name = volume.get('name', 'Unknown')
        publisher = volume.get('publisher', {})
        publisher_name = publisher.get('name', 'Unknown') if publisher else 'Unknown'
        
        # Get recent issues
        issue_params = {
            'field_list': 'id,name,issue_number,volume,description,cover_date,image,site_detail_url',
            'filter': f'volume:{volume_id}',
            'sort': 'cover_date:desc',
            'limit': limit
        }
        
        issue_response = self._make_request('issues', issue_params)
        if not issue_response or not issue_response.get('results'):
            return []
        
        issues = issue_response['results']
        
        # Add publisher info and filter
        quality_issues = []
        for issue in issues:
            if issue.get('volume'):
                issue['volume']['publisher'] = volume.get('publisher', {})
            
            if self.is_good_comic(issue):
                quality_issues.append(issue)
        
        return quality_issues
    
    def is_good_comic(self, issue_data: dict) -> bool:
        """Quality check for comics"""
        if not issue_data.get('image'):
            return False
        volume = issue_data.get('volume', {})
        if not volume or not volume.get('name'):
            return False
        return True
    
    def convert_to_comic_format(self, issue_data: dict) -> dict:
        """Convert issue data to our comic format"""
        volume = issue_data.get('volume', {})
        volume_name = volume.get('name', 'Unknown Series')
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
        
        # Determine genre
        publisher = volume.get('publisher', {})
        publisher_name = publisher.get('name', '') if publisher else ''
        
        if any(pub in publisher_name for pub in ['Marvel', 'DC']):
            genre = 'Superhero'
        else:
            genre = 'Action'
        
        return {
            'title': title[:200],
            'description': description[:500],
            'image_url': image_url,
            'characters': [],
            'genre': genre,
            'external_id': f"cv_{issue_data['id']}",
            'source': 'comicvine_flexible'
        }


def fetch_flexible_targeted_comics():
    """Main function"""
    print("🎯 FETCHING COMICS WITH FLEXIBLE MATCHING")
    print("=" * 50)
    
    series_file = Path(__file__).parent.parent / "trending_comics_csv.txt"
    
    if not series_file.exists():
        print(f"❌ Series file not found: {series_file}")
        return
    
    fetcher = FlexibleComicsFetcher(str(series_file))
    db = SessionLocal()
    
    try:
        # Clear previous targeted comics
        print("🧹 Clearing previous targeted comics...")
        prev_targeted = db.query(Comic).filter(Comic.external_id.like('cv_%')).all()
        for comic in prev_targeted:
            db.delete(comic)
        db.commit()
        print(f"   Removed {len(prev_targeted)} previous comics")
        
        # Get comics with flexible matching
        comics = fetcher.fetch_flexible_comics(issues_per_series=3)
        
        print(f"\n📚 Processing {len(comics)} comics...")
        
        added_count = 0
        for issue_data in comics:
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
                
                if added_count % 5 == 0:
                    print(f"   ✅ Added {added_count} comics...")
                
            except Exception as e:
                print(f"   ❌ Error processing comic: {e}")
                continue
        
        db.commit()
        
        # Show results
        total_comics = db.query(Comic).count()
        cv_comics = db.query(Comic).filter(Comic.external_id.like('cv_%')).count()
        
        print(f"\n🎉 SUCCESS! Added {added_count} popular comics!")
        print(f"\n📊 Database Summary:")
        print(f"   Total Comics: {total_comics}")
        print(f"   ComicVine Comics: {cv_comics}")
        
        # Show sample
        print(f"\n🦸 Sample of NEW popular comics:")
        new_comics = db.query(Comic).filter(Comic.external_id.like('cv_%')).order_by(Comic.id.desc()).limit(15).all()
        for i, comic in enumerate(new_comics, 1):
            print(f"   {i}. {comic.title}")
        
        print(f"\n✨ Database now has popular Marvel & DC comics!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    fetch_flexible_targeted_comics()