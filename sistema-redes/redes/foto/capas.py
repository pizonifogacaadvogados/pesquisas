"""Capas de Reels/TikTok e thumbnails do YouTube a partir do próprio vídeo (ou de uma foto).

Escolha do quadro: amostra o vídeo e pontua cada quadro por rosto (tamanho e centralização, detector YuNet) e
nitidez (variância do Laplaciano) — o editor de miniaturas faz o mesmo à mão: rosto grande, olhar, foco.

  capa_reels(...)  → 1080×1920; título no bloco central y 285-1635, que é o que a grade 3:4 do perfil mostra
                     (R12); gera também a prévia `capa_grade.png` (1080×1440) para conferir o recorte.
  thumbnail(...)   → 1280×720 (≤ 2 MB); pessoa recortada (RVM) à direita, fundo desfocado e escurecido,
                     até 5 palavras com contorno duro à esquerda, nada no canto inferior direito (selo de duração).
Boas práticas (R14): 1-5 palavras, rosto expressivo, alto contraste, um assunto só; paleta sóbria em temas sérios.
"""
import json
import subprocess
from pathlib import Path

import numpy as np
from PIL import Image, ImageFilter

from ..nucleo import perfis as _perfis
from ..nucleo import rosto
from .motor import _esc, identidade, pagina, renderizar


def _dur(video):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(video)],
                         capture_output=True, text=True).stdout.strip()
    return float(out or 0)


def _quadro(video, t, largura=None):
    vf = ["-vf", f"scale={largura}:-2"] if largura else []
    r = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{t:.3f}", "-i", str(video), "-frames:v", "1", *vf,
                        "-f", "image2pipe", "-vcodec", "png", "-"], capture_output=True)
    from io import BytesIO
    return np.asarray(Image.open(BytesIO(r.stdout)).convert("RGB"))


def _sem_graficos(fonte):
    """A capa nunca usa quadro com legenda queimada: se `fonte` é um final.mp4 da produção, usa o base.mp4 ao lado."""
    f = Path(fonte)
    base = f.parent / "base.mp4"
    return base if f.name.startswith("final") and base.exists() else f


def melhor_quadro(fonte, amostras=24, evitar_inicio=0.6, excluir=(), distancia=3.0):
    """Devolve (rgb, t, pontuação). `fonte` pode ser vídeo ou imagem.
    `excluir`: tempos já usados (outra opção de capa); o quadro escolhido fica a ≥ `distancia` s deles."""
    fonte = _sem_graficos(fonte)
    if Path(fonte).suffix.lower() in (".jpg", ".jpeg", ".png", ".webp"):
        return np.asarray(Image.open(fonte).convert("RGB")), 0.0, 1.0
    import cv2
    det = rosto.Detector()
    dur = _dur(fonte)
    melhor = (None, 0.0, -1.0)
    for i in range(amostras):
        t = evitar_inicio + (dur - evitar_inicio - 0.3) * (i + 0.5) / amostras
        if any(abs(t - e) < distancia for e in excluir):
            continue
        q = _quadro(fonte, t, 480)
        h, w = q.shape[:2]
        rs = det(q)
        nitidez = float(cv2.Laplacian(cv2.cvtColor(q, cv2.COLOR_RGB2GRAY), cv2.CV_64F).var())
        if rs:
            x, y, a, b, c = rs[0]
            centro = 1 - abs((x + a / 2) / w - 0.5)
            pont = c * (b / h) * centro * np.log1p(nitidez)
        else:
            pont = 0.05 * np.log1p(nitidez)
        if pont > melhor[2]:
            melhor = (None, t, pont)
    t = melhor[1]
    return _quadro(fonte, t), t, round(float(melhor[2]), 3)


def _salvar_rgb(rgb, arq):
    Image.fromarray(rgb).save(arq, quality=92)
    return Path(arq)


