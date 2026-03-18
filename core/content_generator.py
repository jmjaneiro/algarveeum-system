import os
import json
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()

# We use the recommended sonnet or haiku for text generation. Haiku is fast and cheap, Sonnet is smarter.
# We'll default to haiku for generation to keep it lightweight but effective.
CLAUDE_MODEL = "claude-3-haiku-20240307" 

def generate_content(article_title: str, article_summary: str, url: str) -> dict:
    """
    Uses the Anthropic Claude API to generate an Instagram Post, 
    Instagram Story, and Facebook Post based on a given article.
    
    Tone: civic, empowering, non-partisan, youth-oriented, proud of regional identity.
    Language: European Portuguese. No touristic/beach-holiday language.
    
    Returns a dictionary with 'instagram_post', 'instagram_story', and 'facebook_post' keys.
    """
    client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    if not client.api_key:
        raise ValueError("ANTHROPIC_API_KEY not found in environment variables.")
        
    system_prompt = (
        "You are an expert social media manager and regional civic activist for 'Algarve É Um', "
        "a Portuguese civic movement fighting internal regionalism in the Algarve. "
        "Your tone must be civic, proud, sometimes poetic, direct, non-partisan, and empowering. "
        "Target audience: Portuguese young adults (18-35), residents/diaspora, progressive. "
        "Language: Strict European Portuguese (PT-PT). "
        "CRITICAL: Never use touristic, beach-holiday, or 'sun and sea' language. The Algarve is a living region, not just a destination. "
        "Your output must be in valid JSON format with exactly three string keys: 'instagram_post', 'instagram_story', and 'facebook_post'."
    )
    
    user_prompt = f"""
    Based on the following news article, generate content for our social platforms.
    
    Article Title: {article_title}
    Article Summary: {article_summary}
    URL: {url}
    
    Requirements:
    1. 'instagram_post': Engaging caption (max 2200 chars), include 3-5 relevant hashtags (e.g., #AlgarveÉUm, #OÚltimoReino, #EscolhiOAlgarve), and a clear call-to-action (e.g., sharing an opinion or reading the link in bio).
    2. 'instagram_story': Max 3 lines, one bold punchy statement, very direct. 
    3. 'facebook_post': Slightly longer, more informative version of the Instagram post, can include the URL directly in the text.
    
    Output ONLY a JSON object.
    """
    
    response = client.messages.create(
        model=CLAUDE_MODEL,
        max_tokens=1024,
        system=system_prompt,
        messages=[
            {"role": "user", "content": user_prompt}
        ]
    )
    
    try:
        # Extract the JSON from the output block
        content_text = response.content[0].text
        # Sometimes Claude adds markdown JSON block markers
        if content_text.startswith("```json"):
            content_text = content_text.split("```json")[1].split("```")[0].strip()
        elif content_text.startswith("```"):
            content_text = content_text.split("```")[1].split("```")[0].strip()
            
        result = json.loads(content_text)
        return result
    except Exception as e:
        print(f"Error parsing Claude response: {e}")
        print(f"Raw response: {response.content[0].text}")
        raise ValueError("Failed to generate or parse valid JSON content.")

if __name__ == "__main__":
    # Simple test
    print("Testing content generator...")
    # Note: Requires valid ANTHROPIC_API_KEY in environment
    # res = generate_content("Novo plano de mobilidade focado no interior algarvio", "O governo anunciou verbas para autocarros na serra.", "http://example.com")
    # print(json.dumps(res, indent=2, ensure_ascii=False))
