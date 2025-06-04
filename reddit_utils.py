import praw
import os
import re
from datetime import datetime, timedelta
from maps_utils import initialize_gmaps_client, extract_place_names, verify_and_get_place_details, format_place_details
from tqdm import tqdm
from typing import List, Dict, Any

# Default configuration - normally these would be in environment variables
# In a production app, never hardcode these values
REDDIT_CLIENT_ID = os.getenv("REDDIT_CLIENT_ID", "YOUR_CLIENT_ID")
REDDIT_CLIENT_SECRET = os.getenv("REDDIT_CLIENT_SECRET", "YOUR_CLIENT_SECRET")
REDDIT_USER_AGENT = os.getenv("REDDIT_USER_AGENT", "TravelMate Lite AI v1.0")

def initialize_reddit_client() -> praw.Reddit:
    """Initialize the Reddit API client"""
    client_id = os.getenv('REDDIT_CLIENT_ID')
    client_secret = os.getenv('REDDIT_CLIENT_SECRET')
    
    if not client_id or not client_secret:
        raise ValueError("REDDIT_CLIENT_ID and REDDIT_CLIENT_SECRET environment variables must be set")
    
    return praw.Reddit(
        client_id=client_id,
        client_secret=client_secret,
        user_agent="TravelMate/1.0"
    )

def get_time_filter_timestamp(time_filter: str) -> float:
    """Convert time filter to Unix timestamp"""
    now = datetime.now()
    if time_filter == 'week':
        return (now - timedelta(weeks=1)).timestamp()
    elif time_filter == 'month':
        return (now - timedelta(days=30)).timestamp()
    elif time_filter == 'year':
        return (now - timedelta(days=365)).timestamp()
    return 0  # 'all' time filter

def fetch_reddit_data(subreddit: str, query: str, time_filter: str = 'month', min_score: int = 5) -> List[Dict[str, Any]]:
    """
    Fetch relevant posts and comments from a subreddit.
    
    Args:
        subreddit (str): Subreddit name
        query (str): Search query (city/region name)
        time_filter (str): Time filter ('week', 'month', 'year', 'all')
        min_score (int): Minimum score threshold for posts
    
    Returns:
        List[Dict]: List of posts with their comments
    """
    reddit = initialize_reddit_client()
    subreddit = reddit.subreddit(subreddit)
    time_threshold = get_time_filter_timestamp(time_filter)
    
    print(f"\nSearching r/{subreddit} for posts about {query}...")
    posts_data = []
    
    # Search for posts
    for submission in tqdm(subreddit.search(query, sort='relevance', time_filter=time_filter), desc="Fetching posts"):
        # Skip if post is too old or score is too low
        if submission.created_utc < time_threshold or submission.score < min_score:
            continue
        
        # Get post data
        post_data = {
            'title': submission.title,
            'selftext': submission.selftext,
            'score': submission.score,
            'created_utc': submission.created_utc,
            'url': f"https://reddit.com{submission.permalink}",
            'comments': []
        }
        
        # Get comments
        submission.comments.replace_more(limit=0)  # Remove MoreComments objects
        for comment in submission.comments.list():
            if comment.score >= min_score:
                post_data['comments'].append({
                    'body': comment.body,
                    'score': comment.score,
                    'created_utc': comment.created_utc
                })
        
        posts_data.append(post_data)
    
    return posts_data

class MockRedditClient:
    """A mock Reddit client for demo purposes when API credentials aren't available"""
    def __init__(self):
        pass
    
    def subreddit(self, subreddit_name):
        return MockSubreddit(subreddit_name)

class MockSubreddit:
    """A mock Subreddit for demo purposes"""
    def __init__(self, name):
        self.name = name
    
    def search(self, query, limit=None, sort='relevance', time_filter='year'):
        # Return mock data based on the query
        mock_data = []
        if 'barcelona' in query.lower():
            mock_data = MOCK_BARCELONA_DATA
        elif 'tokyo' in query.lower():
            mock_data = MOCK_TOKYO_DATA
        elif 'new york' in query.lower():
            mock_data = MOCK_NEW_YORK_DATA
        return mock_data[:limit if limit else len(mock_data)]

# Mock data for demonstration purposes
MOCK_BARCELONA_DATA = [
    {
        'title': 'Best cafes in Barcelona',
        'selftext': 'I spent a month in Barcelona and discovered some amazing cafes. Satan\'s Coffee Corner in Gothic Quarter has excellent pour-overs. Nomad Coffee is another must-visit for specialty coffee lovers. For a more local experience, try Cafe El Magnifico - they roast their own beans.',
        'created_utc': datetime.now() - timedelta(days=45),
        'score': 124,
        'num_comments': 37,
        'comments': [
            'Definitely check out Brunch & Cake too. Amazing breakfast and coffee.',
            'SlowMov in Gracia is my favorite. Great atmosphere and coffee beans from local roasters.',
            'For a great coffee with a view, try Cafe Cremat in Montjuic. A bit off the beaten path but worth it.'
        ]
    },
    {
        'title': 'Hidden gems in Barcelona that tourists miss',
        'selftext': 'After living in Barcelona for 3 years, here are some spots tourists often miss: Bunkers del Carmel for the best sunset views, the Labyrinth Park of Horta for a peaceful escape, and the Montjuic Cemetery for history and impressive sculpture.',
        'created_utc': datetime.now() - timedelta(days=120),
        'score': 321,
        'num_comments': 74,
        'comments': [
            'The Hospital de Sant Pau is incredible and much less crowded than Sagrada Familia.',
            'El Born Centre Cultural is worth visiting. It\'s built on archaeological ruins and has great exhibits.',
            'Check out Carrer d\'Enric Granados for local restaurants without the tourist prices.'
        ]
    }
]

