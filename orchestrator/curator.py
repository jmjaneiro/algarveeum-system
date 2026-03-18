import os
import json
import sys
from anthropic import Anthropic
from dotenv import load_dotenv

# Ensure we can import from core even if run from different directories
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.supabase_client import supabase
from core.content_generator import generate_content
from core.quality_scorer import score_content

load_dotenv()

CLAUDE_MODEL = "claude-3-haiku-20240307"

def is_duplicate(url: str) -> bool:
    """Checks if the article URL already exists in Supabase."""
    try:
        response = supabase.table("published_content").select("id").eq("url", url).execute()
        return len(response.data) > 0
    except Exception as e:
        print(f"Error checking duplicate: {e}")
        return False

def select_best_articles(articles: list, max_count: int = 3) -> list:
    """Uses Claude API to pick the most mission-relevant articles from the list."""
    if not articles:
        return []
        
    client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    system_prompt = (
        "You are an AI curator for 'Algarve É Um', a Portuguese civic movement fighting internal "
        "regionalism in the Algarve. Select the most relevant news articles that align with our core "
        "values: youth retention, public transport/mobility, regional identity, sustainability, and "
        "civic engagement. Reject articles purely about tourism, beaches, or foreign holidays.\n\n"
        "Return a JSON list of integers corresponding to the indices of the selected articles."
    )
    
    # Format articles for prompt
    articles_text = "\n\n".join([f"[{i}] {a['title']}\nSummary: {a['summary']}" for i, a in enumerate(articles)])
    user_prompt = f"Select up to {max_count} best articles from this list. Return ONLY a JSON list of integers.\n\n{articles_text}"
    
    try:
        response = client.messages.create(
            model=CLAUDE_MODEL,
            max_tokens=256,
            system=system_prompt,
            messages=[{"role": "user", "content": user_prompt}]
        )
        
        content_text = response.content[0].text
        if "```json" in content_text:
            content_text = content_text.split("```json")[1].split("```")[0].strip()
        elif "```" in content_text:
            content_text = content_text.split("```")[1].split("```")[0].strip()
            
        indices = json.loads(content_text)
        if not isinstance(indices, list):
            indices = []
            
        return [articles[i] for i in indices if 0 <= i < len(articles)][:max_count]
    except Exception as e:
        print(f"Error parsing curator response: {e}")
        # Fallback to the first max_count articles
        return articles[:max_count]

def curate_and_prepare_content(articles: list) -> list:
    """
    Main AI Curation workflow:
    1. Filter out duplicates from local DB
    2. Pick 3 best articles
    3. Generate content for each
    4. Score content
    5. Discard if score <= 60, otherwise save to DB and keep
    """
    print(f"Checking {len(articles)} articles for duplicates...")
    new_articles = [a for a in articles if not is_duplicate(a['url'])]
    print(f"Found {len(new_articles)} new, unique articles.")
    
    best_articles = select_best_articles(new_articles, max_count=3)
    final_results = []
    
    for article in best_articles:
        print(f"Processing: {article['title']}")
        gen = generate_content(article['title'], article['summary'], article['url'])
        scoring = score_content(gen)
        
        score = scoring.get("score", 0)
        suggestions = scoring.get("improvement_suggestions", [])
        
        if score > 60:
            print(f"  -> VALIDATED: Score {score}")
            
            try:
                # 1. Insert into published_content
                pc_data = {
                    "url": article['url'],
                    "title": article['title'],
                    "summary": article['summary'][:1000] if article['summary'] else "",
                    "status": "pending"
                }
                pc_res = supabase.table("published_content").insert(pc_data).execute()
                content_id = pc_res.data[0]['id']
                
                # 2. Insert into generated_posts (Insta Post, Insta Story, FB Post)
                gp_data = [
                    {
                        "content_id": content_id,
                        "platform": "instagram_post",
                        "caption": gen.get("instagram_post", ""),
                        "score": score,
                        "improvement_suggestions": suggestions
                    },
                    {
                        "content_id": content_id,
                        "platform": "instagram_story",
                        "story_text": gen.get("instagram_story", ""),
                        "score": score,
                        "improvement_suggestions": suggestions
                    },
                    {
                        "content_id": content_id,
                        "platform": "facebook_post",
                        "caption": gen.get("facebook_post", ""),
                        "score": score,
                        "improvement_suggestions": suggestions
                    }
                ]
                supabase.table("generated_posts").insert(gp_data).execute()
                
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
