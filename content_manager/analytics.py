import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.supabase_client import supabase

def get_overall_performance() -> dict:
    """Aggregates all performance metrics from the analytics table."""
    try:
        res = supabase.table("analytics").select("*").execute()
        data = res.data
        
        if not data:
            return {"status": "No analytics data available yet."}
            
        total_likes = sum(item.get("likes", 0) for item in data)
        total_reach = sum(item.get("reach", 0) for item in data)
        total_shares = sum(item.get("shares", 0) for item in data)
        total_saves = sum(item.get("saves", 0) for item in data)
        
        # Calculate average engagement rate across all posts
        engagement_rates = [item.get("engagement_rate", 0) for item in data if item.get("engagement_rate")]
        avg_engagement = sum(engagement_rates) / len(engagement_rates) if engagement_rates else 0
        
        return {
            "total_posts_tracked": len(data),
            "total_likes": total_likes,
            "total_reach": total_reach,
            "total_shares": total_shares,
            "total_saves": total_saves,
            "average_engagement_rate": round(avg_engagement, 2)
        }
    except Exception as e:
        print(f"Failed to fetch overall performance: {e}")
        return {}

def get_top_performing_hashtags(limit: int = 5) -> list:
    """Fetches the top hashtags based on average engagement from hashtag_performance table."""
    try:
        res = (supabase.table("hashtag_performance")
               .select("*")
               .order("avg_engagement", desc=True)
               .limit(limit)
               .execute())
        return res.data
    except Exception as e:
        print(f"Failed to fetch hashtag performance: {e}")
        return []

def get_best_content_types() -> dict:
    """
    Joins calendar_entries with analytics to determine which content_type
    yields the highest engagement rate. 
    (Requires inner join logic or application-side aggregation).
    """
    try:
        # Fetching calendar entries that have a post_id
        calendar_res = supabase.table("calendar_entries").select("content_type, post_id").execute()
        
        # Fetching analytics
        analytics_res = supabase.table("analytics").select("post_id, engagement_rate").execute()
        
        analytics_map = {a["post_id"]: a["engagement_rate"] for a in analytics_res.data}
        
        type_stats = {}
        for entry in calendar_res.data:
            c_type = entry.get("content_type")
            post_id = entry.get("post_id")
            if not post_id or post_id not in analytics_map:
                continue
                
            eng = float(analytics_map[post_id] or 0)
            
            if c_type not in type_stats:
                type_stats[c_type] = {"total_eng": 0, "count": 0}
                
            type_stats[c_type]["total_eng"] += eng
            type_stats[c_type]["count"] += 1
            
        return {
            ctype: round(stats["total_eng"] / stats["count"], 2) 
            for ctype, stats in type_stats.items()
        }
        
    except Exception as e:
        print(f"Failed to calculate best content types: {e}")
        return {}

if __name__ == "__main__":
    print("--- Algarve É Um: Analytics Snapshot ---")
    print("\nOverall Performance:")
    print(get_overall_performance())
    print("\nTop Hashtags:")
    for h in get_top_performing_hashtags():
        print(f" - {h['hashtag']}: {h['avg_engagement']}% avg engagement")
    print("\nBest Content Types:")
    print(get_best_content_types())
