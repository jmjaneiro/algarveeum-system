import os
import resend
from dotenv import load_dotenv

load_dotenv()

def send_approval_email(curated_results: list):
    """
    Sends an HTML email with the curated content options for approval.
    Each option gets a specialized 'Aprovar' and 'Rejeitar' button that points 
    to the webhook server.
    """
    resend.api_key = os.getenv("RESEND_API_KEY")
    to_email = os.getenv("EDITOR_EMAIL")
    webhook_base = os.getenv("WEBHOOK_BASE_URL", "http://localhost:8000").rstrip("/")
    
    if not resend.api_key or not to_email:
        print("Missing RESEND_API_KEY or EDITOR_EMAIL. Skipping email dispatch.")
        return

    html_content = """
    <html>
    <head>
        <style>
            body { font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; color: #333; line-height: 1.6; }
            .container { max-width: 650px; margin: 0 auto; padding: 20px; }
            .header { background-color: #f4f4f4; padding: 15px; text-align: center; border-bottom: 3px solid #e15b22; }
            .post-box { border: 1px solid #ddd; padding: 15px; margin-bottom: 25px; border-radius: 5px; }
            .title { font-size: 18px; font-weight: bold; margin-bottom: 5px; }
            .url { font-size: 12px; color: #888; margin-bottom: 10px; display: block; }
            .score { font-weight: bold; color: #e15b22; }
            .content-section { background-color: #fafafa; padding: 10px; border-left: 3px solid #ccc; margin-top: 10px; }
            .btn { display: inline-block; padding: 10px 20px; color: #fff; text-decoration: none; border-radius: 4px; margin-right: 10px; font-weight: bold; }
            .btn-approve { background-color: #28a745; }
            .btn-reject { background-color: #dc3545; }
            .actions { margin-top: 15px; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h2>Algarve É Um - Revisão Diária de Conteúdo</h2>
                <p>Aqui estão as propostas de publicações geradas para hoje.</p>
            </div>
    """
    
    for item in curated_results:
        article = item.get('article', {})
        content = item.get('content', {})
        scoring = item.get('scoring', {})
        content_id = item.get('content_id')
        
        score = scoring.get('score', 0)
        
        approve_url = f"{webhook_base}/approve/{content_id}"
        reject_url = f"{webhook_base}/reject/{content_id}"
        
        html_content += f"""
            <div class="post-box">
                <div class="title">{article.get('title', 'Sem título')}</div>
                <a href="{article.get('url', '#')}" class="url" target="_blank">Ler Artigo Original</a>
                <p><strong>Score AI:</strong> <span class="score">{score}/100</span></p>
                
                <div class="content-section">
                    <strong>Instagram Post:</strong><br>
                    {content.get('instagram_post', '').replace(chr(10), '<br>')}
                </div>
                
                <div class="content-section">
                    <strong>Instagram Story:</strong><br>
                    {content.get('instagram_story', '').replace(chr(10), '<br>')}
                </div>
                
                <div class="content-section">
                    <strong>Facebook Post:</strong><br>
                    {content.get('facebook_post', '').replace(chr(10), '<br>')}
                </div>
                
                <div class="actions">
                    <a href="{approve_url}" class="btn btn-approve">✅ Aprovar</a>
                    <a href="{reject_url}" class="btn btn-reject">❌ Rejeitar</a>
                </div>
            </div>
        """
        
    html_content += """
        </div>
    </body>
    </html>
    """

    try:
        params = {
            "from": "Algarve É Um <onboarding@resend.dev>", # Replace with custom domain email if available
            "to": [to_email],
            "subject": f"[{len(curated_results)} Artigos] Revisão de Conteúdo - Algarve É Um",
            "html": html_content
        }
        
        res = resend.Emails.send(params)
        print(f"Email successfully sent to {to_email}. ID: {res.get('id')}")
    except Exception as e:
        print(f"Failed to send email: {e}")

if __name__ == "__main__":
    # Test layout
    print("Testing email sender module (requires valid RESEND_API_KEY)...")
    mock_data = [{
        "article": {"title": "Test Title", "url": "http://example.com"},
        "content": {
            "instagram_post": "Este é o post. #AlgarveÉUm\n\nPartilha a tua opinião!",
            "instagram_story": "Uma história forte.",
            "facebook_post": "Post maior para facebook."
        },
        "scoring": {"score": 85},
        "content_id": "test-uuid-123"
    }]
    # send_approval_email(mock_data)
