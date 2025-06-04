# TravelMate: AI-Powered Travel Recommendations

TravelMate is an intelligent travel recommendation system that combines Reddit discussions with Google Maps data to provide personalized, verified travel recommendations. It ensures that all recommended places actually exist and are currently operating.

## Features

- 🔍 Intelligent place extraction from Reddit discussions
- ✅ Place verification through Google Maps API
- 🌟 Rating-based filtering (4.0+ stars only)
- 📍 Complete location information with maps links
- 🎯 Interest-based recommendations
- 🤖 AI-powered personalization using Mistral
- 📱 Real-time operating status checks
- 🌍 Multi-source data (Reddit + Google Maps)

## Prerequisites

- Python 3.8+
- Reddit API credentials
- Google Maps API key
- Mistral AI API key

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/travelmate.git
   cd travelmate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up environment variables:
   ```bash
   export REDDIT_CLIENT_ID="your_reddit_client_id"
   export REDDIT_CLIENT_SECRET="your_reddit_client_secret"
   export GOOGLE_MAPS_API_KEY="your_google_maps_api_key"
   export MISTRAL_API_KEY="your_mistral_api_key"
   ```

## API Setup Guide

### Reddit API Setup
1. Go to https://www.reddit.com/prefs/apps
2. Click "Create App" or "Create Another App"
3. Fill in the details:
   - Name: TravelMate
   - App type: Script
   - Description: Travel recommendation system
   - About URL: Your GitHub repository URL
   - Redirect URI: http://localhost:8080
4. Note down the client ID and client secret

### Google Maps API Setup
1. Go to https://console.cloud.google.com/
2. Create a new project or select an existing one
3. Enable the following APIs:
   - Places API
   - Maps JavaScript API
   - Geocoding API
4. Create credentials (API key)
5. (Optional) Restrict the API key to specific APIs and IP addresses

### Mistral AI Setup
1. Visit https://mistral.ai/
2. Sign up for an API key
3. Store the key securely in your environment variables

## Usage

Basic usage:
```bash
python main.py "City Name" "interest1,interest2,interest3"
```

Example:
```bash
python main.py "Tokyo" "food,temples,shopping"
```

Advanced options:
```bash
python main.py "Paris" "food,art,history" --time-filter month --min-score 10
```

### Command Line Arguments

- `city`: Name of the city or region (required)
- `interests`: Comma-separated list of interests (required)
- `--time-filter`: Time filter for Reddit posts (week/month/year/all)
- `--min-score`: Minimum score threshold for Reddit posts

## System Architecture

### Components
1. **Data Collection Layer**
   - `reddit_utils.py`: Handles Reddit API interactions
   - `maps_utils.py`: Manages Google Maps API interactions

2. **Processing Layer**
   - `place_processor.py`: Core logic for place extraction and verification
   - `config.py`: System configuration and settings

3. **AI Layer**
   - `mistral_utils.py`: Manages AI-powered recommendation generation
   - `prompts.py`: Structured prompts for the AI model

4. **Interface Layer**
   - `main.py`: Command-line interface and orchestration
   - Entry point for the application

### Data Flow
1. User inputs city and interests
2. System fetches relevant Reddit posts
3. Place names are extracted using NLP
4. Places are verified through Google Maps
5. Additional places are fetched if needed
6. AI generates personalized recommendations
7. Results are formatted and presented

## Configuration

You can customize various settings in `config.py`:

### Reddit Settings
```python
REDDIT_DEFAULT_TIME_FILTER = 'month'
REDDIT_MIN_SCORE = 5
REDDIT_SUBREDDITS = ['travel', 'solotravel']
```

### Google Maps Settings
```python
MAPS_MIN_RATING = 4.0
MAPS_SEARCH_RADIUS = 5000  # meters
MAPS_RESULTS_PER_INTEREST = 5
```

### Place Types
```python
PLACE_TYPES = {
    'food': ['restaurant', 'cafe', 'bar'],
    'culture': ['museum', 'art_gallery', 'theater'],
    # ... more types
}
```

## Troubleshooting

### Common Issues

1. **Reddit API Authentication Errors**
   - Verify your client ID and secret
   - Check if the credentials are properly exported
   - Ensure your app is properly registered

2. **Google Maps API Issues**
   - Verify your API key is active
   - Check if you've enabled the necessary APIs
   - Monitor your API usage quotas

3. **Place Verification Problems**
   - Ensure city names are spelled correctly
   - Check if the place exists in Google Maps
   - Verify the minimum rating threshold

4. **Performance Issues**
   - Adjust the time filter for faster results
   - Reduce the number of places per interest
   - Use more specific interest categories

### Debug Mode
Set the DEBUG environment variable for detailed logging:
```bash
export DEBUG=1
python main.py "Tokyo" "food,shopping"
```

## Testing

Run the test suite:
```bash
python -m unittest test_system.py
```

Run specific test cases:
```bash
python -m unittest test_system.py -k test_place_verification
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

### Development Guidelines
- Follow PEP 8 style guide
- Add unit tests for new features
- Update documentation as needed
- Use type hints for better code clarity

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Reddit API for community discussions
- Google Maps API for place verification
- Mistral AI for natural language processing
- PRAW (Python Reddit API Wrapper)
- googlemaps Python client

## Support

For support, please:
1. Check the troubleshooting guide
2. Search existing GitHub issues
3. Create a new issue with:
   - System information
   - Error messages
   - Steps to reproduce