MOCK_TOKYO_DATA = [
    {
        'title': 'Tokyo: Best bars and izakayas for solo travelers',
        'selftext': 'Just returned from 2 weeks in Tokyo. For solo travelers wanting to meet people, I recommend: Golden Gai in Shinjuku (tiny bars with 5-10 seats max), Albatross Bar in Shinjuku (friendly staff who speak English), and Coins Bar in Shibuya (cheap drinks, lots of travelers).',
        'created_utc': datetime.now() - timedelta(days=30),
        'score': 278,
        'num_comments': 63,
        'comments': [
            'Add Whales of August in Shibuya to your list. The owner is super friendly and it\'s a great place to meet locals.',
            'I always go to Mikkeller Tokyo. It\'s a craft beer bar with a mixed crowd of locals and foreigners.',
            'Try any standing bar (tachinomi) around train stations after work hours. Great for meeting locals.'
        ]
    },
    {
        'title': 'Unique experiences in Tokyo',
        'selftext': 'Looking beyond the usual tourist spots, I found these experiences fascinating: Tsukiji Outer Market for breakfast (the inner market moved but the outer is still amazing), a cooking class in Asakusa, and the digital art museum TeamLab Borderless in Odaiba.',
        'created_utc': datetime.now() - timedelta(days=90),
        'score': 412,
        'num_comments': 93,
        'comments': [
            'The Yanaka district is perfect for experiencing old Tokyo. Very few tourists.',
            'Try a baseball game at Tokyo Dome - even if you don\'t like sports, the atmosphere is incredible.',
            'Shimokitazawa neighborhood is great for vintage shopping and indie music venues.'
        ]
    }
]

MOCK_NEW_YORK_DATA = [
    {
        'title': 'NYC on a budget: How to experience the city without breaking the bank',
        'selftext': 'Just spent 10 days in NYC on a tight budget. Some tips: Use the 7-day unlimited MetroCard for all transportation, eat at food trucks and markets instead of restaurants, and take advantage of free museum days (many museums have "pay what you wish" hours).',
        'created_utc': datetime.now() - timedelta(days=15),
        'score': 503,
        'num_comments': 124,
        'comments': [
            'The Staten Island Ferry is completely free and gives you great views of the Statue of Liberty.',
            'Check out Brooklyn\'s Prospect Park instead of always going to Central Park - it\'s less crowded.',
            'The Highline is a fantastic free attraction with great views of the city.'
        ]
    },
    {
        'title': 'Best pizza in New York City - My ranking after trying 30+ spots',
        'selftext': 'After a month in NYC trying as many pizza places as I could, here are my top 5: 1) L&B Spumoni Gardens in Brooklyn (get the square slice), 2) Joe\'s Pizza in Greenwich Village, 3) Scarr\'s Pizza on the Lower East Side, 4) Lucali in Carroll Gardens (be prepared to wait), 5) Di Fara in Midwood (worth the trip to Brooklyn).',
        'created_utc': datetime.now() - timedelta(days=60),
        'score': 718,
        'num_comments': 203,
        'comments': [
            'Prince Street Pizza in Nolita should definitely be on this list. Those pepperoni cups are amazing.',
            'If you\'re looking for something different, try Artichoke Basille\'s Pizza. Their artichoke slice is unique.',
            'John\'s of Bleecker Street is the most underrated pizza in the city. No slices, only whole pies from a coal oven.'
        ]
    }
]

