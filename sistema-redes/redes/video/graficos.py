"""Gráficos profissionais (estudos/08 §3, 07 T3/T6, 10 §4).

- legendas: premium (frase), viral (palavra a palavra), forte (notícia)
- aberturas: tipografia cinética, cinética mono (documental), manchete, título limpo, texto atrás da pessoa
- lower third com linha que se desenha (máscara animada)
- cartão de lei/dado (PNG) e carimbos de checagem
- trilha de luz (light leaks e flashes) para mesclar em modo Tela
"""
import re
import subprocess
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont
from ..nucleo import caminhos

W, H = 1080, 1920
RAIZ = caminhos.RAIZ
FONTES_DIR = caminhos.FONTES
ARQ_FONTE = {
    "Inter": "Inter.ttf", "Playfair Display": "PlayfairDisplay.ttf", "Bebas Neue": "BebasNeue-Regular.ttf",
    "Montserrat": "Montserrat.ttf", "Courier Prime": "CourierPrime-Bold.ttf", "DM Serif Display": "DMSerifDisplay-Regular.ttf",
    "Oswald": "Oswald.ttf", "Anton": "Anton-Regular.ttf",
}


# ------------------------------------------------------------------ utilidades ASS
def t_ass(s):
    s = max(s, 0)
    return f"{int(s // 3600)}:{int(s % 3600 // 60):02d}:{s % 60:05.2f}"


def esc(txt):
    return txt.replace("\\", "").replace("{", "(").replace("}", ")")


def cabecalho(estilos):
    linhas = ["[Script Info]", "ScriptType: v4.00+", f"PlayResX: {W}", f"PlayResY: {H}", "WrapStyle: 0",
              "ScaledBorderAndShadow: yes", "", "[V4+ Styles]",
              "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, "
              "Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, "
              "Alignment, MarginL, MarginR, MarginV, Encoding"]
    linhas += estilos
    linhas += ["", "[Events]", "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text"]
    return linhas


def estilo(nome, fonte, tam, cor="&H00FFFFFF", contorno="&H00000000", fundo="&H64000000", negrito=-1,
           borda=1, esp_contorno=0, sombra=0, alinh=2, mv=0, ml=60, mr=60, espaco=0):
    return (f"Style: {nome},{fonte},{tam},{cor},{cor},{contorno},{fundo},{negrito},0,0,0,100,100,{espaco},0,"
            f"{borda},{esp_contorno},{sombra},{alinh},{ml},{mr},{mv},1")


def dialogo(ini, fim, est, txt, camada=0):
    return f"Dialogue: {camada},{t_ass(ini)},{t_ass(fim)},{est},,0,0,0,,{txt}"


# ------------------------------------------------------------------ legendas
def blocos_frase(palavras, max_palavras=7, max_chars=32):
    """Agrupa palavras em blocos de frase (legenda premium): quebra em pontuação, pausa ou tamanho."""
    blocos, atual = [], []
    for n, w in enumerate(palavras):
        atual.append(w)
        prox = palavras[n + 1] if n + 1 < len(palavras) else None
        chars = sum(len(x["w"]) + 1 for x in atual)
        if prox is None or re.search(r"[.!?;:…]$", w["w"]) or len(atual) >= max_palavras or chars >= max_chars \
                or prox["ini"] - w["fim"] > 0.35 or (re.search(r",$", w["w"]) and len(atual) >= 3):
            blocos.append(atual)
            atual = []
    return blocos


