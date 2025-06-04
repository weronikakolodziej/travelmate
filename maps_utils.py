import os
import googlemaps
from datetime import datetime
import re
from typing import List, Dict, Optional, Any
import time

def initialize_gmaps_client() -> googlemaps.Client:
    """Initialize the Google Maps client"""
    api_key = os.getenv('GOOGLE_MAPS_API_KEY')
    if not api_key:
        raise ValueError("GOOGLE_MAPS_API_KEY environment variable not set")
    return googlemaps.Client(key=api_key)

def search_places_directly(gmaps: googlemaps.Client, city: str, interests: List[str], limit: int = 5) -> List[Dict[str, Any]]:
    """
    Search for places directly on Google Maps based on interests.
    
    Args:
        gmaps: Google Maps client
        city: City/region to search in
        interests: List of user interests
        limit: Maximum number of places per interest
    
    Returns:
        List of verified places
    """
    verified_places = []
    
    for interest in interests:
        try:
            # Search for places
            search_query = f"{interest} in {city}"
            places_result = gmaps.places(search_query)
            
            # Process results
            for place in places_result['results'][:limit]:
                # Get detailed information
                place_id = place['place_id']
                details = gmaps.place(place_id, fields=[
                    'name', 'formatted_address', 'website', 'rating',
                    'formatted_phone_number', 'opening_hours', 'types', 'url'
                ])['result']
                
                # Only include places with good ratings
                if 'rating' in details and details['rating'] >= 4.0:
                    verified_places.append({
                        'name': details.get('name', ''),
                        'address': details.get('formatted_address', ''),
                        'maps_url': details.get('url', ''),
                        'website': details.get('website', None),
                        'rating': details.get('rating', 0.0),
                        'phone': details.get('formatted_phone_number', None),
                        'is_open': details.get('opening_hours', {}).get('open_now', None),
                        'place_type': details.get('types', [])[0] if details.get('types') else None
                    })
        
        except Exception as e:
            print(f"Error searching for {interest} in {city}: {str(e)}")
            continue
    
    return verified_places

def extract_place_names(text):
    """Extract potential place names from text using some common patterns"""
    # Pattern for places in quotes or after common prepositions
    patterns = [
        r'"([^"]+)"',  # Text in quotes
        r'at\s+([A-Z][^,.!?]*)',  # Places after "at"
        r'to\s+([A-Z][^,.!?]*)',  # Places after "to"
        r'in\s+([A-Z][^,.!?]*)',  # Places after "in"
        r'visit\s+([A-Z][^,.!?]*)',  # Places after "visit"
        r'called\s+([A-Z][^,.!?]*)',  # Places after "called"
        r'([A-Z][a-zA-Z\s\']+(?:Café|Cafe|Restaurant|Bar|Hotel|Museum|Park|Temple|Shrine|Market|Mall|Garden|Tower|Castle|Palace))'  # Places with specific suffixes
    ]
    
    places = []
    for pattern in patterns:
        matches = re.finditer(pattern, text)
        for match in matches:
            place = match.group(1).strip()
            if len(place) > 3 and not any(p in place for p in ['I', 'The', 'A ', 'An ']):  # Basic filtering
                places.append(place)
    
    return list(set(places))  # Remove duplicates

def verify_and_get_place_details(gmaps: googlemaps.Client, place_name: str, city: str) -> Optional[Dict[str, Any]]:
    """
    Verify if a place exists and get its details from Google Maps.
    
    Args:
        gmaps: Google Maps client
        place_name: Name of the place to verify
        city: City/region for context
    
    Returns:
        Dict with place details if found and verified, None otherwise
    """
    try:
        # Search for the place
        search_query = f"{place_name}, {city}"
        places_result = gmaps.places(search_query)
        
        if not places_result['results']:
            return None
        
        # Get the first result
        place = places_result['results'][0]
        
        # Get detailed information
        place_id = place['place_id']
        details = gmaps.place(place_id, fields=[
            'name', 'formatted_address', 'website', 'rating',
            'formatted_phone_number', 'opening_hours', 'types', 'url'
        ])['result']
        
        # Check if it's a valid place (has minimum rating of 4.0)
        if 'rating' not in details or details['rating'] < 4.0:
            return None
        
        # Format the response
        return {
            'name': details.get('name', place_name),
            'address': details.get('formatted_address', ''),
            'maps_url': details.get('url', ''),
            'website': details.get('website', None),
            'rating': details.get('rating', 0.0),
            'phone': details.get('formatted_phone_number', None),
            'is_open': details.get('opening_hours', {}).get('open_now', None),
            'place_type': details.get('types', [])[0] if details.get('types') else None
        }
    
    except Exception as e:
        print(f"Error verifying place {place_name}: {str(e)}")
        return None

def format_place_details(place_details):
    """Format place details into a nice string"""
    if not place_details:
        return None
        
    status = "🟢 Open now" if place_details['is_open'] == True else "🔴 Closed now" if place_details['is_open'] == False else "ℹ️ Hours not available"
    
    formatted = f"**{place_details['name']}**\n"
    formatted += f"📍 {place_details['address']}\n"
    if place_details['rating'] != 'No rating':
        formatted += f"⭐ {place_details['rating']}/5\n"
    formatted += f"⏰ {status}\n"
    if place_details['phone']:
        formatted += f"📞 {place_details['phone']}\n"
    formatted += f"🗺️ [View on Google Maps]({place_details['maps_url']})\n"
    if place_details['website']:
        formatted += f"🌐 [Official Website]({place_details['website']})\n"
    if 'place_type' in place_details:
        formatted += f"🏷️ Type: {place_details['place_type'].replace('_', ' ').title()}\n"
    
    return formatted 