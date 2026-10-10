"""Orquestrador: executa uma PAUTA de ponta a ponta — material → braço (vídeo ou foto) → peças por rede →
conformidade → pacote de publicação — e atualiza o status da pauta.

Campos da pauta que o fluxo lê (além de tema, gancho, formato, perfil):
  material      vídeo bruto (reels/video_longo) | pasta/arquivo de spec (carrossel/post/stories)
  srt / transcricao   legenda pronta ou JSON de palavras (sem Whisper)
  react         {"original": …, "reacao": …, "roteiro": {...} ou caminho}   (formato react)
  spec          dict do carrossel/post (alternativa ao arquivo em `material`)
  titulo_capa, thumb_texto, legenda_corpo, hashtags, dur ("25-60"), estilo
  usa_ia, impulsionar, musica, musica_licenca, terceiro, credito          (conformidade)
Saída: `dados/producao/<pauta>/` com as peças, `pacote/` (PUBLICAR.md) e `fluxo.json`.
"""
import json
from pathlib import Path

from PIL import Image

from ..nucleo import aprendizado, caminhos, plataformas
from ..nucleo import perfis as _perfis
from . import pautas as _pautas
from . import publicacao

IMG_POR_FORMATO = {
    "carrossel": ["instagram_carrossel", "tiktok_foto", "linkedin_documento", "facebook_foto", "threads_imagem"],
    "post": ["instagram_feed", "facebook_foto", "linkedin_imagem", "x_imagem", "threads_imagem", "pinterest_imagem"],
    "stories": ["instagram_stories_img", "whatsapp_status_img"],
}
FORMATO_IMG = {(1080, 1350): "4x5", (1080, 1920): "9x16", (1080, 1080): "1x1", (1200, 675): "16x9",
               (1000, 1500): "2x3", (1280, 720): "thumb"}


def _redes_do_perfil(p):
    return set(p.get("redes", {}))


def _destinos(p, formato):
    redes = _redes_do_perfil(p)
    if formato in ("reels", "react", "video_longo"):
        ds = [d for d in plataformas.destinos_do_perfil(p, plataformas.V)]
        if formato == "video_longo" and "youtube_video" not in ds:
            ds.append("youtube_video")
        if formato != "video_longo":
            ds = [d for d in ds if d != "youtube_video"]
        return sorted(set(ds))
    return [d for d in IMG_POR_FORMATO.get(formato, []) if plataformas.destino(d)["rede"] in redes]