def legendas(palavras, tipo, fonte, cor_destaque, delta_tam=0):
    """Retorna (estilos, linhas) da legenda no estilo pedido."""
    out = []
    if tipo == "premium":
        est = [estilo("Leg", fonte, 70 + delta_tam, contorno="&H50000000", fundo="&H96000000", borda=1, esp_contorno=2.2,
                      sombra=2, mv=500, ml=110, mr=110)]   # R18: barra do Reels cresceu (fim de 2025), ≥ 480 px
        for b in blocos_frase(palavras):
            ini, fim = b[0]["ini"], b[-1]["fim"] + 0.12
            for k, atual in enumerate(b):
                a = ini if k == 0 else atual["ini"]
                z = b[k + 1]["ini"] if k + 1 < len(b) else fim
                if z - a < 0.02:
                    continue
                partes = []
                for m, p in enumerate(b):
                    w = esc(p["w"])
                    if m < k:
                        partes.append(w)
                    elif m == k:
                        partes.append(f"{{\\c{cor_destaque}&}}{w}{{\\c&H00FFFFFF&}}")
                    else:
                        partes.append(f"{{\\alpha&H70&}}{w}{{\\alpha&H00&}}")
                entrada = "{\\fad(90,0)\\blur0.6}" if k == 0 else "{\\blur0.6}"
                out.append(dialogo(a, z, "Leg", entrada + " ".join(partes)))
        return est, out
    if tipo == "forte":
        est = [estilo("Leg", fonte, 92 + delta_tam, contorno="&H00000000", borda=1, esp_contorno=5, sombra=0, mv=520, espaco=1)]
        for b in blocos_frase(palavras, max_palavras=3, max_chars=18):
            for k, atual in enumerate(b):
                a = b[0]["ini"] if k == 0 else atual["ini"]
                z = b[k + 1]["ini"] if k + 1 < len(b) else b[-1]["fim"] + 0.1
                partes = [(f"{{\\3c{cor_destaque}&\\bord14}}{esc(p['w'].upper())}{{\\3c&H00000000&\\bord5}}"
                           if m == k else esc(p["w"].upper())) for m, p in enumerate(b)]
                pop = "{\\fscx88\\fscy88\\t(0,80,\\fscx100\\fscy100)}" if k == 0 else ""
                out.append(dialogo(a, z, "Leg", pop + " ".join(partes)))
        return est, out
    # viral (versão 1): palavra a palavra, caixa alta
    est = [estilo("Leg", fonte, 100 + delta_tam, contorno="&H00000000", borda=1, esp_contorno=7, sombra=3, mv=600)]
    for b in blocos_frase(palavras, max_palavras=3, max_chars=16):
        for k, atual in enumerate(b):
            a = b[0]["ini"] if k == 0 else atual["ini"]
            z = b[k + 1]["ini"] if k + 1 < len(b) else b[-1]["fim"] + 0.1
            partes = [(f"{{\\c{cor_destaque}&\\fscx110\\fscy110}}{esc(p['w'].upper())}{{\\c&H00FFFFFF&\\fscx100\\fscy100}}"
                       if m == k else esc(p["w"].upper())) for m, p in enumerate(b)]
            pop = "{\\fscx82\\fscy82\\t(0,90,\\fscx100\\fscy100)}" if k == 0 else ""
            out.append(dialogo(a, z, "Leg", pop + " ".join(partes)))
    return est, out


