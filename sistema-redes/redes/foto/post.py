"""Posts de imagem única e stories: JSON → PNG em qualquer formato (feed 4:5/1:1, stories 9:16, LinkedIn/X 16:9…).

Tipos:
  frase       {"texto", "autor"?}                         citação/manifesto (uma ideia forte)
  manchete    {"rotulo", "titulo", "fonte", "data"?, "foto"?}   notícia/decisão com fonte (print editorial)
  dado        {"numero", "legenda", "fonte"}               número grande com fonte
  comunicado  {"titulo", "texto"}                          aviso institucional (expediente, nota, posicionamento)
  evento      {"dia", "mes", "titulo", "local", "hora"}     agenda, live, palestra, audiência pública
  foto        {"foto", "titulo"?, "texto"?}                foto em tela cheia com texto sobre degradê
  pergunta    {"titulo", "texto"?}                         caixa de pergunta / enquete (stories)
Exemplo de spec: {"tipo": "dado", "numero": "7 dias", "legenda": "para desistir da compra online", "fonte": "Art. 49, CDC"}
Saída: `post_<formato>.png` (+ .html editável). Stories (9x16) respeitam as zonas seguras do Instagram (R12).
"""
import json
from pathlib import Path

from ..nucleo import perfis as _perfis
from ..nucleo import plataformas
from .motor import FORMATOS, _esc, _img, contraste, identidade, pagina, renderizar

CSS = """
.post {{ position: relative; width: {w}px; height: {h}px; padding: {pt}px {pd}px {pb}px {pe}px; display: flex;
  flex-direction: column; justify-content: center; gap: 34px; overflow: hidden; }}
.post .titulo {{ font-size: {t1}px; }} .post .titulo.grande {{ font-size: {t2}px; }}
.post .big {{ font-size: {big}px; }}
.marca {{ position: absolute; left: {pe}px; right: {pd}px; bottom: {mb}px; display: flex; justify-content: space-between;
  align-items: center; font-size: 28px; color: var(--sutil); letter-spacing: 1px; }}
.marca b {{ color: var(--texto); font-weight: 800; letter-spacing: .5px; }}
.aspas {{ font-family: 'Playfair Display', serif; font-size: 220px; line-height: .6; color: var(--acento); height: 90px; }}
.calendario {{ display: inline-flex; flex-direction: column; align-items: center; justify-content: center; width: 220px;
  height: 230px; border-radius: 28px; background: var(--acento); color: var(--fundo); align-self: flex-start; }}
.calendario .d {{ font-size: 120px; font-weight: 900; line-height: 1; }}
.calendario .m {{ font-size: 36px; font-weight: 800; letter-spacing: 4px; text-transform: uppercase; }}
.info {{ font-size: 40px; color: var(--sutil); line-height: 1.4; }}
.fotofundo {{ position: absolute; inset: 0; background-size: cover; background-position: center 30%; }}
.degrade {{ position: absolute; inset: 0; background: linear-gradient(180deg, rgba(0,0,0,0) 35%, rgba(0,0,0,.78) 100%); }}
.sobre {{ position: relative; margin-top: auto; color: #fff; }}
.sobre .sub {{ color: rgba(255,255,255,.85); }}
.caixa {{ background: color-mix(in srgb, var(--texto) 6%, var(--fundo)); border: 3px solid var(--acento);
  border-radius: 36px; padding: 56px; }}
.resposta {{ margin-top: 30px; height: 120px; border-radius: 24px; background: color-mix(in srgb, var(--texto) 10%, var(--fundo));
  display: flex; align-items: center; padding: 0 40px; font-size: 34px; color: var(--sutil); }}
.manchete-foto {{ width: 100%; height: {fh}px; object-fit: cover; border-radius: 22px; }}
"""


def _medidas(fmt, w, h):
    seg = plataformas.DESTINOS["instagram_stories_img"]["segura"] if fmt == "9x16" else None
    largo = w > h
    base = dict(pt=110, pb=150, pe=92, pd=92, mb=56, t1=88, t2=104, big=280, fh=int(h * 0.36))
    if seg:
        base.update(pt=seg[0] + 30, pb=seg[1] + 110, pe=seg[3] + 40, pd=seg[2] + 40, mb=seg[1] + 20, t1=92, t2=112,
                    big=300, fh=520)
    if largo:
        base.update(pt=80, pb=120, pe=120, pd=120, mb=40, t1=76, t2=92, big=220, fh=int(h * 0.42))
    if fmt == "1x1":
        base.update(t1=80, t2=96, big=240, fh=360)
    return base


