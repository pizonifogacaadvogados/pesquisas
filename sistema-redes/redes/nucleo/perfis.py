"""Perfis: cada conta/cliente atendido pelo sistema (escritório, advogado, político, mandato, campanha).

Um perfil concentra tudo o que se repete em cada peça: identidade visual, assinatura, tom, pilares de conteúdo,
redes e frequência, regras (OAB ou TSE), hashtags base e as preferências de edição. Os módulos de vídeo, foto
e gestão leem o perfil para não precisar repetir parâmetros.

Arquivo: `perfis/<id>.json`. Crie com `python -m redes perfil criar <id> --tipo advocacia|politico`.
"""
import copy
import json
import re

from . import caminhos

MODELOS = {
    "advocacia": {
        "id": "", "nome": "Escritório Exemplo Advocacia", "tipo": "advocacia",
        "assinatura": {"nome": "Dra. Ana Souza", "cargo": "Advogada", "registro": "OAB/RS 00.000",
                       "handle": "@escritorio.exemplo"},
        "especialista_titulo": False,
        "email_publico": "",
        "preset_video": "juridico",          # regras de corte/ritmo (nucleo/regras.PRESETS)
        "estilo_video": "auto",              # video/estilos.ESTILOS ou "auto"
        "identidade_foto": "juridico_classico",   # foto/html.IDENTIDADES
        "cores": {"primaria": "#14213D", "destaque": "#B08D57", "fundo": "#F6F2EA"},
        "fundo_foto": "",                    # foto real do escritório (vira fundo do estúdio virtual)
        "foto_autor": "",                    # retrato para capas, carrosséis e thumbnails
        "tom": "didático, sóbrio, próximo; frases curtas; sem juridiquês; sem promessa",
        "pilares": [
            {"nome": "Direitos do dia a dia", "peso": 0.4, "exemplos": ["consumidor", "trabalho", "família"]},
            {"nome": "Mitos e verdades", "peso": 0.2},
            {"nome": "Mudanças na lei e decisões", "peso": 0.2},
            {"nome": "Bastidores e autoridade (sem ostentação)", "peso": 0.2},
        ],
        "redes": {
            "instagram": {"handle": "@escritorio.exemplo", "semana": {"reels": 3, "carrossel": 2, "post": 1, "stories": 5}},
            "tiktok": {"handle": "@escritorio.exemplo", "semana": {"video": 3}},
            "youtube": {"handle": "@escritorioexemplo", "semana": {"shorts": 3, "video": 0}},
            "linkedin": {"handle": "escritorio-exemplo", "semana": {"documento": 1, "video": 1}},
        },
        "horarios": {"seg-sex": ["12:00", "19:00"], "sab": ["10:00"]},
        "hashtags_base": ["#direito", "#advocacia"],
        "cta_permitidos": ["Salve para consultar depois", "Envie para quem precisa saber disso",
                           "Comente sua dúvida (respondo em vídeo)"],
        "musica_biblioteca": "",
        "observacoes": "",
    },
    "politico": {
        "id": "", "nome": "Mandato Exemplo", "tipo": "politico",
        "assinatura": {"nome": "Fulano de Tal", "cargo": "Vereador", "registro": "", "handle": "@fulano"},
        "email_publico": "",
        "candidato": True, "cnpj_campanha": "",
        "preset_video": "politico", "estilo_video": "auto", "identidade_foto": "politico_sobrio",
        "cores": {"primaria": "#0B1F3A", "destaque": "#1F6FEB", "fundo": "#FFFFFF"},
        "fundo_foto": "", "foto_autor": "",
        "tom": "direto, humano, propositivo; histórias reais; nada de ataque pessoal sem prova",
        "pilares": [
            {"nome": "Propostas explicadas", "peso": 0.3},
            {"nome": "Prestação de contas / trabalho", "peso": 0.25},
            {"nome": "Bastidores e pessoas", "peso": 0.25},
            {"nome": "Resposta e checagem", "peso": 0.2},
        ],
        "redes": {
            "instagram": {"handle": "@fulano", "semana": {"reels": 5, "carrossel": 2, "post": 2, "stories": 7}},
            "tiktok": {"handle": "@fulano", "semana": {"video": 5}},
            "youtube": {"handle": "@fulano", "semana": {"shorts": 5}},
            "kwai": {"handle": "@fulano", "semana": {"video": 3}},
            "facebook": {"handle": "fulano", "semana": {"reels": 3, "post": 2}},
            "whatsapp": {"semana": {"status": 5}},
        },
        "horarios": {"seg-sex": ["07:30", "12:00", "19:30"], "sab": ["10:00"], "dom": ["11:00"]},
        "hashtags_base": [],
        "cta_permitidos": ["Compartilhe com quem precisa ver", "Comente sua opinião", "Salve e confira depois"],
        "musica_biblioteca": "",
        "observacoes": "",
    },
}
MODELOS["juridico"] = copy.deepcopy(MODELOS["advocacia"]) | {"tipo": "juridico", "nome": "Conteúdo Jurídico Exemplo"}