# ------------------------------------------------------------------ aberturas
def abertura(tipo, texto, ini, fim, fonte_titulo, fonte_texto, cor_destaque, extra=None):
    """Retorna (estilos, linhas). Para 'texto_atras', as linhas vão no ASS de FUNDO (atrás da pessoa)."""
    extra = extra or {}
    est, out = [], []
    palavras = texto.split()
    if tipo in ("cinetica", "cinetica_mono"):
        est.append(estilo("Cin", fonte_titulo, 104, contorno="&H00000000", fundo="&H00000000", borda=1,
                          esp_contorno=0, sombra=0, alinh=5, ml=80, mr=80))
        linhas = _quebrar(palavras, 14)
        y0 = H * 0.30 - (len(linhas) - 1) * 62
        atraso = 0.0
        f = _fonte(fonte_titulo, 104)
        espaco = f.getlength(" ")
        for li, linha in enumerate(linhas):
            y = y0 + li * 124
            # cada palavra entra com desfoque→nítido, subindo 24px, com easing de saída
            larg_total = sum(f.getlength(w) for w in linha) + (len(linha) - 1) * espaco
            x = W / 2 - larg_total / 2
            for w in linha:
                lw = f.getlength(w)
                cx = x + lw / 2
                a = ini + atraso
                out.append(dialogo(a, fim, "Cin",
                                   f"{{\\an5\\move({cx:.0f},{y + 24:.0f},{cx:.0f},{y:.0f},0,260)\\blur9\\alpha&HFF&"
                                   f"\\t(0,260,0.5,\\blur0\\alpha&H00&)\\fad(0,220)}}{esc(w)}", camada=3))
                x += lw + espaco
                atraso += 0.11
        if tipo == "cinetica_mono" and extra.get("sobrelinha"):
            est.append(estilo("Mono", "Courier Prime", 40, cor="&H00D6E6F0", borda=1, esp_contorno=0, alinh=5))
            txt = esc(extra["sobrelinha"])
            for k in range(1, len(txt) + 1):  # efeito máquina de escrever
                a = ini + k * 0.035
                z = ini + (k + 1) * 0.035 if k < len(txt) else fim
                out.append(dialogo(a, z, "Mono", f"{{\\an5\\pos({W / 2:.0f},{y0 - 120:.0f})}}{txt[:k]}", camada=3))
    elif tipo == "texto_atras":
        # título grande, atrás da cabeça (desenhado no fundo, antes de sobrepor a pessoa)
        est.append(estilo("Atras", fonte_titulo, 230, cor="&H00F4F4F4", contorno="&H00000000", fundo="&H00000000",
                          borda=1, esp_contorno=0, sombra=0, alinh=5, espaco=2))
        linhas = _quebrar(palavras, 9)[:3]
        y0 = H * 0.24 - (len(linhas) - 1) * 105
        for li, linha in enumerate(linhas):
            y = y0 + li * 210
            out.append(dialogo(ini + li * 0.12, fim, "Atras",
                               f"{{\\an5\\pos({W / 2:.0f},{y:.0f})\\fscx92\\fscy92\\alpha&HFF&\\blur6"
                               f"\\t(0,420,0.4,\\fscx100\\fscy100\\alpha&H00&\\blur0)\\fad(0,300)}}"
                               f"{esc(' '.join(linha).upper())}", camada=1))
    elif tipo == "manchete":
        est.append(estilo("Faixa", "Bebas Neue", 64, cor="&H00FFFFFF", contorno="&H002A1AD9", fundo="&H002A1AD9",
                          borda=3, esp_contorno=16, alinh=7, ml=70, espaco=3))
        est.append(estilo("Manchete", fonte_titulo, 96, cor="&H00111111", contorno="&H00FFFFFF", fundo="&H00FFFFFF",
                          borda=3, esp_contorno=20, alinh=7, ml=70, mr=70))
        out.append(dialogo(ini, fim, "Faixa", f"{{\\pos(70,250)\\clip(0,0,0,1920)\\t(0,280,\\clip(0,0,1080,1920))}}"
                                              f"{esc(extra.get('rotulo', 'ANÁLISE'))}", camada=3))
        txt = "\\N".join(" ".join(l) for l in _quebrar(palavras, 18)[:3])
        out.append(dialogo(ini + 0.18, fim, "Manchete", f"{{\\pos(70,350)\\clip(0,0,0,1920)"
                                                         f"\\t(0,380,0.5,\\clip(0,0,1080,1920))}}{esc(txt).upper()}", camada=3))
    else:  # titulo_limpo / titulo_caixa
        caixa = tipo == "titulo_caixa"
        est.append(estilo("Tit", fonte_titulo, 84 if caixa else 76, cor="&H00FFFFFF", contorno="&H2E000000",
                          fundo="&H64000000", borda=3 if caixa else 1, esp_contorno=18 if caixa else 0,
                          sombra=0 if caixa else 3, alinh=8, mv=270, ml=90, mr=90))
        t = texto.upper() if caixa else texto
        out.append(dialogo(ini, fim, "Tit", f"{{\\fad(120,200)\\blur{0 if caixa else 0.5}\\move({W / 2:.0f},300,"
                                            f"{W / 2:.0f},270,0,300)\\an8}}{esc(t)}", camada=3))
    return est, out


def _quebrar(palavras, max_chars):
    linhas, atual = [], []
    for w in palavras:
        if atual and sum(len(x) + 1 for x in atual) + len(w) > max_chars:
            linhas.append(atual)
            atual = []
        atual.append(w)
    if atual:
        linhas.append(atual)
    return linhas


