"""Conformidade automática (semáforo) de qualquer peça antes de publicar.

Checa texto (legenda, roteiro falado, slides), metadados da peça (data, impulsionamento, uso de IA, música,
crédito de terceiro) e o perfil (advocacia × político). Base normativa e fontes: registro R13 e skill
`conformidade`. É uma **primeira barreira**, não substitui a leitura humana: o resultado amarelo/vermelho
sempre vai para o usuário com o motivo e a norma.

Uso:
    from redes.nucleo import conformidade
    r = conformidade.checar(texto, perfil, peca={"data": "2026-10-20", "impulsionar": True, "usa_ia": False})
    r["sinal"]  # "verde" | "amarelo" | "vermelho"
"""
import re
import unicodedata
from datetime import date

# ------------------------------------------------------------------ calendário eleitoral 2026 (R13.01-03)
ELEICAO_2026 = {
    "propaganda_inicio": date(2026, 8, 16),
    "turnos": [date(2026, 10, 4), date(2026, 10, 25)],
    "impulsionamento_fim": [date(2026, 10, 1), date(2026, 10, 22)],
    "retomada_2turno": date(2026, 10, 5),
}


def _norm(t):
    t = unicodedata.normalize("NFKD", t or "").encode("ascii", "ignore").decode().lower()
    return re.sub(r"\s+", " ", t)


def _achar(padroes, texto):
    return sorted({m.group(0) for p in padroes for m in re.finditer(p, texto)})


# ------------------------------------------------------------------ regras de texto
OAB_VERMELHO = {
    "promessa de resultado (Prov. 205/2021 arts. 4º §2º e 6º; CED art. 42)": [
        r"\bgarant(o|imos)\b", r"\b100 ?% (de )?(exito|sucesso|garantid|aprovad)", r"causa ganha", r"(resultado|exito|sucesso|vitoria) garantid", r"voce vai ganhar",
        r"\bsem risco\b"],
    "captação/mercantilização (Prov. 205/2021 art. 5º §3º; CED arts. 39-42)": [
        r"\bcontrate\b", r"ligue (ja|agora)", r"consulta (gratis|gratuita)", r"\bpreco(s)?\b", r"r\$ ?\d",
        r"\bdesconto\b", r"\bpromocao\b", r"\borcamento\b", r"(chame|chama|me chame).{0,20}(whats|direct|dm).{0,30}(contrat|resolver|caso)",
        r"honorarios (a partir|por apenas|baratos)"],
}
OAB_AMARELO = {
    "autopromoção/superlativo (Prov. 205/2021 art. 4º)": [
        r"melhor(es)? advogad", r"maior escritorio", r"\bn(o|º|°)? ?1\b", r"\bimbativel\b", r"\bnumero um\b"],
    "título de especialista: só com especialização formal (CED)": [r"\bespecialista\b"],
    "ostentação (Prov. 205/2021 art. 6º, par. ún.)": [
        r"\b(minha|meu) (ferrari|porsche|lamborghini|mansao|iate|lancha|helicoptero)", r"\bcarro novo\b",
        r"\b(primeira classe|business class)\b"],
    "CTA 'comente X que te mando no direct' pode virar captação (R15; Prov. 205/2021 art. 5º): envie só material "
    "informativo, sem oferta de serviço": [
        r"(coment\w*|digit\w*|escrev\w*).{0,40}(mando|envio|enviarei|mandarei|te passo).{0,25}(dm|direct|inbox|privado|whats)"],
    "caso concreto / cliente (Prov. 205/2021 art. 6º, par. ún.; sigilo)": [
        r"\bmeu cliente\b", r"\bminha cliente\b", r"\bganhei (a|uma) (causa|acao)\b", r"consegui (para|pro|pra) (o|a|meu|minha)"],
}
TSE_VOTO = [r"\bvote (em|no|na)\b", r"\bvotem\b", r"peco (o )?seu voto", r"\bnumero \d{2,5}\b.*\burna\b",
            r"\bconfirma\b.*\b\d{2,5}\b"]
LGPD = {
    "CPF": r"\b\d{3}\.?\d{3}\.?\d{3}-?\d{2}\b",
    "CNPJ": r"\b\d{2}\.?\d{3}\.?\d{3}/?\d{4}-?\d{2}\b",
    "nº de processo (CNJ)": r"\b\d{7}-?\d{2}\.?\d{4}\.?\d\.?\d{2}\.?\d{4}\b",
    "telefone": r"(\(?\b\d{2}\)?\s?)?\b9?\d{4}-?\d{4}\b",
    "e-mail": r"\b[\w.+-]+@[\w-]+\.[\w.]+\b",
}
ROTULO_IA = [r"(gerad|alterad|criad|produzid|manipulad)[oa]s? (com|por) (ia|inteligencia artificial)",
             r"conteudo (sintetico|fabricado)"]


