"""Estilos de produção (estudos/09-estilos.md e 12 §1).

O preset (juridico/politico/dinamico) cuida de conteúdo e conformidade; o estilo, da estética.
"""

ESTILOS = {
    "autentico": dict(
        descricao="selfie premium: acabamento invisível, fala direta",
        look="neutro", lut_intensidade=0.6, grao=0.0, halation=0.0, vinheta=0.10, barras=False,
        fundo="original", camera=dict(punch=1.08, push_in=1.05, snap=None),
        abertura="titulo_limpo", legenda="premium", lower_third=True, emojis=False,
        transicao="corte", sfx="discreto", fonte_titulo="Inter", fonte_texto="Inter",
        cor_destaque="&H00FFD24A", cor_titulo="&H00FFFFFF",
    ),
    "estudio": dict(
        descricao="advogado em estúdio premium: fundo virtual escuro com profundidade",
        look="teal_orange", lut_intensidade=0.65, grao=0.03, halation=0.12, vinheta=0.16, barras=False,
        fundo="estudio", camera=dict(punch=1.08, push_in=1.06, snap=None),
        abertura="texto_atras", legenda="premium", lower_third=True, emojis=False,
        transicao="light_leak", sfx="discreto", fonte_titulo="Playfair Display", fonte_texto="Inter",
        cor_destaque="&H004AB8E8", cor_titulo="&H00F2F2F2",
    ),
    "documental": dict(
        descricao="Vox/Johnny Harris: filme quente, papel, cartões de documento",
        look="filme_quente", lut_intensidade=0.75, grao=0.06, halation=0.10, vinheta=0.20, barras=False,
        fundo="original", camera=dict(punch=1.10, push_in=1.06, snap=None),
        abertura="cinetica_mono", legenda="premium", lower_third=True, emojis=False,
        transicao="flash", sfx="documental", fonte_titulo="DM Serif Display", fonte_texto="Courier Prime",
        cor_destaque="&H0000D5FF", cor_titulo="&H00E8F0F5",
    ),
    "noticiario": dict(
        descricao="telejornal/análise política: contraste alto, barra de notícia",
        look="noticia_frio", lut_intensidade=0.7, grao=0.0, halation=0.0, vinheta=0.10, barras=False,
        fundo="original", camera=dict(punch=1.15, push_in=1.05, snap=1.30),
        abertura="manchete", legenda="forte", lower_third=True, emojis=False,
        transicao="zoom", sfx="impacto", fonte_titulo="Bebas Neue", fonte_texto="Inter",
        cor_destaque="&H003030E6", cor_titulo="&H00FFFFFF",
    ),
    "cinematico": dict(
        descricao="comercial/filme: teal-orange forte, halation, barras animadas",
        look="teal_orange_forte", lut_intensidade=0.7, grao=0.04, halation=0.18, vinheta=0.18, barras=True,
        fundo="desfoque_profundidade", camera=dict(punch=1.06, push_in=1.08, snap=None),
        abertura="cinetica", legenda="premium", lower_third=True, emojis=False,
        transicao="light_leak", sfx="cinema", fonte_titulo="DM Serif Display", fonte_texto="Inter",
        cor_destaque="&H0060C8FF", cor_titulo="&H00FFFFFF",
    ),
    "viral": dict(
        descricao="Hormozi (versão 1): legenda palavra a palavra, emojis, snaps",
        look="vivo", lut_intensidade=0.5, grao=0.0, halation=0.0, vinheta=0.0, barras=False,
        fundo="original", camera=dict(punch=1.20, push_in=None, snap=1.40),
        abertura="titulo_caixa", legenda="viral", lower_third=False, emojis=True,
        transicao="corte", sfx="viral", fonte_titulo="Montserrat", fonte_texto="Montserrat",
        cor_destaque="&H0000E6FF", cor_titulo="&H00FFFFFF",
    ),
}

# paleta de efeitos sonoros por estilo: evento → som
SFX = {
    "discreto": {"transicao": "whoosh_suave", "cartao": "pop", "lower_third": "whoosh_suave", "climax": None, "abertura": "hit_suave"},
    "documental": {"transicao": "flash", "cartao": "papel", "lower_third": "papel", "climax": "riser", "abertura": "maquina"},
    "impacto": {"transicao": "whoosh", "cartao": "hit", "lower_third": "whoosh", "climax": "riser", "abertura": "hit"},
    "cinema": {"transicao": "whoosh_suave", "cartao": "pop", "lower_third": "whoosh_suave", "climax": "riser", "abertura": "hit"},
    "viral": {"transicao": "whoosh", "cartao": "pop", "lower_third": "pop", "climax": "riser", "abertura": "hit"},
}