# ------------------------------------------------------------------ lower third
def lower_third(nome, cargo, ini, fim, fonte, cor_destaque):
    y = 1240
    est = [estilo("LTNome", fonte, 66, cor="&H00FFFFFF", borda=1, esp_contorno=0, sombra=2, fundo="&H78000000", alinh=7),
           estilo("LTCargo", fonte, 46, cor="&H00DDDDDD", borda=1, esp_contorno=0, sombra=1, fundo="&H78000000",
                  alinh=7, negrito=0),
           estilo("LTBarra", fonte, 10, cor=cor_destaque, borda=1, esp_contorno=0, alinh=7)]
    out = [
        # barra vertical que cresce (máscara animada) e depois o texto desliza
        dialogo(ini, fim, "LTBarra", f"{{\\pos(84,{y})\\p1\\clip(80,{y + 150},96,{y + 150})"
                                     f"\\t(0,260,0.5,\\clip(80,{y},96,{y + 150}))\\fad(0,250)}}m 0 0 l 10 0 10 150 0 150{{\\p0}}", 4),
        dialogo(ini + 0.15, fim, "LTNome", f"{{\\move(76,{y - 2},108,{y - 2},0,380)\\clip(100,0,1080,1920)"
                                           f"\\alpha&HFF&\\t(0,320,0.5,\\alpha&H00&)\\fad(0,250)}}{esc(nome)}", 4),
        dialogo(ini + 0.30, fim, "LTCargo", f"{{\\move(76,{y + 84},108,{y + 84},0,380)\\clip(100,0,1080,1920)"
                                            f"\\alpha&HFF&\\t(0,320,0.5,\\alpha&H00&)\\fad(0,250)}}{esc(cargo)}", 4),
    ]
    return est, out


def escrever_ass(caminho, estilos, linhas):
    vistos, est_unicos = set(), []
    for e in estilos:
        nome = e.split(",")[0]
        if nome not in vistos:
            vistos.add(nome)
            est_unicos.append(e)
    Path(caminho).write_text("\n".join(cabecalho(est_unicos) + linhas) + "\n", encoding="utf-8")


# ------------------------------------------------------------------ cartões (PNG)
def _fonte(nome, tam):
    arq = FONTES_DIR / ARQ_FONTE.get(nome, "Inter.ttf")
    try:
        return ImageFont.truetype(str(arq), tam)
    except OSError:
        return ImageFont.load_default()


def cartao(titulo, subtitulo, destino, tema="vidro", fonte_titulo="DM Serif Display", fonte_texto="Inter",
           cor=(232, 184, 74)):
    """Cartão de lei/dado. tema: 'vidro' (escuro translúcido) ou 'papel' (documental)."""
    larg, alt = 860, 330
    im = Image.new("RGBA", (larg + 60, alt + 60), (0, 0, 0, 0))
    sombra = Image.new("RGBA", im.size, (0, 0, 0, 0))
    ImageDraw.Draw(sombra).rounded_rectangle([30, 38, 30 + larg, 38 + alt], 28, fill=(0, 0, 0, 150))
    im.alpha_composite(sombra.filter(ImageFilter.GaussianBlur(16)))
    d = ImageDraw.Draw(im)
    if tema == "papel":
        papel = np.full((alt, larg, 3), (236, 228, 210), float) + np.random.default_rng(1).normal(0, 6, (alt, larg, 3))
        pimg = Image.fromarray(np.clip(papel, 0, 255).astype(np.uint8)).convert("RGBA")
        mascara = Image.new("L", (larg, alt), 0)
        ImageDraw.Draw(mascara).rounded_rectangle([0, 0, larg, alt], 10, fill=255)
        im.paste(pimg, (30, 30), mascara)
        cor_t, cor_s = (30, 26, 22, 255), (70, 62, 54, 255)
        # marca-texto atrás do título
        d.rectangle([70, 92, 70 + min(larg - 80, 40 + len(titulo) * 44), 168], fill=(255, 226, 90, 170))
    else:
        d.rounded_rectangle([30, 30, 30 + larg, 30 + alt], 28, fill=(14, 18, 26, 225), outline=(255, 255, 255, 40), width=2)
        d.rectangle([30, 30, 42, 30 + alt], fill=cor + (255,))
        cor_t, cor_s = (255, 255, 255, 255), (200, 206, 214, 255)
    d.text((76, 78), titulo, font=_fonte(fonte_titulo, 96), fill=cor_t)
    y = 200
    for linha in _quebrar(subtitulo.split(), 34)[:2]:
        d.text((80, y), " ".join(linha), font=_fonte(fonte_texto, 40), fill=cor_s)
        y += 54
    Path(destino).parent.mkdir(parents=True, exist_ok=True)
    im.save(destino)
    return destino


