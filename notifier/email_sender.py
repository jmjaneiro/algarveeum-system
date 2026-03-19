import os
import resend
from dotenv import load_dotenv

load_dotenv()

def send_raw_articles_email(articles: list, calendar_id: str, content_type: str):
    """
    Sends an email to the editor with raw articles from Tavily.
    The editor clicks 'Gerar Post' to trigger Claude processing via the webhook.
    """
    resend.api_key = os.getenv("RESEND_API_KEY")
    editor_email = os.getenv("EDITOR_EMAIL")
    webhook_url = os.getenv("WEBHOOK_BASE_URL", "http://localhost:10000").rstrip("/")
    
    if not resend.api_key or not editor_email:
        print("RESEND_API_KEY or EDITOR_EMAIL missing from .env")
        return

    html_content = f"""
    <html>
      <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
        <h2 style="color: #2c3e50;">Algarve É Um - Jornal Diário</h2>
        <p>Olá! Abaixo tens a lista bruta de <strong>todas as notícias relevantes das últimas 48h</strong> recolhidas diretamente dos jornais regionais, processadas para garantir variedade de fontes.</p>
        <p>O teu papel de Editor Principal: lê as manchetes cruas e escolhe a notícia com melhor impacto. Clica em <strong>Gerar Post</strong> para a Inteligência Artificial escrever a Story e o FB Post.</p>
        <hr style="border: 0; border-top: 1px solid #eee; margin: 25px 0;">
    """
    
    for idx, art in enumerate(articles, 1):
        c_id = art['content_id']
        cal_query = f"?calendar_id={calendar_id}" if calendar_id else ""
        gen_url = f"{webhook_url}/generate/{c_id}{cal_query}"
        reject_url = f"{webhook_url}/reject/{c_id}"
        
        # Meta Dados Editoriais do Claude
        meta = art.get('editorial_metadata', {})
        meta_html = ""
        if meta:
            score = meta.get('relevance_score', '?')
            urgency = meta.get('urgency', '?').upper()
            angle = meta.get('content_angle', '')
            dimensions = ", ".join(meta.get('content_dimensions', []))
            
            meta_html = f"""
            <div style="margin: 12px 0; padding: 12px; background-color: #ecf0f1; border-radius: 4px; font-size: 0.9em; border-left: 3px solid #e67e22;">
                <strong>Nota IA:</strong> {score}/10 | <strong>Urgência:</strong> {urgency} <br/>
                <strong style="color:#e67e22">Ângulo de Publicação:</strong> {angle} <br/>
                <span style="color:#7f8c8d; font-size:0.85em;">Dimensões: {dimensions}</span>
            </div>
            """
        
        html_content += f"""
        <div style="background: #f9f9f9; padding: 15px; margin-bottom: 20px; border-radius: 5px; border-left: 4px solid #3498db;">
            <h3 style="margin-top: 0; color: #2980b9;">{idx}. {art['title']}</h3>
            {meta_html}
            <p style="font-size: 0.9em; color: #666;">{art['summary']}</p>
            <p><a href="{art['url']}" target="_blank" style="color: #3498db; text-decoration: none;">Ler Notícia Original 🔗</a></p>
            <div style="margin-top: 15px;">
                <a href="{gen_url}" target="_blank" style="background-color: #2ecc71; color: white; padding: 10px 15px; text-decoration: none; border-radius: 3px; font-weight: bold; display: inline-block;">Gerar Post com IA 🤖</a>
                <a href="{reject_url}" target="_blank" style="background-color: #e74c3c; color: white; padding: 10px 15px; text-decoration: none; border-radius: 3px; font-weight: bold; display: inline-block; margin-left: 10px;">Descartar 🗑️</a>
            </div>
        </div>
        """
        
    html_content += """
        <p style="font-size: 0.8em; color: #999; margin-top: 30px;">Gerado automaticamente pelo sistema Algarve É Um.</p>
      </body>
    </html>
    """
    
    params = {
        "from": "Algarve E Um <onboarding@resend.dev>",
        "to": [editor_email],
        "subject": f"[{content_type}] Escolhe as Notícias de Hoje para Gerar Posts",
        "html": html_content
    }
    
    try:
        email = resend.Emails.send(params)
        print(f"Email sent successfully! ID: {email['id']}")
    except Exception as e:
        print(f"Error sending email via Resend: {e}")