def html_post(spec, idv, w, h, fmt, autor, base):
    t = spec["tipo"]
    corpo, classe = "", "post"
    if t == "frase":
        corpo = (f'<div class="aspas">“</div><div class="titulo grande">{_esc(spec["texto"])}</div>'
                 + (f'<div class="sub">— {_esc(spec["autor"])}</div>' if spec.get("autor") else ""))
    elif t == "manchete":
        foto = _img(spec.get("foto"), base)
        corpo = ((f'<img class="manchete-foto" src="{foto}">' if foto else "")
                 + f'<div class="rotulo">{_esc(spec.get("rotulo", "NOTÍCIA"))}</div><div class="linha"></div>'
                 f'<div class="titulo">{_esc(spec["titulo"])}</div>'
                 f'<div class="fonte">Fonte: {_esc(spec.get("fonte", ""))}{" · " + _esc(spec["data"]) if spec.get("data") else ""}</div>')
    elif t == "dado":
        corpo = (f'<div class="big">{_esc(str(spec["numero"]))}</div><div class="titulo">{_esc(spec["legenda"])}</div>'
                 + (f'<div class="fonte">Fonte: {_esc(spec["fonte"])}</div>' if spec.get("fonte") else ""))
    elif t == "comunicado":
        corpo = (f'<div class="rotulo">{_esc(spec.get("rotulo", "COMUNICADO"))}</div><div class="linha"></div>'
                 f'<div class="titulo">{_esc(spec["titulo"])}</div><div class="corpo">{_esc(spec.get("texto", ""))}</div>')
    elif t == "evento":
        corpo = (f'<div class="calendario"><div class="d">{_esc(str(spec["dia"]))}</div><div class="m">{_esc(spec["mes"])}</div></div>'
                 f'<div class="titulo">{_esc(spec["titulo"])}</div>'
                 f'<div class="info">{_esc(spec.get("local", ""))}<br>{_esc(spec.get("hora", ""))}</div>')
    elif t == "foto":
        foto = _img(spec["foto"], base)
        corpo = (f'<div class="fotofundo" style="background-image:url(\'{foto}\')"></div><div class="degrade"></div>'
                 f'<div class="sobre"><div class="titulo">{_esc(spec.get("titulo", ""))}</div>'
                 + (f'<div class="sub">{_esc(spec["texto"])}</div>' if spec.get("texto") else "") + "</div>")
    elif t == "pergunta":
        corpo = (f'<div class="caixa"><div class="titulo">{_esc(spec["titulo"])}</div>'
                 + (f'<div class="sub">{_esc(spec["texto"])}</div>' if spec.get("texto") else "")
                 + '<div class="resposta">Escreva sua pergunta…</div></div>')
    else:
        raise ValueError(f"tipo de post desconhecido: {t}")
    marca_cor = ' style="color:rgba(255,255,255,.8)"' if t == "foto" else ""
    marca = (f'<div class="marca"{marca_cor}><b{marca_cor}>{_esc(autor.get("nome", ""))}</b>'
             f'<span>{_esc(autor.get("handle", ""))}</span></div>')
    css = CSS.format(w=w, h=h, **_medidas(fmt, w, h))
    return pagina(corpo + marca, idv, w, h, css, classe)


def gerar(spec, pasta, formatos=("4x5",), perfil=None, base=None):
    """Gera o post em cada formato. `perfil` (id ou dict) define identidade e assinatura."""
    pasta = Path(pasta)
    pasta.mkdir(parents=True, exist_ok=True)
    base = Path(base or pasta)
    p = _perfis.carregar(perfil) if perfil is not None else None
    idv = identidade(spec.get("identidade") or (p or "juridico_classico"))
    a = (p or {}).get("assinatura", {})
    autor = spec.get("autor_marca") or {"nome": a.get("nome", ""), "handle": a.get("handle", "")}
    saidas, alertas = [], []
    palavras = sum(len(str(spec.get(c, "")).split()) for c in ("titulo", "texto", "legenda"))
    if palavras > 30:
        alertas.append(f"{palavras} palavras: post de imagem funciona com ≤ 30 (detalhe vai na legenda)")
    if spec["tipo"] in ("manchete", "dado") and not spec.get("fonte"):
        alertas.append("sem fonte: dado/notícia precisa de fonte e data (credibilidade e LDA)")
    c = contraste(idv["fundo"], idv["texto"])
    if c < 4.5:
        alertas.append(f"contraste {c}:1 abaixo de 4,5:1 (WCAG)")
    for fmt in formatos:
        w, h = FORMATOS[fmt]
        png = renderizar(html_post(spec, idv, w, h, fmt, autor, base), pasta / f"post_{fmt}.png", w, h)
        saidas.append(png)
    rel = {"tipo": spec["tipo"], "arquivos": [s.name for s in saidas], "contraste": c, "alertas": alertas}
    (pasta / "post.json").write_text(json.dumps(rel, ensure_ascii=False, indent=1), encoding="utf-8")
    return rel
