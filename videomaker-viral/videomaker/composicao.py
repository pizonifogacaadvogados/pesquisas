"""Composição de pessoa recortada sobre fundo, com as técnicas de um compositor profissional.

O que faz um recorte parecer "colado" (diagnóstico da versão 2) e o que este módulo faz contra:
  1. Cor diferente entre pessoa e fundo (pretos, brancos, temperatura)  → `casar_cor`
  2. Borda dura, sem a luz do ambiente "abraçando" a pessoa              → `light_wrap` (filtro)
  3. Fundo nítido demais ou sintético demais                              → `placa_de_fundo` (foto real
     com desfoque de lente, bokeh e leve queda de luz) — o fundo procedural fica como reserva
  4. Pessoa e fundo com texturas diferentes                               → grão comum depois da composição
     (já feito no render) e o mesmo LUT sobre tudo

Referências: Nuke/After Effects "Light Wrap", Ron Brinkmann, *The Art and Science of Digital
Compositing*; registro R11.22.
"""
import subprocess
from pathlib import Path

import numpy as np
from PIL import Image, ImageFilter

W, H = 1080, 1920


def _quadros(video, n=8, lado=320, gray=False):
    dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0",
                                str(video)], capture_output=True, text=True).stdout.strip() or 1)
    out = []
    for i in range(n):
        t = dur * (i + 0.5) / n
        raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{t:.3f}", "-i", str(video), "-frames:v", "1",
                              "-vf", f"scale={lado}:{lado}", "-f", "rawvideo", "-pix_fmt", "gray" if gray else "rgb24",
                              "-"], capture_output=True).stdout
        if raw:
            out.append(np.frombuffer(raw, np.uint8).reshape(lado, lado, *(() if gray else (3,))).astype(np.float32) / 255)
    return out


def _lin(c):
    return np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)


def casar_cor(video, matte, fundo_png, forca=0.45):
    # Regra de compositor: o ambiente "manda" nas SOMBRAS; nos médios (pele) o ajuste é mínimo (±4%),
    # senão o rosto fica azulado/arroxeado (erro visto no 1º teste v3, fundo azul-noite).
    """Mede a pessoa (dentro do matte) e o fundo e devolve um filtro ffmpeg que aproxima a pessoa
    do ambiente: equilíbrio de cor (ganho por canal), nível de preto e brilho médio.
    `forca` 0-1: quanto puxar (0,4-0,5 é o ponto de um compositor: integra sem apagar a pele)."""
    vq, mq = _quadros(video), _quadros(matte, gray=True)
    px = np.concatenate([v[m > 0.9] for v, m in zip(vq, mq)]) if vq else np.zeros((1, 3))
    bg = np.asarray(Image.open(fundo_png).convert("RGB").resize((270, 480)), np.float32).reshape(-1, 3) / 255
    # tom: média em luz linear (cinza do mundo) de pessoa e fundo
    mp, mb = _lin(px).mean(0) + 1e-4, _lin(bg).mean(0) + 1e-4
    tint_p, tint_b = mp / mp.mean(), mb / mb.mean()
    ganho = (tint_b / tint_p) ** forca
    ganho = ganho / ganho.mean()
    sombra = np.clip((ganho - 1) * 0.5, -0.08, 0.08)       # tinta forte nas sombras (colorbalance)
    ganho = np.clip(1 + (ganho - 1) * 0.25, 0.96, 1.04)     # pele quase intacta
    # pretos: a pessoa não pode ter preto mais "fundo" que o ambiente (sinal clássico de recorte)
    preto_p = np.percentile(px.mean(1), 2)
    preto_b = np.percentile(bg.mean(1), 2)
    elevar = float(np.clip((preto_b - preto_p) * forca, 0, 0.06))
    # exposição: fundo escuro de estúdio → pessoa um pouco abaixo (sem matar o rosto)
    lum_p, lum_b = float(np.median(px.mean(1))), float(np.median(bg.mean(1)))
    brilho = float(np.clip((lum_b - lum_p) * 0.18 * forca / 0.45, -0.06, 0.02))
    r, g, b = (float(x) for x in ganho)
    rs, gs, bs = (float(x) for x in sombra)
    filtro = (f"colorbalance=rs={rs:.3f}:gs={gs:.3f}:bs={bs:.3f},"
              f"colorchannelmixer=rr={r:.3f}:gg={g:.3f}:bb={b:.3f},"
              f"colorlevels=romin={elevar:.3f}:gomin={elevar:.3f}:bomin={elevar:.3f},"
              f"eq=brightness={brilho:.3f}")
    return filtro, {"ganho_rgb": [round(r, 3), round(g, 3), round(b, 3)],
                    "sombras_rgb": [round(rs, 3), round(gs, 3), round(bs, 3)], "elevar_pretos": round(elevar, 3),
                    "brilho": round(brilho, 3), "lum_pessoa": round(lum_p, 3), "lum_fundo": round(lum_b, 3)}