def _ajustar_imagem(png, destino, saida):
    """Converte a arte para o tamanho exato do destino (só redimensiona se a proporção bater; senão encaixa)."""
    d = plataformas.destino(destino)
    im = Image.open(png).convert("RGB")
    if im.size != (d["w"], d["h"]):
        alvo = d["w"] / d["h"]
        if abs(im.width / im.height - alvo) < 0.02:
            im = im.resize((d["w"], d["h"]), Image.LANCZOS)
        else:
            fundo = im.resize((d["w"], d["h"])).filter(__import__("PIL.ImageFilter", fromlist=["x"]).GaussianBlur(30))
            esc = min(d["w"] / im.width, d["h"] / im.height)
            im2 = im.resize((int(im.width * esc), int(im.height * esc)), Image.LANCZOS)
            fundo.paste(im2, ((d["w"] - im2.width) // 2, (d["h"] - im2.height) // 2))
            im = fundo
    im.save(saida, quality=93)
    return Path(saida)


def _formato_para(destino):
    d = plataformas.destino(destino)
    return FORMATO_IMG.get((d["w"], d["h"]), "4x5")


def _ler_spec(pauta):
    if pauta.get("spec"):
        return pauta["spec"], Path(caminhos.RAIZ)
    m = Path(pauta.get("material") or "")
    if m.is_dir():
        m = next(iter(sorted(m.glob("*.json"))), m)
    if not m.exists():
        raise FileNotFoundError(f"pauta {pauta['id']}: informe 'spec' ou um JSON em 'material'")
    return json.loads(m.read_text(encoding="utf-8")), m.parent


def _video(pauta, p, pasta, destinos):
    from ..video import analise, capcut, exportar, plano, producao, react, render
    from ..foto import capas
    prod_dir = pasta / "video"
    prod_dir.mkdir(parents=True, exist_ok=True)
    texto, final = "", None
    if pauta["formato"] == "react":
        r = pauta.get("react") or {}
        roteiro = r.get("roteiro")
        if isinstance(roteiro, str):
            roteiro = json.loads(Path(roteiro).read_text(encoding="utf-8"))
        final, rel = react.renderizar(r["original"], r["reacao"], roteiro, prod_dir)
        texto = r.get("texto", "")
        info = {"react": rel}
    else:
        dmin, _, dmax = str(pauta.get("dur", "25-60")).partition("-")
        an = analise.analisar(pauta["material"], prod_dir / "analise.json", srt=pauta.get("srt"),
                              transcricao=pauta.get("transcricao"))
        pl = plano.gerar(an, p.get("preset_video", "juridico"), float(dmin), float(dmax or dmin))
        plano.salvar(pl, prod_dir / "plano.json")
        render.renderizar(pl, prod_dir, base=True, final=False)
        a = p.get("assinatura", {})
        estilo = pauta.get("estilo") or p.get("estilo_video", "auto")
        fundo = p.get("fundo_foto") or None
        if fundo and not Path(fundo).is_absolute():
            fundo = str(caminhos.RAIZ / fundo)
        abre_com_efeito = any(x["tipo"] in ("titulo", "camadas") and float(x["ini"]) < 1.0
                              for x in pauta.get("efeitos", []))
        prod, final = producao.produzir(pl, prod_dir / "base.mp4", prod_dir, estilo, nome=a.get("nome"),
                                        cargo=_perfis.assinatura_texto(p) or None, titulo=pauta.get("titulo_abertura"),
                                        musica=pauta.get("musica"), biblioteca_musica=p.get("musica_biblioteca") or None,
                                        fundo_foto=fundo, sem_abertura=abre_com_efeito)
        if pauta.get("versao_limpa", True):     # R18: versão sem legenda queimada (recorte/voz em cache)
            info_limpa = producao.renderizar(prod, prod_dir / "base.mp4", prod_dir, sem_legenda=True,
                                             saida="final_sem_legenda.mp4")
        capcut.salvar_v2(prod, pl, prod_dir)
        vid = aprendizado.registrar_video(prod, pl, prod_dir)
        texto = " ".join(w["w"] for w in prod["palavras"])
        info = {"estilo": prod["estilo"], "aprendizado_id": vid, "composicao": prod.get("composicao"),
                "voz": prod.get("voz_tratamento")}
        if pauta.get("versao_limpa", True):
            info["final_sem_legenda"] = str(info_limpa)
    if pauta.get("efeitos"):     # efeitos de edição IA (R15) sobre o vídeo produzido
        from ..video import efeitos
        pal = prod["palavras"] if pauta["formato"] != "react" else None
        r_ef = efeitos.aplicar(final, pauta["efeitos"], prod_dir / "final_efeitos.mp4", tema=pauta.get("tema_efeitos"),
                               perfil=p, palavras=pal, prod=prod if pauta["formato"] != "react" else None)
        final = Path(r_ef["saida"])
        info["efeitos"] = r_ef["efeitos"]
        info.setdefault("avisos_efeitos", []).extend(r_ef["avisos"])
    from ..video import qc       # o Claude revisa o próprio corte antes de entregar (R18)
    r_qc = qc.revisar(final, pasta / "qc")
    info["qc"] = {"sinal": r_qc["sinal"], "folha": r_qc["folha"]}
    exp = exportar.exportar(final, pasta / "exportar", destinos)
    pecas = {d: [pasta / "exportar" / f for f in v["arquivos"]] for d, v in exp["destinos"].items()}
    capa = capas.capa_reels(final, pauta.get("titulo_capa") or pauta.get("gancho") or pauta["tema"], pasta / "capa", p,
                            rotulo=pauta.get("pilar", ""))
    for d in pecas:
        if plataformas.destino(d)["rede"] in ("instagram", "facebook", "tiktok", "kwai"):
            pecas[d].append(pasta / "capa" / capa["capa"])
    if "youtube_video" in pecas:
        th = capas.thumbnail(final, pauta.get("thumb_texto") or pauta["tema"][:30], pasta / "thumb", p)
        pecas["youtube_video"].append(pasta / "thumb" / th["thumbnail"])
    alertas = [f"{d}: {a}" for d, v in exp["destinos"].items() for a in v["alertas"]] + \
        [f"capa: {a}" for a in capa["alertas"]] + [f"efeitos: {a}" for a in info.get("avisos_efeitos", [])] + \
        [f"qc: {i['texto']}" for i in r_qc["itens"]]
    return pecas, texto, {"final": str(final), **info, "alertas_exportacao": alertas}


def _foto(pauta, p, pasta, destinos):
    from ..foto import carrossel, post
    spec, base = _ler_spec(pauta)
    arte = pasta / "arte"
    formatos = sorted({_formato_para(d) for d in destinos} - {"thumb"}) or ["4x5"]
    pecas, alt = {}, ""
    if pauta["formato"] == "carrossel":
        spec.setdefault("identidade", p.get("identidade_foto", "juridico_classico"))
        a = p.get("assinatura", {})
        spec.setdefault("autor", {"nome": a.get("nome"), "handle": a.get("handle"), "foto": p.get("foto_autor") or None})
        rels = {f: carrossel.gerar(spec, arte, f if f in carrossel.FORMATOS else "4x5", base=base) for f in formatos}
        alt = publicacao.texto_alternativo(spec["slides"])
        texto = " ".join(str(v) for s in spec["slides"] for v in s.values() if isinstance(v, str))
        for d in destinos:
            f = _formato_para(d)
            r = rels.get(f) or rels[formatos[0]]
            if plataformas.destino(d)["tipo"] == plataformas.D:
                pecas[d] = [arte / r["pdf"]]
            else:
                lim = plataformas.destino(d).get("itens", (1, 20))[1]
                pecas[d] = [_ajustar_imagem(arte / png, d, arte / f"{d}_{i + 1:02d}.jpg")
                            for i, png in enumerate(r["png"][:lim])]
        alertas = sorted({a for r in rels.values() for a in r["alertas"]})
    else:
        rel = post.gerar(spec, arte, formatos, perfil=p, base=base)
        alt = publicacao.texto_alternativo(spec.get("texto") or spec.get("titulo") or "")
        texto = " ".join(str(v) for v in spec.values() if isinstance(v, str))
        for d in destinos:
            pecas[d] = [_ajustar_imagem(arte / f"post_{_formato_para(d)}.png", d, arte / f"{d}.jpg")]
        alertas = rel["alertas"]
    return pecas, texto, {"alt": alt, "alertas_arte": alertas}


def executar(pauta_id, pasta=None, agenda=None):
    pauta = _pautas.obter(pauta_id)
    p = _perfis.carregar(pauta["perfil"])
    pasta = Path(pasta or caminhos.DADOS / "producao" / pauta_id)
    pasta.mkdir(parents=True, exist_ok=True)
    destinos = pauta.get("destinos") or _destinos(p, pauta["formato"])
    if not destinos:
        raise RuntimeError(f"perfil {p['id']} não tem redes para o formato {pauta['formato']}")
    if pauta["formato"] in ("reels", "react", "video_longo"):
        pecas, texto, info = _video(pauta, p, pasta, destinos)
    else:
        pecas, texto, info = _foto(pauta, p, pasta, destinos)
    if not agenda and pauta.get("data_alvo"):
        agenda = {d: f"{pauta['data_alvo']} {pauta.get('hora', '19:00')}" for d in pecas}
    peca = {k: pauta[k] for k in ("usa_ia", "impulsionar", "musica", "musica_licenca", "terceiro", "credito",
                                  "ia_rosto_voz_real") if k in pauta}
    if pauta["formato"] == "react":
        peca.setdefault("terceiro", True)
        peca.setdefault("credito", (pauta.get("react") or {}).get("credito"))
    pac = publicacao.pacote(p, pasta / "pacote", pecas, pauta.get("gancho") or pauta["tema"],
                            pauta.get("legenda_corpo", ""), pauta.get("hashtags"), texto, peca, agenda,
                            alt=info.get("alt"), avisos=info.get("alertas_exportacao", []) + info.get("alertas_arte", []))
    if info.get("qc"):          # entrega profissional versionada (R18): prévia, .srt, QC e nota de entrega
        from . import entrega
        pj = pasta / "video" / "producao.json"
        pal = json.loads(pj.read_text(encoding="utf-8")).get("palavras") if pj.exists() else None
        info["entrega"] = entrega.preparar(pasta, info["final"], pal, info["qc"], pasta / "pacote" / "PUBLICAR.md",
                                           pauta.get("tema", ""), list(pecas), limpo=info.get("final_sem_legenda"))
    status = "produzido"
    _pautas.atualizar(pauta_id, status=status, pecas={"pasta": str(pasta), "pacote": str(pasta / "pacote"),
                                                     "conformidade": pac["conformidade"]["sinal"]})
    res = {"pauta": pauta_id, "perfil": p["id"], "formato": pauta["formato"], "destinos": destinos,
           "conformidade": pac["conformidade"]["sinal"], "publicar": str(pasta / "pacote" / "PUBLICAR.md"), **info}
    (pasta / "fluxo.json").write_text(json.dumps(res, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    return res
