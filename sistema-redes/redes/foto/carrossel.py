"""Carrosséis profissionais (estudos/17): JSON → HTML/CSS → PNG (Chrome headless) → PDF.

Especificação (carrossel.json):
{
  "identidade": "juridico_classico",          # ver IDENTIDADES
  "autor": {"nome": "Dra. Ana Souza", "handle": "@anasouza.adv", "foto": "foto.jpg"},
  "slides": [
    {"tipo": "capa", "rotulo": "DIREITO DO CONSUMIDOR", "titulo": "Comprou online e se arrependeu?",
     "subtitulo": "Você tem 7 dias. Mas quase ninguém sabe disso:"},
    {"tipo": "promessa", "texto": "Em 5 slides você vai saber exatamente o que fazer."},
    {"tipo": "item", "numero": 1, "titulo": "O prazo é de 7 dias", "texto": "Contados do recebimento do produto.",
     "destaque": "7 dias"},
    {"tipo": "dado", "numero": "7", "legenda": "dias para desistir", "fonte": "Art. 49, CDC"},
    {"tipo": "mito", "afirmacao": "Preciso explicar o motivo.", "veredito": "MITO", "texto": "A lei não exige justificativa."},
    {"tipo": "texto", "texto": "Arrependimento é direito, não favor."},          # manifesto
    {"tipo": "citacao", "texto": "...", "autor": "Nome", "handle": "@x", "foto": "x.jpg"},
    {"tipo": "print", "imagem": "manchete.png", "fonte": "G1, 08/10/2026"},
    {"tipo": "lista", "titulo": "Resumo", "itens": ["…", "…"]},
    {"tipo": "cta", "titulo": "Salve para consultar depois", "texto": "Envie para quem comprou online esta semana."}
  ]
}
Saída: slide_01.png … (4:5, 3:4 ou 9:16) + carrossel.pdf (LinkedIn) + relatorio.json (alertas de texto e contraste).
"""
import html
import json
import platform
import shutil
import subprocess
from pathlib import Path

from ..nucleo import caminhos

FORMATOS = {"4x5": (1080, 1350), "3x4": (1080, 1440), "9x16": (1080, 1920)}
IDENTIDADES = {
    "juridico_classico": dict(fundo="#F6F2EA", texto="#14213D", acento="#B08D57", sutil="#6B7280", escuro="#14213D",
                              claro="#F6F2EA", titulo="Playfair Display", corpo="Inter", peso_titulo=600),
    "juridico_moderno": dict(fundo="#1F2328", texto="#F4F5F7", acento="#3CC8B4", sutil="#A0A7B1", escuro="#121417",
                             claro="#F4F5F7", titulo="Inter", corpo="Inter", peso_titulo=800),
    "politico_sobrio": dict(fundo="#FFFFFF", texto="#0B1F3A", acento="#1F6FEB", sutil="#5B6573", escuro="#0B1F3A",
                            claro="#FFFFFF", titulo="Inter", corpo="Inter", peso_titulo=900),
    "manifesto": dict(fundo="#0E0E10", texto="#FFFFFF", acento="#FFD23F", sutil="#9A9AA0", escuro="#0E0E10",
                      claro="#FFFFFF", titulo="Bebas Neue", corpo="Inter", peso_titulo=400),
}
ARQ = {"Inter": "Inter.ttf", "Playfair Display": "PlayfairDisplay.ttf", "Bebas Neue": "BebasNeue-Regular.ttf",
       "DM Serif Display": "DMSerifDisplay-Regular.ttf", "Montserrat": "Montserrat.ttf", "Anton": "Anton-Regular.ttf"}


# ------------------------------------------------------------------ contraste (WCAG)
def _lum(hexcor):
    h = hexcor.lstrip("#")
    c = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    c = [x / 12.92 if x <= 0.03928 else ((x + 0.055) / 1.055) ** 2.4 for x in c]
    return 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2]


def contraste(a, b):
    la, lb = sorted([_lum(a), _lum(b)], reverse=True)
    return round((la + 0.05) / (lb + 0.05), 2)


