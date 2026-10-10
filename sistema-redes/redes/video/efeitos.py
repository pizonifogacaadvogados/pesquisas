"""Efeitos de "edição com IA" (registro R15): o repertório visual dos criadores que editam com Claude Code/Codex
(Tiago Lemos, André Nunes, edicaomia.com.br, castilho.ia), refeito em HyperFrames + GSAP e aplicado sobre
qualquer vídeo vertical 1080×1920 por uma lista de efeitos com tempo:

  OVERLAYS (transparentes, por cima do vídeo)
    titulo     kicker espaçado + título grande com gradiente e brilho ("AQUELE VÍDEO COM / EDIÇÃO INCRÍVEL")
    pergunta   card de pergunta no topo ("PERGUNTA · Dá para…?"), formato "você pergunta, eu respondo"
    card       card flutuante inclinado com imagem (print, post salvo, decisão) e etiqueta ("SALVO")
    hud        visão computacional com rastreamento REAL do rosto, olhos e boca (YuNet), rótulos e contador
  CENAS (ocupam a tela; o vídeo do trecho entra dentro da composição)
    camadas    perspectiva 3D: o quadro se abre em 5 camadas (fundo, recorte, legenda, ícones, título) e fecha
    lista      motion explicativo: título + itens que acendem no tempo da fala + apresentador em janela
    transcricao  linha do tempo da fala: palavras em blocos, forma de onda real, cursor e contador
  COR
    pb         trecho em preto e branco (ênfase), opcionalmente com título

Especificação (lista JSON), tempos em segundos do vídeo de entrada:
  [{"tipo": "titulo", "ini": 0, "fim": 3.2, "kicker": "AQUELE VÍDEO COM", "texto": "EDIÇÃO INCRÍVEL"},
   {"tipo": "pergunta", "ini": 0.3, "fim": 4, "texto": "Posso desistir de uma compra online?"},
   {"tipo": "card", "ini": 6, "fim": 11, "imagem": "print.png", "etiqueta": "SALVO"},
   {"tipo": "hud", "ini": 12, "fim": 16},
   {"tipo": "camadas", "ini": 0, "fim": 4, "titulo": "SEUS DIREITOS", "legenda": "7 dias para desistir"},
   {"tipo": "lista", "ini": 20, "fim": 28, "rotulo": "CDC · ART. 49", "titulo": "Três pontos",
    "itens": [{"titulo": "Prazo", "texto": "7 dias", "t": 20.5}, …]},
   {"tipo": "transcricao", "ini": 30, "fim": 36},
   {"tipo": "pb", "ini": 8, "fim": 10}]
Tema: cores do perfil (acento) ou "roxo" (o clima "tech" das referências). Uso: `aplicar(video, efeitos, saida)`.
"""
import html
import json
import shutil
import subprocess
from pathlib import Path

import numpy as np

from ..nucleo import caminhos, rosto
from . import motion

W, H, FPS = 1080, 1920, 30
TEMAS = {
    "roxo": {"acento": "#8B5CF6", "acento2": "#C4B5FD", "fundo": "#0D0A1C", "painel": "#17122E", "texto": "#F5F3FF",
             "sutil": "#A79FC9"},
    "dourado": {"acento": "#C9A45C", "acento2": "#E9D3A4", "fundo": "#0B1220", "painel": "#121B2E", "texto": "#F7F4EC",
                "sutil": "#9FA8BA"},
    "azul": {"acento": "#3B82F6", "acento2": "#BFDBFE", "fundo": "#08111F", "painel": "#0F1B30", "texto": "#F1F5FF",
             "sutil": "#94A3B8"},
}
OVERLAYS = {"titulo", "pergunta", "card", "hud"}
CENAS = {"camadas", "lista", "transcricao"}

FONTES_CSS = """
@font-face { font-family: Inter; src: url(fontes/Inter.ttf); font-weight: 100 900; }
@font-face { font-family: Montserrat; src: url(fontes/Montserrat.ttf); font-weight: 100 900; }
@font-face { font-family: Anton; src: url(fontes/Anton-Regular.ttf); }
@font-face { font-family: Mono; src: url(fontes/CourierPrime-Bold.ttf); font-weight: 700; }
* { margin: 0; padding: 0; box-sizing: border-box; }
html, body { width: 1080px; height: 1920px; overflow: hidden; background: transparent; }
#root { position: relative; width: 100%; height: 100%; font-family: Inter, sans-serif; color: var(--texto); }
.clip { position: absolute; inset: 0; }
.mask { overflow: hidden; display: block; }
.mask > span { display: block; }
"""


def _esc(t):
    return html.escape(str(t or "")).replace("\n", "<br>")


def _sonda(video):
    out = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
                          "stream=width,height:format=duration", "-of", "json", str(video)],
                         capture_output=True, text=True).stdout
    j = json.loads(out)
    s = j["streams"][0]
    return s["width"], s["height"], float(j["format"]["duration"])


