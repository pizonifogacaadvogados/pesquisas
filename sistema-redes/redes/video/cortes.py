"""Reutilizar (R15, castilho.ia e edicaomia): um material vira muitas peças.

  cortes(...)     vídeo longo (podcast, live, palestra, entrevista) → N clipes curtos sem sobreposição,
                  cada um com o melhor gancho, cortes de pausa/vício, legenda e enquadramento 9:16
  variacoes(...)  o MESMO trecho com ganchos diferentes (frases fortes da janela abrindo o vídeo) para
                  testar com Trial Reels / anúncios (versões A, B, C…)
Cada peça sai em `<pasta>/<nome>/` com `plano.json`, `base.mp4` e `final.mp4` (motor rápido) — e pode
seguir para a produção completa (`produzir`/`rerender`) ou para os efeitos (`efeitos`).
"""
import copy
import json
from pathlib import Path

from . import momentos, plano, render


def _blocos_livres(palavras, usados):
    """Sequências contíguas de palavras ainda não usadas."""
    blocos, atual = [], []
    for k, p in enumerate(palavras):
        if k in usados:
            if atual:
                blocos.append(atual)
            atual = []
        else:
            atual.append(k)
    if atual:
        blocos.append(atual)
    return blocos


def escolher_clipes(analise, n=10, dur_min=25, dur_max=60):
    """Janelas não sobrepostas, da melhor para a pior. Devolve [{ini, fim, idx, nota, gancho}].
    Nota do clipe: gancho forte, faz sentido sem o contexto anterior, conteúdo denso e termina fechando a frase."""
    palavras = analise["palavras"]
    usados, clipes = set(), []
    for _ in range(n):
        melhor = None
        for bloco in _blocos_livres(palavras, usados):
            ws = [palavras[k] for k in bloco]
            if len(ws) < 12 or ws[-1]["fim"] - ws[0]["ini"] < dur_min * 0.8:
                continue
            sel = momentos.selecionar(ws, dur_min, dur_max)
            i, j = sel["janela"]
            fs = sel["frases"][i:j + 1]
            notas = [f["nota"] for f in fs if not f.get("descartavel")] or [0]
            # pesos inspirados no claude-shorts (R16): gancho 0,30 · sentido sozinho 0,25 · conteúdo 0,35 · fecho 0,10
            sozinho = 0 if momentos._depende_do_anterior(fs[0]) else 100
            fecho = 100 if palavras[fs[-1]["idx"][-1]]["w"].rstrip().endswith((".", "!", "?")) else 40
            nota = (0.30 * sel["gancho"]["nota"] + 0.25 * sozinho + 0.35 * sum(notas) / len(notas) + 0.10 * fecho)
            idx = [bloco[k] for f in fs for k in f["idx"]]
            if melhor is None or nota > melhor["nota"]:
                melhor = {"idx": idx, "nota": round(nota, 1), "gancho": sel["gancho"]["texto"],
                          "ini": palavras[idx[0]]["ini"], "fim": palavras[idx[-1]]["fim"]}
        if not melhor:
            break
        usados |= set(melhor["idx"])
        clipes.append(melhor)
    return clipes


def _sub_analise(analise, idx):
    a = copy.deepcopy(analise)
    a["palavras"] = [analise["palavras"][k] for k in idx]
    return a


def cortes(analise, pasta, n=10, preset="juridico", dur_min=25, dur_max=60, renderizar=True, enquadramento="corte"):
    pasta = Path(pasta)
    pasta.mkdir(parents=True, exist_ok=True)
    clipes = escolher_clipes(analise, n, dur_min, dur_max)
    rel = []
    for c, info in enumerate(clipes, 1):
        sub = pasta / f"clipe_{c:02d}"
        sub.mkdir(exist_ok=True)
        pl = plano.gerar(_sub_analise(analise, info["idx"]), preset, dur_min, dur_max)
        plano.salvar(pl, sub / "plano.json")
        if renderizar:
            render.renderizar(pl, sub, enquadramento=enquadramento, base=True, final=True)
        rel.append({"clipe": sub.name, "trecho_original": [round(info["ini"], 1), round(info["fim"], 1)],
                    "duracao": pl["duracao_final"], "nota": info["nota"], "gancho": pl["selecao"]["gancho"]})
    (pasta / "cortes.json").write_text(json.dumps(rel, ensure_ascii=False, indent=1), encoding="utf-8")
    return rel


def variacoes(analise, pasta, k=3, preset="juridico", dur_min=25, dur_max=60, renderizar=True, enquadramento="corte"):
    """Mesmo trecho, ganchos diferentes: as k frases mais fortes da janela (que não dependem da anterior)."""
    pasta = Path(pasta)
    pasta.mkdir(parents=True, exist_ok=True)
    sel = momentos.selecionar(analise["palavras"], dur_min, dur_max)
    i, j = sel["janela"]
    cand = [(n, f) for n, f in enumerate(sel["frases"]) if i <= n <= j and not f.get("descartavel")
            and not momentos._depende_do_anterior(f) and (f["fim"] - f["ini"]) <= 7.0]
    cand.sort(key=lambda x: -x[1]["nota"])
    rel = []
    for v, (n, f) in enumerate(cand[:k]):
        nome = f"versao_{chr(65 + v)}"
        sub = pasta / nome
        sub.mkdir(exist_ok=True)
        pl = plano.gerar(analise, preset, dur_min, dur_max, gancho_forcado=n)
        plano.salvar(pl, sub / "plano.json")
        if renderizar:
            render.renderizar(pl, sub, enquadramento=enquadramento, base=True, final=True)
        rel.append({"versao": nome, "gancho": f["texto"], "nota_gancho": f["nota"], "duracao": pl["duracao_final"]})
    (pasta / "variacoes.json").write_text(json.dumps(rel, ensure_ascii=False, indent=1), encoding="utf-8")
    return rel
