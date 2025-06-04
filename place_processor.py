from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
from maps_utils import initialize_gmaps_client, verify_and_get_place_details, search_places_directly
import re
from tqdm import tqdm

@dataclass
class RedditPost:
    """Structure for storing Reddit post data"""
    title: str
    content: str
    date: datetime
    comments: List[str]
    score: int

@dataclass
class Place:
    """Structure for storing verified place information"""
    name: str
    address: str
    maps_url: str
    website: Optional[str]
    rating: float
    phone: Optional[str]
    is_open: Optional[bool]
    place_type: Optional[str]
    reddit_mentions: List[str]  # Store context from Reddit mentions
    source: str  # 'reddit', 'maps', or 'both'

class PlaceProcessor:
    """Handles the extraction and verification of places from Reddit data"""
    
    def __init__(self):
        self.gmaps = initialize_gmaps_client()
        # Patterns for place name extraction
        self.place_patterns = [
            r'"([^"]+)"',  # Text in quotes
            r'(?:at|in|visit|called|to)\s+([A-Z][^,.!?]*)',  # Places after specific words
            r'([A-Z][a-zA-Z\s\']+(?:Café|Cafe|Restaurant|Bar|Hotel|Museum|Park|Temple|Shrine|Market|Mall|Garden|Tower|Castle|Palace))',  # Places with specific suffixes
            r'(?:the|The)\s+([A-Z][^,.!?]*(?:Café|Cafe|Restaurant|Bar|Hotel|Museum|Park|Temple|Shrine|Market|Mall|Garden|Tower|Castle|Palace))'  # Places with "the" prefix
        ]
    
    def extract_places_from_text(self, text: str) -> List[str]:
        """Extract potential place names from text"""
        places = []
        for pattern in self.place_patterns:
            matches = re.finditer(pattern, text)
            for match in matches:
                place = match.group(1).strip()
                if len(place) > 3 and not any(p in place for p in ['I', 'A ', 'An ']):
                    places.append(place)
        return list(set(places))
    
    def process_reddit_data(self, posts: List[RedditPost], city: str) -> Tuple[List[Place], List[str]]:
        """
        Process Reddit posts to extract and verify places.
        Returns verified places and their Reddit context.
        """
        print("\n🔍 Extracting and verifying places from Reddit discussions...")
        potential_places = {}  # Dict to store place names and their mentions
        
        # Extract places from posts and comments
        for post in tqdm(posts, desc="Processing Reddit posts"):
            # Extract from title and content
            text = f"{post.title}\n{post.content}"
            places = self.extract_places_from_text(text)
            
            # Store context for each place
            for place in places:
                if place not in potential_places:
                    potential_places[place] = []
                potential_places[place].append(f"Mentioned in post: {post.title}")
            
            # Extract from comments
            for comment in post.comments:
                places = self.extract_places_from_text(comment)
                for place in places:
                    if place not in potential_places:
                        potential_places[place] = []
                    potential_places[place].append(f"From comment: {comment[:100]}...")
        
        # Verify places with Google Maps
        verified_places = []
        print(f"\n🗺️ Verifying {len(potential_places)} potential places with Google Maps...")
        for place_name, mentions in tqdm(potential_places.items(), desc="Verifying places"):
            details = verify_and_get_place_details(self.gmaps, place_name, city)
            if details:
                place = Place(
                    name=details['name'],
                    address=details['address'],
                    maps_url=details['maps_url'],
                    website=details['website'],
                    rating=details['rating'],
                    phone=details['phone'],
                    is_open=details['is_open'],
                    place_type=details.get('place_type'),
                    reddit_mentions=mentions,
                    source='reddit'
                )
                verified_places.append(place)
        
        return verified_places, list(potential_places.keys())
    
    def supplement_with_maps_data(self, verified_places: List[Place], city: str, interests: List[str]) -> List[Place]:
        """
        Supplement Reddit-verified places with additional places from Google Maps
        if fewer than 10 verified places were found.
        """
        if len(verified_places) >= 10:
            return verified_places
        
        print(f"\n🔍 Found only {len(verified_places)} verified places from Reddit. Searching Google Maps...")
        
        # Get additional places from Google Maps
        maps_places = search_places_directly(self.gmaps, city, interests)
        
        # Convert to Place objects and mark as from Maps
        existing_names = {place.name for place in verified_places}
        for place_data in maps_places:
            if place_data['name'] not in existing_names:
                place = Place(
                    name=place_data['name'],
                    address=place_data['address'],
                    maps_url=place_data['maps_url'],
                    website=place_data['website'],
                    rating=place_data['rating'],
                    phone=place_data['phone'],
                    is_open=place_data['is_open'],
                    place_type=place_data['place_type'],
                    reddit_mentions=[],
                    source='maps'
                )
                verified_places.append(place)
        
        # Sort by rating and limit to top 10
        verified_places.sort(key=lambda x: float(x.rating) if isinstance(x.rating, (int, float)) else 0, reverse=True)
        return verified_places[:10]
    
    def format_places_data(self, places: List[Place], city: str) -> str:
        """Format verified places data for the LLM prompt"""
        formatted_text = f"Verified Places in {city}:\n\n"
        
        # Group places by source
        reddit_places = [p for p in places if p.source in ['reddit', 'both']]
        maps_places = [p for p in places if p.source == 'maps']
        
        # Format Reddit-mentioned places first
        if reddit_places:
            formatted_text += "Places Mentioned in Reddit Discussions:\n"
            for place in reddit_places:
                formatted_text += self._format_place(place)
            formatted_text += "\n---\n\n"
        
        # Format places found through Maps
        if maps_places:
            formatted_text += "Additional Highly-Rated Places from Google Maps:\n"
            for place in maps_places:
                formatted_text += self._format_place(place)
        
        return formatted_text
    
    def _format_place(self, place: Place) -> str:
        """Helper method to format a single place"""
        formatted = f"📍 {place.name}"
        if place.place_type:
            formatted += f" ({place.place_type.replace('_', ' ').title()})"
        formatted += "\n"
        
        if isinstance(place.rating, (int, float)):
            formatted += f"⭐ Rating: {place.rating}/5\n"
        
        status = "🟢 Open now" if place.is_open == True else "🔴 Closed now" if place.is_open == False else "ℹ️ Hours not available"
        formatted += f"⏰ {status}\n"
        
        formatted += f"📌 Address: {place.address}\n"
        formatted += f"🗺️ [View on Google Maps]({place.maps_url})\n"
        
        if place.phone:
            formatted += f"📞 {place.phone}\n"
        if place.website:
            formatted += f"🌐 [Official Website]({place.website})\n"
        
        if place.reddit_mentions:
            formatted += "\n💬 Reddit Context:\n"
            for mention in place.reddit_mentions[:2]:  # Limit to 2 mentions
                formatted += f"- {mention}\n"
        
        formatted += "\n"
        return formatted 