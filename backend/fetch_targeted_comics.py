#!/usr/bin/env python3
"""
Script to fetch comics from the user's specific popular series list
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


class TargetedComicsFetcher(ComicVineService):
    def __init__(self, series_file_path: str):
        super().__init__()
        self.series_list = self.load_series_from_file(series_file_path)
        
    def load_series_from_file(self, file_path: str) -> list:
        """Load series list from CSV file"""
        series_list = []
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    series_list.append({
                        'title': row['Title'].strip(),
                        'publisher': row['Publisher'].strip(),
                        'type': row['Series Type'].strip()
                    })
            print(f"📋 Loaded {len(series_list)} series from file")
            return series_list
        except Exception as e:
            print(f"❌ Error loading series file: {e}")
            return []
    
    def fetch_targeted_comics(self, issues_per_series: int = 3) -> list:
        """Fetch comics from the targeted series list"""
        print(f"🎯 Fetching comics from {len(self.series_list)} targeted series...")
        
        all_comics = []
        
        for i, series in enumerate(self.series_list, 1):
            series_title = series['title']
            publisher = series['publisher']
            series_type = series['type']
            
            print(f"\n{i}. 📖 Searching for: {series_title} ({publisher})")
            
            # Get issues from this specific series
            series_comics = self.get_series_issues(series_title, publisher, issues_per_series)
            
            if series_comics:
                print(f"   ✅ Found {len(series_comics)} issues")
                all_comics.extend(series_comics)
            else:
                print(f"   ❌ No issues found")
            
            # Rate limiting
            time.sleep(0.3)
            
        return all_comics
    
    def get_series_issues(self, series_name: str, publisher_name: str, limit: int) -> list:
        """Get recent issues from a specific series"""
        try:
            # Search for volumes matching the series name and publisher
            volume_params = {
                'field_list': 'id,name,publisher,start_year,count_of_issues,description',
                'filter': f'publisher.name:{publisher_name}',
                'limit': 30  # Get more volumes to search through
            }
            
            volume_response = self._make_request('volumes', volume_params)
            if not volume_response or not volume_response.get('results'):
                return []
            
            # Find the best matching volume
            best_volume = None
            best_match_score = 0
            
            for volume in volume_response['results']:
                vol_name = volume.get('name', '').lower()
                series_lower = series_name.lower()
                
                # Calculate match score
                if series_lower in vol_name:
                    # Exact substring match gets high score
                    score = 100
                    # Bonus for exact match
                    if vol_name == series_lower:
                        score = 200
                    # Bonus for starting with series name
                    elif vol_name.startswith(series_lower):
                        score = 150
                    
                    # Prefer newer series
                    start_year = volume.get('start_year', 0)
                    try:
                        year = int(start_year) if start_year else 0
                        if year >= 2020:  # Very recent
                            score += 50
                        elif year >= 2010:  # Modern
                            score += 20
                    except:
                        pass
                    
                    if score > best_match_score:
                        best_match_score = score
                        best_volume = volume
            
            if not best_volume:
                return []
            
            volume_id = best_volume['id']
            volume_name = best_volume.get('name', 'Unknown')
            start_year = best_volume.get('start_year', 'Unknown')
            issue_count = best_volume.get('count_of_issues', 0)
            
            print(f"      📚 Found volume: {volume_name} ({start_year}) - {issue_count} issues")
            
            # Get recent issues from this volume
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
            
            # Add publisher info to issues
            for issue in issues:
                if issue.get('volume'):
                    issue['volume']['publisher'] = best_volume.get('publisher', {})
            
            # Filter for quality
            quality_issues = []
            for issue in issues:
                if self.is_good_comic(issue):
                    quality_issues.append(issue)
            
            return quality_issues
            
        except Exception as e:
            print(f"      ❌ Error: {e}")
            return []
    
    def is_good_comic(self, issue_data: dict) -> bool:
        """Quality check for comics"""
        # Must have image
        if not issue_data.get('image'):
            return False
        
        # Must have volume info
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
            'source': 'comicvine_targeted'
        }


def fetch_from_targeted_series():
    """Main function to fetch comics from targeted series"""
    print("🎯 FETCHING COMICS FROM TARGETED POPULAR SERIES")
    print("=" * 55)
    
    # Path to the series file
    series_file = Path(__file__).parent.parent / "trending_comics_csv.txt"
    
    if not series_file.exists():
        print(f"❌ Series file not found: {series_file}")
        return
    
    fetcher = TargetedComicsFetcher(str(series_file))
    
    if not fetcher.series_list:
        print("❌ No series loaded from file")
        return
    
    db = SessionLocal()
    
    try:
        # Get targeted comics (3 issues per series)
        targeted_comics = fetcher.fetch_targeted_comics(issues_per_series=3)
        
        print(f"\n📚 Processing {len(targeted_comics)} targeted comics...")
        
        added_count = 0
        for issue_data in targeted_comics:
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
        
        print(f"\n🎉 SUCCESS! Added {added_count} targeted comics!")
        print(f"\n📊 Updated Database Summary:")
        print(f"   Total Comics: {total_comics}")
        print(f"   ComicVine Comics: {cv_comics}")
        
        # Show sample of new comics
        print(f"\n🦸 Sample of NEW targeted comics:")
        new_comics = db.query(Comic).filter(Comic.external_id.like('cv_%')).order_by(Comic.id.desc()).limit(10).all()
        for i, comic in enumerate(new_comics, 1):
            print(f"   {i}. {comic.title}")
        
        print(f"\n✨ Database now includes comics from your targeted series!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    fetch_from_targeted_series()