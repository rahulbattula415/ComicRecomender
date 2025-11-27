#!/usr/bin/env python3
"""
Debug script to test ComicVine API responses
"""
import os
import sys
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent
sys.path.append(str(backend_dir))

from app.services.comicvine import ComicVineService

def debug_comicvine_search():
    """Debug ComicVine API to see what we're getting"""
    print("🔍 DEBUG: Testing ComicVine API responses")
    print("=" * 50)
    
    service = ComicVineService()
    
    # Test 1: Search for Batman volumes
    print("\n1. Testing Batman volume search:")
    volume_params = {
        'field_list': 'id,name,publisher,start_year,count_of_issues,description',
        'filter': 'name:Batman,publisher.name:DC Comics',
        'limit': 3
    }
    
    response = service._make_request('volumes', volume_params)
    if response and response.get('results'):
        print(f"   Found {len(response['results'])} Batman volumes:")
        for vol in response['results'][:3]:
            print(f"   - {vol.get('name')} ({vol.get('start_year')}) - {vol.get('count_of_issues')} issues")
            print(f"     Publisher: {vol.get('publisher', {}).get('name', 'Unknown')}")
    else:
        print("   No Batman volumes found!")
        print(f"   Response: {response}")
    
    # Test 2: Search for Spider-Man volumes
    print("\n2. Testing Spider-Man volume search:")
    volume_params = {
        'field_list': 'id,name,publisher,start_year,count_of_issues,description',
        'filter': 'name:Spider-Man,publisher.name:Marvel',
        'limit': 3
    }
    
    response = service._make_request('volumes', volume_params)
    if response and response.get('results'):
        print(f"   Found {len(response['results'])} Spider-Man volumes:")
        for vol in response['results'][:3]:
            print(f"   - {vol.get('name')} ({vol.get('start_year')}) - {vol.get('count_of_issues')} issues")
            print(f"     Publisher: {vol.get('publisher', {}).get('name', 'Unknown')}")
    else:
        print("   No Spider-Man volumes found!")
        print(f"   Response: {response}")
    
    # Test 3: General DC search
    print("\n3. Testing general DC Comics search:")
    volume_params = {
        'field_list': 'id,name,publisher,start_year,count_of_issues',
        'filter': 'publisher.name:DC Comics',
        'sort': 'count_of_issues:desc',
        'limit': 5
    }
    
    response = service._make_request('volumes', volume_params)
    if response and response.get('results'):
        print(f"   Found {len(response['results'])} DC volumes:")
        for vol in response['results'][:5]:
            print(f"   - {vol.get('name')} ({vol.get('start_year')}) - {vol.get('count_of_issues')} issues")
    else:
        print("   No DC volumes found!")
        print(f"   Response: {response}")
    
    # Test 4: General Marvel search
    print("\n4. Testing general Marvel search:")
    volume_params = {
        'field_list': 'id,name,publisher,start_year,count_of_issues',
        'filter': 'publisher.name:Marvel',
        'sort': 'count_of_issues:desc',
        'limit': 5
    }
    
    response = service._make_request('volumes', volume_params)
    if response and response.get('results'):
        print(f"   Found {len(response['results'])} Marvel volumes:")
        for vol in response['results'][:5]:
            print(f"   - {vol.get('name')} ({vol.get('start_year')}) - {vol.get('count_of_issues')} issues")
    else:
        print("   No Marvel volumes found!")
        print(f"   Response: {response}")

if __name__ == "__main__":
    debug_comicvine_search()