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
from pathlib import Path

from .motor import (FORMATOS, IDENTIDADES, _esc, _destacar, _img, _css, _foto_png, achar_chrome,  # noqa: F401
                    contraste, identidade)


CSS_EDITORIAL = """
.slide.ed .titulo { font-size: 92px; line-height: .98; letter-spacing: -2px; }
.slide.ed .titulo.grande { font-size: 118px; }
.fx { display: flex; align-items: center; gap: 18px; }
.fx-p { flex: 0 0 250px; text-align: center; } .fx-p img, .fx-vazio { width: 250px; height: 400px; object-fit: cover;
  border-radius: 28px; border: 8px solid #111; background: #ddd; }
.fx-r { font-size: 24px; letter-spacing: 4px; margin-top: 12px; color: var(--sutil); text-transform: uppercase; }
.fx-seta { font-size: 56px; color: var(--acento); }
.fx-m { flex: 1; text-align: center; } .fx-mt { font-family: 'Playfair Display', serif; font-weight: 700; font-size: 46px; margin-top: 14px; }
.fx-ms { font-size: 26px; color: var(--sutil); }
.ic { flex: 0 0 74px; height: 74px; border-radius: 20px; display: flex; align-items: center; justify-content: center; font-size: 36px;
  background: color-mix(in srgb, var(--acento) 14%, white); color: var(--acento); font-weight: 800; }
.ic.grande { width: 150px; height: 150px; margin: 0 auto; font-size: 90px; border-radius: 36px; }
.grade { display: grid; grid-template-columns: 1fr 1fr; gap: 18px; }
.cd { display: flex; gap: 18px; align-items: center; background: rgba(255,255,255,.75); border-radius: 22px; padding: 20px 22px;
  box-shadow: 0 6px 20px rgba(0,0,0,.05); }
.cd-t { font-family: 'Playfair Display', serif; font-weight: 700; font-size: 34px; line-height: 1.1; }
.cd-s { font-size: 23px; color: var(--sutil); line-height: 1.3; margin-top: 4px; }
.term { background: #16181D; border-radius: 26px; padding: 28px 34px 34px; box-shadow: 0 24px 60px rgba(0,0,0,.25); }
.term-b i { display: inline-block; width: 22px; height: 22px; border-radius: 50%; margin-right: 10px; background: #E5604D; }
.term-b i:nth-child(2) { background: #E9B44C; } .term-b i:nth-child(3) { background: #5BB26C; }
.term pre { margin-top: 24px; color: #EDEDED; font: 500 31px/1.5 'Courier New', monospace; white-space: pre-wrap; }
.pe { font-family: 'Playfair Display', serif; font-style: italic; font-size: 44px; color: var(--acento2, var(--acento)); line-height: 1.2; }
.ad { display: flex; align-items: center; gap: 20px; } .ad-c { position: relative; flex: 1; }
.ad-c img { width: 100%; height: 520px; object-fit: cover; border-radius: 26px; }
.ad-c.depois img { box-shadow: 0 0 0 6px var(--acento); }
.ad-tag { position: absolute; left: 50%; top: -22px; transform: translateX(-50%); background: #16181D; color: #fff; font-size: 22px;
  letter-spacing: 3px; padding: 8px 18px; border-radius: 999px; white-space: nowrap; } .ad-c.depois .ad-tag { background: var(--acento); }
.ad-l { display: grid; grid-template-columns: 1fr 1fr; gap: 12px 24px; font-size: 30px; }
.ad-i { display: flex; gap: 14px; align-items: center; } .ad-i .ic { flex: 0 0 44px; height: 44px; font-size: 24px; border-radius: 12px; }
.cp { text-align: center; display: flex; flex-direction: column; gap: 30px; align-items: center; }
.cp .rotulo { letter-spacing: 14px; font-size: 34px; }
.cp-p { font-family: 'Playfair Display', serif; font-weight: 900; font-size: 190px; line-height: .9; color: var(--acento2, var(--texto)); }
.cp-t { font-family: 'Playfair Display', serif; font-size: 50px; line-height: 1.2; }
"""


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
    elif t == "fluxo":
        de, meio, para = s.get("de", {}), s.get("meio", {}), s.get("para", {})
        def ponta(x):
            img = _img(x.get("imagem"), base)
            return ('<div class="fx-p">' + (f'<img src="{img}">' if img else '<div class="fx-vazio"></div>')
                    + f'<div class="fx-r">{_esc(x.get("rotulo", ""))}</div></div>')
        cards = "".join(f'<div class="cd"><div class="ic">{_esc(c.get("icone", "•"))}</div><div><div class="cd-t">'
                        f'{_esc(c["titulo"])}</div><div class="cd-s">{_esc(c.get("texto", ""))}</div></div></div>'
                        for c in s.get("cards", []))
        corpo = (f'<div class="titulo">{_esc(s.get("titulo", ""))}</div><div class="fx">{ponta(de)}<div class="fx-seta">→</div>'
                 f'<div class="fx-m"><div class="ic grande">{_esc(meio.get("icone", "✳"))}</div><div class="fx-mt">'
                 f'{_esc(meio.get("titulo", ""))}</div><div class="fx-ms">{_esc(meio.get("sub", ""))}</div></div>'
                 f'<div class="fx-seta">→</div>{ponta(para)}</div><div class="grade">{cards}</div>')
    elif t == "grade":
        cards = "".join(f'<div class="cd"><div class="ic">{_esc(c.get("icone", "•"))}</div><div><div class="cd-t">'
                        f'{_esc(c["titulo"])}</div><div class="cd-s">{_esc(c.get("texto", ""))}</div></div></div>'
                        for c in s.get("cards", []))
        corpo = (f'<div class="titulo">{_esc(s.get("titulo", ""))}</div><div class="grade">{cards}</div>'
                 + (f'<div class="pe">{_esc(s["rodape"])}</div>' if s.get("rodape") else ""))
    elif t == "terminal":
        corpo = (f'<div class="titulo">{_esc(s.get("titulo", ""))}</div><div class="term"><div class="term-b"><i></i><i></i><i></i></div>'
                 f'<pre>{html.escape(s.get("codigo", ""))}</pre></div>'
                 + (f'<div class="pe">{_esc(s["rodape"])}</div>' if s.get("rodape") else ""))
    elif t == "antes_depois":
        a, b = s.get("antes", {}), s.get("depois", {})
        itens = "".join(f'<div class="ad-i"><span class="ic">✓</span>{_esc(i)}</div>' for i in s.get("itens", []))
        corpo = (f'<div class="titulo">{_esc(s.get("titulo", ""))}</div><div class="ad"><div class="ad-c">'
                 f'<div class="ad-tag">{_esc(a.get("rotulo", "ANTES"))}</div><img src="{_img(a.get("imagem"), base)}"></div>'
                 f'<div class="fx-seta">→</div><div class="ad-c depois"><div class="ad-tag">{_esc(b.get("rotulo", "DEPOIS"))}</div>'
                 f'<img src="{_img(b.get("imagem"), base)}"></div></div><div class="ad-l">{itens}</div>'
                 + (f'<div class="pe">{_esc(s["rodape"])}</div>' if s.get("rodape") else ""))
    elif t == "cta_palavra":
        corpo = (f'<div class="cp"><div class="rotulo">{_esc(s.get("rotulo", "COMENTE"))}</div>'
                 f'<div class="cp-p">“{_esc(s["palavra"])}”</div><div class="cp-t">{_esc(s.get("texto", ""))}</div>'
                 + (f'<div class="pe">{_esc(s["rodape"])}</div>' if s.get("rodape") else "") + "</div>")
    seta = '<div class="seta">deslize →</div>' if n == 1 and total > 1 and not idv.get("cabecalho") else ""
    if idv.get("cabecalho"):
        rodape = (f'<div class="cab"><span><b>{n:02d}</b> / {total:02d}</span><span>{_esc(s.get("kicker", ""))}</span></div>'
                  f'<div class="rodape"><span></span><span>{_esc(autor.get("nome") or autor.get("handle", ""))}</span></div>')
        return (f'<!doctype html><html><head><meta charset="utf-8"><style>{_css(idv, w, h)}{CSS_EDITORIAL}</style></head>'
                f'<body><div class="{classe} ed">{corpo}{rodape}</div></body></html>')
    rodape = f'<div class="rodape"><span>{_esc(autor.get("handle", ""))}</span><span>{n}/{total}</span></div>'
    return (f'<!doctype html><html><head><meta charset="utf-8"><style>{_css(idv, w, h)}</style></head>'
            f'<body><div class="{classe}">{corpo}{seta}{rodape}</div></body></html>')


