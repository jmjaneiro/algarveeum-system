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
        <h2 style="color: #2c3e50;">Algarve É Um - Curadoria Diária</h2>
        <p>Bom dia! Hoje o tema editorial do calendário é: <strong>{content_type}</strong></p>
        <p>A pesquisa automática das últimas 24/48h encontrou as seguintes notícias regionais. Escolhe a mais interessante para as nossas redes sociais:</p>
    """
    
    for idx, art in enumerate(articles, 1):
        c_id = art['content_id']
        # Pass calendar_id if it exists
        cal_query = f"?calendar_id={calendar_id}" if calendar_id else ""
        gen_url = f"{webhook_url}/generate/{c_id}{cal_query}"
        reject_url = f"{webhook_url}/reject/{c_id}"
        
        html_content += f"""
        <div style="background: #f9f9f9; padding: 15px; margin-bottom: 20px; border-radius: 5px; border-left: 4px solid #3498db;">
            <h3 style="margin-top: 0; color: #2980b9;">{idx}. {art['title']}</h3>
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