def _projeto(pasta, corpo, js, dur, tema, extra_css=""):
    pasta.mkdir(parents=True, exist_ok=True)
    if not (pasta / "fontes").exists():
        shutil.copytree(caminhos.FONTES, pasta / "fontes")
    shutil.copy(motion._gsap_local(), pasta / "gsap.min.js")
    vars_ = "".join(f"--{k}: {v}; " for k, v in tema.items())
    doc = f"""<!doctype html>
<html lang="pt-BR"><head><meta charset="UTF-8" /><meta name="viewport" content="width={W}, height={H}" />
<script src="gsap.min.js"></script>
<style>:root {{ {vars_} }}{FONTES_CSS}{extra_css}</style></head>
<body><div id="root" data-composition-id="main" data-start="0" data-duration="{dur:.3f}" data-width="{W}" data-height="{H}">
{corpo}
</div>
<script>
const tl = gsap.timeline({{ paused: true }});
{js}
window.__timelines["main"] = tl;
</script></body></html>"""
    (pasta / "index.html").write_text(doc, encoding="utf-8")
    (pasta / "meta.json").write_text(json.dumps({"id": "efeito", "name": "efeito"}), encoding="utf-8")
    return pasta


# ====================================================================== OVERLAYS
def _titulo(e, d):
    kick = f'<div class="t-kick">{_esc(e.get("kicker", ""))}</div>' if e.get("kicker") else ""
    linhas = "".join(f'<span class="mask"><span class="t-l">{_esc(l)}</span></span>'
                     for l in str(e["texto"]).split("\n"))
    corpo = f'<div id="tit" class="clip" data-start="0" data-duration="{d:.3f}"><div class="t-box">{kick}{linhas}</div></div>'
    css = """
.t-box { position: absolute; left: 50px; right: 50px; top: 300px; text-align: center; }
.t-kick { font: 700 34px/1 Mono, monospace; letter-spacing: .5em; color: var(--acento2); margin-bottom: 18px;
  text-shadow: 0 0 18px var(--acento); }
.t-l { font: 900 150px/0.95 Montserrat, sans-serif; letter-spacing: -2px; text-transform: uppercase;
  background: linear-gradient(180deg, #FFFFFF 15%, var(--acento2) 60%, var(--acento) 100%);
  -webkit-background-clip: text; background-clip: text; color: transparent;
  filter: drop-shadow(0 0 22px color-mix(in srgb, var(--acento) 70%, transparent)); }
"""
    js = (f'tl.fromTo("#tit .t-kick", {{opacity: 0, y: -16}}, {{opacity: 1, y: 0, duration: .5, ease: "power3.out"}}, .05);'
          f'tl.fromTo("#tit .t-l", {{yPercent: 105, scale: 1.08}}, {{yPercent: 0, scale: 1, duration: .75, ease: "expo.out", stagger: .09}}, .12);'
          f'tl.to("#tit .t-box", {{opacity: 0, y: -30, duration: .4, ease: "power2.in"}}, {max(d - .45, .9):.3f});')
    return corpo, js, css


def _pergunta(e, d):
    corpo = (f'<div id="perg" class="clip" data-start="0" data-duration="{d:.3f}"><div class="p-card">'
             f'<div class="p-rot">{_esc(e.get("rotulo", "PERGUNTA"))}</div><div class="p-tx">{_esc(e["texto"])}</div></div></div>')
    css = """
.p-card { position: absolute; left: 80px; right: 80px; top: 300px; background: rgba(245,243,255,.94); color: #15102B;
  border-radius: 30px; padding: 34px 40px 40px; box-shadow: 0 30px 80px rgba(0,0,0,.45); transform-origin: 20% 0%; }
.p-rot { font: 800 28px/1 Inter, sans-serif; letter-spacing: .28em; color: var(--acento); margin-bottom: 14px; }
.p-tx { font: 800 54px/1.12 Montserrat, sans-serif; letter-spacing: -.5px; }
"""
    js = (f'tl.fromTo("#perg .p-card", {{opacity: 0, y: -40, scale: .92}}, {{opacity: 1, y: 0, scale: 1, duration: .7, ease: "back.out(1.6)"}}, .05);'
          f'tl.to("#perg .p-card", {{opacity: 0, y: -50, duration: .4, ease: "power2.in"}}, {max(d - .45, .8):.3f});')
    return corpo, js, css


def _card(e, d, pasta):
    img = Path(e["imagem"]).resolve()
    destino = pasta / ("card" + img.suffix)
    shutil.copy(img, destino)
    corpo = (f'<div id="cardf" class="clip" data-start="0" data-duration="{d:.3f}"><div class="c-wrap"><div class="c-card">'
             f'<img src="{destino.name}"><div class="c-tag">{_esc(e.get("etiqueta", "SALVO"))}</div>'
             + (f'<div class="c-tit">{_esc(e["titulo"])}</div>' if e.get("titulo") else "") + "</div></div></div>")
    css = """
.c-wrap { position: absolute; right: 36px; top: 430px; width: 340px; perspective: 1400px; }
.c-card { position: relative; width: 340px; border-radius: 34px; overflow: hidden; background: #fff;
  box-shadow: 0 0 0 3px color-mix(in srgb, var(--acento) 70%, white), 0 30px 70px rgba(0,0,0,.55),
  0 0 60px color-mix(in srgb, var(--acento) 45%, transparent); transform: rotate(-5deg); }
.c-card img { display: block; width: 100%; }
.c-tag { position: absolute; left: 22px; top: 22px; background: #15102B; color: #fff; font: 800 24px/1 Mono, monospace;
  letter-spacing: .2em; padding: 10px 14px; border-radius: 10px; }
.c-tit { position: absolute; left: 0; right: 0; bottom: 0; padding: 18px 22px; font: 700 28px/1.2 Inter, sans-serif;
  color: #fff; background: linear-gradient(transparent, rgba(0,0,0,.75)); }
"""
    flutua = max(d - 1.6, .5)
    js = (f'tl.fromTo("#cardf .c-wrap", {{x: 520, rotation: 14, opacity: 0}}, {{x: 0, rotation: 0, opacity: 1, duration: .9, ease: "expo.out"}}, .05);'
          f'tl.fromTo("#cardf .c-wrap", {{y: 0}}, {{y: -26, duration: {flutua / 2:.3f}, ease: "sine.inOut", yoyo: true, repeat: 1, immediateRender: false}}, .95);'
          f'tl.to("#cardf .c-wrap", {{x: 520, rotation: 10, opacity: 0, duration: .5, ease: "power3.in"}}, {max(d - .55, 1):.3f});')
    return corpo, js, css


