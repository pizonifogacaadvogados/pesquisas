"""Regras de edição extraídas dos estudos (ver estudos/01 a 05).

Tudo que é "gosto editorial" fica aqui, para ajustar sem mexer no resto do código.
"""
import re
import unicodedata

# ---------------------------------------------------------------- presets (E3 §8)
PRESETS = {
    "dinamico": dict(
        pausa_max=0.30,          # corta silêncio acima disso (s)
        folga=0.06,              # mantém em volta da fala (s)
        punch=1.20,              # escala do punch-in alternado
        snap=1.40,               # escala do snap zoom
        snap_intervalo=7.0,      # mínimo entre snap zooms (s)
        emoji_intervalo=4.5,     # mínimo entre emojis (s)
        emoji_dur=1.2,
        palavras_legenda=3,
        caixa_alta=True,
        cor_atual="&H0000E6FF",  # amarelo (ASS = &HAABBGGRR)
        cor_destaque="&H0088FF2B",  # verde
        zoom_lento=True,
        sfx=True,
        sfx_fortes=True,         # riser/hit/buzzer
        emojis_bloqueados=set(),
    ),
    "juridico": dict(
        pausa_max=0.40,
        folga=0.08,
        punch=1.10,
        snap=1.22,
        snap_intervalo=12.0,
        emoji_intervalo=10.0,
        emoji_dur=1.4,
        palavras_legenda=4,
        caixa_alta=False,
        cor_atual="&H0000D7FF",  # amarelo-ouro
        cor_destaque="&H00FFB04A",  # azul claro
        zoom_lento=True,
        sfx=True,
        sfx_fortes=False,
        # Provimento 205/2021: nada que remeta a dinheiro/resultado/ostentação
        emojis_bloqueados={"💰", "🤑", "🏆", "💸", "🥇"},
    ),
    "politico": dict(
        pausa_max=0.30,
        folga=0.06,
        punch=1.18,
        snap=1.45,
        snap_intervalo=6.0,
        emoji_intervalo=6.5,
        emoji_dur=1.1,
        palavras_legenda=3,
        caixa_alta=True,
        cor_atual="&H0000E6FF",  # amarelo
        cor_destaque="&H003030FF",  # vermelho
        zoom_lento=True,
        sfx=True,
        sfx_fortes=True,
        emojis_bloqueados=set(),
    ),
}

# ---------------------------------------------------------------- vícios (E2 §2.3)
VICIOS_SEMPRE = {"éé", "ééé", "hã", "hãa", "hum", "humm", "hmm", "ahn", "aham", "uh", "um", "eh", "ehh", "ãh", "ããh"}
# só são vício quando isolados por pausa ou alongados ("é..." vs "é de sete dias")
VICIOS_CONTEXTO = {"é", "né", "tipo", "assim", "então", "bom", "enfim", "ah", "aí"}

# ---------------------------------------------------------------- gancho (E2 §3)
GATILHOS_GANCHO = [
    r"\bvoc[eê] sabia\b", r"\bningu[eé]m\b", r"\bnunca\b", r"\bjamais\b", r"\berro\b", r"\berrado\b",
    r"\bproibid", r"\bilegal\b", r"\bcuidado\b", r"\baten[cç][aã]o\b", r"\bdireito\b",
    r"\bn[aã]o pode\b", r"\bverdade\b", r"\bmentira\b", r"\bmito\b", r"\bsegredo\b", r"\bpior\b",
    r"\bimportante\b", r"\bgr[aá]tis\b", r"\bperder\b", r"\bganhar\b", r"\burgente\b", r"\bescândalo\b",
    r"\bcontradi", r"\bdisse\b", r"\bvergonha\b", r"\babsurdo\b", r"\bpor que\b",
]
REGANCHOS = [r"\bmas\b", r"\bs[oó] que\b", r"\bagora\b", r"\be o pior\b", r"\bpresta aten", r"\bolha s[oó]\b"]