def carimbo(texto, destino, cor=(230, 40, 40)):
    """Carimbo de checagem (FALSO / VERDADE / FORA DE CONTEXTO)."""
    f = _fonte("Bebas Neue", 150)
    caixa = ImageDraw.Draw(Image.new("L", (1, 1))).textbbox((0, 0), texto, font=f)
    lw, lh = caixa[2] - caixa[0] + 80, caixa[3] - caixa[1] + 70
    im = Image.new("RGBA", (lw + 40, lh + 40), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([20, 20, 20 + lw, 20 + lh], 18, outline=cor + (255,), width=12)
    d.text((60, 30 - caixa[1] + 20), texto, font=f, fill=cor + (255,))
    im = im.rotate(-8, expand=True, resample=Image.BICUBIC)
    im.save(destino)
    return destino


# ------------------------------------------------------------------ trilha de luz
def trilha_luz(eventos, duracao, destino, fps=30, intensidade=1.0):
    """Vídeo preto com light leaks e flashes nos tempos pedidos, para mesclar em modo Tela.

    eventos: [{"t": 3.2, "tipo": "light_leak"|"flash"}]
    """
    lw, lh = 270, 480  # gerado em baixa resolução e ampliado (luz é suave)
    n = int(np.ceil(duracao * fps))
    yy, xx = np.mgrid[0:lh, 0:lw]
    rng = np.random.default_rng(5)
    params = []
    for e in eventos:
        cores = [(255, 140, 50), (255, 70, 40), (255, 200, 120)]
        params.append((e, rng.uniform(-0.2, 1.2, 3), rng.uniform(0.1, 0.9, 3), cores))
    proc = subprocess.Popen(["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{lw}x{lh}",
                             "-r", str(fps), "-i", "-", "-vf", f"scale={W}:{H}:flags=bicubic,gblur=sigma=6",
                             "-c:v", "libx264", "-crf", "20", "-pix_fmt", "yuv420p", str(destino)], stdin=subprocess.PIPE)
    preto = np.zeros((lh, lw, 3), np.uint8).tobytes()
    for i in range(n):
        t = i / fps
        quadro = None
        for e, xs, ys, cores in params:
            dt = t - e["t"]
            if e["tipo"] == "flash" and -0.04 <= dt <= 0.16:
                k = max(0.0, 1 - abs(dt) / 0.16) ** 1.5
                q = np.full((lh, lw, 3), 255.0 * k * 0.6)
            elif e["tipo"] == "light_leak" and -0.45 <= dt <= 0.75:
                k = np.sin(np.pi * (dt + 0.45) / 1.2) ** 2
                q = np.zeros((lh, lw, 3))
                for j in range(3):
                    lado = -0.25 if j % 2 == 0 else 1.25  # nasce fora do quadro, nas bordas
                    cx = (lado + (0.35 if lado < 0 else -0.35) * (dt + 0.45) / 1.2) * lw
                    cy = ys[j] * lh * 0.8
                    blob = np.exp(-(((xx - cx) / (lw * 0.45)) ** 2 + ((yy - cy) / (lh * 0.35)) ** 2))
                    q += blob[..., None] * np.array(cores[j], float) * k * 0.55
            else:
                continue
            quadro = q if quadro is None else quadro + q
        proc.stdin.write(preto if quadro is None else np.clip(quadro * intensidade, 0, 255).astype(np.uint8).tobytes())
    proc.stdin.close()
    proc.wait()
    return destino
