from typing import List
from datetime import datetime, timedelta
from reddit_utils import fetch_reddit_data
from place_processor import PlaceProcessor, RedditPost
from prompts import get_recommendation_prompt
from mistral_utils import get_recommendations
import argparse

def process_reddit_data(subreddit_data: List[dict]) -> List[RedditPost]:
    """Convert raw Reddit data to RedditPost objects"""
    posts = []
    for post in subreddit_data:
        posts.append(RedditPost(
            title=post['title'],
            content=post.get('selftext', ''),
            date=datetime.fromtimestamp(post['created_utc']),
            comments=[c['body'] for c in post.get('comments', [])],
            score=post['score']
        ))
    return posts

def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(description='Travel Recommendation System')
    parser.add_argument('city', help='City or region to get recommendations for')
    parser.add_argument('interests', help='Comma-separated list of interests (e.g., "food,culture,history")')
    parser.add_argument('--time-filter', default='month', choices=['week', 'month', 'year', 'all'],
                       help='Time filter for Reddit posts')
    parser.add_argument('--min-score', type=int, default=5,
                       help='Minimum score for Reddit posts')
    args = parser.parse_args()

    # Process interests
    interests = [i.strip() for i in args.interests.split(',')]

    print(f"\n🌍 Starting travel recommendation process for {args.city}")
    print(f"🎯 Interests: {', '.join(interests)}")

    try:
        # 1. Fetch Reddit data
        print("\n📱 Fetching data from Reddit...")
        subreddits = ['travel', 'solotravel']
        reddit_data = []
        
        for subreddit in subreddits:
            data = fetch_reddit_data(
                subreddit=subreddit,
                query=args.city,
                time_filter=args.time_filter,
                min_score=args.min_score
            )
            reddit_data.extend(data)

        if not reddit_data:
            print("⚠️ No relevant Reddit posts found. Proceeding with direct Google Maps search...")
        else:
            print(f"✅ Found {len(reddit_data)} relevant Reddit posts")

        # 2. Process and verify places
        processor = PlaceProcessor()
        reddit_posts = process_reddit_data(reddit_data)
        verified_places, potential_places = processor.process_reddit_data(reddit_posts, args.city)
        
        print(f"\n📊 Place Verification Summary:")
        print(f"- Found {len(potential_places)} potential places in discussions")
        print(f"- {len(verified_places)} places verified through Google Maps")

        # 3. Supplement with additional places if needed
        verified_places = processor.supplement_with_maps_data(verified_places, args.city, interests)
        print(f"- Final count: {len(verified_places)} verified places")

        # 4. Format data for the LLM
        formatted_data = processor.format_places_data(verified_places, args.city)

        # 5. Generate recommendations using Mistral
        print("\n🤖 Generating personalized recommendations...")
        recommendations = get_recommendations(
            city=args.city,
            interests=args.interests,
            formatted_data=formatted_data
        )

        # 6. Output results
        print("\n🎉 Recommendations generated successfully!")
        print("\n" + "="*80 + "\n")
        print(recommendations)
        print("\n" + "="*80)

    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        return 1

    return 0

if __name__ == "__main__":
    exit(main()) 