def _palavras(s):
    campos = ("titulo", "subtitulo", "texto", "afirmacao", "legenda")
    n = sum(len(str(s.get(c, "")).split()) for c in campos)
    n += sum(len(str(c.get("titulo", "")).split()) + len(str(c.get("texto", "")).split()) for c in s.get("cards", []))
    return n + sum(len(i.split()) for i in s.get("itens", []))


def gerar(spec, pasta, formato="4x5", base=None):
    pasta = Path(pasta)
    pasta.mkdir(parents=True, exist_ok=True)
    base = Path(base or pasta)
    w, h = FORMATOS[formato]
    idv = identidade(spec.get("identidade", "juridico_classico"))
    autor = spec.get("autor", {})
    chrome = achar_chrome()
    slides = spec["slides"]
    pngs, alertas = [], []
    for n, s in enumerate(slides, 1):
        pal = _palavras(s)
        limite = 12 if s["tipo"] in ("capa", "texto") else 70 if s["tipo"] in ("fluxo", "grade") else 30
        if pal > limite:
            alertas.append(f"slide {n} ({s['tipo']}): {pal} palavras (recomendado ≤ {limite})")
        arq = pasta / f"slide_{n:02d}_{formato}.html"
        arq.write_text(html_slide(s, idv, autor, n, len(slides), w, h, base), encoding="utf-8")
        png = pasta / f"slide_{n:02d}_{formato}.png"
        _foto_png(arq, png, w, h, chrome)
        pngs.append(png)
    if not 5 <= len(slides) <= 12:
        alertas.append(f"{len(slides)} slides (recomendado 7-10)")
    if slides and slides[-1]["tipo"] not in ("cta", "cta_palavra"):
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

__all__ = ["FORMATOS", "IDENTIDADES", "gerar", "mosaico", "html_slide", "contraste", "identidade"]
