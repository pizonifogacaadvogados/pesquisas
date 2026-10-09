"""Motion graphics de verdade: composição HTML + GSAP renderizada pelo HyperFrames (HeyGen, Apache-2.0).

Por que: a versão 2 desenhava os gráficos em ASS/PNG (legenda de cinema, mas animação "de PowerPoint":
fade + subida linear). Editores profissionais fazem motion em After Effects com curvas de easing,
revelação por máscara, escalonamento (stagger) e movimento secundário. O GSAP tem as mesmas curvas
(expo/power/back) e o HyperFrames renderiza quadro a quadro, determinístico, com canal alfa.

Saída: overlay transparente (MOV ProRes 4444) com lower third, cartões e chamada; o render do
`producao` sobrepõe o overlay ao vídeo já com cor (texto fica nítido, fora do LUT e do grão).

Requisitos: Node 22+ e `npx hyperframes` (baixa o Chrome headless na 1ª vez).
"""
import html
import json
import shutil
import subprocess
from pathlib import Path

FONTES = Path(__file__).resolve().parent.parent / "fontes"
W, H = 1080, 1920
VERSAO_HF = "0.8.143"
VERSAO_GSAP = "3.14.2"
CACHE = Path(__file__).resolve().parent.parent / "modelos" / "js"


def _gsap_local():
    """gsap.min.js local (sem CDN: a rede pode bloquear e o render precisa ser reprodutível)."""
    alvo = CACHE / f"gsap-{VERSAO_GSAP}.min.js"
    if not alvo.exists():
        import tarfile
        import tempfile
        CACHE.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory() as tmp:
            subprocess.run(["npm", "pack", f"gsap@{VERSAO_GSAP}", "--silent"], cwd=tmp, check=True,
                           capture_output=True)
            tgz = next(Path(tmp).glob("gsap-*.tgz"))
            with tarfile.open(tgz) as t:
                alvo.write_bytes(t.extractfile("package/dist/gsap.min.js").read())
    return alvo

CSS = """
@font-face { font-family: Inter; src: url(fontes/Inter.ttf); font-weight: 100 900; }
@font-face { font-family: Playfair; src: url(fontes/PlayfairDisplay.ttf); font-weight: 400 900; }
* { margin: 0; padding: 0; box-sizing: border-box; }
html, body { width: 1080px; height: 1920px; overflow: hidden; background: transparent; }
#root { width: 100%; height: 100%; position: relative; font-family: Inter, sans-serif; }
.clip { position: absolute; inset: 0; }
.mask { overflow: hidden; display: block; }
.mask > span { display: block; will-change: transform; }

/* lower third: barra de acento que se desenha, nome e cargo revelados por máscara */
.lt { position: absolute; left: 84px; bottom: 560px; }
.lt-barra { width: 6px; height: 132px; background: var(--acento); position: absolute; left: 0; top: 4px;
            transform-origin: 50% 100%; }
.lt-fundo { position: absolute; left: 0; top: 0; height: 140px; width: 760px;
            background: linear-gradient(90deg, rgba(8,12,20,.62), rgba(8,12,20,0));
            transform-origin: 0 50%; }
.lt-txt { position: relative; padding-left: 30px; }
.lt-nome { font-weight: 700; font-size: 64px; letter-spacing: -0.01em; color: #fff; line-height: 1.08; }
.lt-cargo { font-weight: 500; font-size: 38px; color: rgba(255,255,255,.82); margin-top: 8px; letter-spacing: .01em; }

/* cartão de norma: vidro escuro, número grande serifado, linha que se desenha */
.card { position: absolute; left: 90px; right: 90px; top: 330px; padding: 46px 54px 50px;
        background: rgba(10,14,22,.58); border: 1px solid rgba(255,255,255,.14); border-radius: 26px;
        backdrop-filter: blur(18px); -webkit-backdrop-filter: blur(18px); }
.card-rot { font-weight: 600; font-size: 30px; letter-spacing: .22em; color: var(--acento); }
.card-tit { font-family: Playfair, serif; font-weight: 700; font-size: 104px; color: #fff; line-height: 1.02;
            margin-top: 14px; }
.card-linha { height: 3px; background: var(--acento); margin: 26px 0 22px; transform-origin: 0 50%; }
.card-sub { font-weight: 500; font-size: 40px; color: rgba(255,255,255,.86); line-height: 1.25; }

/* chamada (kicker) de abertura */
.kick { position: absolute; left: 0; right: 0; top: 250px; text-align: center; }
.kick-rot { font-weight: 700; font-size: 34px; letter-spacing: .32em; color: var(--acento); }
"""