CSS_CAPA = """
.capa {{ position: relative; width: 1080px; height: 1920px; overflow: hidden; }}
.capa .bg {{ position: absolute; inset: 0; background: url('{bg}') center/cover; }}
.capa .vel {{ position: absolute; inset: 0; background: linear-gradient(180deg, rgba(0,0,0,0) 30%, rgba(0,0,0,.25) 52%,
  rgba(0,0,0,.82) 78%, rgba(0,0,0,.9) 100%); }}
.capa .bloco {{ position: absolute; left: 90px; right: 90px; top: 1080px; }}
.capa .rot {{ font-size: 34px; font-weight: 800; letter-spacing: 7px; color: var(--acento); text-transform: uppercase;
  margin-bottom: 26px; }}
.capa .tit {{ font-family: '{fonte}', sans-serif; font-weight: 800; font-size: {tam}px; line-height: 1.02; color: #fff;
  letter-spacing: -1px; text-shadow: 0 6px 30px rgba(0,0,0,.5); }}
.capa .tit mark {{ background: none; color: var(--acento); padding: 0; }}
/* opção B: manchete em caixa branca (outro estilo, para o cliente escolher) */
.capa .b .vel {{ background: linear-gradient(180deg, rgba(0,0,0,0) 45%, rgba(0,0,0,.45) 100%); }}
.capa .b .bloco {{ top: 1120px; }}
.capa .b .rot {{ display: table; background: var(--acento); color: #fff; padding: 10px 18px; letter-spacing: 5px; margin-bottom: 22px; }}
.capa .b .tit {{ display: inline; background: #fff; color: #111; line-height: 1.32; padding: 4px 20px; text-shadow: none;
  -webkit-box-decoration-break: clone; box-decoration-break: clone; }}
.capa .b .tit mark {{ color: var(--acento); }}
"""

CSS_THUMB = """
.th {{ position: relative; width: 1280px; height: 720px; overflow: hidden; background: var(--escuro); }}
.th .bg {{ position: absolute; inset: 0; background: url('{bg}') center/cover; }}
.th .vel {{ position: absolute; inset: 0; background: linear-gradient(90deg, rgba(0,0,0,.88) 0%, rgba(0,0,0,.66) 45%,
  rgba(0,0,0,.4) 100%); }}
.th .pessoa {{ position: absolute; right: -10px; bottom: 0; height: 700px; filter: drop-shadow(0 10px 40px rgba(0,0,0,.6)); }}
.th .txt {{ position: absolute; left: 64px; top: 70px; width: 690px; }}
.th .rot {{ display: inline-block; background: var(--acento); color: #111; font-weight: 900; font-size: 30px;
  letter-spacing: 3px; padding: 8px 18px; border-radius: 8px; margin-bottom: 22px; text-transform: uppercase; }}
.th .tit {{ font-family: '{fonte}', sans-serif; font-weight: 900; font-size: 116px; line-height: .98; color: #fff;
  text-transform: uppercase; -webkit-text-stroke: 3px #000; paint-order: stroke fill;
  text-shadow: 0 8px 0 rgba(0,0,0,.35); }}
.th .tit mark {{ background: none; color: var(--acento); padding: 0; }}
"""


def _tam_titulo(titulo):
    n = len(titulo.replace("==", "").split())
    return 104 if n <= 6 else 88 if n <= 9 else 76


