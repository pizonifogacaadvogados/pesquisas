"""Aprendizado contínuo: o sistema melhora a cada vídeo.

Três fontes de aprendizado, guardadas em `memoria/` (versionada no repositório):
  1. registro de cada vídeo produzido (estilo, gancho, duração, recursos usados)
  2. feedback do usuário em linguagem natural → ajustes de parâmetros
     ("zoom demais", "legenda pequena", "música alta", "gostei do estúdio"…)
  3. métricas reais da publicação (taxa de pulo 3s, retenção, envios, salvamentos)
     → ranking de estilos e ganchos por resultado

Os ajustes acumulados (memoria/ajustes.json) são aplicados automaticamente pelo diretor,
e o resumo legível (memoria/LICOES.md) é lido pela skill-mãe antes de cada edição.
"""
import json
import re
from datetime import datetime
from pathlib import Path
from . import caminhos

MEM = caminhos.MEMORIA
LIMITES = {"camera_mult": (0.5, 1.6), "legenda_tam_delta": (-16, 30), "musica_db_delta": (-10, 8),
           "transicao_intensidade": (0.2, 1.5), "lut_intensidade_delta": (-0.3, 0.2), "emoji_freq_mult": (0.3, 2.0),
           "cortes_pausa_delta": (-0.15, 0.25)}
# frase do usuário → (parâmetro, passo)
REGRAS_FEEDBACK = [
    (r"zoom (demais|exagerad|muito)|muito zoom|enjoa", "camera_mult", -0.15),
    (r"(pouco|mais) (zoom|movimento)|parado|est[aá]tico", "camera_mult", +0.15),
    (r"legenda (pequena|miuda|miúda)|n[aã]o (d[aá]|consigo) (pra )?ler|letra pequena", "legenda_tam_delta", +6),
    (r"legenda (grande|enorme|exagerada)", "legenda_tam_delta", -6),
    (r"m[uú]sica (alta|forte|atrapalha)|n[aã]o ouvi a voz", "musica_db_delta", -3),
    (r"m[uú]sica (baixa|fraca)|sem energia", "musica_db_delta", +2),
    (r"(luz|light leak|clar[aã]o|flash) (demais|forte|exagerad)", "transicao_intensidade", -0.25),
    (r"cor (forte|exagerad|artificial)|filtro (forte|demais)", "lut_intensidade_delta", -0.1),
    (r"emoji(s)? (demais|infantil)", "emoji_freq_mult", -0.3),
    (r"(cortes|corte) (bruscos?|demais|rob[oó]tico)|sem respiro", "cortes_pausa_delta", +0.08),
    (r"(lento|arrastado|devagar|enrolando)", "cortes_pausa_delta", -0.05),
]


def _ler(nome, padrao):
    p = MEM / nome
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else padrao


def _gravar(nome, dados):
    MEM.mkdir(exist_ok=True)
    (MEM / nome).write_text(json.dumps(dados, ensure_ascii=False, indent=1), encoding="utf-8")


def ajustes():
    return _ler("ajustes.json", {})


def registrar_video(prod, plano, pasta):
    videos = _ler("videos.json", [])
    vid = f"v{len(videos) + 1:04d}"
    c = prod["camadas"]
    videos.append({
        "id": vid, "data": datetime.now().isoformat(timespec="minutes"), "pasta": str(pasta),
        "estilo": prod["estilo"], "preset": prod["preset"], "duracao": prod["duracao"],
        "gancho": plano["selecao"]["gancho"], "abertura": c["abertura"]["tipo"], "humor": prod.get("humor_trilha"),
        "recursos": {"cartoes": len(c["cartoes"]), "broll": len(c["broll"]), "transicoes": len(c["transicoes"]),
                     "emojis": len(c["emojis"]), "musica": bool(c.get("musica")), "fundo": c["fundo"]["tipo"]},
        "feedback": [], "metricas": [],
    })
    _gravar("videos.json", videos)
    escrever_licoes()
    return vid


