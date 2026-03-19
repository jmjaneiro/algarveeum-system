import os
import re
import random
from datetime import datetime
from tavily import TavilyClient
from dotenv import load_dotenv

load_dotenv()

TRUSTED_DOMAINS = [
    "sulinformacao.pt", "postal.pt", "algarveprimeiro.com", "barlavento.pt",
    "publico.pt", "observador.pt", "expresso.pt", "tsf.pt", "rr.sapo.pt",
    "algarve.pt", "cm-faro.pt", "cm-loule.pt", "cm-portimao.pt", "cm-tavira.pt",
    "cm-albufeira.pt", "cm-silves.pt"
]

def search_recent_news(content_type: str) -> list:
    """
    Uses Tavily API to search recent articles natively, and then computationally 
    verifies published dates and URL timestamps to guarantee no stale news (e.g. from 2018) slips by.
    """
    api_key = os.getenv("TAVILY_API_KEY")
    if not api_key:
        raise ValueError("TAVILY_API_KEY not found.")
        
    client = TavilyClient(api_key=api_key)
    
    days_limit = 1
    
    if content_type == "community_spotlight":
        query = '"Algarve" AND ("associação" OR "jovens" OR "projeto" OR "iniciativa") -futebol'
        days_limit = 7
    elif content_type == "civic_call_to_action":
        query = '"Algarve" AND ("habitação" OR "transportes" OR "saúde" OR "protesto" OR "mobilidade")'
        days_limit = 2
    elif content_type == "historical_fact":
        query = '"Algarve" AND ("história" OR "património" OR "cultura" OR "tradição")'
        days_limit = 30  
    elif content_type == "regional_beauty":
        query = '"Algarve" AND ("serra" OR "interior" OR "natureza" OR "aldeia" OR "ria formosa") -resort'
        days_limit = 14
    elif content_type == "practical_utility":
        query = '"Algarve" AND ("aviso" OR "meteorologia" OR "transportes" OR "cp" OR "eva" OR "emprego" OR "bolsas" OR "obras" OR "corte de água")'
        days_limit = 2
    elif content_type == "cultural_entertainment":
        query = '"Algarve" AND ("evento" OR "gratuito" OR "festa" OR "gastronomia" OR "artista" OR "desporto" OR "música" OR "feira")'
        days_limit = 7
    elif content_type == "interactive_conversational":
        query = '"Algarve" AND ("tradição" OR "memória" OR "antigamente" OR "comunidade" OR "freguesia" OR "regionalismo")'
        days_limit = 30
    else: 
        queries = [
            '"Algarve" AND ("desenvolvimento" OR "governo" OR "economia")',
            '"Algarve" AND ("sustentabilidade" OR "ambiente" OR "seca" OR "barragem")',
            '"Algarve" AND ("juventude" OR "habitação" OR "emprego" OR "saúde")'
        ]
        query = random.choice(queries)
        days_limit = 1
        
    print(f"Searching Tavily for '{content_type}' (Range limit: {days_limit} days). Query: {query}")
    
    try:
        response = client.search(
            query=query, 
            search_depth="advanced",
            topic="news",
            days=days_limit,
            max_results=15,
            include_domains=TRUSTED_DOMAINS
        )
    except Exception as e:
        print(f"Tavily search failed: {e}")
        return []
    
    results = []
    tourism_keywords = ["melhor destino de férias", "hotel", "resort", "turistas", "all-inclusive", "pacote de férias", "agência de viagens"]
    
    now = datetime.now()
    current_year = now.year
    last_year = current_year - 1
    
    # Regex to find years in URLs (like /2018/ or -2018-)
    year_regex = re.compile(r'(?:/|-)(20\d{2})(?:/|-)')
    
    for r in response.get("results", []):
        url = r.get("url", "").lower()
        content = r.get("content", "").lower()
        title = r.get("title", "").lower()
        pub_date_str = r.get("published_date")
        
        # 1. Hard tourism filter
        if any(tk in content for tk in tourism_keywords) or any(tk in title for tk in tourism_keywords):
            continue 
            
        # 2. Strict Date Filtering via URL Patterns (e.g. publico.pt/2018/...)
        should_skip = False
        year_matches = year_regex.findall(url)
        if year_matches:
            found_year = int(year_matches[0])
            # If the article is from a previous year, and we aren't in Jan/Feb looking at late Dec.
            if found_year < current_year and now.month > 2:
                print(f"  [X] Rejeitado por data antiga no URL ({found_year}): {url}")
                should_skip = True
            elif found_year < last_year:
                # Anything older than last year is always blocked for standard news
                print(f"  [X] Rejeitado por data incrivelmente antiga no URL ({found_year}): {url}")
                should_skip = True
                
        if should_skip:
            continue
                    
        # 3. Strict Date Filtering via published_date Metadata from Tavily
        if pub_date_str:
            try:
                # Simple extraction of year "YYYY" from ISO strings like "2018-05-12T15:00:00Z"
                pub_year = int(pub_date_str[:4])
                if pub_year < current_year and now.month > 2:
                    print(f"  [X] Rejeitado por data antiga no Metadata ({pub_year}): {url}")
                    continue
                elif pub_year < last_year:
                    print(f"  [X] Rejeitado por data incrivelmente antiga no Metadata ({pub_year}): {url}")
                    continue
            except Exception:
                pass
            
        results.append({
            "title": r.get("title"),
            "url": r.get("url"),
            "summary": r.get("content"),
            "published_date": pub_date_str
        })
        
    return results[:10]

if __name__ == "__main__":
    arts = search_recent_news("news_reaction")
    print(f"Found {len(arts)} valid articles after Python-side strict date filtering.")
