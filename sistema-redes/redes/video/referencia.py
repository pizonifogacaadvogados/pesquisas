"""Dissecar um vídeo de REFERÊNCIA (ex.: um Reels do @tiagolemosx) e comparar com o nosso.

Por que existe: o YouTube/Instagram não abrem deste servidor (proxy 403, até com yt-dlp — R08.51). O caminho é você
baixar (ou gravar a tela) no computador do escritório, só para estudo, e rodar:
    python3 -m redes referencia ref.mp4 [--comparar nosso_final.mp4]
Mede o que um editor sênior mede ao "desmontar" um vídeo:
  cortes        cada troca de plano (filtro de cena do ffmpeg) → cortes por minuto, plano médio, maior plano
  ritmo         mudanças de plano + zooms (rosto mudando de tamanho) — o mesmo critério do QC
  som           loudness, pico, silêncios (há respiração cortada? há trilha o tempo todo?)
  rosto         % do tempo com rosto, tamanho médio do rosto (enquadramento: close, médio, aberto)
  cor           brilho, contraste e saturação médios (o "look")
  folha         um quadro por plano (até 40) para estudar composição, legenda e gráficos
Saída: `ref/<nome>/referencia.json` + `REFERENCIA.md` + `planos.png`. Com `--comparar`, uma tabela lado a lado.
"""
import json
import re
import subprocess
from pathlib import Path

import numpy as np

from . import qc


def cortes(video, limiar=0.30):
    s = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", str(video), "-an", "-vf",
                        f"select='gt(scene,{limiar})',showinfo", "-f", "null", "-"], capture_output=True, text=True).stderr
    return [round(float(x), 2) for x in re.findall(r"pts_time:([\d.]+)", s)]


def _cor(video):
    qs, _ = qc._quadros(video, 1, largura=160)
    import cv2
    hsv = np.stack([cv2.cvtColor(q, cv2.COLOR_RGB2HSV) for q in qs])
    y = qs.mean(axis=3)
    return {"brilho": round(float(y.mean()) / 255, 2), "contraste": round(float(y.std(axis=(1, 2)).mean()) / 255, 2),
            "saturacao": round(float(hsv[..., 1].mean()) / 255, 2)}


def _tamanho_rosto(video):
    from ..nucleo import rosto
    qs, (w, h) = qc._quadros(video, 2, largura=270)
    det = rosto.Detector()
    tams = [r[0][3] / h for r in (det(q) for q in qs) if r]
    if not tams:
        return None, "sem rosto"
    m = float(np.median(tams))
    return round(m, 2), ("close" if m > 0.32 else "médio" if m > 0.18 else "aberto")


def analisar(video, saida=None):
    video = Path(video)
    pasta = Path(saida) if saida else Path("ref") / video.stem
    pasta.mkdir(parents=True, exist_ok=True)
    r_qc = qc.revisar(video, pasta / "qc")
    m = r_qc["medidas"]
    cs = cortes(video)
    marcos = [0.0] + cs + [m["dur"]]
    planos = [b - a for a, b in zip(marcos, marcos[1:]) if b - a > 0.05]
    tam, enq = _tamanho_rosto(video)
    rel = {"video": str(video), "duracao": m["dur"], "resolucao": f"{m['w']}x{m['h']}", "fps": m["fps"],
           "cortes": len(cs), "cortes_por_min": round(len(cs) / max(m["dur"], 1) * 60, 1),
           "plano_medio_s": round(float(np.mean(planos)), 2) if planos else None,
           "maior_plano_s": round(max(planos), 2) if planos else None,
           "mudancas_visuais": m.get("mudancas_plano"), "seg_por_mudanca": m.get("seg_por_mudanca"),
           "lufs": m.get("lufs"), "silencios": len(m.get("silencios", [])),
           "rosto_visivel_pct": m.get("rosto_visivel_pct"), "rosto_altura": tam, "enquadramento": enq,
           **_cor(video), "tempos_corte": cs}
    # folha: um quadro no meio de cada plano (até 40)
    meios = [round((a + b) / 2, 2) for a, b in zip(marcos, marcos[1:]) if b - a > 0.05][:40]
    tmp = pasta / "_q"
    tmp.mkdir(exist_ok=True)
    for n, t in enumerate(meios):
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", str(t), "-i", str(video), "-frames:v", "1", "-vf",
                        f"scale=200:-2,drawtext=text='{t}s':x=4:y=4:fontsize=14:fontcolor=white:box=1:boxcolor=black@0.6",
                        str(tmp / f"{n:03d}.png")], check=True)
    if meios:
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(tmp / "%03d.png"), "-vf",
                        f"tile=8x{(len(meios) + 7) // 8}:padding=3:color=0x111111", "-frames:v", "1",
                        str(pasta / "planos.png")], check=True)
    for f in tmp.glob("*.png"):
        f.unlink()
    tmp.rmdir()
    (pasta / "referencia.json").write_text(json.dumps(rel, ensure_ascii=False, indent=1), encoding="utf-8")
    (pasta / "REFERENCIA.md").write_text(formatar([rel]), encoding="utf-8")
    return rel


CAMPOS = [("duracao", "Duração (s)"), ("cortes_por_min", "Cortes por minuto"), ("plano_medio_s", "Plano médio (s)"),
          ("maior_plano_s", "Maior plano (s)"), ("seg_por_mudanca", "Mudança visual a cada (s)"), ("lufs", "Loudness (LUFS)"),
          ("silencios", "Silêncios > 1,2 s"), ("rosto_visivel_pct", "Rosto visível (%)"), ("enquadramento", "Enquadramento"),
          ("brilho", "Brilho"), ("contraste", "Contraste"), ("saturacao", "Saturação"), ("resolucao", "Resolução")]


def formatar(rels):
    cab = "| Medida | " + " | ".join(Path(r["video"]).name for r in rels) + " |"
    linhas = ["# Dissecação de referência", "", cab, "|---|" + "---|" * len(rels)]
    linhas += [f"| {rot} | " + " | ".join(str(r.get(k)) for r in rels) + " |" for k, rot in CAMPOS]
    linhas += ["", "Leitura: compare cortes/min, plano médio e enquadramento primeiro (ritmo e linguagem); depois cor e som.",
               "Estude `planos.png`: onde fica a legenda, que gráfico entra em cada plano, quando há zoom."]
    return "\n".join(linhas) + "\n"


def comparar(ref, nosso, saida=None):
    a = analisar(ref, saida)
    b = analisar(nosso, Path(saida or Path("ref") / Path(ref).stem) / "nosso")
    md = formatar([a, b])
    (Path(saida or Path("ref") / Path(ref).stem) / "COMPARACAO.md").write_text(md, encoding="utf-8")
    return md
