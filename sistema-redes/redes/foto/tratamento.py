"""Tratamento de imagem para redes: fotos do autor, fotos de evento, prints de notícia/decisão.

  tratar(foto, formato)      corrige orientação (EXIF), enquadra no formato pelo rosto (olhos no terço superior),
                             equilibra cor e exposição (suave), aplica o look do perfil (LUT .cube) e nitidez leve
  recortar_pessoa(foto)      PNG com transparência (RVM) para capas, thumbnails e composições
  anonimizar(img, caixas)    desfoca ou tarja áreas (nomes, CPF, rostos de terceiros) — LGPD; as caixas são
                             marcadas por quem revisa (o Claude lê a imagem e informa as coordenadas)
  moldura_print(img)         print com cantos arredondados, sombra, fundo da identidade e linha de fonte/data
"""
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps

from ..nucleo import caminhos, rosto  # noqa: F401
from ..nucleo import perfis as _perfis
from .motor import FORMATOS, identidade


def _abrir(foto):
    im = Image.open(foto)
    return ImageOps.exif_transpose(im).convert("RGB")


def enquadrar(im, w, h):
    """Recorte w:h guiado pelo rosto: olhos ~ no terço superior, rosto centralizado na horizontal."""
    rgb = np.asarray(im)
    H, W = rgb.shape[:2]
    alvo = w / h
    cw, ch = (W, int(W / alvo)) if W / H < alvo else (int(H * alvo), H)
    cw, ch = min(cw, W), min(ch, H)
    try:
        rs = rosto.Detector()(rgb)
    except RuntimeError:
        rs = []
    if rs:
        x, y, a, b, _ = rs[0]
        cx, olhos = x + a / 2, y + b * 0.4
        x0 = int(np.clip(cx - cw / 2, 0, W - cw))
        y0 = int(np.clip(olhos - ch / 3, 0, H - ch))
    else:
        x0, y0 = (W - cw) // 2, int((H - ch) * 0.35)
    return im.crop((x0, y0, x0 + cw, y0 + ch)).resize((w, h), Image.LANCZOS), bool(rs)


def corrigir(im, forca=0.6):
    """Equilíbrio de cor (cinza do mundo, parcial) + níveis 0,5-99,5% (suave). Não 'estoura' a pele."""
    a = np.asarray(im, np.float32) / 255
    media = a.reshape(-1, 3).mean(0) + 1e-4
    ganho = (media.mean() / media) ** (0.5 * forca)
    a = np.clip(a * ganho, 0, 1)
    lo, hi = np.percentile(a, 0.5), np.percentile(a, 99.5)
    if hi - lo > 0.2:
        b = (a - lo) / (hi - lo)
        a = a + (b - a) * forca
    return Image.fromarray((np.clip(a, 0, 1) * 255).astype(np.uint8))


def aplicar_look(im, look, intensidade=0.7):
    """Aplica o mesmo look de cor dos vídeos do perfil (`video/luts.py`): fotos e vídeos com a mesma cara."""
    from ..video import luts
    orig = np.asarray(im, np.float32) / 255
    out = luts.aplicar(orig, luts.LOOKS[look])
    return Image.fromarray((np.clip(orig + (out - orig) * intensidade, 0, 1) * 255).astype(np.uint8))


def tratar(foto, pasta, formatos=("4x5",), perfil=None, look=None, nome=None):
    """Foto → uma versão tratada por formato. Devolve {formato: caminho} e alertas."""
    pasta = Path(pasta)
    pasta.mkdir(parents=True, exist_ok=True)
    p = _perfis.carregar(perfil)
    from ..video import estilos
    look = look or estilos.ESTILOS.get(p.get("estilo_video") if p.get("estilo_video") != "auto" else "estudio",
                                       estilos.ESTILOS["estudio"])["look"]
    im = corrigir(_abrir(foto))
    im = aplicar_look(im, look)
    im = im.filter(ImageFilter.UnsharpMask(radius=1.2, percent=60, threshold=2))
    saidas, alertas = {}, []
    if min(im.size) < 1080:
        alertas.append(f"foto com {im.size[0]}x{im.size[1]}: abaixo de 1080 px no lado menor (vai perder nitidez)")
    for fmt in formatos:
        w, h = FORMATOS[fmt]
        q, achou = enquadrar(im, w, h)
        if not achou:
            alertas.append(f"{fmt}: nenhum rosto detectado; recorte central")
        arq = pasta / f"{nome or Path(foto).stem}_{fmt}.jpg"
        q.save(arq, quality=92, subsampling=0)
        saidas[fmt] = arq
    return {"arquivos": {k: str(v) for k, v in saidas.items()}, "look": look, "alertas": alertas}


def recortar_pessoa(foto, destino):
    from ..video import recorte
    rgb = np.asarray(_abrir(foto))
    m = recorte.matte_imagem(rgb)
    Image.fromarray(np.dstack([rgb, (m * 255).astype(np.uint8)])).save(destino)
    return Path(destino)


def anonimizar(img, caixas, destino, modo="desfoque"):
    """`caixas`: lista de (x, y, w, h) em px ou frações 0-1 da imagem. `modo`: desfoque | tarja."""
    im = _abrir(img)
    W, H = im.size
    for x, y, w, h in caixas:
        if max(x, y, w, h) <= 1:
            x, y, w, h = x * W, y * H, w * W, h * H
        box = tuple(int(v) for v in (x, y, x + w, y + h))
        if modo == "tarja":
            ImageDraw.Draw(im).rectangle(box, fill=(0, 0, 0))
        else:
            reg = im.crop(box)
            pequeno = reg.resize((max(1, reg.width // 18), max(1, reg.height // 18)), Image.BILINEAR)
            im.paste(pequeno.resize(reg.size, Image.NEAREST).filter(ImageFilter.GaussianBlur(4)), box)
    im.save(destino, quality=92)
    return Path(destino)


def moldura_print(img, destino, perfil=None, fonte="", data="", largura=1080, altura=1350):
    """Print sobre o fundo da identidade, com sombra, cantos arredondados e a linha 'Fonte: X · data'."""
    idv = identidade(_perfis.carregar(perfil))
    im = _abrir(img)
    margem = 80
    esc = min((largura - 2 * margem) / im.width, (altura - 2 * margem - 120) / im.height)
    im = im.resize((int(im.width * esc), int(im.height * esc)), Image.LANCZOS)
    fundo = Image.new("RGB", (largura, altura), idv["fundo"])
    x, y = (largura - im.width) // 2, (altura - 120 - im.height) // 2
    mascara = Image.new("L", im.size, 0)
    ImageDraw.Draw(mascara).rounded_rectangle((0, 0, *im.size), 22, fill=255)
    sombra = Image.new("L", (largura, altura), 0)
    ImageDraw.Draw(sombra).rounded_rectangle((x, y + 18, x + im.width, y + 18 + im.height), 22, fill=110)
    fundo.paste(Image.new("RGB", fundo.size, (0, 0, 0)), (0, 0), sombra.filter(ImageFilter.GaussianBlur(30)))
    fundo.paste(im, (x, y), mascara)
    if fonte or data:
        f = ImageFont.truetype(str(caminhos.FONTES / "Inter.ttf"), 30)
        txt = "Fonte: " + " · ".join(v for v in (fonte, data) if v)
        ImageDraw.Draw(fundo).text((margem, altura - 100), txt, fill=idv["sutil"], font=f)
    fundo.save(destino, quality=92)
    return Path(destino)