# ------------------------------------------------------------------ HTML
def _css(idv, w, h):
    faces = "\n".join(f"@font-face {{ font-family: '{n}'; src: url('file://{(caminhos.FONTES / a).as_posix()}'); "
                      f"font-weight: 100 900; }}" for n, a in ARQ.items())
    return f"""{faces}
* {{ box-sizing: border-box; margin: 0; padding: 0; }}
html, body {{ width: {w}px; height: {h + 240}px; overflow: hidden; }}
body {{ background: var(--fundo); color: var(--texto); font-family: '{idv['corpo']}', sans-serif;
  --fundo: {idv['fundo']}; --texto: {idv['texto']}; --acento: {idv['acento']}; --sutil: {idv['sutil']};
  -webkit-font-smoothing: antialiased; }}
.slide {{ position: relative; width: {w}px; height: {h}px; padding: 120px 92px 150px; display: flex;
  flex-direction: column; justify-content: center; gap: 36px; }}
.rotulo {{ font-size: 30px; letter-spacing: 6px; font-weight: 700; color: var(--acento); text-transform: uppercase; }}
.titulo {{ font-family: '{idv['titulo']}', serif; font-weight: {idv['peso_titulo']}; font-size: 96px; line-height: 1.08;
  letter-spacing: {'1px' if idv['titulo'] == 'Bebas Neue' else '-1px'}; }}
.titulo.grande {{ font-size: {150 if idv['titulo'] == 'Bebas Neue' else 112}px; }}
.sub {{ font-size: 44px; line-height: 1.35; color: var(--sutil); font-weight: 400; }}
.corpo {{ font-size: 46px; line-height: 1.38; font-weight: 400; }}
.corpo b, .titulo b {{ font-weight: 800; }}
mark {{ background: linear-gradient(transparent 58%, color-mix(in srgb, var(--acento) 55%, transparent) 58%);
  color: inherit; padding: 0 4px; }}
.num {{ font-family: '{idv['titulo']}', serif; font-size: 120px; line-height: 1; color: var(--acento); font-weight: 700; }}
.big {{ font-family: '{idv['titulo']}', serif; font-size: 300px; line-height: .9; color: var(--acento); font-weight: 700; }}
.fonte {{ font-size: 28px; color: var(--sutil); letter-spacing: .5px; }}
.selo {{ display: inline-block; align-self: flex-start; font-weight: 900; font-size: 44px; letter-spacing: 4px; padding: 10px 26px;
  border: 6px solid currentColor; border-radius: 10px; transform: rotate(-4deg); }}
.linha {{ width: 120px; height: 8px; background: var(--acento); border-radius: 4px; }}
.lista li {{ font-size: 42px; line-height: 1.35; margin: 0 0 22px 46px; }}
.lista li::marker {{ color: var(--acento); font-weight: 800; }}
.print {{ width: 100%; border-radius: 22px; box-shadow: 0 24px 60px rgba(0,0,0,.28); }}
.foto {{ width: 150px; height: 150px; border-radius: 50%; object-fit: cover; border: 5px solid var(--acento); }}
.autor {{ display: flex; align-items: center; gap: 26px; }}
.autor .nome {{ font-size: 40px; font-weight: 800; }} .autor .handle {{ font-size: 32px; color: var(--sutil); }}
.rodape {{ position: absolute; left: 92px; right: 92px; top: {h - 100}px; display: flex; justify-content: space-between;
  font-size: 28px; color: var(--sutil); letter-spacing: 1px; }}
.seta {{ position: absolute; right: 92px; top: {h - 170}px; font-size: 34px; color: var(--acento); font-weight: 700; }}
.invertido {{ background: var(--texto); color: var(--fundo); }}
.invertido .sub, .invertido .fonte {{ color: color-mix(in srgb, var(--fundo) 70%, transparent); }}
"""


def _esc(t):
    """Escapa HTML mas permite **negrito** e ==marca-texto==."""
    s = html.escape(t or "")
    import re
    s = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", s)
    s = re.sub(r"==(.+?)==", r"<mark>\1</mark>", s)
    return s.replace("\n", "<br>")


def _destacar(texto, trecho):
    return texto.replace(trecho, f"=={trecho}==") if trecho and trecho in texto else texto


def _img(caminho, base):
    if not caminho:
        return ""
    p = Path(caminho)
    if not p.is_absolute():
        p = (base / p).resolve()
    return f"file://{p.as_posix()}"


