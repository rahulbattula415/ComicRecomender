#!/usr/bin/env python3
"""
Test script to verify Marvel API connection
"""

import sys
import os
import requests
import hashlib
import time

sys.path.append(os.path.dirname(__file__))

from app.core.config import settings

def test_marvel_api():
    """Test Marvel API connection with the provided keys"""
    
    print("🔍 Testing Marvel API connection...")
    print(f"Public Key: {settings.marvel_public_api_key[:20]}...")
    print(f"Private Key: {settings.marvel_private_api_key[:20]}...")
    
    if not settings.marvel_public_api_key or not settings.marvel_private_api_key:
        print("❌ Missing Marvel API keys in settings")
        return
    
    try:
        # Marvel API authentication with both keys
        timestamp = str(int(time.time()))
        public_key = settings.marvel_public_api_key
        private_key = settings.marvel_private_api_key
        
        # Create hash: md5(timestamp + private_key + public_key)
        hash_input = f"{timestamp}{private_key}{public_key}"
        auth_hash = hashlib.md5(hash_input.encode()).hexdigest()
        
        # Test with a simple query
        params = {
            'ts': timestamp,
            'apikey': public_key,
            'hash': auth_hash,
            'limit': 1
        }
        
        print("🌐 Making API request...")
        response = requests.get(
            f"{settings.marvel_api_base_url}/characters",
            params=params,
            timeout=10
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text[:500]}...")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Marvel API connection successful!")
            print(f"Attribution: {data.get('attributionText', 'No attribution')}")
            
            # Test comic search
            print("\n🔍 Testing comic search...")
            comic_params = {
                'ts': timestamp,
                'apikey': public_key,
                'hash': auth_hash,
                'titleStartsWith': 'Spider-Man',
                'limit': 3
            }
            
            comic_response = requests.get(
                f"{settings.marvel_api_base_url}/comics",
                params=comic_params,
                timeout=10
            )
            
            if comic_response.status_code == 200:
                comic_data = comic_response.json()
                comics = comic_data.get('data', {}).get('results', [])
                print(f"✅ Found {len(comics)} Spider-Man comics!")
                for comic in comics[:3]:
                    print(f"  - {comic.get('title', 'Unknown title')}")
            else:
                print(f"❌ Comic search failed: {comic_response.status_code}")
                
        else:
            print(f"❌ API Error: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error testing Marvel API: {e}")

def test_alternative_approach():
    """Test a simplified approach without authentication"""
    
    print("\n🔄 Testing alternative approach...")
    
    try:
        # Try without authentication (some endpoints might be public)
        response = requests.get(
            f"{settings.marvel_api_base_url}/characters",
            params={'limit': 1},
            timeout=10
        )
        
        print(f"No-auth Status Code: {response.status_code}")
        print(f"No-auth Response: {response.text[:300]}...")
        
    except Exception as e:
        print(f"❌ Error with no-auth approach: {e}")

if __name__ == "__main__":
    test_marvel_api()
    test_alternative_approach()