def _rastrear(video, ini, fim, fps_amostra=6):
    """Rosto, olhos e boca (YuNet) por amostra, em coordenadas 1080×1920 do vídeo."""
    w, h, _ = _sonda(video)
    lw = 540
    lh = int(lw * h / w) // 2 * 2
    proc = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{ini:.3f}", "-t", f"{fim - ini:.3f}", "-i", str(video), "-vf",
                           f"fps={fps_amostra},scale={lw}:{lh}", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
                          capture_output=True).stdout
    n = len(proc) // (lw * lh * 3)
    det = rosto.Detector()
    sx, sy = W / lw, H / lh
    kf, ultimo = [], None
    for i in range(n):
        q = np.frombuffer(proc[i * lw * lh * 3:(i + 1) * lw * lh * 3], np.uint8).reshape(lh, lw, 3)
        m = det.marcos(q)
        if m and "olho_d" in m:
            x, y, a, b = m["caixa"]
            x, y, a, b = x * sx, y * sy, a * sx, b * sy
            ex = [m["olho_d"][0] * sx, m["olho_e"][0] * sx]
            ey = [m["olho_d"][1] * sy, m["olho_e"][1] * sy]
            mx = [m["boca_d"][0] * sx, m["boca_e"][0] * sx]
            my = [m["boca_d"][1] * sy, m["boca_e"][1] * sy]
            olhos = (min(ex) - a * .16, min(ey) - b * .1, max(ex) + a * .16, max(ey) + b * .1)
            boca = (min(mx) - a * .1, min(my) - b * .12, max(mx) + a * .1, max(my) + b * .12)
            ultimo = {"t": i / fps_amostra, "rosto": (x, y, x + a, y + b), "olhos": olhos, "boca": boca, "conf": m["conf"]}
        if ultimo:
            kf.append(dict(ultimo, t=i / fps_amostra))
    return kf


def _hud(e, d, video):
    kf = _rastrear(video, e["ini"], e["fim"])
    if not kf:
        return None
    conf = np.median([k["conf"] for k in kf])
    alvos = [("rosto", f"ROSTO {conf:.2f}".replace(".", ","), "dir"), ("olhos", "OLHOS", "esq"), ("boca", "BOCA", "dir")]
    corpo = [f'<div id="hud" class="clip" data-start="0" data-duration="{d:.3f}">',
             '<div class="h-top"><div class="h-t1">VISÃO COMPUTACIONAL</div><div class="h-t2">RECONHECENDO · QUADRO <span id="hq">0000</span></div></div>',
             f'<div class="h-obj"><div class="h-t2">OBJETOS</div><div class="h-n">{len(alvos):02d}</div></div>',
             '<div class="h-scan"></div>']
    js = ['tl.fromTo("#hud .h-scan", {y: -40, opacity: .9}, {y: 1960, opacity: .0, duration: 1.1, ease: "power1.inOut"}, 0);',
          'tl.fromTo("#hud .h-top, #hud .h-obj", {opacity: 0}, {opacity: 1, duration: .4}, 0);',
          f'const q = {{v: 0}}; tl.fromTo(q, {{v: 0}}, {{v: {int(d * FPS)}, duration: {d:.3f}, ease: "none", '
          f'onUpdate: () => {{ document.getElementById("hq").textContent = String(Math.round(q.v) + {int(e["ini"] * FPS)}).padStart(4, "0"); }}}}, 0);']
    for nome, rot, lado in alvos:
        for c in ("tl", "tr", "bl", "br"):
            corpo.append(f'<div class="h-c h-{c}" id="{nome}-{c}"></div>')
        corpo.append(f'<div class="h-lab h-{lado}" id="{nome}-lab"><span>{_esc(rot)}</span></div>')
        pos = []
        for k in kf:
            x0, y0, x1, y1 = k[nome]
            pos.append({"tl": (x0, y0), "tr": (x1, y0), "bl": (x0, y1), "br": (x1, y1),
                        "lab": (x1 + 14, y0 - 4) if lado == "dir" else (x0 - 214, (y0 + y1) / 2 - 22), "t": k["t"]})
        for parte in ("tl", "tr", "bl", "br", "lab"):
            sel = f"#{nome}-{parte}"
            x, y = pos[0][parte]
            js.append(f'tl.fromTo("{sel}", {{x: {x:.1f}, y: {y:.1f}, opacity: 0}}, {{opacity: 1, duration: .35}}, .2);')
            seq = [f"[{p['t']:.3f},{p[parte][0]:.1f},{p[parte][1]:.1f}]" for p in pos]
            js.append(f'(() => {{ const k = [{",".join(seq)}]; for (let i = 1; i < k.length; i++) '
                      f'tl.fromTo("{sel}", {{x: k[i-1][1], y: k[i-1][2]}}, {{x: k[i][1], y: k[i][2], duration: k[i][0]-k[i-1][0], '
                      f'ease: "sine.inOut", immediateRender: false}}, k[i-1][0]); }})();')
    js.append(f'tl.to("#hud", {{opacity: 0, duration: .35}}, {max(d - .4, .5):.3f});')
    corpo.append("</div>")
    css = """
.h-top { position: absolute; left: 70px; top: 230px; } .h-obj { position: absolute; right: 70px; top: 230px; text-align: right; }
.h-t1 { font: 700 36px/1.2 Mono, monospace; letter-spacing: .14em; color: #fff; text-shadow: 0 2px 8px rgba(0,0,0,.6); }
.h-t2 { font: 700 26px/1.4 Mono, monospace; letter-spacing: .22em; color: rgba(255,255,255,.85); text-shadow: 0 2px 8px rgba(0,0,0,.6); }
.h-n { font: 700 72px/1 Mono, monospace; color: #fff; }
.h-scan { position: absolute; left: 0; right: 0; top: 0; height: 6px;
  background: linear-gradient(90deg, transparent, var(--acento2), transparent); box-shadow: 0 0 30px var(--acento); }
.h-c { position: absolute; left: 0; top: 0; width: 34px; height: 34px; border-color: rgba(255,255,255,.95); border-style: solid; }
.h-tl { border-width: 4px 0 0 4px; margin: -2px 0 0 -2px; } .h-tr { border-width: 4px 4px 0 0; margin: -2px 0 0 -32px; }
.h-bl { border-width: 0 0 4px 4px; margin: -32px 0 0 -2px; } .h-br { border-width: 0 4px 4px 0; margin: -32px 0 0 -32px; }
.h-lab { position: absolute; left: 0; top: 0; }
.h-lab span { display: inline-block; font: 700 28px/1 Mono, monospace; letter-spacing: .08em; padding: 9px 12px; border-radius: 6px;
  background: color-mix(in srgb, var(--acento2) 85%, white); color: #15102B; box-shadow: 0 6px 20px rgba(0,0,0,.35); }
.h-esq span { width: 200px; text-align: center; }
"""
    return "\n".join(corpo), "\n".join(js), css


