"""Análise visual quadro a quadro (estudos/16 §1): o "olho" do videomaker.

Amostra o vídeo (4 quadros/s) e mede, por quadro:
  rosto (posição, tamanho), luz do rosto × fundo, textura do fundo, movimento, troca de cena.
Agrega num diagnóstico com recomendações de edição, usado pelo diretor e pela skill.
"""
import json
import subprocess
from pathlib import Path

import numpy as np

MODELO_ROSTO = Path(__file__).resolve().parents[1] / "modelos" / "haarcascade_frontalface_default.xml"


def _quadros(video, fps=4, largura=360):
    info = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height",
                           "-of", "csv=p=0", str(video)], capture_output=True, text=True, check=True).stdout
    w, h = map(int, info.strip().split(",")[:2])
    lh = int(largura * h / w) // 2 * 2
    proc = subprocess.Popen(["ffmpeg", "-v", "error", "-i", str(video), "-vf", f"fps={fps},scale={largura}:{lh}",
                             "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
    tam = largura * lh * 3
    i = 0
    while True:
        buf = proc.stdout.read(tam)
        if len(buf) < tam:
            break
        yield i / fps, np.frombuffer(buf, np.uint8).reshape(lh, largura, 3)
        i += 1
    proc.wait()


def analisar(video, destino=None, fps=4):
    import cv2
    detector = cv2.CascadeClassifier(str(MODELO_ROSTO))
    amostras, anterior, hist_ant = [], None, None
    for t, q in _quadros(video, fps):
        cinza = cv2.cvtColor(q, cv2.COLOR_RGB2GRAY)
        hh, ww = cinza.shape
        rostos = detector.detectMultiScale(cinza, scaleFactor=1.15, minNeighbors=5, minSize=(ww // 12, ww // 12))
        a = {"t": round(t, 2)}
        mascara_fundo = np.ones_like(cinza, bool)
        if len(rostos):
            x, y, w, h = max(rostos, key=lambda r: r[2] * r[3])
            a.update(rosto=True, cx=round((x + w / 2) / ww, 3), cy=round((y + h / 2) / hh, 3), tam=round(h / hh, 3),
                     luz_rosto=round(float(cinza[y:y + h, x:x + w].mean()) / 255, 3))
            # corpo: retângulo abaixo do rosto também não é fundo
            mascara_fundo[max(0, y - h // 2):, max(0, x - w):min(ww, x + 2 * w)] = False
        else:
            a["rosto"] = False
        fundo = cinza[mascara_fundo]
        a["luz_fundo"] = round(float(fundo.mean()) / 255, 3) if fundo.size else None
        a["textura_fundo"] = round(float(cv2.Laplacian(cinza, cv2.CV_64F)[mascara_fundo].std()), 2) if fundo.size else None
        a["movimento"] = round(float(np.abs(cinza.astype(int) - anterior).mean()), 2) if anterior is not None else 0.0
        hist = cv2.calcHist([q], [0, 1, 2], None, [8, 8, 8], [0, 256] * 3).flatten()
        hist /= hist.sum() or 1
        a["corte_cena"] = bool(hist_ant is not None and 0.5 * np.abs(hist - hist_ant).sum() > 0.45)
        anterior, hist_ant = cinza.astype(int), hist
        amostras.append(a)
    diag = diagnosticar(amostras)
    res = {"fonte": str(video), "amostras": amostras, "diagnostico": diag}
    if destino:
        Path(destino).write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
    return res


def diagnosticar(am):
    com = [a for a in am if a.get("rosto")]
    d = {"quadros": len(am), "presenca_rosto": round(len(com) / max(len(am), 1), 2)}
    rec = []
    if com:
        cx = np.array([a["cx"] for a in com])
        d.update(rosto_x=round(float(np.median(cx)), 3), rosto_y=round(float(np.median([a["cy"] for a in com])), 3),
                 rosto_tam=round(float(np.median([a["tam"] for a in com])), 3), deriva_x=round(float(cx.std()), 3),
                 luz_rosto=round(float(np.median([a["luz_rosto"] for a in com])), 3))
        if abs(d["rosto_x"] - 0.5) > 0.06:
            rec.append({"acao": "reenquadrar_no_rosto", "motivo": f"rosto em x={d['rosto_x']:.2f}, fora do centro"})
        if d["deriva_x"] > 0.08:
            rec.append({"acao": "rastreamento", "motivo": "a pessoa se move bastante na horizontal"})
        if d["luz_rosto"] < 0.30:
            rec.append({"acao": "reiluminar_rosto", "motivo": "rosto escuro (Relight / curvas)"})
    fundos = [a for a in am if a.get("luz_fundo") is not None]
    if fundos:
        d["luz_fundo"] = round(float(np.median([a["luz_fundo"] for a in fundos])), 3)
        d["textura_fundo"] = round(float(np.median([a["textura_fundo"] for a in fundos])), 2)
        liso = d["textura_fundo"] < 6
        d["fundo"] = "liso" if liso else "com_textura"
        if liso:
            rec.append({"acao": "estudio_virtual", "motivo": "fundo liso e sem profundidade: candidato a estúdio virtual"})
        if com and d["luz_fundo"] - d.get("luz_rosto", 0) > 0.25:
            rec.append({"acao": "contraluz", "motivo": "fundo bem mais claro que o rosto: reduzir realces do fundo ou trocar o fundo"})
    mov = [a["movimento"] for a in am[1:] if not a["corte_cena"]]
    if mov:
        d["movimento_medio"] = round(float(np.median(mov)), 2)
        if d["movimento_medio"] > 9 and d.get("deriva_x", 0) < 0.05:
            rec.append({"acao": "estabilizar", "motivo": "movimento de câmera alto com rosto estável"})
        if d["movimento_medio"] < 1.2:
            rec.append({"acao": "mais_movimento_virtual", "motivo": "plano muito estático: usar push-ins"})
    d["cortes_de_cena"] = [a["t"] for a in am if a["corte_cena"]]
    if len(d["cortes_de_cena"]) > 3:
        rec.append({"acao": "color_match", "motivo": "várias cenas/câmeras: igualar cor"})
    d["recomendacoes"] = rec
    return d


def estilo_sugerido(diag, preset):
    acoes = {r["acao"] for r in diag.get("recomendacoes", [])}
    if preset == "politico":
        return "noticiario"
    if preset == "dinamico":
        return "viral"
    return "estudio" if "estudio_virtual" in acoes or "contraluz" in acoes else "autentico"
