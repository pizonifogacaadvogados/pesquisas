"""Pautas: o backlog de conteúdo de cada perfil, do tema à publicação.

Fluxo de status: ideia → roteiro → material (gravado/fotos prontos) → produzido → aprovado → publicado (→ medido).
Cada pauta guarda o perfil, o pilar, o formato, o gancho, as fontes/normas, o material e as peças geradas.
Arquivo: `dados/pautas.json` (lista). A skill `gestor-redes` cria e move pautas; o comando
`python -m redes pauta …` faz o mesmo pela linha de comando.

`sugerir()` não "inventa" conteúdo: gera pautas-esqueleto a partir de FORMATOS DE PAUTA comprovados por nicho
(estudos 05, 11, 12, 17) para o Claude preencher com o tema do momento.
"""
import json
from datetime import date, datetime

from ..nucleo import caminhos
from ..nucleo import perfis as _perfis

STATUS = ["ideia", "roteiro", "material", "produzido", "aprovado", "publicado", "medido"]
FORMATOS = ["reels", "carrossel", "post", "stories", "react", "video_longo", "documento"]

# formatos de pauta por nicho: (modelo de gancho, formato sugerido, pilar)
MODELOS_PAUTA = {
    "advocacia": [
        ("Você sabia que {direito}?", "reels", "Direitos do dia a dia"),
        ("{n} direitos que você tem quando {situacao}", "carrossel", "Direitos do dia a dia"),
        ("Mito ou verdade: {afirmacao}", "reels", "Mitos e verdades"),
        ("O erro que faz você perder {o_que}", "reels", "Direitos do dia a dia"),
        ("O que muda com {lei_ou_decisao}", "carrossel", "Mudanças na lei e decisões"),
        ("Advogado reage: {video_em_alta}", "react", "Mitos e verdades"),
        ("Prazo: você tem {prazo} para {acao}", "post", "Direitos do dia a dia"),
        ("Passo a passo: como {procedimento}", "carrossel", "Direitos do dia a dia"),
        ("Por trás de um processo de {area}", "reels", "Bastidores e autoridade (sem ostentação)"),
        ("Pergunta da semana: {duvida}", "stories", "Direitos do dia a dia"),
    ],
    "politico": [
        ("A proposta para {tema}, explicada em 1 minuto", "reels", "Propostas explicadas"),
        ("{n} coisas que fizemos por {bairro_ou_tema}", "carrossel", "Prestação de contas / trabalho"),
        ("Um dia com {pessoa_ou_grupo}", "reels", "Bastidores e pessoas"),
        ("É verdade que {boato}? Os fatos", "react", "Resposta e checagem"),
        ("O que o projeto {projeto} muda na sua vida", "carrossel", "Propostas explicadas"),
        ("Números: {indicador}", "post", "Prestação de contas / trabalho"),
        ("Agenda: {evento}", "post", "Bastidores e pessoas"),
        ("Você pergunta, eu respondo: {tema}", "stories", "Resposta e checagem"),
    ],
}
MODELOS_PAUTA["juridico"] = MODELOS_PAUTA["advocacia"]


def _arq():
    return caminhos.DADOS / "pautas.json"


def listar(perfil=None, status=None):
    if not _arq().exists():
        return []
    ps = json.loads(_arq().read_text(encoding="utf-8"))
    return [p for p in ps if (perfil is None or p["perfil"] == perfil) and (status is None or p["status"] == status)]


def _gravar(ps):
    caminhos.DADOS.mkdir(parents=True, exist_ok=True)
    _arq().write_text(json.dumps(ps, ensure_ascii=False, indent=1), encoding="utf-8")


def obter(pid):
    for p in listar():
        if p["id"] == pid:
            return p
    raise KeyError(f"pauta {pid} não existe")


def criar(perfil, tema, formato="reels", gancho="", pilar="", fontes=None, material="", data_alvo=None, **extra):
    _perfis.carregar(perfil)        # valida que o perfil existe
    if formato not in FORMATOS:
        raise ValueError(f"formato deve ser um de {FORMATOS}")
    ps = listar()
    n = max([int(p["id"][1:]) for p in ps] or [0]) + 1
    agora = datetime.now().isoformat(timespec="seconds")
    p = {"id": f"p{n:04d}", "perfil": perfil, "tema": tema, "formato": formato, "gancho": gancho, "pilar": pilar,
         "fontes": fontes or [], "material": material, "data_alvo": data_alvo, "status": "ideia",
         "pecas": {}, "historico": [{"quando": agora, "status": "ideia"}], **extra}
    ps.append(p)
    _gravar(ps)
    return p


def atualizar(pid, **campos):
    ps = listar()
    for p in ps:
        if p["id"] == pid:
            if "status" in campos:
                if campos["status"] not in STATUS:
                    raise ValueError(f"status deve ser um de {STATUS}")
                p["historico"].append({"quando": datetime.now().isoformat(timespec="seconds"), "status": campos["status"]})
            for k, v in campos.items():
                if k == "pecas":
                    p["pecas"].update(v)
                else:
                    p[k] = v
            _gravar(ps)
            return p
    raise KeyError(f"pauta {pid} não existe")


def sugerir(perfil, quantidade=6):
    """Esqueletos de pauta equilibrando os pilares do perfil pelos pesos (o Claude preenche os {campos})."""
    p = _perfis.carregar(perfil)
    modelos = MODELOS_PAUTA.get(p["tipo"], MODELOS_PAUTA["advocacia"])
    pesos = {x["nome"]: x.get("peso", 0) for x in p.get("pilares", [])}
    usados = {}
    for x in listar(p["id"]):
        usados[x.get("pilar")] = usados.get(x.get("pilar"), 0) + 1
    total = sum(usados.values()) or 1
    # pilares mais "devidos" primeiro: peso − participação atual
    ordem = sorted(modelos, key=lambda m: -(pesos.get(m[2], 0.1) - usados.get(m[2], 0) / total))
    return [{"gancho_modelo": g, "formato": f, "pilar": pl} for g, f, pl in ordem[:quantidade]]


def painel(perfil=None):
    """Contagem por status (o 'quadro kanban' em texto)."""
    ps = listar(perfil)
    linhas = []
    for s in STATUS:
        itens = [p for p in ps if p["status"] == s]
        linhas.append(f"{s:>10}: {len(itens):>3}  " + "; ".join(f"{p['id']} {p['tema'][:40]}" for p in itens[:4])
                      + (" …" if len(itens) > 4 else ""))
    atrasadas = [p for p in ps if p.get("data_alvo") and p["status"] not in ("publicado", "medido")
                 and date.fromisoformat(p["data_alvo"]) < date.today()]
    if atrasadas:
        linhas.append(f"⚠ atrasadas: {', '.join(p['id'] for p in atrasadas)}")
    return "\n".join(linhas)
