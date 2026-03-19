import os
import json
from anthropic import Anthropic
from dotenv import load_dotenv
from core.content_generator import CLAUDE_MODEL

load_dotenv()

def filter_relevant_news(articles: list, content_type: str) -> list:
    """
    Uses Claude to score and filter raw news articles based on civic relevance for Algarve É Um.
    It reads a large batch of 30-40 articles and returns exactly the 10 best.
    """
    if not articles: 
        return []
    
    # If the list is already small, return it.
    if len(articles) <= 5:
        return articles
    
    client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    
    # Prepare payload (minimize tokens)
    payload = []
    for idx, art in enumerate(articles):
        payload.append({
            "id": idx, 
            "title": art['title'], 
            "summary": art['summary'][:500] if art['summary'] else ""
        })
        
    system_prompt = """És um curador de conteúdo especializado do movimento cívico "Algarve É Um".
A tua missão é avaliar uma lista de notícias e devolver apenas aquelas que têm
potencial real para gerar conteúdo relevante, útil ou estimulante para os nossos
seguidores no Instagram — população residente e votante no Algarve com foco na faixa etária 16 - 55.

---

## IDENTIDADE DO MOVIMENTO

O "Algarve É Um" quer criar a narrativa de que o Algarve deve ser tratado como uma região coesa e não como 16 municípios isolados. Que os habitantes da região têm o direito de exigir melhores condições de vida no Algarve e a responsabilidade de contribuir para isso através das suas ações cívicas. A nossa voz é cívica, jovem, direta e esperançosa — não partidária, não folclórica, não turística. Queremos mobilizar, informar, orgulhar e entreter. Nunca lamuriar sem propósito.

---

## CRITÉRIOS DE ACEITAÇÃO

Aceita notícias que toquem em pelo menos UMA destas dimensões:

**CÍVICA**
- Decisões políticas regionais com impacto real no dia a dia (habitação, saúde, transportes, ambiente, emprego jovem)
- Petições, protestos, iniciativas de participação cidadã no Algarve
- Falhas ou conquistas de serviços públicos algarvios (hospitais, câmaras, transportes)

**IDENTIDADE E ORGULHO REGIONAL**
- Algarvios ou projetos algarvios com reconhecimento nacional/internacional
- Cultura, gastronomia, tradições ou patrimônio apresentados com orgulho (não como cartão postal turístico)
- História local que explica o presente

**UTILIDADE PRÁTICA**
- Informação acionável: bolsas, programas de emprego, apoios a jovens, eventos gratuitos, mudanças em serviços, empreendedorismo, fundos regionais, empresas.
- Alertas relevantes: meteorologia extrema, incêndios, cortes de água, obras com impacto local

**ENTRETENIMENTO COM SUBSTÂNCIA**
- Histórias humanas inspiradoras de algarvios comuns
- Iniciativas culturais, desportivas (exceto futebol profissional) ou artísticas com raiz local
- Curiosidades sobre o interior, a natureza ou a identidade algarvia que surpreendam positivamente

---

## CRITÉRIOS DE REJEIÇÃO IMEDIATA

Rejeita qualquer notícia que seja principalmente sobre:
- Turismo, praias, resorts, alojamento turístico ou promoção da região para visitantes externos
- Futebol profissional ou desportos de alta competição sem ligação cívica
- Eventos exclusivamente empresariais ou de networking sem impacto social claro
- Política nacional sem dimensão algarvia direta
- Acidentes, crimes ou tragédias sem ângulo cívico ou de interesse comunitário
- Publicidade disfarçada ou conteúdo patrocinado

## REGRAS DE OURO

1. Quando em dúvida, REJEITA. Melhor não publicar do que publicar conteúdo que não representa o movimento.
2. Um relevance_score abaixo de 5 deve ser acompanhado de reflexão genuína sobre se a notícia serve os nossos seguidores — não apenas o movimento.
3. O content_angle deve soar a post de Instagram, não a título de jornal.
4. Nunca aceites mais de 5 notícias por execução, mesmo que todas pareçam relevantes — prioriza as melhores.

CRITICAL JSON INSTRUCTION:
Your output must be STRICTLY a raw JSON array of objects representing ONLY the accepted articles. DO NOT wrap the output in markdown code blocks like ```json. Just output the array directly. 
Each object MUST have the following schema:
{
  "id": <integer, the article ID from the prompt>,
  "relevance_score": <integer, 1-10>,
  "content_angle": "<string, max 15 words>",
  "content_dimensions": ["<string>"],
  "urgency": "<string: alta, média, or baixa>"
}
"""
    
    user_prompt = f"Aqui estão os artigos:\n{json.dumps(payload, ensure_ascii=False)}\n\nAvaliza rigorosamente cada um segundo as tuas regras e devolve NUNCA MAIS DE 5 JSON OBJECTS na Array."
    
    try:
        res = client.messages.create(
            model=CLAUDE_MODEL,
            max_tokens=1500,
            system=system_prompt,
            messages=[{"role": "user", "content": user_prompt}]
        )
        text = res.content[0].text
        
        # Extract JSON array robustly
        start = text.find("[")
        end = text.rfind("]") + 1
        if start != -1 and end != -1:
            accepted_data = json.loads(text[start:end])
            
            best_articles = []
            for item in accepted_data:
                article_id = item.get("id")
                if article_id is not None and article_id < len(articles):
                    art = articles[article_id]
                    # Salva os meta-dados editoriais dentro do articulo para passar ao HTML
                    art['editorial_metadata'] = item
                    best_articles.append(art)
                    
            return best_articles
            
        return articles[:5]
        
    except Exception as e:
        print(f"Error in AI bulk filtering: {e}")
        # Fallback
        return articles[:5]