def _palavras_mascara(texto, cls):
    return "".join(f'<span class="mask" style="display:inline-block;margin-right:.26em"><span class="{cls}">'
                   f"{html.escape(p)}</span></span>" for p in texto.split())


def _seek_seguro(linhas):
    """Toda fromTo depois da primeira no mesmo alvo recebe immediateRender:false (seek nos dois sentidos)."""
    import re
    vistos, out = set(), []
    for bloco in linhas:
        def troca(m):
            alvo = m.group(1)
            if alvo in vistos:
                return re.sub(r"\}, \{", "}, {immediateRender: false, ", m.group(0), count=1)
            vistos.add(alvo)
            return m.group(0)
        out.append(re.sub(r'tl\.fromTo\("([^"]+)", \{[^}]*\}, \{', troca, bloco))
    return out


def composicao(prod, destino, acento="#C9A45C", inicio=0.0, fim=None):
    """Escreve o projeto HyperFrames (index.html) com os gráficos de `prod` entre `inicio` e `fim`."""
    destino = Path(destino)
    destino.mkdir(parents=True, exist_ok=True)
    if not (destino / "fontes").exists():
        shutil.copytree(FONTES, destino / "fontes")
    shutil.copy(_gsap_local(), destino / "gsap.min.js")
    cam = prod["camadas"]
    fim = fim or prod["duracao"]
    dur = fim - inicio
    corpo, js = [], []

    def janela(a, b):
        a, b = max(a - inicio, 0), min(b - inicio, dur)
        return a, b, b - a

    ab = cam.get("abertura") or {}
    if ab.get("rotulo"):
        a, b, d = janela(ab["ini"], ab["fim"])
        if d > 0.3:
            corpo.append(f'<div id="kick" class="clip" data-start="{a:.3f}" data-duration="{d:.3f}" data-track-index="1">'
                         f'<div class="kick"><span class="mask"><span class="kick-rot">{html.escape(ab["rotulo"])}'
                         f"</span></span></div></div>")
            js.append(f'tl.fromTo("#kick .kick-rot", {{yPercent: 110}}, {{yPercent: 0, duration: .7, ease: "expo.out"}}, {a + .15:.3f});'
                      f'tl.fromTo("#kick .kick", {{scale: 1.06, opacity: 0}}, {{scale: 1, opacity: 1, duration: 1.1, ease: "power3.out"}}, {a + .15:.3f});'
                      f'tl.to("#kick .kick-rot", {{yPercent: -110, duration: .45, ease: "power3.in"}}, {b - .5:.3f});')

    lt = cam.get("lower_third")
    if lt:
        a, b, d = janela(lt["ini"], lt["fim"])
        if d > 0.5:
            corpo.append(f'<div id="lt" class="clip" data-start="{a:.3f}" data-duration="{d:.3f}" data-track-index="2">'
                         f'<div class="lt"><div class="lt-fundo"></div><div class="lt-barra"></div><div class="lt-txt">'
                         f'<span class="mask"><span class="lt-nome">{html.escape(lt["nome"])}</span></span>'
                         f'<span class="mask"><span class="lt-cargo">{html.escape(lt["cargo"])}</span></span>'
                         f"</div></div></div>")
            js.append(f'tl.fromTo("#lt .lt-barra", {{scaleY: 0}}, {{scaleY: 1, duration: .55, ease: "expo.out"}}, {a:.3f});'
                      f'tl.fromTo("#lt .lt-fundo", {{scaleX: 0, opacity: 0}}, {{scaleX: 1, opacity: 1, duration: .9, ease: "expo.out"}}, {a + .08:.3f});'
                      f'tl.fromTo("#lt .lt-nome", {{yPercent: 105}}, {{yPercent: 0, duration: .75, ease: "expo.out"}}, {a + .14:.3f});'
                      f'tl.fromTo("#lt .lt-cargo", {{yPercent: 110}}, {{yPercent: 0, duration: .75, ease: "expo.out"}}, {a + .24:.3f});'
                      # saída: o texto desce pela máscara, a barra recolhe por último (ordem inversa = "fecha")
                      f'tl.to("#lt .lt-cargo", {{yPercent: 110, duration: .4, ease: "power3.in"}}, {b - .62:.3f});'
                      f'tl.to("#lt .lt-nome", {{yPercent: 105, duration: .4, ease: "power3.in"}}, {b - .56:.3f});'
                      f'tl.to("#lt .lt-fundo", {{scaleX: 0, opacity: 0, duration: .45, ease: "power3.in"}}, {b - .5:.3f});'
                      f'tl.to("#lt .lt-barra", {{scaleY: 0, duration: .35, ease: "power3.in"}}, {b - .38:.3f});')

    for n, c in enumerate(cam.get("cartoes", [])):
        a, b, d = janela(c["ini"], c["fim"])
        if d <= 0.5:
            continue
        i = f"card{n}"
        corpo.append(f'<div id="{i}" class="clip" data-start="{a:.3f}" data-duration="{d:.3f}" data-track-index="{3 + n}">'
                     f'<div class="card"><div class="mask"><span class="card-rot">BASE LEGAL</span></div>'
                     f'<div class="card-tit">{_palavras_mascara(c["titulo"], "w")}</div>'
                     f'<div class="card-linha"></div>'
                     f'<div class="mask"><span class="card-sub">{html.escape(c.get("subtitulo", ""))}</span></div>'
                     f"</div></div>")
        js.append(f'tl.fromTo("#{i} .card", {{opacity: 0, y: 46, scale: .965}}, {{opacity: 1, y: 0, scale: 1, duration: .8, ease: "expo.out"}}, {a:.3f});'
                  f'tl.fromTo("#{i} .card-rot", {{yPercent: 110}}, {{yPercent: 0, duration: .6, ease: "expo.out"}}, {a + .12:.3f});'
                  f'tl.fromTo("#{i} .w", {{yPercent: 108}}, {{yPercent: 0, duration: .8, ease: "expo.out", stagger: .07}}, {a + .2:.3f});'
                  f'tl.fromTo("#{i} .card-linha", {{scaleX: 0}}, {{scaleX: 1, duration: .9, ease: "expo.inOut"}}, {a + .35:.3f});'
                  f'tl.fromTo("#{i} .card-sub", {{yPercent: 110}}, {{yPercent: 0, duration: .7, ease: "expo.out"}}, {a + .55:.3f});'
                  # respiração: deriva mínima enquanto parado (o "vivo" dos motion designers)
                  f'tl.fromTo("#{i} .card-tit", {{x: 0}}, {{x: 8, duration: {max(d - 1.6, .5):.3f}, ease: "none"}}, {a + .9:.3f});'
                  f'tl.to("#{i} .card", {{opacity: 0, y: -24, scale: .985, duration: .45, ease: "power3.in"}}, {b - .5:.3f});')

    js = _seek_seguro(js)
    doc = f"""<!doctype html>
<html lang="pt-BR"><head><meta charset="UTF-8" /><meta name="viewport" content="width={W}, height={H}" />
<script src="gsap.min.js"></script>
<style>:root {{ --acento: {acento}; }}{CSS}</style></head>
<body><div id="root" data-composition-id="main" data-start="0" data-duration="{dur:.3f}" data-width="{W}" data-height="{H}">
{chr(10).join(corpo)}
</div>
<script>
const tl = gsap.timeline({{ paused: true }});
{chr(10).join(js)}
window.__timelines["main"] = tl;
</script></body></html>
"""
    (destino / "index.html").write_text(doc, encoding="utf-8")
    (destino / "meta.json").write_text(json.dumps({"id": "videomaker-overlay", "name": "overlay"}), encoding="utf-8")
    return destino / "index.html"


def renderizar_overlay(projeto, saida, fps=30):
    """Renderiza o projeto em MOV ProRes 4444 com alfa. Devolve o caminho ou None se o HyperFrames faltar."""
    projeto, saida = Path(projeto).resolve(), Path(saida).resolve()
    cmd = ["npx", "--yes", f"hyperframes@{VERSAO_HF}", "render", str(projeto), "-o", str(saida),
           "--format", "mov", "-f", str(fps), "--quiet"]
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=1800)
    except (FileNotFoundError, subprocess.TimeoutExpired) as e:
        print(f"[motion] HyperFrames indisponível ({e}); mantendo gráficos ASS/PNG")
        return None
    if r.returncode != 0 or not saida.exists():
        print(f"[motion] falha no render do overlay:\n{(r.stdout + r.stderr)[-1500:]}")
        return None
    return saida
