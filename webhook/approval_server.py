import os
import sys
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from dotenv import load_dotenv

# Ensure we can import from core
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.supabase_client import supabase

load_dotenv()

app = FastAPI(title="Algarve É Um - Webhook Server")

def get_html_response(message: str, is_success: bool = True) -> str:
    """Generates a clean HTML confirmation page in European Portuguese."""
    color = "#28a745" if is_success else "#dc3545"
    return f"""
    <html>
        <head>
            <title>Confirmação - Algarve É Um</title>
            <meta charset="utf-8">
            <style>
                body {{ font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; display: flex; justify-content: center; align-items: center; height: 100vh; background-color: #f4f4f4; margin: 0; }}
                .card {{ background-color: #fff; padding: 40px; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); text-align: center; max-width: 400px; }}
                h1 {{ color: {color}; }}
                p {{ font-size: 16px; color: #555; }}
            </style>
        </head>
        <body>
            <div class="card">
                <h1>{"Sucesso" if is_success else "Atenção"}</h1>
                <p>{message}</p>
                <p style="margin-top:20px; font-size:12px; color:#aaa;">Pode fechar esta janela.</p>
            </div>
        </body>
    </html>
    """

@app.get("/approve/{content_id}", response_class=HTMLResponse)
async def approve_content(content_id: str):
    """Marks the content as approved in Supabase."""
    try:
        data = {"status": "approved"}
        res = supabase.table("published_content").update(data).eq("id", content_id).execute()
        if not res.data:
            return HTMLResponse(content=get_html_response("Conteúdo não encontrado ou ID inválido.", False), status_code=404)
            
        return HTMLResponse(content=get_html_response("O conteúdo foi aprovado com sucesso! Estes posts estão prontos para publicação."))
    except Exception as e:
        print(f"Error approving content: {e}")
        return HTMLResponse(content=get_html_response("Ocorreu um erro ao processar a aprovação.", False), status_code=500)

@app.get("/reject/{content_id}", response_class=HTMLResponse)
async def reject_content(content_id: str):
    """Marks the content as rejected in Supabase."""
    try:
        data = {"status": "rejected"}
        res = supabase.table("published_content").update(data).eq("id", content_id).execute()
        if not res.data:
            return HTMLResponse(content=get_html_response("Conteúdo não encontrado ou ID inválido.", False), status_code=404)
            
        return HTMLResponse(content=get_html_response("O conteúdo foi rejeitado e descartado."))
    except Exception as e:
        print(f"Error rejecting content: {e}")
        return HTMLResponse(content=get_html_response("Ocorreu um erro ao processar a rejeição.", False), status_code=500)

@app.get("/", response_class=HTMLResponse)
async def root():
    return HTMLResponse(content="<h1>Algarve É Um - Webhook Server Ativo</h1>")

if __name__ == "__main__":
    import uvicorn
    # Make sure this runs on a port exposed/forwarded to WEBHOOK_BASE_URL (e.g., using ngrok in dev)
    uvicorn.run(app, host="0.0.0.0", port=8000)
