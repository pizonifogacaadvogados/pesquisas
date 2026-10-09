"""Gera LUTs 3D (.cube) a partir de parâmetros de look (estudos/08 §4, 09).

O mesmo arquivo serve para o render (ffmpeg lut3d) e para importar no CapCut
(Ajustar → LUT → Importar), garantindo a mesma cor nos dois caminhos.
"""
from pathlib import Path

import numpy as np

LOOKS = {
    # contraste: força da curva S; sombras/realces: tom RGB somado; sat: multiplicador
    "neutro": dict(contraste=0.10, sat=1.02, sombras=(0, 0, 0), realces=(0, 0, 0), preto=0.0, pele=0.0),
    "teal_orange": dict(contraste=0.18, sat=1.05, sombras=(-0.03, 0.01, 0.04), realces=(0.035, 0.012, -0.03),
                        preto=0.012, pele=0.03),
    "teal_orange_forte": dict(contraste=0.26, sat=1.08, sombras=(-0.05, 0.015, 0.065), realces=(0.05, 0.015, -0.045),
                              preto=0.02, pele=0.04),
    "filme_quente": dict(contraste=0.14, sat=0.88, sombras=(0.015, 0.0, -0.02), realces=(0.04, 0.02, -0.03),
                         preto=0.045, pele=0.02),
    "noticia_frio": dict(contraste=0.22, sat=1.0, sombras=(-0.01, 0.0, 0.025), realces=(0.0, 0.005, 0.015),
                         preto=0.0, pele=0.0),
    "vivo": dict(contraste=0.14, sat=1.15, sombras=(0, 0, 0.01), realces=(0.01, 0.005, 0), preto=0.0, pele=0.01),
}


def _curva_s(x, forca):
    """Curva S suave centrada em 0,5 (mistura com smoothstep)."""
    s = x * x * (3 - 2 * x)
    return x + (s - x) * forca * 2


def aplicar(rgb, p):
    """rgb: array (...,3) em 0..1 → rgb ajustado."""
    x = np.clip(rgb, 0, 1)
    x = _curva_s(x, p["contraste"])
    lum = (0.2126 * x[..., 0] + 0.7152 * x[..., 1] + 0.0722 * x[..., 2])[..., None]
    # split toning: sombras frias / realces quentes, ponderado pela luminância
    peso_s = np.clip(1 - lum * 2, 0, 1)
    peso_r = np.clip(lum * 2 - 1, 0, 1)
    x = x + peso_s * np.array(p["sombras"]) + peso_r * np.array(p["realces"])
    # proteção/realce de pele: tons laranja (r>g>b) recebem leve aquecimento
    laranja = np.clip((x[..., 0] - x[..., 2]) * 2, 0, 1)[..., None] * np.clip(1 - np.abs(lum - 0.55) * 2.2, 0, 1)
    x = x + laranja * np.array([p["pele"], p["pele"] * 0.45, -p["pele"] * 0.3])
    # saturação
    lum = (0.2126 * x[..., 0] + 0.7152 * x[..., 1] + 0.0722 * x[..., 2])[..., None]
    x = lum + (x - lum) * p["sat"]
    # pretos levantados (filme)
    x = p["preto"] + x * (1 - p["preto"])
    return np.clip(x, 0, 1)


def gerar_cube(look, destino, tamanho=33):
    p = LOOKS[look]
    destino = Path(destino)
    destino.parent.mkdir(parents=True, exist_ok=True)
    g = np.linspace(0, 1, tamanho)
    # ordem .cube: R varia mais rápido
    b, gg, r = np.meshgrid(g, g, g, indexing="ij")
    rgb = np.stack([r, gg, b], axis=-1).reshape(-1, 3)
    out = aplicar(rgb, p)
    linhas = [f'TITLE "videomaker {look}"', f"LUT_3D_SIZE {tamanho}", "DOMAIN_MIN 0.0 0.0 0.0", "DOMAIN_MAX 1.0 1.0 1.0"]
    linhas += [f"{v[0]:.6f} {v[1]:.6f} {v[2]:.6f}" for v in out]
    destino.write_text("\n".join(linhas) + "\n", encoding="ascii")
    return destino