def html_slide(s, idv, autor, n, total, w, h, base):
    t = s["tipo"]
    classe = "slide"
    corpo = ""
    if t == "capa":
        foto = _img(autor.get("foto"), base)
        corpo = (f'<div class="rotulo">{_esc(s.get("rotulo", ""))}</div><div class="linha"></div>'
                 f'<div class="titulo grande">{_esc(s["titulo"])}</div>'
                 + (f'<div class="sub">{_esc(s["subtitulo"])}</div>' if s.get("subtitulo") else "")
                 + (f'<div class="autor"><img class="foto" src="{foto}"><div><div class="nome">{_esc(autor.get("nome"))}</div>'
                    f'<div class="handle">{_esc(autor.get("handle"))}</div></div></div>' if foto else ""))
    elif t == "promessa":
        corpo = f'<div class="titulo">{_esc(s["texto"])}</div>'
    elif t == "item":
        corpo = (f'<div class="num">{s.get("numero", "")}</div><div class="titulo">{_esc(s["titulo"])}</div>'
                 f'<div class="corpo">{_esc(_destacar(s.get("texto", ""), s.get("destaque")))}</div>')
    elif t == "dado":
        corpo = (f'<div class="big">{_esc(str(s["numero"]))}</div><div class="titulo">{_esc(s["legenda"])}</div>'
                 + (f'<div class="fonte">Fonte: {_esc(s["fonte"])}</div>' if s.get("fonte") else ""))
    elif t == "mito":
        cor = {"MITO": "#D64545", "VERDADE": "#2E9E6A", "DEPENDE": "#D9912B"}.get(s.get("veredito", "MITO").upper(), "#D64545")
        corpo = (f'<div class="corpo" style="color:var(--sutil)">“{_esc(s["afirmacao"])}”</div>'
                 f'<div class="selo" style="color:{cor}">{_esc(s.get("veredito", "MITO"))}</div>'
                 f'<div class="titulo">{_esc(s.get("texto", ""))}</div>')
    elif t == "texto":
        classe += " invertido" if s.get("invertido") else ""
        corpo = f'<div class="titulo grande">{_esc(s["texto"])}</div>'
    elif t == "citacao":
        foto = _img(s.get("foto"), base)
        corpo = (f'<div class="num">“</div><div class="titulo">{_esc(s["texto"])}</div>'
                 f'<div class="autor">' + (f'<img class="foto" src="{foto}">' if foto else "")
                 + f'<div><div class="nome">{_esc(s.get("autor", ""))}</div><div class="handle">{_esc(s.get("handle", ""))}</div></div></div>')
    elif t == "print":
        corpo = (f'<img class="print" src="{_img(s["imagem"], base)}">'
                 + (f'<div class="corpo">{_esc(s["texto"])}</div>' if s.get("texto") else "")
                 + f'<div class="fonte">Fonte: {_esc(s.get("fonte", ""))}</div>')
    elif t == "lista":
        itens = "".join(f"<li>{_esc(i)}</li>" for i in s["itens"])
        corpo = f'<div class="titulo">{_esc(s.get("titulo", ""))}</div><ol class="lista">{itens}</ol>'
    elif t == "cta":
        classe += " invertido"
        foto = _img(autor.get("foto"), base)
        corpo = (f'<div class="titulo grande">{_esc(s["titulo"])}</div>'
                 + (f'<div class="sub">{_esc(s["texto"])}</div>' if s.get("texto") else "")
                 + (f'<div class="autor"><img class="foto" src="{foto}"><div><div class="nome">{_esc(autor.get("nome"))}</div>'
                    f'<div class="handle">{_esc(autor.get("handle"))}</div></div></div>' if foto else
                    f'<div class="autor"><div><div class="nome">{_esc(autor.get("nome"))}</div>'
                    f'<div class="handle">{_esc(autor.get("handle"))}</div></div></div>'))
    seta = '<div class="seta">deslize →</div>' if n == 1 and total > 1 else ""
    rodape = f'<div class="rodape"><span>{_esc(autor.get("handle", ""))}</span><span>{n}/{total}</span></div>'
    return (f'<!doctype html><html><head><meta charset="utf-8"><style>{_css(idv, w, h)}</style></head>'
            f'<body><div class="{classe}">{corpo}{seta}{rodape}</div></body></html>')


