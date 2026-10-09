"""Fundos de estúdio virtual gerados por código (sem banco de imagens).

Cada fundo é uma imagem 1080×1920 pensada para ficar ATRÁS da pessoa recortada:
escura, com profundidade (bokeh desfocado), luz de fundo atrás da cabeça e vinheta.
Também é exportado como PNG para importar no CapCut.
"""
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

W, H = 1080, 1920

FUNDOS = {
    # base (topo→baixo), cor das luzes de bokeh, cor da luz atrás da cabeça
    "escritorio_noturno": dict(base=((14, 22, 38), (6, 9, 16)), bokeh=[(255, 190, 120), (255, 214, 160), (120, 160, 255)],
                               luz=(70, 95, 140), n_bokeh=38, estantes=True),
    "biblioteca": dict(base=((40, 26, 18), (14, 9, 7)), bokeh=[(255, 196, 120), (255, 170, 90)],
                       luz=(120, 82, 50), n_bokeh=26, estantes=True),
    "neutro_premium": dict(base=((38, 40, 44), (14, 15, 17)), bokeh=[(200, 205, 215)], luz=(90, 94, 102),
                           n_bokeh=14, estantes=False),
    "marca_azul": dict(base=((16, 38, 74), (6, 14, 30)), bokeh=[(120, 180, 255), (255, 255, 255)], luz=(60, 110, 190),
                       n_bokeh=30, estantes=False),
    "noticia_vermelho": dict(base=((70, 10, 16), (18, 4, 8)), bokeh=[(255, 80, 80), (255, 255, 255)], luz=(140, 30, 40),
                             n_bokeh=22, estantes=False),
}


def gerar(nome, destino, semente=3):
    p = FUNDOS[nome]
    destino = Path(destino)
    if destino.exists():
        return destino
    rng = np.random.default_rng(semente)
    y = np.linspace(0, 1, H)[:, None, None]
    topo, base = np.array(p["base"][0], float), np.array(p["base"][1], float)
    img = np.broadcast_to(topo * (1 - y) + base * y, (H, W, 3)).copy()

    camada = Image.new("RGB", (W, H), (0, 0, 0))
    d = ImageDraw.Draw(camada)
    if p["estantes"]:  # lombadas de livros/estantes, depois desfocadas: dá textura de ambiente
        for linha in range(5):
            y0 = 260 + linha * 290
            x = -20
            while x < W:
                larg = int(rng.integers(18, 46))
                alt = int(rng.integers(170, 240))
                tom = np.array(p["base"][0]) * rng.uniform(1.4, 3.2)
                d.rectangle([x, y0 + 240 - alt, x + larg, y0 + 240], fill=tuple(np.clip(tom, 0, 255).astype(int)))
                x += larg + int(rng.integers(2, 6))
            d.rectangle([0, y0 + 240, W, y0 + 256], fill=tuple(np.clip(np.array(p["base"][0]) * 2.2, 0, 255).astype(int)))
        camada = camada.filter(ImageFilter.GaussianBlur(14))
    bokeh = Image.new("RGB", (W, H), (0, 0, 0))
    db = ImageDraw.Draw(bokeh)
    colocados = 0
    while colocados < p["n_bokeh"]:
        cx, cy = rng.uniform(0, W), rng.uniform(0, H * 0.7)
        if 0.28 * W < cx < 0.72 * W and 0.12 * H < cy < 0.62 * H:  # nada atrás da cabeça
            continue
        r = rng.uniform(14, 52)
        cor = np.array(p["bokeh"][rng.integers(len(p["bokeh"]))]) * rng.uniform(0.10, 0.30)
        db.ellipse([cx - r, cy - r, cx + r, cy + r], fill=tuple(cor.astype(int)))
        colocados += 1
    bokeh = bokeh.filter(ImageFilter.GaussianBlur(16))

    img = img + np.asarray(camada, float) * 0.55 + np.asarray(bokeh, float)
    # luz suave atrás da cabeça (separa a pessoa do fundo)
    yy, xx = np.mgrid[0:H, 0:W]
    luz = np.exp(-(((xx - W / 2) / (W * 0.42)) ** 2 + ((yy - H * 0.36) / (H * 0.22)) ** 2))[..., None]
    img = img + luz * np.array(p["luz"], float) * 0.9
    # vinheta
    vin = 1 - 0.55 * np.clip(((xx - W / 2) / (W * 0.75)) ** 2 + ((yy - H / 2) / (H * 0.65)) ** 2, 0, 1)
    img = img * vin[..., None]
    # granulação fina para não "bandear" o degradê
    img = img + rng.normal(0, 1.6, img.shape)
    destino.parent.mkdir(parents=True, exist_ok=True)
    Image.fromarray(np.clip(img, 0, 255).astype(np.uint8)).save(destino)
    return destino