# ====================================================================== CENAS (vídeo dentro)
def _recortar_trecho(video, ini, fim, destino):
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-ss", f"{ini:.3f}", "-t", f"{fim - ini:.3f}", "-i", str(video), "-an",
                    "-vf", f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},fps={FPS}",
                    "-c:v", "libx264", "-crf", "16", "-pix_fmt", "yuv420p", str(destino)], check=True)
    return destino


def _camadas(e, d, video, pasta):
    from . import recorte
    from PIL import Image
    seg = _recortar_trecho(video, e["ini"], e["fim"], pasta / "trecho.mp4")
    meio = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{d / 2:.3f}", "-i", str(seg), "-frames:v", "1", "-f", "rawvideo",
                           "-pix_fmt", "rgb24", "-"], capture_output=True).stdout
    rgb = np.frombuffer(meio, np.uint8).reshape(H, W, 3)
    m = recorte.matte_imagem(rgb)
    Image.fromarray(np.dstack([rgb, (m * 255).astype(np.uint8)])).save(pasta / "recorte.png")
    nomes = ["01 · VÍDEO", "02 · RECORTE", "03 · LEGENDA", "04 · ÍCONES", "05 · TÍTULO"]
    icones = "".join(f'<div class="k-ic" style="top:{760 + i * 200}px">{s}</div>' for i, s in enumerate(["✂", "✦", "▣"]))
    camadas = [
        f'<video class="k-vid" src="trecho.mp4" muted playsinline data-start="0" data-duration="{d:.3f}" data-track-index="0"></video>',
        '<img class="k-rec" src="recorte.png">',
        f'<div class="k-leg">{_esc(e.get("legenda", ""))}</div>',
        icones,
        f'<div class="k-tit">{_esc(e.get("titulo", ""))}</div>',
    ]
    pl = "".join(f'<div class="k-pl" id="k{i}"><div class="k-tag">CAMADA {_esc(n)}</div>{c}</div>'
                 for i, (n, c) in enumerate(zip(nomes, camadas)))
    corpo = (f'<div id="cam" class="clip" data-start="0" data-duration="{d:.3f}"><div class="k-bg"></div>'
             f'<div class="k-palco"><div class="k-mundo">{pl}</div></div><div class="k-rod">5 CAMADAS · PROFUNDIDADE REAL</div></div>')
    css = """
.k-bg { position: absolute; inset: 0; background: radial-gradient(120% 80% at 50% 40%, var(--painel), var(--fundo)); }
.k-palco { position: absolute; inset: 0; perspective: 2600px; perspective-origin: 50% 45%; }
.k-mundo { position: absolute; inset: 0; transform-style: preserve-3d; }
.k-pl { position: absolute; inset: 0; transform-style: preserve-3d; border-radius: 40px; }
.k-pl::after { content: ""; position: absolute; inset: 0; border-radius: 40px; border: 4px solid var(--acento2);
  box-shadow: 0 0 40px var(--acento), inset 0 0 30px color-mix(in srgb, var(--acento) 30%, transparent); opacity: var(--borda, 0); }
.k-tag { position: absolute; left: 30px; top: -64px; font: 700 30px/1 Mono, monospace; letter-spacing: .12em; color: #fff;
  background: color-mix(in srgb, var(--acento) 80%, black); padding: 10px 16px; border-radius: 10px; opacity: var(--borda, 0); }
.k-vid, .k-rec { position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; border-radius: 40px; }
.k-leg { position: absolute; left: 0; right: 0; top: 1240px; text-align: center; font: 800 64px/1.1 Montserrat, sans-serif;
  color: #fff; text-shadow: 0 4px 18px rgba(0,0,0,.6); }
.k-ic { position: absolute; left: 70px; width: 130px; height: 130px; border-radius: 34px; display: flex; align-items: center;
  justify-content: center; font: 700 64px/1 Inter, sans-serif; color: #fff; background: linear-gradient(160deg, var(--acento2), var(--acento));
  box-shadow: 0 20px 50px color-mix(in srgb, var(--acento) 60%, transparent); }
.k-tit { position: absolute; left: 60px; right: 60px; top: 300px; font: 900 140px/0.95 Montserrat, sans-serif; text-transform: uppercase;
  background: linear-gradient(180deg, #fff 20%, var(--acento2)); -webkit-background-clip: text; background-clip: text; color: transparent; }
.k-rod { position: absolute; left: 0; right: 0; bottom: 210px; text-align: center; font: 700 30px/1 Mono, monospace; letter-spacing: .3em;
  color: var(--acento2); opacity: 0; }
"""
    abre, fecha = .35, max(d - 1.0, 1.6)
    js = [f'tl.fromTo("#cam .k-mundo", {{rotationY: 0, rotationX: 0, scale: 1, x: 0}}, {{rotationY: -26, rotationX: 8, scale: .56, x: 90, duration: 1.1, ease: "expo.inOut"}}, {abre});',
          f'tl.fromTo("#cam .k-pl", {{"--borda": 0}}, {{"--borda": 1, duration: .5}}, {abre + .4});',
          f'tl.fromTo("#cam .k-rod", {{opacity: 0}}, {{opacity: 1, duration: .5}}, {abre + .6});']
    for i in range(5):
        js.append(f'tl.fromTo("#cam #k{i}", {{z: 0}}, {{z: {i * 170}, duration: 1.1, ease: "expo.inOut"}}, {abre + .05 * i:.2f});')
        js.append(f'tl.to("#cam #k{i}", {{z: 0, duration: .8, ease: "expo.inOut"}}, {fecha:.2f});')
    js.append(f'tl.fromTo("#cam .k-mundo", {{rotationY: -26}}, {{rotationY: -20, duration: {max(fecha - abre - 1.1, .3):.2f}, ease: "none", immediateRender: false}}, {abre + 1.1:.2f});')
    js.append(f'tl.to("#cam .k-mundo", {{rotationY: 0, rotationX: 0, scale: 1, x: 0, duration: .8, ease: "expo.inOut"}}, {fecha:.2f});')
    js.append(f'tl.to("#cam .k-pl", {{"--borda": 0, duration: .4}}, {fecha + .3:.2f});')
    js.append(f'tl.to("#cam .k-rod", {{opacity: 0, duration: .3}}, {fecha:.2f});')
    return corpo, "\n".join(js), css