def capa_reels(fonte, titulo, pasta, perfil=None, rotulo="", fonte_titulo="Inter", opcoes=2):
    """Capa de Reels 9:16 + prévia da grade 3:4. `opcoes=2` (R18): uma segunda capa com outro momento do vídeo
    (`capa_reels_B.png`) para o cliente escolher; a principal continua `capa_reels.png`."""
    pasta = Path(pasta)
    pasta.mkdir(parents=True, exist_ok=True)
    p = _perfis.carregar(perfil)
    idv = identidade(p)
    usados, nomes, pts = [], [], []
    for n in range(max(1, opcoes)):
        rgb, t, pont = melhor_quadro(fonte, excluir=usados)
        if n and t in usados:
            break
        suf = "" if n == 0 else f"_{chr(65 + n)}"
        bg = _salvar_rgb(rgb, pasta / f"capa_quadro{suf}.jpg")
        corpo = ('<div class="bg"></div><div class="vel"></div><div class="bloco">'
                 + (f'<div class="rot">{_esc(rotulo)}</div>' if rotulo else "")
                 + f'<div class="tit">{_esc(titulo)}</div></div>')
        if n:
            corpo = f'<div class="b">{corpo}</div>'
        png = renderizar(pagina(corpo, idv, 1080, 1920, CSS_CAPA.format(bg=bg.resolve().as_uri(), fonte=fonte_titulo,
                                                                     tam=_tam_titulo(titulo)), "capa"),
                         pasta / f"capa_reels{suf}.png", 1080, 1920)
        Image.open(png).crop((0, 240, 1080, 1680)).save(pasta / f"capa_grade{suf}.png")
        usados.append(t)
        nomes.append(png.name)
        pts.append(pont)
    al = []
    if len(titulo.replace("==", "").split()) > 8:
        al.append("título da capa com mais de 8 palavras: a grade fica ilegível")
    rel = {"capa": nomes[0], "grade": "capa_grade.png", "quadro_t": round(usados[0], 2), "pontuacao": pts[0],
           "opcoes": nomes, "quadros_t": [round(x, 2) for x in usados], "alertas": al}
    (pasta / "capa.json").write_text(json.dumps(rel, ensure_ascii=False, indent=1), encoding="utf-8")
    return rel


def thumbnail(fonte, texto, pasta, perfil=None, rotulo="", fonte_titulo="Inter"):
    from ..video import recorte
    pasta = Path(pasta)
    pasta.mkdir(parents=True, exist_ok=True)
    p = _perfis.carregar(perfil)
    idv = identidade(p)
    rgb, t, pont = melhor_quadro(fonte)
    im = Image.fromarray(rgb)
    # fundo: o próprio quadro, desfocado
    bg = pasta / "thumb_fundo.jpg"
    im.filter(ImageFilter.GaussianBlur(18)).save(bg, quality=90)
    # pessoa recortada, enquadrada do peito para cima
    m = recorte.matte_imagem(rgb)
    rgba = np.dstack([rgb, (m * 255).astype(np.uint8)])
    ys, xs = np.where(m > 0.5)
    if len(xs):
        x0, x1 = xs.min(), xs.max()
        y0 = ys.min()
        alt = int((x1 - x0) * 1.15)
        rgba = rgba[y0:min(rgb.shape[0], y0 + alt), max(0, x0 - 20):x1 + 20]
    pessoa = pasta / "thumb_pessoa.png"
    Image.fromarray(rgba).save(pessoa)
    palavras = texto.replace("==", "").split()
    al = [] if len(palavras) <= 5 else [f"{len(palavras)} palavras: thumbnails com 1-5 palavras têm CTR maior (R14)"]
    corpo = (f'<div class="bg"></div><div class="vel"></div><img class="pessoa" src="{pessoa.resolve().as_uri()}">'
             f'<div class="txt">' + (f'<div class="rot">{_esc(rotulo)}</div>' if rotulo else "")
             + f'<div class="tit">{_esc(texto)}</div></div>')
    png = renderizar(pagina(corpo, idv, 1280, 720, CSS_THUMB.format(bg=bg.resolve().as_uri(), fonte=fonte_titulo), "th"),
                     pasta / "thumbnail.png", 1280, 720)
    jpg = pasta / "thumbnail.jpg"
    Image.open(png).convert("RGB").save(jpg, quality=90)
    if jpg.stat().st_size > 2e6:
        al.append("thumbnail acima de 2 MB")
    # prévia no tamanho em que o celular mostra (≈ 168×94): o texto precisa continuar legível
    Image.open(png).resize((168, 94), Image.LANCZOS).save(pasta / "thumbnail_mini.png")
    rel = {"thumbnail": jpg.name, "mini": "thumbnail_mini.png", "quadro_t": round(t, 2), "pontuacao": pont, "alertas": al}
    (pasta / "thumbnail.json").write_text(json.dumps(rel, ensure_ascii=False, indent=1), encoding="utf-8")
    return rel