# ---------------------------------------------------------------- emojis + SFX (E3 §3)
# radical (sem acento, minúsculo) -> (emoji, som)
LEXICO = [
    ("dinheir", "💰", "pop"), ("reais", "💰", "pop"), ("pagar", "💸", "pop"), ("pagament", "💸", "pop"),
    ("salario", "💵", "pop"), ("multa", "🧾", "pop"), ("imposto", "🧾", "pop"),
    ("lei", "⚖️", "pop"), ("justica", "⚖️", "pop"), ("juiz", "⚖️", "pop"), ("tribunal", "🏛️", "pop"),
    ("stf", "🏛️", "pop"), ("congresso", "🏛️", "pop"), ("governo", "🏛️", "pop"), ("artigo", "📜", "pop"),
    ("contrato", "📄", "pop"), ("document", "📄", "pop"), ("processo", "📂", "pop"),
    ("proibid", "🚫", "buzzer"), ("ilegal", "🚫", "buzzer"), ("nao pode", "🚫", "buzzer"),
    ("errad", "❌", "buzzer"), ("erro", "❌", "buzzer"), ("mentira", "❌", "buzzer"), ("mito", "❌", "buzzer"),
    ("cert", "✅", "ding"), ("verdade", "✅", "ding"), ("direito", "✅", "ding"),
    ("cuidado", "⚠️", "pop"), ("atencao", "⚠️", "pop"), ("alerta", "⚠️", "pop"), ("perig", "⚠️", "pop"),
    ("prazo", "⏳", "pop"), ("dias", "⏳", "pop"), ("tempo", "⏰", "pop"), ("hoje", "⏰", "pop"),
    ("ideia", "💡", "ding"), ("dica", "💡", "ding"), ("segredo", "🤫", "pop"),
    ("absurdo", "😱", "hit"), ("chocante", "😱", "hit"), ("escandalo", "😱", "hit"), ("vergonha", "🤦", "pop"),
    ("olha", "👀", "pop"), ("veja", "👀", "pop"), ("fogo", "🔥", "whoosh"), ("viral", "🔥", "whoosh"),
    ("casa", "🏠", "pop"), ("imovel", "🏠", "pop"), ("aluguel", "🏠", "pop"), ("carro", "🚗", "pop"),
    ("celular", "📱", "pop"), ("internet", "🌐", "pop"), ("compra", "🛒", "pop"), ("loja", "🛒", "pop"),
    ("trabalh", "💼", "pop"), ("empresa", "🏢", "pop"), ("patrao", "💼", "pop"), ("chefe", "💼", "pop"),
    ("familia", "👨‍👩‍👧", "pop"), ("filho", "👶", "pop"), ("divorcio", "💔", "pop"), ("casament", "💍", "pop"),
    ("saude", "🏥", "pop"), ("plano de saude", "🏥", "pop"), ("aposentad", "👴", "pop"), ("inss", "👴", "pop"),
    ("policia", "🚓", "pop"), ("preso", "🚨", "hit"), ("crime", "🚨", "hit"), ("voto", "🗳️", "pop"),
    ("eleic", "🗳️", "pop"), ("candidat", "🗳️", "pop"), ("brasil", "🇧🇷", "pop"),
    ("ganh", "🏆", "ding"), ("vitoria", "🏆", "ding"), ("pergunta", "🤔", "pop"), ("pensao", "👶", "pop"),
]

# ---------------------------------------------------------------- alertas legais (E5)
ALERTAS_OAB = [
    (r"\bhonor[aá]rio", "Menção a honorários (Prov. 205/2021, art. 3º §1º)"),
    (r"\bgr[aá]tis\b|\bgratuit|\bdesconto", "Gratuidade/desconto como captação (Prov. 205/2021)"),
    (r"\bvai ganhar\b|\bgaranti|\bcausa ganha\b|\b100%", "Promessa de resultado (Prov. 205/2021)"),
    (r"\bo melhor\b|\bo [uú]nico\b|\bnúmero 1\b|\bespecialista\b", "Autoengrandecimento/especialidade sem título (Prov. 205/2021)"),
    (r"\bme chama\b|\bchama no direct\b|\bcontrate\b|\bentre em contato\b", "Possível captação de clientela (Prov. 205/2021)"),
    (r"\bmeu cliente\b|\bganhei (a|uma) a[cç][aã]o\b|\bconsegui na justi", "Caso concreto/resultado obtido (Prov. 205/2021, art. 5º §3º)"),
]
ALERTAS_TSE = [
    (r"\bvote\b|\bvotem\b|\bn[aã]o vote\b", "Pedido de voto: verificar período e forma de propaganda (Res. TSE 23.610/2019)"),
    (r"\bintelig[eê]ncia artificial\b|\bIA\b", "Se houver conteúdo gerado por IA: rótulo obrigatório (art. 9º-B)"),
]


def sem_acento(s):
    return "".join(c for c in unicodedata.normalize("NFD", s.lower()) if unicodedata.category(c) != "Mn")


def limpa(w):
    return re.sub(r"[^\wÀ-ÿ%-]", "", w.lower())


def emoji_para(texto_janela, so_compostos=False):
    """Primeiro (emoji, som) do léxico que aparece no texto (sem acento).

    so_compostos=True considera só expressões de várias palavras ("nao pode"), usado
    ao olhar a palavra atual + a seguinte, para o emoji cair na palavra certa.
    """
    t = " " + sem_acento(texto_janela) + " "
    for radical, emoji, som in LEXICO:
        if so_compostos and " " not in radical:
            continue
        if re.search(r"\b" + re.escape(radical), t):
            return emoji, som
    return None


def eh_gatilho(texto, so_compostos=False):
    t = texto.lower()
    return sum(1 for g in GATILHOS_GANCHO if (not so_compostos or " " in g) and re.search(g, t))


def alertas(texto, preset):
    regras = list(ALERTAS_OAB) if preset == "juridico" else []
    if preset == "politico":
        regras += ALERTAS_TSE
    if preset == "juridico":
        regras += ALERTAS_TSE[1:]
    return [msg for padrao, msg in regras if re.search(padrao, texto, re.I)]
