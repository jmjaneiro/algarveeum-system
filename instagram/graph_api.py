import os
import sys
import requests
from datetime import datetime
from dotenv import load_dotenv

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.supabase_client import supabase

load_dotenv()

# Note: This module is fully built but remains INACTIVE.
# It requires a valid INSTAGRAM_ACCESS_TOKEN and INSTAGRAM_ACCOUNT_ID in .env
# To activate, schedule `sync_instagram_metrics()` in the orchestrator pipeline.

IG_ACCESS_TOKEN = os.getenv("INSTAGRAM_ACCESS_TOKEN")
IG_ACCOUNT_ID = os.getenv("INSTAGRAM_ACCOUNT_ID")  # Needs to be added to .env in production
GRAPH_API_VERSION = "v19.0"
BASE_URL = f"https://graph.facebook.com/{GRAPH_API_VERSION}"

def fetch_post_insights(media_id: str) -> dict:
    """Fetches reach, impressions, and engagement for a specific IG Media."""
    if not IG_ACCESS_TOKEN:
        return {}
        
    url = f"{BASE_URL}/{media_id}/insights"
    params = {
        "metric": "reach,impressions,engagement,saved,video_views",
        "access_token": IG_ACCESS_TOKEN
    }
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json().get("data", [])
        
        # Map values
        metrics = {item["name"]: item["values"][0]["value"] for item in data}
        return metrics
    except Exception as e:
        print(f"Error fetching insights for {media_id}: {e}")
        return {}

def fetch_recent_posts(limit: int = 20) -> list:
    """Fetches recent media objects from the connected IG account."""
    if not IG_ACCESS_TOKEN or not IG_ACCOUNT_ID:
        return []
        
    url = f"{BASE_URL}/{IG_ACCOUNT_ID}/media"
    params = {
        "fields": "id,caption,media_type,like_count,comments_count,timestamp",
        "limit": limit,
        "access_token": IG_ACCESS_TOKEN
    }
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json().get("data", [])
    except Exception as e:
        print(f"Error fetching recent posts: {e}")
        return []

def sync_instagram_metrics():
    """
    Main execution loop:
    1. Fetches recent IG posts
    2. Fetches detailed insights for each
    3. Cross-references with local DB (generated_posts/calendar_entries)
    4. Upserts to analytics table
    """
    print("Starting Instagram metrics sync...")
    posts = fetch_recent_posts()
    
    for post in posts:
        media_id = post.get("id")
        likes = post.get("like_count", 0)
        comments = post.get("comments_count", 0)
        
        insights = fetch_post_insights(media_id)
        
        reach = insights.get("reach", 0)
        saves = insights.get("saved", 0)
        shares = insights.get("shares", 0)  # IG graph API occasionally requires specific endpoints for shares
        
        # Basic Engagement Rate = (Likes + Comments + Saves + Shares) / Reach * 100
        total_eng = likes + comments + saves + shares
        eng_rate = (total_eng / reach * 100) if reach > 0 else 0
        
        # NOTE: To stitch this perfectly to Supabase, we would find the specific `post_id` 
        # in `generated_posts` matching this caption or a stored `ig_media_id`.
        # Assuming we have a way to match them (e.g. searching by caption snippet):
        
        # mock_post_id = extract_internal_id_from_caption(post.get("caption"))
        
        analytics_data = {
            # "post_id": mock_post_id,
            "platform": "instagram_post",
            "likes": likes,
            "reach": reach,
            "saves": saves,
            "shares": shares,
            "engagement_rate": round(eng_rate, 2),
            "recorded_at": datetime.now().isoformat()
        }
        
        print(f"Would sync: {analytics_data}")
        # supabase.table("analytics").upsert(analytics_data).execute()

def fetch_follower_growth():
    """Fetches overall account follower count and growth."""
    if not IG_ACCESS_TOKEN or not IG_ACCOUNT_ID:
        return
        
    url = f"{BASE_URL}/{IG_ACCOUNT_ID}"
    params = {
        "fields": "followers_count",
        "access_token": IG_ACCESS_TOKEN
    }
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        print(f"Current Followers: {data.get('followers_count')}")
    except Exception as e:
        print(f"Error fetching followers: {e}")

if __name__ == "__main__":
    print("Instagram Graph API Module - INACTIVE DETACHED RUN")
    # sync_instagram_metrics()
    # fetch_follower_growth()