def _lista(e, d, video, pasta):
    _recortar_trecho(video, e["ini"], e["fim"], pasta / "trecho.mp4")
    itens = e.get("itens", [])
    li = "".join(f'<div class="l-it" id="li{i}"><div class="l-num">{i + 1:02d}</div><div><div class="l-t">{_esc(x["titulo"])}</div>'
                 f'<div class="l-s">{_esc(x.get("texto", ""))}</div></div></div>' for i, x in enumerate(itens))
    corpo = (f'<div id="lst" class="clip" data-start="0" data-duration="{d:.3f}"><div class="l-bg"></div>'
             f'<div class="l-cab"><div class="l-rot">{_esc(e.get("rotulo", ""))}</div><div class="l-tit">{_esc(e.get("titulo", ""))}</div></div>'
             f'<div class="l-lista">{li}</div>'
             f'<div class="l-jan"><video src="trecho.mp4" muted playsinline data-start="0" data-duration="{d:.3f}" data-track-index="0"></video></div>'
             + (f'<div class="l-lado">{_esc(e["lado"])}</div>' if e.get("lado") else "") + "</div>")
    css = """
.l-bg { position: absolute; inset: 0; background: linear-gradient(170deg, var(--painel), var(--fundo)); }
.l-cab { position: absolute; left: 80px; right: 80px; top: 230px; }
.l-rot { font: 700 30px/1 Inter, sans-serif; letter-spacing: .24em; color: var(--acento2); margin-bottom: 16px; text-transform: uppercase; }
.l-tit { font: 400 104px/0.98 Anton, sans-serif; text-transform: uppercase; color: var(--texto); }
.l-lista { position: absolute; left: 80px; right: 80px; top: 600px; display: flex; flex-direction: column; gap: 22px; }
.l-it { display: flex; gap: 28px; align-items: center; padding: 26px 30px; border-radius: 22px; background: color-mix(in srgb, var(--texto) 5%, transparent);
  border: 2px solid color-mix(in srgb, var(--texto) 10%, transparent); opacity: .35; }
.l-num { font: 700 30px/1 Mono, monospace; color: var(--acento2); min-width: 60px; }
.l-t { font: 400 56px/1 Anton, sans-serif; text-transform: uppercase; } .l-s { font: 500 32px/1.3 Inter, sans-serif; color: var(--sutil); margin-top: 6px; }
.l-jan { position: absolute; right: 70px; bottom: 190px; width: 400px; height: 540px; border-radius: 30px; overflow: hidden;
  box-shadow: 0 30px 80px rgba(0,0,0,.5), 0 0 0 3px color-mix(in srgb, var(--acento2) 50%, transparent); }
.l-jan video { width: 100%; height: 100%; object-fit: cover; }
.l-lado { position: absolute; left: 80px; bottom: 420px; width: 420px; font: 400 76px/1 Anton, sans-serif; text-transform: uppercase; color: var(--texto); }
"""
    js = ['tl.fromTo("#lst .l-cab", {opacity: 0, y: 30}, {opacity: 1, y: 0, duration: .6, ease: "expo.out"}, .05);',
          'tl.fromTo("#lst .l-jan", {opacity: 0, scale: .9, y: 40}, {opacity: 1, scale: 1, y: 0, duration: .8, ease: "expo.out"}, .15);']
    for i, x in enumerate(itens):
        t = max(float(x.get("t", e["ini"] + .4 + i * 1.2)) - e["ini"], .2)
        js.append(f'tl.fromTo("#lst #li{i}", {{x: -60, opacity: 0}}, {{x: 0, opacity: .35, duration: .5, ease: "expo.out"}}, {.3 + .1 * i:.2f});')
        js.append(f'tl.to("#lst #li{i}", {{opacity: 1, scale: 1.03, borderColor: "{TEMAS["roxo"]["acento2"]}", duration: .35, ease: "power2.out"}}, {t:.2f});')
        prox = itens[i + 1].get("t") if i + 1 < len(itens) else None
        if prox:
            js.append(f'tl.to("#lst #li{i}", {{opacity: .55, scale: 1, duration: .3}}, {max(float(prox) - e["ini"], t + .3):.2f});')
    return corpo, "\n".join(js), css


