import os
import random
from tavily import TavilyClient
from dotenv import load_dotenv

load_dotenv()

QUERIES = [
    "Algarve mobilidade transportes públicos",
    "Algarve juventude emigração interior",
    "Algarve governança desenvolvimento regional",
    "Algarve sustentabilidade ambiente",
    "Algarve identidade cultura comunidade"
]

def search_recent_news() -> list:
    """
    Uses Tavily API to search 10-15 recent articles (last 48h) related to the 'Algarve É Um' movement.
    Tries to filter out pure tourism/beach content using negative keywords and basic checks.
    """
    api_key = os.getenv("TAVILY_API_KEY")
    if not api_key:
        raise ValueError("TAVILY_API_KEY not found in environment variables.")
        
    client = TavilyClient(api_key=api_key)
    query = random.choice(QUERIES)
    
    print(f"Searching news via Tavily. Query: '{query}'")
    
    try:
        response = client.search(
            query=f"{query} -turismo -praias -férias", 
            search_depth="advanced",
            topic="news",
            days=2,
            max_results=15
        )
    except Exception as e:
        print(f"Tavily search failed: {e}")
        return []
    
    results = []
    for r in response.get("results", []):
        content = r.get("content", "").lower()
        title = r.get("title", "").lower()
        
        # Additional manual rough filter to skip pure tourism content
        tourism_keywords = ["melhores praias", "hotel", "resort", "turistas britânicos", "férias de verão"]
        if any(tk in content for tk in tourism_keywords) or any(tk in title for tk in tourism_keywords):
            continue 
            
        results.append({
            "title": r.get("title"),
            "url": r.get("url"),
            "summary": r.get("content"),
            "published_date": r.get("published_date")
        })
        
    return results

if __name__ == "__main__":
    # Test script standalone
    articles = search_recent_news()
    print(f"Found {len(articles)} articles.")
    for a in articles:
        print(f"- {a['title']}\n  {a['url']}\n")
