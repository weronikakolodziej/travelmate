import os
import googlemaps
from datetime import datetime
import re

def initialize_gmaps_client():
    """Initialize and return the Google Maps client"""
    api_key = os.getenv("GOOGLE_MAPS_API_KEY")
    if not api_key:
        raise ValueError("Google Maps API key not found in environment variables")
    return googlemaps.Client(key=api_key)

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

def verify_and_get_place_details(gmaps_client, place_name, city):
    """
    Verify a place exists on Google Maps and get its details.
    Returns None if the place cannot be verified.
    """
    try:
        # Search for the place in the specified city
        search_query = f"{place_name}, {city}"
        result = gmaps_client.places(
            search_query,
            type=['establishment', 'point_of_interest', 'tourist_attraction'],
            language='en'
        )
        
        if not result['results']:
            return None
        
        place = result['results'][0]
        
        # Get detailed information
        place_details = gmaps_client.place(place['place_id'], fields=[
            'name', 'formatted_address', 'url', 'website', 'rating',
            'formatted_phone_number', 'opening_hours', 'business_status'
        ])['result']
        
        # Check if the place is permanently closed
        if place_details.get('business_status') == 'CLOSED_PERMANENTLY':
            return None
            
        # Create a clean place details dictionary
        return {
            'name': place_details.get('name', ''),
            'address': place_details.get('formatted_address', ''),
            'maps_url': place_details.get('url', ''),
            'website': place_details.get('website', ''),
            'rating': place_details.get('rating', 'No rating'),
            'phone': place_details.get('formatted_phone_number', ''),
            'is_open': place_details.get('opening_hours', {}).get('open_now', None)
        }
        
    except Exception as e:
        print(f"Error verifying place '{place_name}': {str(e)}")
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
    
    return formatted 