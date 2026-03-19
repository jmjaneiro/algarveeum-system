import os
import sys
import json
from anthropic import Anthropic
from dotenv import load_dotenv

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.supabase_client import supabase
from core.content_generator import generate_content
from core.quality_scorer import score_content

load_dotenv()

CLAUDE_MODEL = "claude-sonnet-4-6"

def is_duplicate(url: str) -> bool:
    try:
        response = supabase.table("published_content").select("id").eq("url", url).execute()
        return len(response.data) > 0
    except Exception as e:
        print(f"Error checking duplicate: {e}")
        return False

def select_best_articles(articles: list, content_type: str, max_count: int = 3) -> list:
    """Allows Claude to pick the most relevant articles filtered strictly by the given calendar content_type."""
    if not articles:
        return []
        
    client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    system_prompt = (
        f"You are an AI curator for 'Algarve É Um', a civic movement fighting regionalism in the Algarve. "
        f"Today's editorial theme from our content calendar is: '{content_type}'. "
        f"Your task is to select the most relevant news articles that flawlessly match this theme AND our movement values. "
        f"Reject any purely touristic, beach holiday, or non-Algarve articles unconditionally. "
        f"Return ONLY a JSON list of integers corresponding to the indices of the selected articles."
    )
    
    articles_text = "\n\n".join([f"[{i}] {a['title']}\nSummary: {a['summary']}" for i, a in enumerate(articles)])
    user_prompt = f"Select up to {max_count} best articles from this list. Return ONLY a valid JSON list of integers like [0, 2].\n\n{articles_text}"
    
    try:
        response = client.messages.create(
            model=CLAUDE_MODEL,
            max_tokens=256,
            system=system_prompt,
            messages=[{"role": "user", "content": user_prompt}]
        )
        content_text = response.content[0].text
        if "```json" in content_text: content_text = content_text.split("```json")[1].split("```")[0].strip()
        elif "```" in content_text: content_text = content_text.split("```")[1].split("```")[0].strip()
            
        indices = json.loads(content_text)
        if not isinstance(indices, list): indices = []
        return [articles[i] for i in indices if 0 <= i < len(articles)][:max_count]
    except Exception as e:
        print(f"Error parsing curator response: {e}")
        return articles[:max_count]

def curate_and_prepare_content(articles: list, content_type: str, calendar_id: str = None) -> list:
    print(f"Checking {len(articles)} articles vs Supabase duplicates...")
    new_articles = [a for a in articles if not is_duplicate(a['url'])]
    
    best_articles = select_best_articles(new_articles, content_type, max_count=3)
    final_results = []
    
    for article in best_articles:
        print(f"Processing ({content_type}): {article['title']}")
        gen = generate_content(article['title'], article['summary'], article['url'])
        scoring = score_content(gen)
        
        score = scoring.get("score", 0)
        suggestions = scoring.get("improvement_suggestions", [])
        
        if score > 60:
            print(f"  -> VALIDATED: Score {score}")
            try:
                # 1. Insert Published Content
                pc_res = supabase.table("published_content").insert({
                    "url": article['url'],
                    "title": article['title'],
                    "summary": article['summary'][:1000] if article['summary'] else "",
                    "status": "pending"
                }).execute()
                content_id = pc_res.data[0]['id']
                
                # 2. Insert Generated Posts
                ig_post = {
                    "content_id": content_id, "platform": "instagram_post",
                    "caption": gen.get("instagram_post", ""), "score": score,
                    "improvement_suggestions": suggestions
                }
                gp_res = supabase.table("generated_posts").insert([
                    ig_post,
                    {"content_id": content_id, "platform": "instagram_story", "story_text": gen.get("instagram_story", ""), "score": score},
                    {"content_id": content_id, "platform": "facebook_post", "caption": gen.get("facebook_post", ""), "score": score}
                ]).execute()
                
                # 3. Link back to calendar so analytics works
                post_db_id = gp_res.data[0]['id']
                if calendar_id:
                    supabase.table("calendar_entries").update({"post_id": post_db_id}).eq("id", calendar_id).execute()
                
                final_results.append({
                    "article": article,
                    "content": gen,
                    "scoring": scoring,
                    "content_id": content_id
                })
            except Exception as e:
                print(f"  -> Database insert error: {e}")
        else:
            print(f"  -> REJECTED: Score too low ({score})")
            
    return final_results
