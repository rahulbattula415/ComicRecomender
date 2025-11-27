#!/usr/bin/env python3
"""
Debug specific issues from Batman series
"""
import os
import sys
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent
sys.path.append(str(backend_dir))

from app.services.comicvine import ComicVineService

def debug_batman_issues():
    """Debug Batman issues specifically"""
    print("🔍 DEBUG: Testing Batman issues")
    print("=" * 40)
    
    service = ComicVineService()
    
    # Get Batman volume first
    volume_params = {
        'field_list': 'id,name,publisher,start_year,count_of_issues',
        'filter': 'name:Batman,publisher.name:DC Comics',
        'limit': 1
    }
    
    volume_response = service._make_request('volumes', volume_params)
    if not volume_response or not volume_response.get('results'):
        print("No Batman volume found!")
        return
        
    batman_volume = volume_response['results'][0]
    print(f"Found Batman volume: {batman_volume['name']} (ID: {batman_volume['id']})")
    
    # Get recent issues from Batman
    issue_params = {
        'field_list': 'id,name,issue_number,volume,description,cover_date,image,site_detail_url',
        'filter': f'volume:{batman_volume["id"]}',
        'sort': 'cover_date:desc',
        'limit': 5
    }
    
    issue_response = service._make_request('issues', issue_params)
    if not issue_response or not issue_response.get('results'):
        print("No Batman issues found!")
        return
        
    issues = issue_response['results']
    print(f"\nFound {len(issues)} recent Batman issues:")
    
    for i, issue in enumerate(issues, 1):
        print(f"\n{i}. {issue.get('name', 'Unnamed')} #{issue.get('issue_number', '?')}")
        print(f"   Cover Date: {issue.get('cover_date', 'Unknown')}")
        print(f"   Has Image: {bool(issue.get('image'))}")
        print(f"   Has Description: {bool(issue.get('description'))}")
        if issue.get('description'):
            desc = issue['description'][:100] + "..." if len(issue.get('description', '')) > 100 else issue.get('description', '')
            print(f"   Description: {desc}")
        
        # Check volume info
        volume = issue.get('volume', {})
        print(f"   Volume Name: {volume.get('name', 'Unknown')}")
        publisher = volume.get('publisher', {})
        print(f"   Publisher: {publisher.get('name', 'Unknown') if publisher else 'Unknown'}")
        print(f"   Volume ID: {volume.get('id', 'Unknown')}")

if __name__ == "__main__":
    debug_batman_issues()