# ------------------------------------------------------------------ render
def achar_chrome():
    candidatos = [shutil.which(x) for x in ("google-chrome", "google-chrome-stable", "chromium", "chromium-browser", "chrome")]
    candidatos += ["/opt/pw-browsers/chromium", "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
                   "C:/Program Files/Google/Chrome/Application/chrome.exe",
                   "C:/Program Files (x86)/Google/Chrome/Application/chrome.exe"]
    for c in candidatos:
        if c and Path(c).exists():
            return c
    raise RuntimeError("Chrome/Chromium não encontrado: instale o Google Chrome.")


def _foto_png(html_path, png, w, h, chrome):
    # renderiza com folga de altura (o headless reserva parte da janela) e recorta no tamanho exato
    r = subprocess.run([chrome, "--headless=new", "--no-sandbox", "--disable-gpu", "--hide-scrollbars",
                        "--force-device-scale-factor=1", f"--window-size={w},{h + 240}", "--virtual-time-budget=3000",
                        "--allow-file-access-from-files", f"--screenshot={png}", html_path.resolve().as_uri()],
                       capture_output=True, text=True, timeout=120)
    if not Path(png).exists():
        raise RuntimeError("falha ao renderizar slide:\n" + r.stderr[-1500:])
    from PIL import Image
    im = Image.open(png)
    im.crop((0, 0, w, h)).save(png)


def _palavras(s):
    campos = ("titulo", "subtitulo", "texto", "afirmacao", "legenda")
    n = sum(len(str(s.get(c, "")).split()) for c in campos)
    return n + sum(len(i.split()) for i in s.get("itens", []))


def gerar(spec, pasta, formato="4x5", base=None):
    pasta = Path(pasta)
    pasta.mkdir(parents=True, exist_ok=True)
    base = Path(base or pasta)
    w, h = FORMATOS[formato]
    idv = IDENTIDADES[spec.get("identidade", "juridico_classico")]
    autor = spec.get("autor", {})
    chrome = achar_chrome()
    slides = spec["slides"]
    pngs, alertas = [], []
    for n, s in enumerate(slides, 1):
        pal = _palavras(s)
        limite = 12 if s["tipo"] in ("capa", "texto") else 30
        if pal > limite:
            alertas.append(f"slide {n} ({s['tipo']}): {pal} palavras (recomendado ≤ {limite})")
        arq = pasta / f"slide_{n:02d}_{formato}.html"
        arq.write_text(html_slide(s, idv, autor, n, len(slides), w, h, base), encoding="utf-8")
        png = pasta / f"slide_{n:02d}_{formato}.png"
        _foto_png(arq, png, w, h, chrome)
        pngs.append(png)
    if not 5 <= len(slides) <= 12:
        alertas.append(f"{len(slides)} slides (recomendado 7-10)")
    if slides and slides[-1]["tipo"] != "cta":
        alertas.append("último slide não é CTA")
    c = contraste(idv["fundo"], idv["texto"])
    if c < 4.5:
        alertas.append(f"contraste texto/fundo {c}:1 (< 4,5:1 WCAG)")
    from PIL import Image
    imgs = [Image.open(p).convert("RGB") for p in pngs]
    pdf = pasta / f"carrossel_{formato}.pdf"
    imgs[0].save(pdf, save_all=True, append_images=imgs[1:], resolution=150)
    rel = {"formato": formato, "slides": len(slides), "png": [p.name for p in pngs], "pdf": pdf.name,
           "contraste": c, "alertas": alertas}
    (pasta / f"relatorio_{formato}.json").write_text(json.dumps(rel, ensure_ascii=False, indent=1), encoding="utf-8")
    return rel


def mosaico(pasta, formato="4x5", largura=270):
    from PIL import Image
    pngs = sorted(Path(pasta).glob(f"slide_*_{formato}.png"))
    ims = [Image.open(p).resize((largura, int(largura * Image.open(p).height / Image.open(p).width))) for p in pngs]
    m = Image.new("RGB", ((largura + 10) * len(ims), ims[0].height), "white")
    for i, im in enumerate(ims):
        m.paste(im, (i * (largura + 10), 0))
    out = Path(pasta) / f"mosaico_{formato}.png"
    m.save(out)
    return out
