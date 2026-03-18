# Algarve É Um - Templates Library
# Reusable structures, tones, and examples for various content pillars.

CONTENT_TEMPLATES = {
    "news_reaction": {
        "description": "Reação a uma notícia atual relevante para a região.",
        "tone": "Civic, incisivo, interventivo, focado em soluções.",
        "structure": "[Headline Impactante] + [Resumo da Notícia] + [A nossa posição/Visão do Movimento] + [CTA]",
        "example": "A ferrovia no Algarve continua parada. Promessas antigas, zero ação. Nós, no Algarve É Um, exigimos mobilidade digna para quem cá vive e trabalha. Lê o artigo no link da bio e junta-te à discussão. #AlgarveÉUm #MobilidadeJá",
        "placeholders": ["{headline}", "{summary}", "{movement_stance}", "{cta}"]
    },
    "historical_fact": {
        "description": "Facto histórico sobre a identidade algarvia.",
        "tone": "Educacional, orgulhoso, enraizado.",
        "structure": "Sabias que... ? + [Facto Histórico] + [Ligação ao Presente/Identidade] + [CTA]",
        "example": "Sabias que Silves foi uma das cidades mais importantes do Al-Andalus? O nosso passado prova que o Algarve não é apenas praia, mas um território com um legado profundo. Partilha se tens orgulho nesta história! #OÚltimoReino #AlgarveÉUm",
        "placeholders": ["{historical_fact}", "{present_connection}", "{cta}"]
    },
    "community_spotlight": {
        "description": "Destaque de uma pessoa/iniciativa local de impacto.",
        "tone": "Empolgado, comunitário, inspirador.",
        "structure": "Conhece o/a [Nome]! + [O que faz] + [Impacto na Região] + [Agradecimento/CTA]",
        "example": "Conhece a Joana! Ela criou um projeto de agricultura sustentável na Serra de Monchique, ajudando a fixar jovens no interior. O verdadeiro Algarve faz-se de pessoas assim. Apoia a Joana partilhando este post. #EscolhiOAlgarve",
        "placeholders": ["{name}", "{what_they_do}", "{impact}", "{cta}"]
    },
    "regional_beauty": {
        "description": "Foco na beleza não-turística do Algarve (serra, interior, tradições).",
        "tone": "Poético, autêntico, telúrico.",
        "structure": "[Descrição Visual/Sensorial] + [Localização (Serra/Interior)] + [Reflexão sobre a nossa terra] + [CTA]",
        "example": "O cheiro a terra molhada na Serra do Caldeirão. Há um Algarve inteiro além da costa, cheio de silêncios que falam alto. Já exploraste o interior hoje? #DoOutroLadoDaSerra",
        "placeholders": ["{description}", "{location}", "{reflection}", "{cta}"]
    },
    "civic_call_to_action": {
        "description": "Chamada à ação para um assunto cívico ou urgência regional.",
        "tone": "Urgente, coletivo, mobilizador.",
        "structure": "[O Problema Urgente] + [Como nos afeta] + [O que precisamos de fazer HOJE] + [CTA Direto]",
        "example": "A falta de habitação para jovens algarvios está a esvaziar a nossa região. Não podemos aceitar. Assina a petição no nosso site e faz a tua voz contar. #AlgarveÉUm #HabitaçãoJá",
        "placeholders": ["{problem}", "{impact}", "{action}", "{cta}"]
    }
}

def get_template(template_name: str) -> dict:
    """Returns the details of a specific template."""
    return CONTENT_TEMPLATES.get(template_name, {})

def get_all_templates() -> list:
    """Returns a list of all available template names."""
    return list(CONTENT_TEMPLATES.keys())
