# Algarve É Um - Templates Library
# Reusable structures, tones, and examples for various content pillars.

CONTENT_TEMPLATES = {
    "news_reaction": {
        "description": "Reação a uma notícia atual relevante para a região.",
        "tone": "Civic, incisivo, interventivo, focado em soluções.",
        "structure": "[Headline Impactante] + [Resumo da Notícia] + [A nossa posição/Visão do Movimento] + [CTA]",
        "example": "A ferrovia no Algarve continua parada. Promessas antigas, zero ação. Nós, no Algarve É Um, exigimos mobilidade digna para quem cá vive e trabalha. Lê o artigo no link da bio e junta-te à discussão. #AlgarveÉUm",
        "placeholders": ["{headline}", "{summary}", "{movement_stance}", "{cta}"]
    },
    "historical_fact": {
        "description": "Facto histórico sobre a identidade algarvia.",
        "tone": "Educacional, orgulhoso, enraizado.",
        "structure": "Sabias que... ? + [Facto Histórico] + [Ligação ao Presente/Identidade] + [CTA]",
        "example": "Sabias que Silves foi uma das cidades mais importantes do Al-Andalus? O nosso passado prova que o Algarve não é apenas praia, mas um território com um legado profundo. Partilha se tens orgulho nesta história! #AlgarveÉUm",
        "placeholders": ["{historical_fact}", "{present_connection}", "{cta}"]
    },
    "community_spotlight": {
        "description": "Destaque de uma pessoa/iniciativa local de impacto.",
        "tone": "Empolgado, comunitário, inspirador.",
        "structure": "Conhece o/a [Nome]! + [O que faz] + [Impacto na Região] + [Agradecimento/CTA]",
        "example": "Conhece a Joana! Ela criou um projeto de agricultura sustentável na Serra de Monchique, ajudando a fixar jovens no interior. O verdadeiro Algarve faz-se de pessoas assim. Apoia a Joana partilhando este post. #AlgarveÉUm",
        "placeholders": ["{name}", "{what_they_do}", "{impact}", "{cta}"]
    },
    "regional_beauty": {
        "description": "Foco na beleza natural do Algarve (serra, interior, tradições e património ambiental).",
        "tone": "Poético, autêntico, telúrico.",
        "structure": "[Descrição Visual/Sensorial] + [Localização] + [Reflexão sobre a nossa terra] + [CTA]",
        "example": "O cheiro a terra molhada na Serra do Caldeirão. Há um Algarve inteiro além da costa, cheio de silêncios que falam alto. Já exploraste o interior hoje? #AlgarveÉUm",
        "placeholders": ["{description}", "{location}", "{reflection}", "{cta}"]
    },
    "civic_call_to_action": {
        "description": "Chamada à ação para um assunto cívico ou urgência regional.",
        "tone": "Urgente, coletivo, mobilizador.",
        "structure": "[O Problema Urgente] + [Como nos afeta] + [O que precisamos de fazer HOJE] + [CTA Direto]",
        "example": "A falta de habitação para jovens algarvios está a esvaziar a nossa região. Não podemos aceitar. Assina a petição no nosso site e faz a tua voz contar. #AlgarveÉUm",
        "placeholders": ["{problem}", "{impact}", "{action}", "{cta}"]
    },
    "practical_utility": {
        "description": "Conteúdo útil imediato para quem vive no Algarve (avisos, mobilidade, concursos, bolsas).",
        "tone": "Prático, solidário, informativo e direto.",
        "structure": "[🚨 AVISO / UTILIDADE] + [A Informação Central] + [Impacto na Rotina/Benefício] + [CTA para Partilhar]",
        "example": "🚨 Alterações nos horários da EVA e da CP a partir de amanhã! Se dependes dos autocarros e comboios regionais, fica atento às reduções nas linhas do sotavento. Partilha com quem precisa de saber. #AlgarveÉUm",
        "placeholders": ["{warning_tag}", "{core_info}", "{impact}", "{cta}"]
    },
    "cultural_entertainment": {
        "description": "Eventos culturais locais, desportos, gastronomia autêntica e artistas algarvios.",
        "tone": "Leve, celebrativo, bairrista com orgulho.",
        "structure": "[Apresentação do Evento/Sabor/Artista] + [O que torna aquilo único e algarvio] + [Detalhes (quando, onde)] + [CTA Interativo]",
        "example": "Hoje o destaque vai para a banda local XYZ, que funde o acordeão algarvio com música eletrónica! Fomos apoiá-los ao concerto gratuito de Faro. Conheces mais artistas locais que devíamos ouvir? Deixa nos comentários. #AlgarveÉUm",
        "placeholders": ["{intro}", "{uniqueness}", "{details}", "{cta}"]
    },
    "interactive_conversational": {
        "description": "Perguntas e debates leves sobre memória, cultura local e costumes regionais.",
        "tone": "Curioso, familiar e de proximidade.",
        "structure": "[Pergunta ou Debatível Direto] + [Breve Contexto Afetivo] + [A nossa posição humilde] + [CTA forte para Comentar]",
        "example": "Cataplana de peixe ou de marisco? Cada concelho tem o seu segredo, e nós queremos saber o teu! De onde és e qual é o ingrediente secreto que não pode faltar na mesa algarvia de domingo? #AlgarveÉUm",
        "placeholders": ["{question}", "{context}", "{movement_view}", "{cta}"]
    }
}

def get_template(template_name: str) -> dict:
    """Returns the details of a specific template."""
    return CONTENT_TEMPLATES.get(template_name, {})

def get_all_templates() -> list:
    """Returns a list of all available template names."""
    return list(CONTENT_TEMPLATES.keys())
