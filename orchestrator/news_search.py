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
    
    # To capture ALL recent news without bias, we use a generic catch-all query.
    # We rely entirely on the include_domains and days_limit to fetch the firehose of local news.
    query = "Algarve últimas notícias"
    days_limit = 2
        
    print(f"Searching Tavily broadly for diverse Algarve news (Range limit: {days_limit} days). Query: {query}")
    
    try:
        response = client.search(
            query=query, 
            search_depth="advanced",
            topic="news",
            days=days_limit,
            max_results=25,
            include_domains=TRUSTED_DOMAINS
        )
    except Exception as e:
        print(f"Tavily search failed: {e}")
        return []
    
    valid_results = []
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
            
        valid_results.append({
            "title": r.get("title"),
            "url": url,
            "summary": r.get("content"),
            "published_date": pub_date_str
        })
        
    # Domain Balancing Algorithm
    # Sul Informação and others publish high volume. Tavily might just pull all from them.
    # We group by domain and pick one from each sequentially.
    from collections import defaultdict
    domain_groups = defaultdict(list)
    
    for res in valid_results:
        domain = res["url"].split("//")[-1].split("/")[0].replace("www.", "")
        domain_groups[domain].append(res)
        
    final_results = []
    while domain_groups and len(final_results) < 10:
        domains = list(domain_groups.keys())
        random.shuffle(domains) # To ensure random domain order presentation
        for dom in domains:
            if domain_groups[dom]:
                final_results.append(domain_groups[dom].pop(0))
            if not domain_groups[dom]:
                del domain_groups[dom]
            if len(final_results) >= 10:
                break
                
    return final_results

if __name__ == "__main__":
    arts = search_recent_news("news_reaction")
    print(f"Found {len(arts)} valid articles after Python-side strict date filtering.")