def fetch_reddit_data(city, interests, subreddits=["travel", "solotravel"], post_limit=5):
    """
    Fetch relevant data from Reddit based on city and interests.
    If fewer than 10 verified places are found, supplement with direct Google Maps search.
    
    Args:
        city (str): The city or region to search for
        interests (str): The user's interests
        subreddits (list): List of subreddits to search
        post_limit (int): Maximum number of posts to retrieve
    
    Returns:
        tuple: (str: Concatenated relevant Reddit data, list: Verified places)
    """
    # Initialize Reddit API and Google Maps
    reddit = initialize_reddit_client()
    try:
        gmaps = initialize_gmaps_client()
    except ValueError as e:
        print(f"Warning: {str(e)}. Place verification will be skipped.")
        gmaps = None
    
    # Calculate the cutoff date (3 years ago)
    cutoff_date = datetime.now() - timedelta(days=3*365)
    
    # Prepare search query
    query = f"{city} {interests}"
    print(f"\nSearching for recent posts about {city}...")
    
    all_data = []
    verified_places = []
    
    # Search each subreddit
    for subreddit_name in subreddits:
        try:
            print(f"\nSearching in r/{subreddit_name}...")
            subreddit = reddit.subreddit(subreddit_name)
            
            # Search for relevant posts
            posts = list(subreddit.search(query, limit=post_limit*2, sort="relevance", time_filter="year"))
            
            for post in posts:
                # Check if post is within the last 3 years
                post_date = datetime.fromtimestamp(post.created_utc)
                if post_date < cutoff_date:
                    continue
                
                # Check if post is relevant
                if is_relevant(post, city):
                    # Extract post data
                    post_data = {
                        "title": getattr(post, "title", "[Title unavailable]"),
                        "content": getattr(post, "selftext", "").strip(),
                        "date": post_date.strftime("%Y-%m-%d"),
                        "score": getattr(post, "score", 0),
                        "comments": []
                    }
                    
                    # Extract and verify places from the post
                    if gmaps:
                        # Extract places from title and content
                        places = extract_place_names(post_data["title"] + " " + post_data["content"])
                        
                        # Verify each place
                        for place in places:
                            details = verify_and_get_place_details(gmaps, place, city)
                            if details:
                                verified_places.append(details)
                    
                    # Add top comments if available
                    if hasattr(post, "comments") and not isinstance(post, dict):
                        post.comments.replace_more(limit=0)
                        for comment in post.comments[:3]:
                            if hasattr(comment, "body") and len(comment.body.strip()) > 15:
                                comment_text = comment.body.strip()
                                post_data["comments"].append(comment_text)
                                
                                # Extract and verify places from comments
                                if gmaps:
                                    places = extract_place_names(comment_text)
                                    for place in places:
                                        details = verify_and_get_place_details(gmaps, place, city)
                                        if details:
                                            verified_places.append(details)
                    
                    all_data.append(post_data)
                    
                    # Break if we have enough recent, relevant posts
                    if len(all_data) >= post_limit:
                        break
            
        except Exception as e:
            print(f"Error fetching data from r/{subreddit_name}: {str(e)}")
    
    # Remove duplicate places
    verified_places = [dict(t) for t in {tuple(d.items()) for d in verified_places}]
    
    # If we have fewer than 10 verified places and have Google Maps access, search directly
    if gmaps and len(verified_places) < 10:
        print(f"\nFound only {len(verified_places)} verified places from Reddit. Searching Google Maps directly...")
        # Split interests into a list
        interest_list = [i.strip() for i in interests.split(',')]
        if not interest_list:
            interest_list = [interests]
            
        # Get additional places from Google Maps
        additional_places = search_places_directly(gmaps, city, interest_list)
        
        # Merge the results, avoiding duplicates by name
        existing_names = {place['name'] for place in verified_places}
        for place in additional_places:
            if place['name'] not in existing_names:
                verified_places.append(place)
                existing_names.add(place['name'])
        
        # Sort all places by rating
        verified_places.sort(key=lambda x: float(x['rating']) if isinstance(x['rating'], (int, float)) else 0, reverse=True)
        verified_places = verified_places[:10]  # Keep top 10
    
    # Format the data for the model
    formatted_data = format_reddit_data(all_data, verified_places)
    
    # If we have no Reddit data but have verified places, create a minimal context
    if not all_data and verified_places:
        formatted_data = f"While no recent Reddit discussions were found about {city}, here are some highly-rated places that match your interests:\n\n"
        formatted_data += format_verified_places_section(verified_places)
    
    return formatted_data, verified_places

def format_verified_places_section(verified_places):
    """Format the verified places section"""
    formatted_text = "VERIFIED PLACES:\n"
    for place in verified_places:
        formatted_text += format_place_details(place) + "\n"
    return formatted_text

def format_reddit_data(posts, verified_places):
    """Format Reddit posts and comments for the model input"""
    formatted_text = ""
    
    # First, add the verified places section
    if verified_places:
        formatted_text += format_verified_places_section(verified_places)
        formatted_text += "\n---\n\n"
    
    # Then add the Reddit posts
    for i, post in enumerate(posts):
        formatted_text += f"POST {i+1} ({post['date']}): {post['title']}\n"
        
        # Add post content if it exists and isn't too long
        if post['content'] and len(post['content']) > 10:
            # Truncate very long posts
            content = post['content'][:1000] + "..." if len(post['content']) > 1000 else post['content']
            formatted_text += f"Content: {content}\n\n"
        
        # Add comments if they exist
        if post['comments']:
            formatted_text += "Top comments:\n"
            for comment in post['comments']:
                formatted_text += f"- {comment}\n"
        
        formatted_text += "\n---\n\n"
    
    return formatted_text

def is_relevant(post, city):
    """Check if a post is relevant to the city"""
    if isinstance(post, dict):
        # For mock data
        title = post.get("title", "").lower()
        content = post.get("selftext", "").lower()
    else:
        # For real Reddit data
        title = getattr(post, "title", "").lower()
        content = getattr(post, "selftext", "").lower()
    
    city_lower = city.lower()
    
    # Check if city is mentioned in title or content
    return city_lower in title or city_lower in content