def checar(texto, perfil=None, peca=None):
    """Devolve {"sinal", "itens": [{"nivel", "regra", "trechos", "acao"}], "resumo"}."""
    perfil = perfil or {}
    peca = peca or {}
    tipo = perfil.get("tipo", "advocacia")
    t = _norm(texto)
    itens = []

    def add(nivel, regra, trechos=(), acao=""):
        itens.append({"nivel": nivel, "regra": regra, "trechos": list(trechos), "acao": acao})

    if tipo in ("advocacia", "juridico"):
        for regra, pads in OAB_VERMELHO.items():
            if (achou := _achar(pads, t)):
                add("vermelho", regra, achou, "reescrever: conteúdo informativo, sem oferta, preço ou promessa")
        for regra, pads in OAB_AMARELO.items():
            if (achou := _achar(pads, t)):
                if "especialista" in regra and perfil.get("especialista_titulo"):
                    continue
                add("amarelo", regra, achou, "rever com sobriedade/discrição")

    # ---------------- eleitoral (perfil político)
    d = peca.get("data")
    d = date.fromisoformat(d) if isinstance(d, str) else d
    if tipo == "politico":
        e = ELEICAO_2026
        if d and d < e["propaganda_inicio"] and (achou := _achar(TSE_VOTO, t)):
            add("vermelho", "propaganda antecipada: pedido explícito de voto antes de 16/08 (Lei 9.504 art. 36-A)", achou,
                "retirar o pedido de voto (pré-campanha pode falar de ideias e qualidades)")
        if d and d in e["turnos"]:
            add("vermelho", "dia da eleição: publicar conteúdo novo ou impulsionar é crime (Lei 9.504 art. 39 §5º IV)",
                [d.isoformat()], "agendar para depois do encerramento da votação")
        if d and peca.get("impulsionar"):
            fora = (d > e["impulsionamento_fim"][0] and d < e["retomada_2turno"]) or d > e["impulsionamento_fim"][1]
            if fora:
                add("vermelho", "impulsionamento fora do prazo (1º turno até 01/10; 2º turno até 22/10/2026 — Res. 23.760)",
                    [d.isoformat()], "publicar sem impulsionar")
            if not re.search(r"propaganda eleitoral", t):
                add("amarelo", "impulsionamento eleitoral deve identificar 'Propaganda Eleitoral' e o CNPJ do contratante "
                    "(Res. 23.610)", acao="incluir a identificação no anúncio")
        if peca.get("usa_ia") and d:
            for turno in e["turnos"]:
                if 0 <= (turno - d).days <= 3 or 0 <= (d - turno).days <= 1:
                    add("vermelho", "conteúdo novo com IA na janela de 72 h antes a 24 h depois do pleito (Res. 23.755/2026)",
                        [d.isoformat()], "publicar sem elementos gerados por IA")
    if peca.get("usa_ia") and not _achar(ROTULO_IA, t):
        nivel = "vermelho" if tipo == "politico" else "amarelo"
        add(nivel, "uso de IA sem rótulo explícito (Res. TSE 23.732/2024 art. 9-B; boa prática nas plataformas)",
            acao="incluir 'Conteúdo gerado/alterado com IA' na peça e na legenda")
    if peca.get("ia_rosto_voz_real"):
        add("vermelho", "IA alterando rosto/voz de pessoa real (deepfake: vedado em propaganda — Res. 23.732; "
            "risco de dano à imagem — Súmula 403/STJ)", acao="não usar")

    # ---------------- LGPD e terceiros
    bruto = texto or ""
    for nome, pad in LGPD.items():
        achados = re.findall(pad, bruto)
        if nome == "telefone":
            achados = [a for a in re.finditer(pad, bruto) if len(re.sub(r"\D", "", a.group(0))) >= 10]
            achados = [a.group(0) for a in achados]
        if nome == "e-mail" and perfil.get("email_publico"):
            achados = [a for a in achados if a != perfil["email_publico"]]
        if achados:
            add("amarelo", f"dado pessoal no texto: {nome} (LGPD)", [str(a) for a in achados][:5],
                "anonimizar, salvo dado público do próprio perfil")
    if peca.get("musica") and not peca.get("musica_licenca"):
        add("amarelo", "música sem licença declarada (Lei 9.610/98; use biblioteca da rede ou licença paga)",
            [str(peca["musica"])], "declarar a licença ou trocar a faixa")
    if peca.get("terceiro") and not peca.get("credito"):
        add("amarelo", "conteúdo de terceiro sem crédito (LDA art. 46, III: citação com indicação da fonte)",
            acao="incluir @autor, data e rede")

    nivel = "vermelho" if any(i["nivel"] == "vermelho" for i in itens) else \
        "amarelo" if any(i["nivel"] == "amarelo" for i in itens) else "verde"
    return {"sinal": nivel, "itens": itens,
            "resumo": {"vermelho": "NÃO publicar sem corrigir", "amarelo": "publicar só depois de revisar os pontos",
                       "verde": "nenhum alerta automático (revisão humana continua necessária)"}[nivel]}


def formatar(r):
    ic = {"verde": "🟢", "amarelo": "🟡", "vermelho": "🔴"}
    linhas = [f"{ic[r['sinal']]} {r['sinal'].upper()}: {r['resumo']}"]
    for i in r["itens"]:
        tr = f" — trechos: {', '.join(i['trechos'])}" if i["trechos"] else ""
        linhas.append(f"  {ic[i['nivel']]} {i['regra']}{tr}" + (f"\n      → {i['acao']}" if i["acao"] else ""))
    return "\n".join(linhas)