OBRIGATORIOS = ("id", "nome", "tipo", "assinatura", "redes")


def _arq(pid):
    return caminhos.PERFIS / f"{pid}.json"


def listar():
    return sorted(p.stem for p in caminhos.PERFIS.glob("*.json")) if caminhos.PERFIS.exists() else []


def criar(pid, tipo="advocacia", **campos):
    if not re.fullmatch(r"[a-z0-9][a-z0-9_-]*", pid):
        raise ValueError("id do perfil: minúsculas, números, '-' e '_' (ex.: escritorio-souza)")
    if tipo not in MODELOS:
        raise ValueError(f"tipo deve ser um de {sorted(MODELOS)}")
    if _arq(pid).exists():
        raise FileExistsError(f"perfil {pid} já existe")
    p = copy.deepcopy(MODELOS[tipo])
    p["id"] = pid
    p.update(campos)
    salvar(p)
    return p


def salvar(p):
    caminhos.PERFIS.mkdir(parents=True, exist_ok=True)
    _arq(p["id"]).write_text(json.dumps(p, ensure_ascii=False, indent=1), encoding="utf-8")
    return _arq(p["id"])


def carregar(pid):
    """Perfil pelo id; `None` devolve um perfil neutro de advocacia (útil para testes e uso avulso)."""
    if pid is None:
        p = copy.deepcopy(MODELOS["advocacia"])
        p["id"] = "_avulso"
        return p
    if isinstance(pid, dict):
        return pid
    a = _arq(pid)
    if not a.exists():
        raise FileNotFoundError(f"perfil '{pid}' não existe (perfis: {', '.join(listar()) or 'nenhum'})")
    p = json.loads(a.read_text(encoding="utf-8"))
    base = copy.deepcopy(MODELOS.get(p.get("tipo"), MODELOS["advocacia"]))
    base.update(p)          # campos novos do modelo aparecem em perfis antigos
    return base


def validar(p):
    """Alertas de configuração (não bloqueiam)."""
    al = [f"campo obrigatório ausente: {c}" for c in OBRIGATORIOS if not p.get(c)]
    if p.get("tipo") in ("advocacia", "juridico") and not p.get("assinatura", {}).get("registro"):
        al.append("advocacia: informe o registro OAB na assinatura (Prov. 205/2021 exige identificação)")
    if p.get("tipo") == "politico" and p.get("candidato") and not p.get("cnpj_campanha"):
        al.append("candidato: informe o CNPJ da campanha (obrigatório em conteúdo impulsionado)")
    if not p.get("fundo_foto"):
        al.append("sem foto do ambiente (fundo_foto): o estúdio virtual usará fundo desenhado (qualidade menor)")
    if not p.get("foto_autor"):
        al.append("sem retrato (foto_autor): capas, thumbnails e carrosséis sairão sem foto")
    soma = sum(x.get("peso", 0) for x in p.get("pilares", []))
    if p.get("pilares") and abs(soma - 1) > 0.05:
        al.append(f"pesos dos pilares somam {soma:.2f} (devem somar 1)")
    for c in ("fundo_foto", "foto_autor"):
        if p.get(c) and not (caminhos.RAIZ / p[c]).exists() and not __import__("pathlib").Path(p[c]).exists():
            al.append(f"{c}: arquivo não encontrado ({p[c]})")
    return al


def assinatura_texto(p):
    a = p.get("assinatura", {})
    return " · ".join(x for x in (a.get("cargo"), a.get("registro")) if x)