def _onda(video, ini, fim, n=180):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{ini:.3f}", "-t", f"{fim - ini:.3f}", "-i", str(video), "-ac", "1",
                          "-ar", "8000", "-f", "s16le", "-"], capture_output=True).stdout
    a = np.frombuffer(raw, np.int16).astype(np.float32) / 32768
    if not len(a):
        return [0.1] * n
    blocos = np.array_split(a, n)
    v = np.array([np.sqrt(np.mean(b ** 2)) if len(b) else 0 for b in blocos])
    return list(np.clip(v / (v.max() or 1), .06, 1))


def _transcricao(e, d, video, pasta, palavras):
    _recortar_trecho(video, e["ini"], e["fim"], pasta / "trecho.mp4")
    pw = [p for p in (palavras or []) if e["ini"] - 3 <= p["ini"] <= e["fim"] + 3]
    if not pw:
        return None
    total = len(palavras)
    idx0 = palavras.index(pw[0])
    larg = [max(150, 40 * len(p["w"]) + 70) for p in pw]
    xs = np.cumsum([0] + [l + 14 for l in larg[:-1]])
    chips = "".join(f'<div class="w-chip" id="w{i}" style="left:{x}px;width:{l}px"><div class="w-tx">{_esc(p["w"])}</div>'
                    f'<div class="w-bars">' + "".join(f'<i style="height:{int(12 + 40 * abs(np.sin(i * 1.7 + j)))}px"></i>' for j in range(8))
                    + '</div><div class="w-on"></div></div>' for i, (p, x, l) in enumerate(zip(pw, xs, larg)))
    onda = _onda(video, e["ini"], e["fim"])
    barras = "".join(f'<rect x="{i * 6}" y="{110 - v * 100:.1f}" width="3.4" height="{v * 200:.1f}" rx="1.7"/>' for i, v in enumerate(onda))
    marcas = "".join(f'<div class="w-mk" style="left:{int(i * (W - 40) / 6) + 20}px">{int((e["ini"] + i * d / 6) // 60)}:{int((e["ini"] + i * d / 6) % 60):02d}</div>'
                     for i in range(7))
    corpo = (f'<div id="trc" class="clip" data-start="0" data-duration="{d:.3f}"><div class="w-bg"></div>'
             f'<div class="w-cab">TRANSCRIÇÃO · AO VIVO</div>'
             f'<div class="w-jan"><video src="trecho.mp4" muted playsinline data-start="0" data-duration="{d:.3f}" data-track-index="0"></video></div>'
             f'<div class="w-cont">PALAVRA <b id="wn">{idx0 + 1}</b> / {total}</div>'
             f'<div class="w-faixa"><div class="w-trilho" id="wt">{chips}</div><div class="w-cursor"></div></div>'
             f'<div class="w-regua">{marcas}</div>'
             f'<svg class="w-onda" viewBox="0 0 {len(onda) * 6} 220" preserveAspectRatio="none">{barras}</svg>'
             f'<div class="w-play" id="wp"></div></div>')
    css = """
.w-bg { position: absolute; inset: 0; background: linear-gradient(180deg, var(--fundo), var(--painel)); }
.w-cab { position: absolute; left: 70px; top: 230px; font: 700 26px/1 Mono, monospace; letter-spacing: .24em; color: var(--sutil); }
.w-jan { position: absolute; left: 150px; right: 150px; top: 290px; height: 900px; border-radius: 26px; overflow: hidden;
  box-shadow: 0 30px 70px rgba(0,0,0,.5); } .w-jan video { width: 100%; height: 100%; object-fit: cover; }
.w-cont { position: absolute; right: 70px; top: 1225px; font: 700 28px/1 Mono, monospace; letter-spacing: .2em; color: var(--sutil); }
.w-cont b { color: var(--texto); }
.w-faixa { position: absolute; left: 0; right: 0; top: 1275px; height: 170px; overflow: hidden; }
.w-trilho { position: absolute; left: 0; top: 0; height: 170px; }
.w-chip { position: absolute; top: 0; height: 170px; border-radius: 16px; background: color-mix(in srgb, var(--texto) 7%, transparent);
  overflow: hidden; display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 16px; }
.w-tx { position: relative; z-index: 2; font: 900 54px/1 Montserrat, sans-serif; color: var(--texto); }
.w-bars { position: relative; z-index: 2; display: flex; gap: 6px; align-items: center; height: 56px; }
.w-bars i { display: block; width: 7px; border-radius: 4px; background: color-mix(in srgb, var(--texto) 55%, transparent); }
.w-on { position: absolute; inset: 0; background: linear-gradient(180deg, var(--acento2), var(--acento)); opacity: 0; z-index: 1; }
.w-cursor { position: absolute; left: 539px; top: -10px; width: 3px; height: 190px; background: #fff; box-shadow: 0 0 12px #fff; }
.w-regua { position: absolute; left: 0; right: 0; top: 1475px; height: 40px; border-top: 2px solid color-mix(in srgb, var(--texto) 25%, transparent); }
.w-mk { position: absolute; top: 8px; font: 700 22px/1 Mono, monospace; color: var(--sutil); }
.w-onda { position: absolute; left: 20px; right: 20px; top: 1540px; width: 1040px; height: 220px; fill: color-mix(in srgb, var(--acento2) 75%, transparent); }
.w-play { position: absolute; left: 20px; top: 1520px; width: 3px; height: 260px; background: var(--acento2); box-shadow: 0 0 14px var(--acento); }
"""
    js = ['tl.fromTo("#trc .w-jan", {opacity: 0, y: 40}, {opacity: 1, y: 0, duration: .6, ease: "expo.out"}, 0);',
          f'tl.fromTo("#trc #wp", {{x: 0}}, {{x: 1036, duration: {d:.3f}, ease: "none"}}, 0);']
    centro = [540 - (x + l / 2) for x, l in zip(xs, larg)]
    tempos = [max(p["ini"] - e["ini"], 0) for p in pw]
    js.append(f'tl.fromTo("#trc #wt", {{x: {centro[0]:.1f}}}, {{x: {centro[0]:.1f}, duration: .01}}, 0);')
    for i in range(1, len(pw)):
        if tempos[i] > d:
            break
        js.append(f'tl.fromTo("#trc #wt", {{x: {centro[i - 1]:.1f}}}, {{x: {centro[i]:.1f}, duration: .18, ease: "power2.out", immediateRender: false}}, {tempos[i]:.3f});')
    for i, p in enumerate(pw):
        a, b = tempos[i], max(p["fim"] - e["ini"], tempos[i] + .1)
        if a > d:
            break
        js.append(f'tl.fromTo("#trc #w{i} .w-on", {{opacity: 0}}, {{opacity: 1, duration: .08}}, {a:.3f});')
        js.append(f'tl.to("#trc #w{i} .w-on", {{opacity: 0, duration: .12}}, {min(b, d - .05):.3f});')
    js.append(f'const wq = {{v: 0}}; const wt = [{",".join(f"{t:.3f}" for t in tempos)}]; '
              f'tl.fromTo(wq, {{v: 0}}, {{v: {d:.3f}, duration: {d:.3f}, ease: "none", onUpdate: () => {{ let k = 0; '
              f'while (k + 1 < wt.length && wt[k + 1] <= wq.v) k++; document.getElementById("wn").textContent = {idx0 + 1} + k; }}}}, 0);')
    return corpo, "\n".join(js), css


