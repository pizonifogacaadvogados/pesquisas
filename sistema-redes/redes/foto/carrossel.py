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
import json
from pathlib import Path

from .motor import (FORMATOS, IDENTIDADES, _esc, _destacar, _img, _css, _foto_png, achar_chrome,  # noqa: F401
                    contraste, identidade)


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


def _palavras(s):
    campos = ("titulo", "subtitulo", "texto", "afirmacao", "legenda")
    n = sum(len(str(s.get(c, "")).split()) for c in campos)
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

__all__ = ["FORMATOS", "IDENTIDADES", "gerar", "mosaico", "html_slide", "contraste", "identidade"]
