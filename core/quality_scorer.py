import os
import json
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()

# We can use haiku for fast, cheap scoring as well
CLAUDE_MODEL = "claude-3-haiku-20240307"

def score_content(content_dict: dict) -> dict:
    """
    Evaluates generated content based on predefined criteria.
    Criteria (100 pts total):
    - Alignment with movement mission (30pts)
    - Emotional resonance for target audience (25pts)
    - Hashtag relevance (15pts)
    - Call-to-action strength (15pts)
    - Authenticity (penalize touristic language) (15pts)
    
    Returns a dictionary:
    {
        "score": int (0-100),
        "improvement_suggestions": list of strings
    }
    """
    client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    if not client.api_key:
        raise ValueError("ANTHROPIC_API_KEY not found in environment variables.")
        
    system_prompt = (
        "You are an expert AI content auditor for 'Algarve É Um', "
        "a civic movement fighting internal regionalism in the Algarve. "
        "Evaluate the provided social media content strictly against these criteria:\n"
        "1. Alignment with movement mission (Max 30pts)\n"
        "2. Emotional resonance for target audience: Portuguese 18-35 (Max 25pts)\n"
        "3. Hashtag relevance using official ones like #AlgarveÉUm (Max 15pts)\n"
        "4. Call-to-action strength (Max 15pts)\n"
        "5. Authenticity / No Touristic Language. Penalize heavily if terms like 'sun, beach, holiday destination' are used (Max 15pts)\n\n"
        "Output ONLY a valid JSON object with EXACTLY two keys:\n"
        "- 'score': an integer from 0 to 100 representing the total sum.\n"
        "- 'improvement_suggestions': a list of strings containing 1-3 highly specific tips to improve the text."
    )
    
    user_prompt = f"""
    Assess this generated content:
    
    Instagram Post: {content_dict.get('instagram_post', '')}
    Instagram Story: {content_dict.get('instagram_story', '')}
    Facebook Post: {content_dict.get('facebook_post', '')}
    """
    
    response = client.messages.create(
        model=CLAUDE_MODEL,
        max_tokens=512,
        system=system_prompt,
        messages=[
            {"role": "user", "content": user_prompt}
        ]
    )
    
    try:
        content_text = response.content[0].text
        if content_text.startswith("```json"):
            content_text = content_text.split("```json")[1].split("```")[0].strip()
        elif content_text.startswith("```"):
            content_text = content_text.split("```")[1].split("```")[0].strip()
            
        result = json.loads(content_text)
        
        # fallback formatting checks
        if "score" not in result:
            result["score"] = 0
        if "improvement_suggestions" not in result:
            result["improvement_suggestions"] = []
            
        return result
    except Exception as e:
        print(f"Error parsing Claude score response: {e}")
        return {
            "score": 0,
            "improvement_suggestions": ["Failed to parse automated score.", str(e)]
        }