# ====================================================================== aplicação
def _tema(tema, perfil):
    if isinstance(tema, dict):
        return tema
    if tema in TEMAS:
        return TEMAS[tema]
    if perfil:
        from ..nucleo import perfis
        p = perfis.carregar(perfil)
        acento = p.get("cores", {}).get("destaque")
        if acento:
            base = dict(TEMAS["dourado"] if p.get("tipo") != "politico" else TEMAS["azul"])
            base["acento"] = acento
            return base
    return TEMAS["roxo"]


def conflitos(efeitos, prod=None):
    """Avisos de choque visual: efeitos de topo × cartões/abertura da produção, e efeitos sobrepostos entre si."""
    av = []
    topo = [e for e in efeitos if e["tipo"] in ("pergunta", "titulo", "hud")]
    cam = (prod or {}).get("camadas", {})
    for e in topo:
        for c in cam.get("cartoes", []):
            if e["ini"] < c["fim"] and c["ini"] < e["fim"]:
                av.append(f"{e['tipo']} ({e['ini']}-{e['fim']} s) cobre o cartão '{c['titulo']}' ({c['ini']:.1f}-{c['fim']:.1f} s): "
                          "mova o efeito ou tire o cartão do producao.json")
        ab = cam.get("abertura") or {}
        if ab.get("tipo") not in (None, "nenhuma") and e["ini"] < ab.get("fim", 0):
            av.append(f"{e['tipo']} começa durante a abertura da produção: use sem_abertura ou mova o efeito")
    cenas = sorted([e for e in efeitos if e["tipo"] in CENAS], key=lambda e: e["ini"])
    for a, b in zip(cenas, cenas[1:]):
        if b["ini"] < a["fim"]:
            av.append(f"cenas sobrepostas: {a['tipo']} e {b['tipo']}")
    return av