def registrar_feedback(vid, texto):
    videos = _ler("videos.json", [])
    aj = ajustes()
    aplicados = []
    for padrao, chave, passo in REGRAS_FEEDBACK:
        if re.search(padrao, texto, re.I):
            base = aj.get(chave, 1.0 if chave.endswith("mult") or chave == "transicao_intensidade" else 0.0)
            lo, hi = LIMITES[chave]
            aj[chave] = round(min(hi, max(lo, base + passo)), 3)
            aplicados.append((chave, aj[chave]))
    for v in videos:
        if v["id"] == vid:
            v["feedback"].append({"texto": texto, "ajustes": aplicados, "data": datetime.now().isoformat(timespec="minutes")})
    _gravar("videos.json", videos)
    _gravar("ajustes.json", aj)
    escrever_licoes()
    return aplicados


def registrar_metricas(vid, plataforma, **m):
    """m: views, taxa_pulo (0-1, pulam nos 3s), retencao_media (0-1), envios, salvamentos, comentarios, curtidas."""
    videos = _ler("videos.json", [])
    for v in videos:
        if v["id"] == vid:
            v["metricas"].append({"plataforma": plataforma, **m, "data": datetime.now().isoformat(timespec="minutes")})
    _gravar("videos.json", videos)
    escrever_licoes()


def _pontuacao(met):
    """Índice de desempenho 0-100: retenção e envios pesam mais (sinais confirmados por Mosseri/TikTok)."""
    views = max(met.get("views", 0), 1)
    s = 0.0
    if "taxa_pulo" in met:
        s += (1 - met["taxa_pulo"]) * 35
    if "retencao_media" in met:
        s += met["retencao_media"] * 30
    s += min(met.get("envios", 0) / views * 1000, 20)        # envios por mil views
    s += min(met.get("salvamentos", 0) / views * 500, 10)
    s += min(met.get("comentarios", 0) / views * 500, 5)
    return round(s, 1)


def ranking():
    videos = _ler("videos.json", [])
    por = {}
    for v in videos:
        for m in v["metricas"]:
            chave = (v["preset"], v["estilo"])
            por.setdefault(chave, []).append(_pontuacao(m))
    return sorted(((k, round(sum(x) / len(x), 1), len(x)) for k, x in por.items()), key=lambda r: -r[1])


def estilo_recomendado(preset):
    r = [x for x in ranking() if x[0][0] == preset and x[2] >= 2]
    return r[0][0][1] if r else None


def escrever_licoes():
    videos = _ler("videos.json", [])
    aj = ajustes()
    l = ["# Lições aprendidas (gerado automaticamente)", "",
         "A skill-mãe lê este arquivo antes de cada edição.", "",
         "## Ajustes ativos (aplicados automaticamente)"]
    l += [f"- `{k}` = {v}" for k, v in aj.items()] or ["- nenhum ainda"]
    l += ["", "## Ranking de estilos por desempenho real (índice 0-100)"]
    rk = ranking()
    l += [f"- {p}/{e}: {s} ({n} medições)" for (p, e), s, n in rk] or ["- sem métricas ainda"]
    l += ["", "## Feedback recente"]
    fb = [(v["id"], f["texto"]) for v in videos for f in v["feedback"]][-15:]
    l += [f"- {i}: \"{t}\"" for i, t in fb] or ["- nenhum ainda"]
    melhores = sorted(((max(_pontuacao(m) for m in v["metricas"]), v) for v in videos if v["metricas"]),
                      key=lambda x: -x[0])[:5]
    l += ["", "## Ganchos que mais funcionaram"]
    l += [f"- ({s}) \"{v['gancho']}\" — {v['estilo']}, {v['duracao']:.0f}s" for s, v in melhores] or ["- sem métricas ainda"]
    l += ["", f"Total de vídeos registrados: {len(videos)}"]
    MEM.mkdir(exist_ok=True)
    (MEM / "LICOES.md").write_text("\n".join(l) + "\n", encoding="utf-8")