def filtro_matte(motor):
    """Tratamento do matte conforme o motor. RVM já entrega alpha de vídeo limpo (cabelo semi-transparente):
    só um encolhimento de 1 px para tirar a franja da parede antiga. rembg precisa de contraste e erosão."""
    if motor == "rvm":
        return "format=gray,lut=y='clip((val-10)*1.04,0,255)',erosion,gblur=sigma=0.7"
    return "format=gray,lut=y='clip((val-150)*2.6+128,0,255)',erosion,erosion,gblur=sigma=1.6"


def light_wrap(bg, matte, pessoa_comp, saida, largura=7, forca=0.35):
    """Trecho de filtergraph: espalha a luz desfocada do fundo sobre a borda interna da pessoa.
    Entradas: rótulos [bg] (fundo), [matte] (cinza) e [pessoa_comp] (fundo+pessoa já compostos).
    Faixa de borda = matte × (1 − blur(matte)); luz = blur forte do fundo; mistura em modo Tela."""
    return (f"[{matte}]split[lwm0][lwm1];[lwm1]gblur=sigma={largura},negate[lwinv];"
            f"[lwm0][lwinv]blend=all_mode=multiply,lut=y='clip(val*{2.2 * forca:.2f},0,255)'[lwfaixa];"
            f"[{bg}]gblur=sigma={largura * 1.6:.0f},format=yuva420p[lwluz0];[lwluz0][lwfaixa]alphamerge[lwluz];"
            f"[{pessoa_comp}][lwluz]overlay=0:0:format=auto[{saida}]")


def placa_de_fundo(foto, destino, desfoque=14, escurecer=0.82, centro_y=0.40):
    """Foto real (escritório, gabinete, estante, plenário vazio…) → placa 1080×1920 como se filmada com
    lente clara: corte 9:16, desfoque de lente com realce de luzes (bokeh), queda de luz nas bordas."""
    destino = Path(destino)
    im = Image.open(foto).convert("RGB")
    esc = max(W / im.width, H / im.height)
    im = im.resize((round(im.width * esc), round(im.height * esc)), Image.LANCZOS)
    x0 = (im.width - W) // 2
    y0 = int(np.clip(im.height * centro_y - H * 0.5, 0, im.height - H))
    im = im.crop((x0, y0, x0 + W, y0 + H))
    a = np.asarray(im, np.float32) / 255
    # desfoque de lente: borra em luz linear e devolve, para as luzes "abrirem" em bokeh
    lin = _lin(a)
    luzes = np.clip(lin - 0.6, 0, None) * 3.0
    base = Image.fromarray((np.clip(lin, 0, 1) ** (1 / 2.2) * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(desfoque))
    bok = Image.fromarray((np.clip(luzes, 0, 1) * 255).astype(np.uint8)).filter(ImageFilter.BoxBlur(desfoque * 0.9))
    out = _lin(np.asarray(base, np.float32) / 255) + _lin(np.asarray(bok, np.float32) / 255) * 0.5
    yy, xx = np.mgrid[0:H, 0:W]
    queda = 1 - 0.35 * (((xx - W / 2) / (W / 2)) ** 2 * 0.6 + ((yy - H * 0.42) / (H / 2)) ** 2 * 0.4)
    out = np.clip(out * escurecer * queda[..., None], 0, 1) ** (1 / 2.2)
    destino.parent.mkdir(parents=True, exist_ok=True)
    Image.fromarray((out * 255).astype(np.uint8)).save(destino)
    return destino
