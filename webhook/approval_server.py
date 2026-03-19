import os
import sys
import re
import requests
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from core.supabase_client import supabase
from core.content_generator import generate_content
from core.quality_scorer import score_content

app = FastAPI(title="Algarve É Um - Webhook")

def get_html_response(message: str, success: bool = True) -> str:
    color = "#2ecc71" if success else "#e74c3c"
    icon = "✅" if success else "❌"
    
    return f"""
    <html>
    <body style="font-family: Arial, sans-serif; display: flex; justify-content: center; align-items: center; height: 100vh; background-color: #f5f6fa; margin: 0;">
        <div style="background: white; padding: 40px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); text-align: center; max-width: 500px;">
            <div style="font-size: 48px; margin-bottom: 20px;">{icon}</div>
            <h2 style="color: {color}; margin-top: 0;">{message}</h2>
            <p style="color: #7f8c8d; font-size: 14px; margin-top: 20px;">Podes fechar esta janela.</p>
        </div>
    </body>
    </html>
    """

def extract_og_image(url: str) -> str:
    """Extracts the OpenGraph image from an article URL using a quick regex."""
    try:
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        resp = requests.get(url, headers=headers, timeout=5)
        # Try finding standard og:image where content is robust
        match = re.search(r'<meta[^>]+(?:property|name)="og:image"[^>]+content="([^"]+)"', resp.text, re.IGNORECASE)
        if not match:
            # Try flipped order
            match = re.search(r'<meta[^>]+content="([^"]+)"[^>]+(?:property|name)="og:image"', resp.text, re.IGNORECASE)
        if match:
            return match.group(1)
    except Exception as e:
        print(f"Failed to fetch OG image for {url}: {e}")
    return ""

@app.get("/generate/{content_id}", response_class=HTMLResponse)
async def generate_post(content_id: str, calendar_id: str = None):
    try:
        res = supabase.table("published_content").select("*").eq("id", content_id).execute()
        if not res.data:
            return HTMLResponse(content=get_html_response("Artigo não encontrado. Verifica as chaves RLS.", False), status_code=404)
            
        article = res.data[0]
        if article.get("status") in ["approved", "pending"]:
             pass 
             
        # Scrape thumbnail directly from the article's website (for Stories)
        print(f"Fetching Hero Image from: {article['url']}")
        image_url = extract_og_image(article['url'])
             
        # Call Claude to Generate and Score
        gen = generate_content(article['title'], article['summary'], article['url'])
        scoring = score_content(gen)
        score = scoring.get("score", 0)
        
        # Save Generated Post
        gp_res = supabase.table("generated_posts").insert([
            {"content_id": content_id, "platform": "instagram_story", "story_text": gen.get("instagram_story", ""), "score": score},
            {"content_id": content_id, "platform": "facebook_post", "caption": gen.get("facebook_post", ""), "score": score, "improvement_suggestions": scoring.get("improvement_suggestions", [])}
        ]).execute()
        
        post_db_id = gp_res.data[0]['id']
        
        supabase.table("published_content").update({"status": "approved"}).eq("id", content_id).execute()
        
        if calendar_id:
            supabase.table("calendar_entries").update({"post_id": post_db_id}).eq("id", calendar_id).execute()
            
        image_html = ""
        if image_url:
            image_html = f"""
            <div style="text-align: center; margin: 20px 0;">
                <p style="font-size: 12px; color: #7f8c8d; margin-bottom: 5px;">Guarda esta imagem no telemóvel para usar como fundo na Story:</p>
                <img src="{image_url}" style="max-width: 100%; max-height: 250px; border-radius: 8px; box-shadow: 0 4px 8px rgba(0,0,0,0.1);" />
            </div>
            """
        
        html_success = f"""
        <html>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <body style="font-family: Arial, sans-serif; text-align: center; padding: 20px; background-color: #f0f8ff;">
            <h2 style="color: #2ecc71;">Post Gerado com Sucesso! 🚀</h2>
            
            <div style="background: white; text-align: left; padding: 20px; border-radius: 8px; margin: 20px auto; max-width: 600px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
                {image_html}
                
                <h3 style="color: #f77737; border-bottom: 2px solid #f77737; padding-bottom: 5px;">📷 Instagram Story</h3>
                <p style="white-space: pre-wrap; font-size: 16px; background-color: #fffaf5; padding: 15px; border-radius: 5px;">{gen.get("instagram_story", "")}</p>
                
                <h3 style="color: #1877f2; border-bottom: 2px solid #1877f2; padding-bottom: 5px; margin-top: 30px;">📘 Facebook Post</h3>
                <p style="white-space: pre-wrap; font-size: 16px; background-color: #f5f8ff; padding: 15px; border-radius: 5px;">{gen.get("facebook_post", "")}</p>
            </div>
            
            <div style="margin-top: 30px; margin-bottom: 40px;">
                <p style="font-size: 14px; color: #555;">No Mac, copia o texto e usa o Universal Clipboard para colar no iPhone, ou abre este e-mail diretamente no teu telemóvel.</p>
                <a href="https://business.facebook.com/creatorstudio/home" target="_blank" style="background-color: #1877f2; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px; font-weight: bold; font-size: 16px;">Meta Business Suite</a>
            </div>
        </body>
        </html>
        """
        return HTMLResponse(content=html_success)
        
    except Exception as e:
        print(f"Error dynamically generating content: {e}")
        return HTMLResponse(content=get_html_response(f"Ocorreu um erro ao comunicar com a Inteligência Artificial: {e}", False), status_code=500)

@app.get("/reject/{content_id}", response_class=HTMLResponse)
async def reject_content(content_id: str):
    try:
        data = {"status": "rejected"}
        res = supabase.table("published_content").update(data).eq("id", content_id).execute()
        if not res.data:
            return HTMLResponse(content=get_html_response("Erro: Chave Supabase sem permissões ou ID inexistente.", False), status_code=404)
        return HTMLResponse(content=get_html_response("O artigo foi descartado com sucesso. Não foi gerado nenhum post."))
    except Exception as e:
        print(f"Error rejecting content: {e}")
        return HTMLResponse(content=get_html_response(f"Erro no servidor: {e}", False), status_code=500)
