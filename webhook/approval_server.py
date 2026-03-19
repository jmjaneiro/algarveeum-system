import os
import sys
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

@app.get("/generate/{content_id}", response_class=HTMLResponse)
async def generate_post(content_id: str, calendar_id: str = None):
    """Fetches raw article, calls Claude dynamically, and returns the generated content directly to the browser view."""
    try:
        # Get raw article
        res = supabase.table("published_content").select("*").eq("id", content_id).execute()
        if not res.data:
            return HTMLResponse(content=get_html_response("Artigo não encontrado. Verifica as chaves RLS.", False), status_code=404)
            
        article = res.data[0]
        if article.get("status") in ["approved", "pending"]:
             pass 
             
        # Call Claude to Generate and Score
        gen = generate_content(article['title'], article['summary'], article['url'])
        scoring = score_content(gen)
        score = scoring.get("score", 0)
        
        # Save Generated Post
        ig_post = {
            "content_id": content_id, "platform": "instagram_post",
            "caption": gen.get("instagram_post", ""), "score": score,
            "improvement_suggestions": scoring.get("improvement_suggestions", [])
        }
        gp_res = supabase.table("generated_posts").insert([
            ig_post,
            {"content_id": content_id, "platform": "instagram_story", "story_text": gen.get("instagram_story", ""), "score": score},
            {"content_id": content_id, "platform": "facebook_post", "caption": gen.get("facebook_post", ""), "score": score}
        ]).execute()
        
        post_db_id = gp_res.data[0]['id']
        
        # Mark as approved so it's ready for syndication scripts later
        supabase.table("published_content").update({"status": "approved"}).eq("id", content_id).execute()
        
        # Bind safely to calendar slot
        if calendar_id:
            supabase.table("calendar_entries").update({"post_id": post_db_id}).eq("id", calendar_id).execute()
        
        html_success = f"""
        <html>
        <body style="font-family: Arial, sans-serif; text-align: center; padding: 40px; background-color: #f0f8ff;">
            <h1 style="color: #2ecc71;">Sucesso! Post Gerado (Score Automático: {score}/100)</h1>
            <p><strong>Artigo:</strong> {article['title']}</p>
            <p>O conteúdo já foi guardado na Base de Dados e está pronto a copiar e publicar nas redes sociais.</p>
            <div style="background: white; text-align: left; padding: 25px; border-radius: 8px; margin: 30px auto; max-width: 600px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
                <h3 style="color: #e1306c; border-bottom: 2px solid #e1306c; padding-bottom: 5px;">📱 Instagram (Feed)</h3>
                <p style="white-space: pre-wrap; font-size: 15px;">{gen.get("instagram_post", "")}</p>
                
                <h3 style="color: #f77737; border-bottom: 2px solid #f77737; padding-bottom: 5px; margin-top: 30px;">📷 Instagram Story</h3>
                <p style="white-space: pre-wrap; font-size: 15px;">{gen.get("instagram_story", "")}</p>
                
                <h3 style="color: #1877f2; border-bottom: 2px solid #1877f2; padding-bottom: 5px; margin-top: 30px;">📘 Facebook Post</h3>
                <p style="white-space: pre-wrap; font-size: 15px;">{gen.get("facebook_post", "")}</p>
            </div>
            
            <div style="margin-top: 40px;">
                <a href="https://business.facebook.com/creatorstudio/home" target="_blank" style="background-color: #1877f2; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px; font-weight: bold; font-size: 16px;">Ir para o Meta Business Suite 👉</a>
            </div>
        </body>
        </html>
        """
        return HTMLResponse(content=html_success)
        
    except Exception as e:
        print(f"Error dynamically generating content: {e}")
        return HTMLResponse(content=get_html_response(f"Ocorreu um erro ao comunicar com o Claude AI: {e}", False), status_code=500)

@app.get("/reject/{content_id}", response_class=HTMLResponse)
async def reject_content(content_id: str):
    """Marks the raw or pending content as rejected."""
    try:
        data = {"status": "rejected"}
        res = supabase.table("published_content").update(data).eq("id", content_id).execute()
        if not res.data:
            return HTMLResponse(content=get_html_response("Erro: Chave Supabase sem permissões ou ID inexistente.", False), status_code=404)
        return HTMLResponse(content=get_html_response("O artigo foi descartado com sucesso. Não foi gerado nenhum post."))
    except Exception as e:
        print(f"Error rejecting content: {e}")
        return HTMLResponse(content=get_html_response(f"Erro no servidor: {e}", False), status_code=500)
