import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime
from reddit_utils import process_reddit_data, initialize_reddit_client
from maps_utils import verify_and_get_place_details
from place_processor import PlaceProcessor, RedditPost, Place

class TestTravelRecommendationSystem(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures"""
        self.sample_reddit_post = {
            'title': 'Great places in Tokyo',
            'selftext': 'You must visit the Senso-ji Temple',
            'created_utc': datetime.now().timestamp(),
            'comments': [{'body': 'The Meiji Shrine is also amazing!'}],
            'score': 10
        }
        
        self.sample_place_details = {
            'name': 'Senso-ji Temple',
            'formatted_address': '2-3-1 Asakusa, Taito City, Tokyo 111-0032, Japan',
            'url': 'https://maps.google.com/?cid=123',
            'website': 'https://www.senso-ji.jp',
            'rating': 4.5,
            'formatted_phone_number': '+81 3-3842-0181',
            'opening_hours': {'open_now': True},
            'types': ['place_of_worship', 'tourist_attraction']
        }

    def test_process_reddit_data(self):
        """Test Reddit data processing"""
        posts = [self.sample_reddit_post]
        processed = process_reddit_data(posts)
        
        self.assertEqual(len(processed), 1)
        self.assertIsInstance(processed[0], RedditPost)
        self.assertEqual(processed[0].title, 'Great places in Tokyo')
        self.assertEqual(len(processed[0].comments), 1)

    @patch('praw.Reddit')
    def test_reddit_client_initialization(self, mock_reddit):
        """Test Reddit client initialization"""
        with patch.dict('os.environ', {
            'REDDIT_CLIENT_ID': 'test_id',
            'REDDIT_CLIENT_SECRET': 'test_secret'
        }):
            client = initialize_reddit_client()
            mock_reddit.assert_called_once()

    @patch('googlemaps.Client')
    def test_place_verification(self, mock_gmaps):
        """Test place verification with Google Maps"""
        mock_gmaps.places.return_value = {'results': [{'place_id': '123'}]}
        mock_gmaps.place.return_value = {'result': self.sample_place_details}
        
        processor = PlaceProcessor()
        processor.gmaps = mock_gmaps
        
        details = verify_and_get_place_details(mock_gmaps, 'Senso-ji Temple', 'Tokyo')
        
        self.assertIsNotNone(details)
        self.assertEqual(details['name'], 'Senso-ji Temple')
        self.assertTrue(isinstance(details['rating'], float))

    def test_place_processor(self):
        """Test the PlaceProcessor class"""
        processor = PlaceProcessor()
        
        # Test place extraction
        text = 'You should visit the Senso-ji Temple and the Meiji Shrine'
        places = processor.extract_places_from_text(text)
        
        self.assertIn('Senso-ji Temple', places)
        self.assertIn('Meiji Shrine', places)

    def test_place_formatting(self):
        """Test place formatting for output"""
        place = Place(
            name='Senso-ji Temple',
            address='2-3-1 Asakusa, Taito City, Tokyo',
            maps_url='https://maps.google.com/?cid=123',
            website='https://www.senso-ji.jp',
            rating=4.5,
            phone='+81 3-3842-0181',
            is_open=True,
            place_type='tourist_attraction',
            reddit_mentions=['Mentioned in post: Great places in Tokyo'],
            source='reddit'
        )
        
        processor = PlaceProcessor()
        formatted = processor._format_place(place)
        
        self.assertIn('Senso-ji Temple', formatted)
        self.assertIn('4.5/5', formatted)
        self.assertIn('🟢 Open now', formatted)

if __name__ == '__main__':
    unittest.main() 