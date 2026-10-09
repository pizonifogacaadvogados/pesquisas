"""D3: gera o plano de edição (plano.json) a partir da análise.

O plano é a "partitura" da edição. Tanto o render ffmpeg quanto o roteiro do CapCut
leem este arquivo, e o Claude pode revisá-lo e editá-lo à mão antes de executar.

Tempos:
  segmentos[].ini/fim  -> tempo no vídeo BRUTO (para cortar)
  todo o resto          -> tempo no vídeo EDITADO (base.mp4 / timeline do CapCut)
"""
import json
import re
from pathlib import Path

from . import momentos
from ..nucleo import regras


def _vicios(ws, pausa=0.25):
    """Índices de palavras a remover: vícios de linguagem e repetições imediatas."""
    fora = set()
    for k, w in enumerate(ws):
        lw = regras.limpa(w["w"])
        antes = w["ini"] - ws[k - 1]["fim"] if k > 0 else 1.0
        depois = ws[k + 1]["ini"] - w["fim"] if k + 1 < len(ws) else 1.0
        if lw in regras.VICIOS_SEMPRE:
            fora.add(k)
        elif lw in regras.VICIOS_CONTEXTO and ((antes > pausa and depois > pausa) or w["fim"] - w["ini"] > 0.5):
            fora.add(k)
        elif k + 1 < len(ws) and lw and lw == regras.limpa(ws[k + 1]["w"]) and depois < 0.5 and len(lw) <= 6:
            fora.add(k)  # "o o", "que que": fica só a segunda
    return fora


def _segmentos(ws, fora, cfg, pausas_permitidas=()):
    """Agrupa palavras mantidas em segmentos contínuos (cada fronteira = um corte)."""
    segs, atual = [], []
    for k, w in enumerate(ws):
        if k in fora:
            if atual:
                segs.append(atual)
                atual = []
            continue
        if atual:
            gap = w["ini"] - ws[atual[-1]]["fim"]
            limite = 0.65 if k in pausas_permitidas else cfg["pausa_max"]
            if gap > limite:
                segs.append(atual)
                atual = []
        atual.append(k)
    if atual:
        segs.append(atual)
    out = []
    for s in segs:
        ini = max(ws[s[0]]["ini"] - cfg["folga"], 0)
        fim = ws[s[-1]]["fim"] + cfg["folga"]
        if out and ini < out[-1]["fim"]:  # folgas se sobrepõem: divide no meio
            meio = (out[-1]["fim"] + ini) / 2
            out[-1]["fim"], ini = meio, meio
        out.append({"ini": round(ini, 3), "fim": round(fim, 3), "palavras": s})
    return out


def _r(x):
    return round(x, 3)