def renderizar_efeito(e, video, pasta, tema, palavras=None):
    """Renderiza um efeito → (arquivo .mov, tipo 'overlay'|'cena') ou None se não se aplica."""
    d = e["fim"] - e["ini"]
    pasta.mkdir(parents=True, exist_ok=True)
    t = e["tipo"]
    if t == "titulo":
        r = _titulo(e, d)
    elif t == "pergunta":
        r = _pergunta(e, d)
    elif t == "card":
        r = _card(e, d, pasta)
    elif t == "hud":
        r = _hud(e, d, video)
    elif t == "camadas":
        r = _camadas(e, d, video, pasta)
    elif t == "lista":
        r = _lista(e, d, video, pasta)
    elif t == "transcricao":
        r = _transcricao(e, d, video, pasta, palavras)
    else:
        raise ValueError(f"efeito desconhecido: {t}")
    if not r:
        return None
    corpo, js, css = r
    _projeto(pasta, corpo, js, d, tema, css)
    mov = pasta.parent / f"{pasta.name}.mov"
    chave = (pasta / "index.html").read_text(encoding="utf-8")
    cache = pasta / ".render_ok"
    if not (mov.exists() and cache.exists() and cache.read_text(encoding="utf-8") == chave):   # só re-renderiza o que mudou
        mov = motion.renderizar_overlay(pasta, mov, fps=FPS)
        if mov:
            cache.write_text(chave, encoding="utf-8")
    return (mov, "cena" if t in CENAS else "overlay") if mov else None


def aplicar(video, efeitos, saida, tema="roxo", perfil=None, palavras=None, pasta_trabalho=None, prod=None):
    """Aplica a lista de efeitos ao vídeo (áudio original preservado). Devolve o relatório."""
    video, saida = Path(video).resolve(), Path(saida).resolve()
    trab = Path(pasta_trabalho or saida.parent / (saida.stem + "_efeitos"))
    trab.mkdir(parents=True, exist_ok=True)
    tm = _tema(tema, perfil)
    _, _, dur = _sonda(video)
    avisos = conflitos(efeitos, prod)
    efeitos = sorted([dict(x) for x in efeitos], key=lambda x: (x["tipo"] in OVERLAYS, x["ini"]))  # cenas por baixo
    entradas, partes, atual, k, rel = ["-i", str(video)], [], "0:v", 1, []
    for n, e in enumerate(efeitos):
        e["ini"], e["fim"] = max(0.0, float(e["ini"])), min(float(e["fim"]), dur)
        if e["fim"] - e["ini"] < .5:
            rel.append({"efeito": e["tipo"], "status": "ignorado (menos de 0,5 s)"})
            continue
        if e["tipo"] == "pb":
            partes.append(f"[{atual}]hue=s=0:enable='between(t,{e['ini']:.3f},{e['fim']:.3f})',"
                          f"eq=contrast=1.08:enable='between(t,{e['ini']:.3f},{e['fim']:.3f})'[pb{n}]")
            atual = f"pb{n}"
            rel.append({"efeito": "pb", "ini": e["ini"], "fim": e["fim"]})
            if e.get("texto"):
                efeitos.append({"tipo": "titulo", "ini": e["ini"], "fim": e["fim"], "texto": e["texto"]})
            continue
        r = renderizar_efeito(e, video, trab / f"{n:02d}_{e['tipo']}", tm, palavras)
        if not r:
            rel.append({"efeito": e["tipo"], "status": "não aplicado (sem rosto/palavras ou HyperFrames ausente)"})
            continue
        mov, tipo = r
        entradas += ["-itsoffset", f"{e['ini']:.3f}", "-i", str(mov)]
        partes.append(f"[{k}:v]format=yuva420p,setpts=PTS-STARTPTS+{e['ini']:.3f}/TB[e{n}];"
                      f"[{atual}][e{n}]overlay=0:0:eof_action=pass:enable='between(t,{e['ini']:.3f},{e['fim']:.3f})'[o{n}]")
        atual, k = f"o{n}", k + 1
        rel.append({"efeito": e["tipo"], "tipo": tipo, "ini": e["ini"], "fim": e["fim"]})
    if atual == "0:v":
        shutil.copyfile(video, saida)
    else:
        filtro = ";".join(partes)
        cmd = ["ffmpeg", "-y", "-v", "error", *entradas, "-filter_complex", filtro, "-map", f"[{atual}]", "-map", "0:a?",
               "-c:v", "libx264", "-crf", "17", "-preset", "medium", "-pix_fmt", "yuv420p", "-c:a", "copy", str(saida)]
        r = subprocess.run(cmd, capture_output=True, text=True)
        if r.returncode != 0:
            raise RuntimeError(f"falha ao compor efeitos:\n{r.stderr[-2000:]}")
    (trab / "efeitos.json").write_text(json.dumps(rel, ensure_ascii=False, indent=1), encoding="utf-8")
    return {"saida": str(saida), "efeitos": rel, "avisos": avisos}
