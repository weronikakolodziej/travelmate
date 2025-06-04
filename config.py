"""Configuration settings for the Travel Recommendation System"""

# Reddit API settings
REDDIT_DEFAULT_TIME_FILTER = 'month'
REDDIT_MIN_SCORE = 5
REDDIT_SUBREDDITS = ['travel', 'solotravel']

# Google Maps API settings
MAPS_MIN_RATING = 4.0
MAPS_SEARCH_RADIUS = 5000  # meters
MAPS_RESULTS_PER_INTEREST = 5

# Place extraction settings
MIN_PLACE_NAME_LENGTH = 3
EXCLUDED_WORDS = ['I', 'A', 'An', 'The', 'This', 'That']

# Place types to consider
PLACE_TYPES = {
    'food': ['restaurant', 'cafe', 'bar', 'food'],
    'culture': ['museum', 'art_gallery', 'theater', 'library'],
    'nature': ['park', 'garden', 'natural_feature'],
    'shopping': ['shopping_mall', 'market', 'store'],
    'entertainment': ['amusement_park', 'movie_theater', 'zoo'],
    'landmarks': ['tourist_attraction', 'point_of_interest', 'landmark'],
    'religious': ['church', 'temple', 'mosque', 'place_of_worship'],
    'historical': ['historic_site', 'monument', 'castle']
}

# Recommendation settings
MAX_PLACES_PER_CATEGORY = 3
MAX_TOTAL_PLACES = 10
MIN_REDDIT_MENTIONS = 1

# Output formatting
EMOJI_MAP = {
    'food': '🍽️',
    'culture': '🎨',
    'nature': '🌳',
    'shopping': '🛍️',
    'entertainment': '🎪',
    'landmarks': '🏛️',
    'religious': '⛪',
    'historical': '🏰'
} 