def gerar(analise, preset="dinamico", dur_min=25, dur_max=60, cold_open=True):
    cfg = dict(regras.PRESETS[preset])
    from ..nucleo import aprendizado
    cfg["pausa_max"] = round(cfg["pausa_max"] + aprendizado.ajustes().get("cortes_pausa_delta", 0.0), 3)
    palavras = analise["palavras"]
    sel = momentos.selecionar(palavras, dur_min, dur_max)
    i, j = sel["janela"]
    fs = sel["frases"]
    idx = [k for f in fs[i:j + 1] for k in f["idx"]]
    ws = [palavras[k] for k in idx]
    pos = {k: n for n, k in enumerate(idx)}           # índice global -> índice na janela

    climax_ini = pos.get(sel["climax"]["idx"][0])
    fora = _vicios(ws)
    corpo = _segmentos(ws, fora, cfg, pausas_permitidas={climax_ini} if climax_ini is not None else ())
    for s in corpo:
        s["papel"] = "corpo"

    segs = list(corpo)
    if cold_open and sel["cold_open"]:
        g = [pos[k] for k in sel["gancho"]["idx"] if k in pos]
        gseg = _segmentos(ws, fora | set(range(len(ws))) - set(g), cfg)
        segs = [dict(s, papel="gancho") for s in gseg] + segs

    # ------------------------------------------------ linha do tempo editada
    out_palavras, off = [], 0.0
    for n, s in enumerate(segs):
        s["out_ini"] = _r(off)
        for k in s["palavras"]:
            w = ws[k]
            out_palavras.append({"w": w["w"], "ini": _r(off + w["ini"] - s["ini"]), "fim": _r(off + w["fim"] - s["ini"]),
                                 "energia": w.get("energia", 0.5), "seg": n, "k": k})
        off += s["fim"] - s["ini"]
        s["out_fim"] = _r(off)
    duracao = _r(off)

    eventos = []
    # punch-in alternado: um enquadramento por segmento (E3 §2)
    for n, s in enumerate(segs):
        nivel = cfg["punch"] if (n % 2 == 1 or s["papel"] == "gancho") else 1.0
        if nivel != 1.0:
            eventos.append({"tipo": "zoom", "modo": "punch", "ini": s["out_ini"], "fim": s["out_fim"], "escala": nivel})
        if n > 0 and segs[n - 1]["papel"] == "gancho" and s["papel"] == "corpo":
            eventos.append({"tipo": "sfx", "som": "whoosh", "t": _r(max(s["out_ini"] - 0.12, 0)), "motivo": "fim do gancho"})

    # palavras-chave -> emoji, snap zoom, SFX
    ult_emoji, ult_snap = -99.0, -99.0
    for n, w in enumerate(out_palavras):
        prox = out_palavras[n + 1]["w"] if n + 1 < len(out_palavras) else ""
        par = w["w"] + " " + prox
        achado = regras.emoji_para(par, so_compostos=True) or regras.emoji_para(w["w"])
        forte = regras.eh_gatilho(w["w"]) > 0 or regras.eh_gatilho(par, so_compostos=True) > 0
        w["destaque"] = bool(achado or forte or re.search(r"\d", w["w"]))
        if not (achado or forte):
            continue
        seg = segs[w["seg"]]
        if achado and achado[0] not in cfg["emojis_bloqueados"] and w["ini"] - ult_emoji >= cfg["emoji_intervalo"] \
                and w["ini"] >= 0.6:
            emoji, som = achado
            if not cfg["sfx_fortes"] and som in ("buzzer", "hit"):
                som = "pop"
            eventos.append({"tipo": "emoji", "emoji": emoji, "palavra": w["w"], "ini": w["ini"],
                            "fim": _r(w["ini"] + cfg["emoji_dur"]), "lado": "direita" if len(eventos) % 2 else "esquerda"})
            if cfg["sfx"]:
                eventos.append({"tipo": "sfx", "som": som, "t": w["ini"], "motivo": f"emoji {emoji}"})
            ult_emoji = w["ini"]
        if w["energia"] >= 0.55 and w["ini"] - ult_snap >= cfg["snap_intervalo"] and w["ini"] >= 1.0:
            fim = _r(min(w["fim"] + 0.6, seg["out_fim"]))
            if fim - w["ini"] >= 0.35:
                eventos.append({"tipo": "zoom", "modo": "snap", "ini": w["ini"], "fim": fim, "escala": cfg["snap"],
                                "palavra": w["w"]})
                if cfg["sfx"]:
                    eventos.append({"tipo": "sfx", "som": "whoosh", "t": _r(max(w["ini"] - 0.08, 0)), "motivo": "snap zoom"})
                ult_snap = w["ini"]

    # clímax: zoom lento + riser/hit (E1 §4, E3 §2)
    cl = sel["climax"]
    cl_k = {pos[g] for g in cl["idx"] if g in pos}
    cl_out = [w for w in out_palavras if segs[w["seg"]]["papel"] == "corpo" and w["k"] in cl_k]
    if cl_out and cfg["zoom_lento"]:
        a0 = a = cl_out[0]["ini"]
        b = cl_out[-1]["fim"]
        # encadeia: se há snap zoom dentro do clímax, o zoom lento começa depois dele
        snaps = [e for e in eventos if e["tipo"] == "zoom" and e["modo"] == "snap" and e["ini"] < b and e["fim"] > a]
        if snaps:
            a = max(e["fim"] for e in snaps)
        if b - a >= 1.0:
            eventos.append({"tipo": "zoom", "modo": "lento", "ini": a, "fim": b, "escala": 1.08, "motivo": "clímax"})
        if cfg["sfx_fortes"] and a0 >= 1.3:
            eventos.append({"tipo": "sfx", "som": "riser", "t": _r(a0 - 1.2), "motivo": "antes do clímax"})
            eventos.append({"tipo": "sfx", "som": "hit", "t": a0, "motivo": "clímax"})

    # título do gancho nos primeiros ~3s
    abertura = {n for n, s in enumerate(segs) if s["papel"] == "gancho"} or {0}
    primeira = [w["w"] for w in out_palavras if w["seg"] in abertura]
    titulo = " ".join(primeira[:7]).strip(" ,.;:")
    if titulo:
        eventos.append({"tipo": "titulo", "texto": titulo.upper() if cfg["caixa_alta"] else titulo,
                        "ini": 0.0, "fim": _r(min(3.0, max(segs[max(abertura)]["out_fim"], 2.0)))})

    # legendas: blocos de N palavras (E3 §1)
    legendas, bloco = [], []
    for n, w in enumerate(out_palavras):
        bloco.append(w)
        prox = out_palavras[n + 1] if n + 1 < len(out_palavras) else None
        if prox is None or len(bloco) >= cfg["palavras_legenda"] or re.search(r"[.!?,;:…]$", w["w"]) \
                or prox["ini"] - w["fim"] > 0.35:
            legendas.append({"ini": bloco[0]["ini"], "fim": _r(prox["ini"] if prox and prox["ini"] - w["fim"] < 0.35 else w["fim"] + 0.15),
                             "palavras": [{"w": x["w"], "ini": x["ini"], "fim": x["fim"], "destaque": x["destaque"]} for x in bloco]})
            bloco = []

    # emoji não disputa espaço com o título do gancho: desce para a altura do peito
    tit = next((e for e in eventos if e["tipo"] == "titulo"), None)
    for e in eventos:
        if e["tipo"] == "emoji":
            e["y"] = 0.40 if tit and e["ini"] < tit["fim"] else 0.24

    eventos.sort(key=lambda e: (e.get("ini", e.get("t", 0)), e["tipo"]))
    texto = " ".join(w["w"] for w in out_palavras)
    return {
        "versao": 1,
        "preset": preset,
        "fonte": analise["fonte"],
        "fonte_info": {k: analise.get(k) for k in ("duracao", "largura", "altura", "fps")},
        "saida": {"largura": 1080, "altura": 1920, "fps": 30},
        "duracao_final": duracao,
        "selecao": {
            "trecho_bruto": [fs[i]["ini"], fs[j]["fim"]],
            "gancho": sel["gancho"]["texto"], "cold_open": bool(segs[0]["papel"] == "gancho"),
            "climax": cl["texto"],
            "notas": [{"texto": f["texto"], "nota": f["nota"], "ini": f["ini"]} for f in fs[i:j + 1]],
        },
        "segmentos": [{"ini": s["ini"], "fim": s["fim"], "papel": s["papel"], "out_ini": s["out_ini"], "out_fim": s["out_fim"]}
                      for s in segs],
        "cortes_removidos": len(segs) - 1,
        "eventos": eventos,
        "legendas": legendas,
        "texto": texto,
        "alertas": regras.alertas(texto, preset),
    }


def salvar(plano, caminho):
    Path(caminho).write_text(json.dumps(plano, ensure_ascii=False, indent=1), encoding="utf-8")
