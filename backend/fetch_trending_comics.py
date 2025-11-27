#!/usr/bin/env python3
"""
Script to fetch popular Marvel and DC comics from ComicVine API
This version focuses exclusively on popular, mainstream Marvel and DC titles
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


class PopularMarvelDCFetcher(ComicVineService):
    def __init__(self):
        super().__init__()
        
        # Popular Marvel series to target
        self.popular_marvel_series = [
            'Spider-Man', 'Amazing Spider-Man', 'Spectacular Spider-Man',
            'X-Men', 'Uncanny X-Men', 'X-Force', 'Wolverine',
            'Avengers', 'New Avengers', 'Mighty Avengers',
            'Captain America', 'Iron Man', 'Thor', 'Hulk',
            'Fantastic Four', 'Deadpool', 'Daredevil',
            'Doctor Strange', 'Black Widow', 'Captain Marvel',
            'Guardians of the Galaxy', 'Black Panther'
        ]
        
        # Popular DC series to target
        self.popular_dc_series = [
            'Batman', 'Detective Comics', 'Batman and Robin',
            'Superman', 'Action Comics', 'Superman: Man of Steel',
            'Wonder Woman', 'Justice League', 'Justice League of America',
            'The Flash', 'Green Lantern', 'Green Arrow',
            'Aquaman', 'Teen Titans', 'Titans',
            'Nightwing', 'Robin', 'Batgirl', 'Catwoman',
            'Harley Quinn', 'Suicide Squad', 'Birds of Prey',
            'Shazam', 'Green Lantern Corps'
        ]
        
    def get_popular_marvel_dc_comics(self, limit: int = 100) -> list:
        """Get popular Marvel and DC comics using targeted series search"""
        print(f"🔍 Fetching top {limit} popular Marvel and DC comics...")
        
        all_comics = []
        
        # Get Marvel comics (50% of total)
        print("�️ Fetching popular Marvel comics...")
        marvel_comics = self._get_publisher_comics('Marvel', limit // 2)
        all_comics.extend(marvel_comics)
        
        # Get DC comics (50% of total)
        print("🦇 Fetching popular DC comics...")
        dc_comics = self._get_publisher_comics('DC Comics', limit // 2)
        all_comics.extend(dc_comics)
        
        # If we don't have enough comics, get some recent popular ones
        if len(all_comics) < limit // 2:
            print("📈 Getting additional recent popular comics...")
            additional_comics = self._get_recent_popular_comics(limit - len(all_comics))
            all_comics.extend(additional_comics)
        
        # Remove duplicates and sort by quality
        unique_comics = self._deduplicate_and_sort(all_comics)
        
        return unique_comics[:limit]
        
    def _get_publisher_comics(self, publisher_name: str, limit: int) -> list:
        """Get comics from specific publisher focusing on popular series"""
        comics = []
        
        # Get series list based on publisher
        if publisher_name == 'Marvel':
            target_series = self.popular_marvel_series
        else:  # DC Comics
            target_series = self.popular_dc_series
            
        # Get recent issues from each popular series
        issues_per_series = max(1, limit // len(target_series))
        
        for series_name in target_series:
            if len(comics) >= limit:
                break
                
            print(f"   📖 Searching for: {series_name}")
            series_comics = self._get_series_recent_issues(series_name, publisher_name, issues_per_series)
            comics.extend(series_comics)
            
            # Rate limiting
            time.sleep(0.3)
            
        return comics
        
    def _get_series_recent_issues(self, series_name: str, publisher_name: str, limit: int) -> list:
        """Get recent issues from a specific series"""
        try:
            # First find the volume/series - use broader search but filter by publisher
            volume_params = {
                'field_list': 'id,name,publisher,start_year,count_of_issues,description',
                'filter': f'publisher.name:{publisher_name}',
                'limit': 50  # Get more volumes to search through
            }
            
            volume_response = self._make_request('volumes', volume_params)
            if not volume_response or not volume_response.get('results'):
                return []
                
            # Find volumes that match our series name
            matching_volumes = []
            for volume in volume_response['results']:
                vol_name = volume.get('name', '').lower()
                if series_name.lower() in vol_name:
                    matching_volumes.append(volume)
            
            if not matching_volumes:
                return []
                
            # Find the best matching volume (most issues, most recent)
            best_volume = None
            best_score = 0
            
            for volume in matching_volumes:
                # Score based on issue count and recency
                issue_count = volume.get('count_of_issues', 0)
                start_year_str = volume.get('start_year', '0')
                
                # Convert start_year to integer safely
                try:
                    start_year = int(start_year_str) if start_year_str else 0
                except (ValueError, TypeError):
                    start_year = 0
                
                # Only consider modern comics (1980 and later)
                if start_year < 1980:
                    continue
                
                # Prefer recent series with many issues
                score = issue_count + (start_year - 1990) * 3  # Higher boost for recent series
                if score > best_score:
                    best_score = score
                    best_volume = volume
                    
            if not best_volume:
                return []
                
            print(f"      Found: {best_volume.get('name')} ({best_volume.get('start_year')}) - {best_volume.get('count_of_issues')} issues")
                
            # Get recent issues from this volume
            issue_params = {
                'field_list': 'id,name,issue_number,volume,description,cover_date,image,site_detail_url',
                'filter': f'volume:{best_volume["id"]}',
                'sort': 'cover_date:desc',
                'limit': limit * 3  # Get extra to filter for quality
            }
            
            issue_response = self._make_request('issues', issue_params)
            if not issue_response or not issue_response.get('results'):
                return []
                
            issues = issue_response['results']
            print(f"      Found {len(issues)} issues from this volume")
            
            # Add publisher info to each issue since it's missing from the API response
            for issue in issues:
                if issue.get('volume'):
                    issue['volume']['publisher'] = best_volume.get('publisher', {})
            
            # Filter for quality issues with relaxed criteria
            quality_issues = []
            for issue in issues:
                if self.is_basic_quality_comic(issue) and len(quality_issues) < limit:
                    quality_issues.append(issue)
                    
            print(f"      Added {len(quality_issues)} quality issues")
            return quality_issues
            
        except Exception as e:
            print(f"   ❌ Error fetching {series_name}: {e}")
            return []
            
    def _get_recent_popular_comics(self, limit: int) -> list:
        """Get recent popular comics from both Marvel and DC"""
        try:
            print("   Getting recent issues from Marvel and DC...")
            
            # Get recent issues from both publishers
            params = {
                'field_list': 'id,name,issue_number,volume,description,cover_date,image,site_detail_url',
                'filter': 'cover_date:2015-01-01|2025-01-01',  # Last 10 years
                'sort': 'date_added:desc',
                'limit': limit * 3  # Get extra to filter
            }
            
            response = self._make_request('issues', params)
            if not response or not response.get('results'):
                return []
                
            issues = response['results']
            print(f"   Found {len(issues)} recent issues")
            
            # Filter for Marvel and DC only
            marvel_dc_issues = []
            for issue in issues:
                volume = issue.get('volume', {})
                if volume:
                    # Try to get publisher from volume name (fallback)
                    vol_name = volume.get('name', '').lower()
                    is_marvel = any(word in vol_name for word in ['spider', 'avengers', 'x-men', 'iron', 'captain america', 'thor', 'hulk'])
                    is_dc = any(word in vol_name for word in ['batman', 'superman', 'justice', 'flash', 'wonder woman', 'green lantern'])
                    
                    if (is_marvel or is_dc) and self.is_basic_quality_comic(issue):
                        marvel_dc_issues.append(issue)
                        
                        if len(marvel_dc_issues) >= limit:
                            break
            
            print(f"   Added {len(marvel_dc_issues)} recent Marvel/DC issues")
            return marvel_dc_issues
            
        except Exception as e:
            print(f"   ❌ Error getting recent comics: {e}")
            return []
        
    def _deduplicate_and_sort(self, comics: list) -> list:
        """Remove duplicates and sort by quality indicators"""
        seen_ids = set()
        unique_comics = []
        
        for comic in comics:
            comic_id = comic.get('id')
            if comic_id not in seen_ids:
                seen_ids.add(comic_id)
                unique_comics.append(comic)
                
        # Sort by quality indicators (description length, image availability)
        def quality_score(comic):
            score = 0
            if comic.get('description'):
                score += min(len(comic['description']), 500)  # Up to 500 points for description
            if comic.get('image'):
                score += 100  # 100 points for having an image
            if comic.get('volume', {}).get('name'):
                score += 50   # 50 points for volume name
            return score
            
        unique_comics.sort(key=quality_score, reverse=True)
        return unique_comics
        
    def is_basic_quality_comic(self, issue_data: dict) -> bool:
        """Basic quality check for comics - less restrictive"""
        # Must have image
        if not issue_data.get('image'):
            return False
            
        # Must have volume info
        volume = issue_data.get('volume')
        if not volume or not volume.get('name'):
            return False
            
        return True
        
    def is_quality_comic(self, issue_data: dict) -> bool:
        """Check if a comic meets quality standards for inclusion - STRICT filtering"""
        # Must have description
        description = issue_data.get('description', '')
        if not description or len(description) < 50:
            return False
            
        # Must have image
        if not issue_data.get('image'):
            return False
            
        # Must have volume info
        volume = issue_data.get('volume')
        if not volume or not volume.get('name'):
            return False
            
        # Get publisher info
        publisher = volume.get('publisher', {})
        publisher_name = publisher.get('name', '') if publisher else ''
        
        # ONLY allow Marvel and DC Comics
        if not any(pub in publisher_name for pub in ['Marvel', 'DC Comics']):
            return False
            
        # Filter out adult content or inappropriate titles - STRICT
        title = volume.get('name', '').lower()
        issue_name = issue_data.get('name', '').lower()
        combined_text = f"{title} {issue_name} {description.lower()}"
        
        # Extensive inappropriate content filter
        inappropriate_keywords = [
            # Adult content
            'adult', 'explicit', 'mature', 'xxx', 'hentai', 'nsfw', 'erotic', 'nude',
            # Violence/inappropriate themes
            'gore', 'torture', 'extreme violence', 'disturbing',
            # Other inappropriate
            'parody', 'satire', 'joke', 'spoof', 'comedy', 'humor',
            # Alt/indie versions that might be inappropriate
            'ultimate destruction', 'marvel zombies', 'what if', 'elseworlds'
        ]
        
        if any(keyword in combined_text for keyword in inappropriate_keywords):
            return False
            
        # Only allow mainstream, popular series
        approved_series_keywords = [
            'spider-man', 'batman', 'superman', 'wonder woman', 'flash', 'green lantern',
            'captain america', 'iron man', 'thor', 'hulk', 'avengers', 'justice league',
            'x-men', 'fantastic four', 'teen titans', 'aquaman', 'green arrow',
            'wolverine', 'deadpool', 'daredevil', 'black widow', 'captain marvel',
            'black panther', 'doctor strange', 'guardians of the galaxy',
            'nightwing', 'robin', 'batgirl', 'harley quinn', 'catwoman'
        ]
        
        # Must contain at least one approved series keyword
        if not any(keyword in combined_text for keyword in approved_series_keywords):
            return False
            
        return True
    
    def convert_to_comic_format(self, issue_data: dict) -> dict:
        """Enhanced conversion with better title formatting and genre detection"""
        volume = issue_data.get('volume', {})
        volume_name = volume.get('name', 'Unknown Series') if volume else 'Unknown Series'
        issue_number = issue_data.get('issue_number', '1')
        issue_name = issue_data.get('name') or f"Issue #{issue_number}"
        
        # Create a cleaner title
        if issue_name and issue_name.lower() != f"issue #{issue_number}".lower():
            title = f"{volume_name} #{issue_number}: {issue_name}"
        else:
            title = f"{volume_name} #{issue_number}"
            
        # Clean up title
        title = title.replace('  ', ' ').strip()
        
        # Extract and clean description
        description = issue_data.get('description', '')
        if description:
            import re
            description = re.sub(r'<[^>]+>', '', description)
            description = re.sub(r'\s+', ' ', description).strip()
        else:
            description = f"Issue #{issue_number} of {volume_name}"
            
        # Get best quality image
        image_data = issue_data.get('image', {})
        image_url = None
        if image_data:
            image_url = (image_data.get('medium_url') or 
                        image_data.get('small_url') or 
                        image_data.get('thumb_url'))
        
        # Smart genre detection
        genre = self._detect_genre(volume_name, description)
        
        return {
            'title': title,
            'description': description[:500],  # Limit description length
            'image_url': image_url,
            'characters': [],
            'genre': genre,
            'external_id': f"cv_{issue_data['id']}",
            'source': 'comicvine'
        }
    
    def _detect_genre(self, title: str, description: str) -> str:
        """Detect genre based on title and description - focused on Marvel/DC genres"""
        combined_text = f"{title} {description}".lower()
        
        # Marvel/DC focused genre keywords
        genre_keywords = {
            'Superhero': [
                'spider', 'batman', 'superman', 'hero', 'super', 'avengers', 'justice',
                'captain', 'iron man', 'thor', 'hulk', 'flash', 'wonder woman',
                'wolverine', 'x-men', 'mutant', 'power', 'villain', 'save', 'protect'
            ],
            'Action': [
                'fight', 'battle', 'combat', 'war', 'attack', 'defend', 'enemy',
                'threat', 'danger', 'mission', 'adventure', 'team', 'force'
            ],
            'Drama': [
                'origin', 'story', 'past', 'family', 'relationship', 'life', 'death',
                'secret', 'identity', 'personal', 'emotional', 'human'
            ],
            'Sci-Fi': [
                'space', 'alien', 'future', 'technology', 'cosmic', 'galaxy',
                'universe', 'dimension', 'time', 'science'
            ],
            'Fantasy': [
                'magic', 'mystical', 'ancient', 'gods', 'supernatural', 'spell',
                'realm', 'mythical', 'legend'
            ],
            'Crime': [
                'detective', 'crime', 'criminal', 'investigate', 'mystery',
                'corruption', 'justice', 'law'
            ]
        }
        
        # Check for genre matches
        for genre, keywords in genre_keywords.items():
            if any(keyword in combined_text for keyword in keywords):
                return genre
                
        # Default to Superhero for Marvel/DC content
        return 'Superhero'


def fetch_popular_marvel_dc_comics():
    """Main function to fetch and add popular Marvel and DC comics"""
    print("🚀 Fetching TOP 100 POPULAR MARVEL & DC COMICS")
    print("=" * 55)
    
    fetcher = PopularMarvelDCFetcher()
    db = SessionLocal()
    
    try:
        # Clear previous ComicVine comics to make room for better ones
        print("🧹 Clearing previous ComicVine comics...")
        prev_cv_comics = db.query(Comic).filter(Comic.external_id.like('cv_%')).all()
        for comic in prev_cv_comics:
            db.delete(comic)
        db.commit()
        print(f"   Removed {len(prev_cv_comics)} previous ComicVine comics")
        
        # Get popular Marvel and DC comics
        popular_comics = fetcher.get_popular_marvel_dc_comics(100)
        
        print(f"\n📚 Processing {len(popular_comics)} popular Marvel & DC comics...")
        
        added_count = 0
        for issue_data in popular_comics:
            try:
                # Use basic quality check first, then detailed if needed
                if not fetcher.is_basic_quality_comic(issue_data):
                    continue
                    
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
                    print(f"   ✅ Added {added_count} popular comics...")
                    
            except Exception as e:
                print(f"   ❌ Error processing comic: {e}")
                continue
        
        db.commit()
        
        # Show results
        total_comics = db.query(Comic).count()
        marvel_comics = db.query(Comic).filter(Comic.external_id.like('marvel_%')).count()
        cv_comics = db.query(Comic).filter(Comic.external_id.like('cv_%')).count()
        
        print(f"\n🎉 SUCCESS! Added {added_count} popular Marvel & DC comics!")
        print(f"\n📊 Updated Database Summary:")
        print(f"   Total Comics: {total_comics}")
        print(f"   Marvel Comics: {marvel_comics}")
        print(f"   Popular ComicVine Comics: {cv_comics}")
        
        # Show sample of new comics
        print(f"\n🦸 Sample of NEW popular Marvel & DC comics:")
        new_comics = db.query(Comic).filter(Comic.external_id.like('cv_%')).limit(15).all()
        for i, comic in enumerate(new_comics, 1):
            publisher = "🕷️ MARVEL" if "marvel" in comic.title.lower() else "🦇 DC"
            print(f"   {i}. {publisher}: {comic.title}")
            
        print(f"\n✨ Your recommendation system now features the most popular Marvel & DC comics!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    fetch_popular_marvel_dc_comics()