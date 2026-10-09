"""Motor HTML/CSS → PNG (Chrome headless) do braço de foto: identidades visuais, tipografia, contraste.

Usado por carrossel, post, stories, capas e thumbnails. O design é HTML/CSS (o mesmo que um designer faria no
Figma/Canva), renderizado em pixel exato; fontes OFL locais (`fontes/`).
"""
import html
import re
import shutil
import subprocess
from pathlib import Path

from ..nucleo import caminhos

FORMATOS = {"4x5": (1080, 1350), "3x4": (1080, 1440), "9x16": (1080, 1920), "1x1": (1080, 1080),
            "16x9": (1920, 1080), "2x3": (1000, 1500), "thumb": (1280, 720), "191x1": (1200, 627)}
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




def identidade(nome_ou_perfil):
    """Identidade visual pelo nome, por um dict pronto ou derivada de um perfil (cores do perfil sobre a base)."""
    if isinstance(nome_ou_perfil, str):
        if nome_ou_perfil not in IDENTIDADES:
            raise KeyError(f"identidade desconhecida: {nome_ou_perfil} (opções: {', '.join(IDENTIDADES)})")
        return dict(IDENTIDADES[nome_ou_perfil])
    p = nome_ou_perfil or {}
    if "fundo" in p and "texto" in p and "acento" in p:      # já é uma identidade
        return dict(IDENTIDADES["juridico_classico"]) | p
    idv = dict(IDENTIDADES.get(p.get("identidade_foto", "juridico_classico"), IDENTIDADES["juridico_classico"]))
    c = p.get("cores") or {}
    if c.get("destaque"):
        idv["acento"] = c["destaque"]
    if c.get("primaria") and idv["fundo"].upper() in ("#F6F2EA", "#FFFFFF"):
        idv["texto"] = idv["escuro"] = c["primaria"]
    if c.get("fundo") and contraste(c["fundo"], idv["texto"]) >= 4.5:
        idv["fundo"] = idv["claro"] = c["fundo"]
    return idv


def renderizar(html_doc, png, w, h, pasta_html=None):
    """HTML completo → PNG w×h. Grava o .html ao lado (útil para revisar/editar)."""
    png = Path(png)
    arq = Path(pasta_html or png.parent) / (png.stem + ".html")
    arq.write_text(html_doc, encoding="utf-8")
    _foto_png(arq, png, w, h, achar_chrome())
    return png


def pagina(corpo, idv, w, h, css_extra="", classe="slide"):
    return (f'<!doctype html><html><head><meta charset="utf-8"><style>{_css(idv, w, h)}{css_extra}</style></head>'
            f'<body><div class="{classe}">{corpo}</div></body></html>')
