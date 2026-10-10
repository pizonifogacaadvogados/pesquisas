"""Produção profissional (versão 2): diretor + render em camadas.

Fluxo:
  plano.json (v1: cortes, palavras, gancho, clímax) + base.mp4 (já cortado, 9:16)
     → dirigir()  → producao.json  (decisões de direção; editável pelo Claude)
     → renderizar() → final.mp4     (composição em camadas, ver estudos/07 §1)

Ordem das camadas no render:
  fundo (estúdio / desfoque / original) → texto atrás da pessoa → pessoa recortada
  → câmera virtual (punch, push-in com easing, snap) → cor (LUT + halation + vinheta)
  → B-roll → cartões → emojis → legendas/abertura/lower third → trilha de luz (Tela)
  → grão → barras de cinema
"""
import json
import os
import re
import shutil
import subprocess
from pathlib import Path

from ..nucleo import aprendizado, regras
from . import assets, audio, composicao, estilos, fundos, graficos, luts, motion, recorte

W, H, FPS = 1080, 1920, 30

# ------------------------------------------------------------------ referências legais faladas
NUM = {"zero": 0, "um": 1, "uma": 1, "dois": 2, "duas": 2, "três": 3, "tres": 3, "quatro": 4, "cinco": 5, "seis": 6,
       "sete": 7, "oito": 8, "nove": 9, "dez": 10, "onze": 11, "doze": 12, "treze": 13, "quatorze": 14, "catorze": 14,
       "quinze": 15, "dezesseis": 16, "dezessete": 17, "dezoito": 18, "dezenove": 19, "vinte": 20, "trinta": 30,
       "quarenta": 40, "cinquenta": 50, "sessenta": 60, "setenta": 70, "oitenta": 80, "noventa": 90, "cem": 100,
       "cento": 100, "duzentos": 200, "trezentos": 300, "quatrocentos": 400, "quinhentos": 500, "seiscentos": 600,
       "setecentos": 700, "oitocentos": 800, "novecentos": 900, "primeiro": 1, "segundo": 2, "terceiro": 3,
       "quarto": 4, "quinto": 5, "sexto": 6, "sétimo": 7, "oitavo": 8, "nono": 9, "décimo": 10}
NORMAS = [(r"c[óo]digo de defesa do consumidor|\bcdc\b", "CDC", "Código de Defesa do Consumidor"),
          (r"\bclt\b|consolida[çc][ãa]o das leis do trabalho", "CLT", "Consolidação das Leis do Trabalho"),
          (r"constitui[çc][ãa]o", "CF", "Constituição Federal"),
          (r"c[óo]digo civil", "CC", "Código Civil"), (r"c[óo]digo penal", "CP", "Código Penal"),
          (r"c[óo]digo de processo civil|\bcpc\b", "CPC", "Código de Processo Civil"),
          (r"c[óo]digo eleitoral", "CE", "Código Eleitoral"), (r"lei maria da penha", "Lei 11.340", "Lei Maria da Penha"),
          (r"estatuto da crian[çc]a|\beca\b", "ECA", "Estatuto da Criança e do Adolescente"),
          (r"\blgpd\b|lei geral de prote[çc][ãa]o de dados", "LGPD", "Lei Geral de Proteção de Dados")]


def numero_por_extenso(palavras):
    """'quarenta e nove' → 49; aceita dígitos. Retorna (valor, n_palavras_consumidas)."""
    total, usadas = 0, 0
    for w in palavras:
        lw = regras.limpa(w)
        if lw.isdigit():
            return int(lw), usadas + 1
        if lw == "e" and usadas:
            usadas += 1
            continue
        if lw in NUM:
            total += NUM[lw]
            usadas += 1
        else:
            break
    return (total, usadas) if usadas else (None, 0)


def referencias_legais(palavras):
    """Detecta 'artigo X da/do NORMA' na fala → [{t, titulo, subtitulo}]."""
    refs = []
    texto_low = [regras.limpa(p["w"]) for p in palavras]
    for i, w in enumerate(texto_low):
        if w not in ("artigo", "art"):
            continue
        num, k = numero_por_extenso([p["w"] for p in palavras[i + 1:i + 6]])
        if num is None:
            continue
        resto = " ".join(p["w"] for p in palavras[i + 1 + k:i + 1 + k + 8]).lower()
        sigla, nome = "", ""
        for padrao, s, n in NORMAS:
            if re.search(padrao, resto):
                sigla, nome = s, n
                break
        refs.append({"t": palavras[i]["ini"], "titulo": f"Art. {num}" + (f" · {sigla}" if sigla else ""),
                     "subtitulo": nome or "Referência citada"})
    return refs


# ------------------------------------------------------------------ direção
def _palavras(plano):
    return [p for b in plano["legendas"] for p in b["palavras"]]


def _frases(palavras):
    out, atual = [], []
    for n, p in enumerate(palavras):
        atual.append(p)
        prox = palavras[n + 1] if n + 1 < len(palavras) else None
        if prox is None or re.search(r"[.!?…]$", p["w"]) or len(atual) >= 16:
            out.append({"ini": atual[0]["ini"], "fim": atual[-1]["fim"], "texto": " ".join(x["w"] for x in atual)})
            atual = []
    return out


def _titulo_curto(gancho):
    g = gancho.strip()
    if re.match(r"(?i)voc[eê] sabia", g):
        return "Você sabia?"
    ws = re.sub(r"[^\wÀ-ÿ ]", "", g).split()
    return " ".join(ws[:3]) if ws else g


def dirigir(plano, estilo="estudio", nome=None, cargo=None, titulo=None, broll_dir=None, musica=None,
            biblioteca_musica=None, diagnostico=None, fundo_foto=None, sem_abertura=False):
    """`sem_abertura`: quando um efeito (titulo/camadas, `video/efeitos.py`) vai abrir o vídeo."""
    e = estilos.ESTILOS[estilo]
    pal = _palavras(plano)
    dur = plano["duracao_final"]
    frases = _frases(pal)
    sel = plano["selecao"]
    cam = e["camera"]
    pal_sfx = estilos.SFX[e["sfx"]]
    prod = {"versao": 2, "estilo": estilo, "preset": plano["preset"], "duracao": dur, "camadas": {}, "palavras": pal}

    # fundo
    fundo = {"tipo": e["fundo"]}
    if e["fundo"] == "estudio":
        fundo["imagem"] = {"juridico": "escritorio_noturno", "politico": "marca_azul"}.get(plano["preset"], "neutro_premium")
    if fundo_foto:  # foto real do ambiente (padrão profissional); o procedural fica só como reserva
        fundo.update(tipo="estudio", foto=str(Path(fundo_foto).resolve()))
    prod["camadas"]["fundo"] = fundo

    # câmera: punch por corte + push-in alternado por frase + snap no clímax (se o estilo usa)
    mov = []
    for n, s in enumerate(plano["segmentos"]):
        if n % 2 == 1 and cam.get("punch"):
            mov.append({"tipo": "punch", "ini": s["out_ini"], "fim": s["out_fim"], "escala": cam["punch"]})
    if cam.get("push_in"):
        for n, f in enumerate(frases):
            if f["fim"] - f["ini"] >= 2.5 and n % 2 == 0:
                mov.append({"tipo": "push_in", "ini": f["ini"], "fim": f["fim"], "escala": cam["push_in"]})
    clim = next((f for f in frases if sel["climax"][:25].lower() in f["texto"].lower()), None)
    if cam.get("snap") and clim:
        mov.append({"tipo": "snap", "ini": clim["ini"], "fim": min(clim["ini"] + 1.2, clim["fim"]), "escala": cam["snap"]})
    prod["camadas"]["camera"] = mov

    # abertura
    tit = titulo or (_titulo_curto(sel["gancho"]) if e["abertura"] == "texto_atras" else sel["gancho"].rstrip("?.!") +
                     ("?" if sel["gancho"].strip().endswith("?") else ""))
    if e["abertura"] in ("cinetica", "cinetica_mono", "titulo_limpo", "titulo_caixa", "manchete") and len(tit) > 60:
        tit = " ".join(tit.split()[:9])
    ab_fim = min(3.4, dur * 0.25)
    prod["camadas"]["abertura"] = {"tipo": e["abertura"], "texto": tit, "ini": 0.0, "fim": ab_fim,
                                   "rotulo": "ANÁLISE" if plano["preset"] == "politico" else "ENTENDA",
                                   "sobrelinha": "BRASIL · 2026" if e["abertura"] == "cinetica_mono" else None}
    if sem_abertura:
        prod["camadas"]["abertura"] = {"tipo": "nenhuma", "texto": "", "ini": 0.0, "fim": 0.0, "rotulo": None}

    sons = []
    if pal_sfx.get("abertura"):
        sons.append({"som": pal_sfx["abertura"], "t": 0.0, "vol": 0.5})

    # lower third
    if e["lower_third"] and nome:
        li = ab_fim + 0.4
        prod["camadas"]["lower_third"] = {"nome": nome, "cargo": cargo or "", "ini": li, "fim": min(li + 3.8, dur - 0.5)}
        if pal_sfx.get("lower_third"):
            sons.append({"som": pal_sfx["lower_third"], "t": li, "vol": 0.35})

    # cartões de lei (detectados na fala) — o Claude pode editar/acrescentar cartões de dado
    cartoes = []
    for r in referencias_legais(pal):
        if r["t"] < ab_fim or any(abs(r["t"] - c["ini"]) < 5 for c in cartoes):
            continue
        cartoes.append({"titulo": r["titulo"], "subtitulo": r["subtitulo"], "ini": r["t"], "fim": min(r["t"] + 3.4, dur - 0.3)})
        if pal_sfx.get("cartao"):
            sons.append({"som": pal_sfx["cartao"], "t": r["t"], "vol": 0.4})
    prod["camadas"]["cartoes"] = cartoes

    # transições entre blocos de ideia: fronteiras de frase a cada ~10-15s
    trans, ult = [], ab_fim + 4
    if e["transicao"] != "corte":
        for f in frases[1:]:
            if f["ini"] - ult >= 10 and f["ini"] < dur - 4 and not any(abs(f["ini"] - c["ini"]) < 1.5 for c in cartoes):
                trans.append({"tipo": e["transicao"], "t": f["ini"]})
                ult = f["ini"]
                if pal_sfx.get("transicao"):
                    sons.append({"som": pal_sfx["transicao"], "t": max(f["ini"] - 0.25, 0), "vol": 0.35})
    prod["camadas"]["transicoes"] = trans
    if e["transicao"] == "zoom":
        for t in trans:
            mov.append({"tipo": "zoom_through", "ini": t["t"] - 0.18, "fim": t["t"] + 0.18, "escala": 1.22})

    # clímax: riser antes, se a paleta tiver
    if clim and pal_sfx.get("climax") and clim["ini"] > 2.5:
        sons.append({"som": pal_sfx["climax"], "t": clim["ini"] - 1.2, "vol": 0.25})

    # B-roll por palavra-chave (arquivos nomeados pelo tema: contrato.mp4, stf.jpg…)
    broll = []
    if broll_dir and Path(broll_dir).is_dir():
        arquivos = [p for p in Path(broll_dir).iterdir() if p.suffix.lower() in (".mp4", ".mov", ".jpg", ".jpeg", ".png")]
        ult_b = ab_fim
        for p in pal:
            alvo = regras.sem_acento(regras.limpa(p["w"]))
            for arq in arquivos:
                chave = regras.sem_acento(arq.stem.lower().split("_")[0])
                if len(chave) >= 4 and alvo.startswith(chave) and p["ini"] - ult_b >= 8 and p["ini"] < dur - 3:
                    broll.append({"arquivo": str(arq.resolve()), "ini": p["ini"], "fim": min(p["ini"] + 2.4, dur - 0.5),
                                  "palavra": p["w"]})
                    ult_b = p["ini"]
                    break
    prod["camadas"]["broll"] = broll

    prod["camadas"]["emojis"] = [ev for ev in plano["eventos"] if ev["tipo"] == "emoji"] if e["emojis"] else []
    if e["emojis"]:
        sons += [{"som": ev["som"], "t": ev["t"], "vol": 0.4} for ev in plano["eventos"] if ev["tipo"] == "sfx"]
    prod["camadas"]["legenda"] = {"tipo": e["legenda"], "fonte": e["fonte_texto"] if e["legenda"] != "forte" else "Inter"}
    prod["camadas"]["sfx"] = sorted(sons, key=lambda s: s["t"])
    # trilha: clima pelo conteúdo; faixa da biblioteca licenciada (ou a indicada); automação de volume
    humor = audio.humor_do_video(plano["texto"], plano["preset"], estilo)
    musica = musica or audio.escolher_musica(biblioteca_musica, humor)
    if musica:
        pontos = audio.automacao(pal, dur, clim["ini"] if clim else None)
        prod["camadas"]["musica"] = {"arquivo": str(Path(musica).resolve()), "humor": humor, "automacao_db": pontos}
        # transições caem na batida da música (até 0,3s de ajuste)
        bat = audio.batidas(musica)
        novos = audio.alinhar_a_batidas([t["t"] for t in trans], bat)
        for t, n in zip(trans, novos):
            t["t"] = round(n, 3)
    else:
        prod["camadas"]["musica"] = None
    prod["humor_trilha"] = humor
    # aprendizado: ajustes acumulados a partir do feedback e das métricas
    aj = aprendizado.ajustes()
    if aj:
        cm = aj.get("camera_mult", 1.0)
        for m in mov:
            m["escala"] = round(1 + (m["escala"] - 1) * cm, 3)
        prod["ajustes_aplicados"] = aj
        if prod["camadas"].get("musica") and aj.get("musica_db_delta"):
            prod["camadas"]["musica"]["automacao_db"] = [(t, db + aj["musica_db_delta"] if db > -50 else db)
                                                         for t, db in prod["camadas"]["musica"]["automacao_db"]]
        if aj.get("emoji_freq_mult", 1.0) < 1 and prod["camadas"]["emojis"]:
            passo = max(1, round(1 / aj["emoji_freq_mult"]))
            prod["camadas"]["emojis"] = prod["camadas"]["emojis"][::passo]
    if diagnostico:
        prod["diagnostico_visual"] = diagnostico
    prod["camadas"]["cor"] = {"look": e["look"],
                              "intensidade": round(min(1, max(0, e["lut_intensidade"] + aprendizado.ajustes().get("lut_intensidade_delta", 0))), 2),
                              "halation": e["halation"],
                              "vinheta": e["vinheta"], "grao": e["grao"], "barras": e["barras"]}
    return prod


# ------------------------------------------------------------------ render
def _expr_camera(mov):
    termos = []
    for m in mov:
        a, b, s = m["ini"], m["fim"], m["escala"] - 1
        d = max(b - a, 0.05)
        if m["tipo"] == "punch":
            termos.append(f"{s:.3f}*gte(t,{a:.3f})*lt(t,{b:.3f})")
        elif m["tipo"] == "push_in":  # smoothstep (ease in-out)
            p = f"clip((t-{a:.3f})/{d:.3f},0,1)"
            termos.append(f"{s:.3f}*gte(t,{a:.3f})*lt(t,{b:.3f})*({p}*{p}*(3-2*{p}))")
        elif m["tipo"] == "snap":  # ease-out cúbico na entrada, solta no fim
            p = f"clip((t-{a:.3f})/0.22,0,1)"
            q = f"clip(({b:.3f}-t)/0.25,0,1)"
            termos.append(f"{s:.3f}*gte(t,{a:.3f})*lt(t,{b:.3f})*(1-pow(1-{p},3))*({q}*{q}*(3-2*{q}))")
        elif m["tipo"] == "zoom_through":
            c = (a + b) / 2
            termos.append(f"{s:.3f}*gte(t,{a:.3f})*lt(t,{b:.3f})*(1-abs(t-{c:.3f})/{d / 2:.3f})")
    return "1+" + "+".join(termos) if termos else "1"


def _ass_para_hex(cor):
    """'&H00BBGGRR' (ASS) → '#RRGGBB' (CSS)."""
    v = cor.replace("&H", "").replace("&", "")[-6:]
    return f"#{v[4:6]}{v[2:4]}{v[0:2]}"


def _tem_audio(video):
    out = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "a", "-show_entries", "stream=index",
                          "-of", "csv=p=0", str(video)], capture_output=True, text=True).stdout
    return bool(out.strip())


def renderizar(prod, base, pasta, sfx_dir=None):
    pasta = Path(pasta).resolve()
    pasta.mkdir(parents=True, exist_ok=True)
    a_dir = pasta / "assets"
    dur = prod["duracao"]
    cam = prod["camadas"]
    cor = cam["cor"]
    # fontes ao lado do ASS (caminho relativo funciona em qualquer sistema)
    if not (pasta / "fontes").exists():
        shutil.copytree(graficos.FONTES_DIR, pasta / "fontes")

    entradas = ["-i", str(base)]
    k = 1
    partes = []
    precisa_matte = cam["fundo"]["tipo"] in ("estudio", "desfoque_profundidade") or cam["abertura"]["tipo"] == "texto_atras"

    # ---------- 1. fundo + pessoa
    if precisa_matte:
        matte, motor = recorte.matte_auto(base, a_dir / "matte.mp4")
        prod.setdefault("composicao", {})["recorte"] = motor
        entradas += ["-i", str(matte)]
        k_m = k
        k += 1
        partes.append(f"[{k_m}:v]{composicao.filtro_matte(motor)},split[m][mlw]")
        if cam["fundo"]["tipo"] == "estudio":
            if cam["fundo"].get("foto"):
                bg = composicao.placa_de_fundo(cam["fundo"]["foto"], a_dir / "fundo_foto.png")
            else:
                bg = fundos.gerar(cam["fundo"]["imagem"], a_dir / f"fundo_{cam['fundo']['imagem']}.png")
            entradas += ["-loop", "1", "-framerate", str(FPS), "-t", f"{dur:.3f}", "-i", str(bg)]
            partes.append(f"[{k}:v]scale={W}:{H},format=yuv420p[bg0]")
            k += 1
            partes.append("[0:v]split[v0][v1]")
            casar, medidas = composicao.casar_cor(base, matte, bg)
            prod["composicao"]["cor"] = medidas
            partes.append(f"[v1]{casar}[vp]")
        else:
            partes.append("[0:v]split=3[v0][v1][v2]")
            fonte_bg = "[v2]gblur=sigma=16,eq=brightness=-0.05:saturation=0.85[bg0]" \
                if cam["fundo"]["tipo"] == "desfoque_profundidade" else "[v2]null[bg0]"
            partes.append(fonte_bg)
            partes.append("[v1]null[vp]")
        partes.append("[vp]format=yuva420p[vpa];[vpa][m]alphamerge[pessoa]")
        partes.append("[v0]nullsink")
        if cam["abertura"]["tipo"] == "texto_atras":
            ab = cam["abertura"]
            e = estilos.ESTILOS[prod["estilo"]]
            est, lin = graficos.abertura("texto_atras", ab["texto"], ab["ini"], ab["fim"], e["fonte_titulo"],
                                         e["fonte_texto"], e["cor_destaque"])
            graficos.escrever_ass(pasta / "fundo.ass", est, lin)
            partes.append("[bg0]subtitles=fundo.ass:fontsdir=fontes[bg1]")
        else:
            partes.append("[bg0]null[bg1]")
        partes.append("[bg1]split[bg2][bglw]")
        partes.append("[bg2][pessoa]overlay=0:0:format=auto[cena0]")
        if cam["fundo"]["tipo"] == "estudio":  # luz do ambiente abraçando a borda
            partes.append(composicao.light_wrap("bglw", "mlw", "cena0", "cena"))
        else:
            partes.append("[bglw]nullsink;[mlw]nullsink;[cena0]null[cena]")
    else:
        partes.append("[0:v]null[cena]")

    # ---------- 2. câmera virtual
    z = _expr_camera(cam["camera"])
    partes.append(f"[cena]scale=w='2*trunc({W}*({z})/2)':h='2*trunc({H}*({z})/2)':eval=frame,"
                  f"crop={W}:{H}:(iw-{W})/2:(ih-{H})*0.36,setsar=1[cam]")

    # ---------- 3. cor: LUT (com intensidade) + halation + vinheta
    lut = luts.gerar_cube(cor["look"], a_dir / f"look_{cor['look']}.cube")
    shutil.copy(lut, pasta / "look.cube")
    partes.append(f"[cam]split[c0][c1];[c1]lut3d=file=look.cube:interp=tetrahedral[c2];"
                  f"[c0][c2]blend=all_mode=normal:all_opacity={cor['intensidade']:.2f}[lut]")
    if cor["halation"] > 0:
        partes.append(f"[lut]split[h0][h1];[h1]colorlevels=rimin=0.72:gimin=0.72:bimin=0.72,gblur=sigma=22,"
                      f"colorchannelmixer=rr=1:gg=0.42:bb=0.12[h2];"
                      f"[h0]format=gbrp[h0r];[h2]format=gbrp[h2r];"
                      f"[h0r][h2r]blend=all_mode=screen:all_opacity={cor['halation']:.2f},format=yuv420p[hal]")
    else:
        partes.append("[lut]null[hal]")
    if cor["vinheta"] > 0:
        partes.append(f"[hal]vignette=angle={0.628 * cor['vinheta'] / 0.18:.3f}:mode=forward[corv]")
    else:
        partes.append("[hal]null[corv]")
    atual = "corv"

    # ---------- 4. B-roll (Ken Burns com easing, mesma LUT)
    for n, b in enumerate(cam["broll"]):
        d = b["fim"] - b["ini"]
        img = Path(b["arquivo"]).suffix.lower() in (".jpg", ".jpeg", ".png")
        entradas += (["-loop", "1", "-framerate", str(FPS), "-t", f"{d:.3f}"] if img else ["-t", f"{d:.3f}"]) + ["-i", b["arquivo"]]
        p = f"clip(t/{d:.3f},0,1)"
        kb = f"(1+0.10*({p}*{p}*(3-2*{p})))"
        partes.append(f"[{k}:v]scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},fps={FPS},"
                      f"scale=w='2*trunc({W}*{kb}/2)':h='2*trunc({H}*{kb}/2)':eval=frame,crop={W}:{H},"
                      f"lut3d=file=look.cube,fade=t=in:st=0:d=0.12,fade=t=out:st={max(d - 0.12, 0):.3f}:d=0.12,"
                      f"setpts=PTS-STARTPTS+{b['ini']:.3f}/TB[b{n}]")
        partes.append(f"[{atual}][b{n}]overlay=0:0:enable='between(t,{b['ini']:.3f},{b['fim']:.3f})':eof_action=pass[ob{n}]")
        atual, k = f"ob{n}", k + 1

    # ---------- 4b. motion graphics (HyperFrames + GSAP): lower third, cartões e chamada em overlay com alfa
    e = estilos.ESTILOS[prod["estilo"]]
    overlay = None
    if prod.get("motion", os.environ.get("REDES_SEM_MOTION") != "1"):
        fins = [c["fim"] for c in cam["cartoes"]] + ([cam["lower_third"]["fim"]] if cam.get("lower_third") else [])
        if fins:
            proj = motion.composicao(prod, a_dir / "motion", acento=_ass_para_hex(e["cor_destaque"]), fim=min(max(fins) + 0.3, dur))
            overlay = motion.renderizar_overlay(proj.parent, a_dir / "motion.mov", fps=FPS)
    prod.setdefault("composicao", {})["motion"] = bool(overlay)

    # ---------- 5. cartões (entram subindo com fade) — só sem overlay de motion
    tema = "papel" if prod["estilo"] == "documental" else "vidro"
    for n, c in enumerate([] if overlay else cam["cartoes"]):
        png = graficos.cartao(c["titulo"], c["subtitulo"], a_dir / f"cartao_{n}.png", tema=tema,
                              fonte_titulo=e["fonte_titulo"], fonte_texto=e["fonte_texto"])
        entradas += ["-loop", "1", "-framerate", str(FPS), "-t", f"{dur:.3f}", "-i", str(png)]
        a, b = c["ini"], c["fim"]
        partes.append(f"[{k}:v]format=rgba,fade=t=in:st={a:.3f}:d=0.28:alpha=1,"
                      f"fade=t=out:st={max(b - 0.3, a):.3f}:d=0.3:alpha=1[cd{n}]")
        partes.append(f"[{atual}][cd{n}]overlay=x=(W-w)/2:y='300+40*pow(1-clip((t-{a:.3f})/0.35,0,1),3)'"
                      f":enable='between(t,{a:.3f},{b:.3f})':eval=frame[oc{n}]")
        atual, k = f"oc{n}", k + 1

    # ---------- 6. emojis (só no estilo viral)
    for n, em in enumerate(cam["emojis"]):
        png = assets.emoji_png(em["emoji"], a_dir / "emojis")
        entradas += ["-loop", "1", "-framerate", str(FPS), "-t", f"{dur:.3f}", "-i", str(png)]
        a, b = em["ini"], em["fim"]
        x = 0.22 * W if em.get("lado") == "esquerda" else 0.76 * W
        y = em.get("y", 0.24) * H
        esc = (f"if(lt(t,{a:.3f}),0.01,if(lt(t-{a:.3f},0.12),0.6+(t-{a:.3f})/0.12*0.6,"
               f"if(lt(t-{a:.3f},0.25),1.2-(t-{a:.3f}-0.12)/0.13*0.2,1)))")
        partes.append(f"[{k}:v]scale=w='2*trunc(220*{esc}/2)':h=-2:eval=frame[e{n}]")
        partes.append(f"[{atual}][e{n}]overlay=x='{x:.0f}-w/2':y='{y:.0f}-h/2':"
                      f"enable='between(t,{a:.3f},{b:.3f})':eval=frame[oe{n}]")
        atual, k = f"oe{n}", k + 1

    # ---------- 7. legendas + abertura + lower third (ASS de frente)
    pal = prod["palavras"]
    est, lin = graficos.legendas(pal, cam["legenda"]["tipo"], cam["legenda"]["fonte"], e["cor_destaque"],
                                 delta_tam=aprendizado.ajustes().get("legenda_tam_delta", 0))
    ab = cam["abertura"]
    if ab["tipo"] not in ("texto_atras", "nenhuma"):
        e2, l2 = graficos.abertura(ab["tipo"], ab["texto"], ab["ini"], ab["fim"], e["fonte_titulo"], e["fonte_texto"],
                                   e["cor_destaque"], extra=ab)
        est, lin = est + e2, lin + l2
        # legenda só começa depois da abertura em aberturas grandes (evita disputa visual)
        if ab["tipo"] in ("cinetica", "cinetica_mono", "manchete"):
            lin = [x for x in lin if not x.startswith("Dialogue: 0,") or _ini_ass(x) >= ab["fim"] - 0.05]
    if cam.get("lower_third") and not overlay:
        lt = cam["lower_third"]
        e3, l3 = graficos.lower_third(lt["nome"], lt["cargo"], lt["ini"], lt["fim"], e["fonte_texto"], e["cor_destaque"])
        est, lin = est + e3, lin + l3
    graficos.escrever_ass(pasta / "frente.ass", est, lin)
    partes.append(f"[{atual}]subtitles=frente.ass:fontsdir=fontes[txt]")
    atual = "txt"
    if overlay:
        entradas += ["-i", str(overlay)]
        partes.append(f"[{k}:v]format=yuva420p[mg];[{atual}][mg]overlay=0:0:format=auto:eof_action=pass[mgo]")
        atual, k = "mgo", k + 1

    # ---------- 8. trilha de luz (light leak / flash) em modo Tela
    luz = [t for t in cam["transicoes"] if t["tipo"] in ("light_leak", "flash")]
    if luz:
        trilha = graficos.trilha_luz(luz, dur, a_dir / "trilha_luz.mp4",
                                     intensidade=aprendizado.ajustes().get("transicao_intensidade", 1.0))
        entradas += ["-i", str(trilha)]
        partes.append(f"[{atual}]format=gbrp[l0];[{k}:v]format=gbrp,scale={W}:{H}[l1];"
                      f"[l0][l1]blend=all_mode=screen,format=yuv420p[luz]")
        atual, k = "luz", k + 1

    # ---------- 9. grão + barras
    fim_v = []
    if cor["grao"] > 0:
        fim_v.append(f"noise=alls={max(1, round(cor['grao'] * 100))}:allf=t")
    if cor["barras"]:
        fim_v.append("drawbox=x=0:y=0:w=iw:h='ih*0.06*min(1,t/0.9)':color=black:t=fill")
        fim_v.append("drawbox=x=0:y='ih-ih*0.06*min(1,t/0.9)':w=iw:h='ih*0.06*min(1,t/0.9)':color=black:t=fill")
    fim_v.append("format=yuv420p")
    partes.append(f"[{atual}]" + ",".join(fim_v) + "[vout]")

    # ---------- 10. áudio: voz + SFX + música com ducking
    tem_a = _tem_audio(base)
    partes.append("[0:a]aformat=sample_rates=48000:channel_layouts=stereo,highpass=f=70,"
                  "acompressor=threshold=0.12:ratio=2.5:attack=8:release=120[voz]" if tem_a else
                  f"anullsrc=r=48000:cl=stereo,atrim=0:{dur:.3f}[voz]")
    mix = ["[vozm]"]
    musica = cam.get("musica")
    partes.append("[voz]asplit=2[vozm][vozsc]" if musica else "[voz]anull[vozm]")
    for n, s in enumerate(cam["sfx"]):
        arq = assets.sfx(s["som"], a_dir / "sfx", sfx_dir)
        entradas += ["-i", str(arq)]
        ms = int(max(s["t"], 0) * 1000)
        partes.append(f"[{k}:a]aformat=sample_rates=48000:channel_layouts=stereo,volume={s.get('vol', 0.4)},"
                      f"adelay={ms}|{ms}[s{n}]")
        mix.append(f"[s{n}]")
        k += 1
    if musica:
        entradas += ["-stream_loop", "-1", "-i", musica["arquivo"]]
        vol = audio.expressao_volume(musica["automacao_db"]) if musica.get("automacao_db") else str(musica.get("volume", 0.12))
        # automação de volume (como keyframes manuais) + passa-baixa leve para abrir espaço à voz
        partes.append(f"[{k}:a]aformat=sample_rates=48000:channel_layouts=stereo,atrim=0:{dur:.3f},"
                      f"volume=volume='{vol}':eval=frame,lowpass=f=9000[mus0]")
        # ducking residual suave, só como rede de segurança
        partes.append("[mus0][vozsc]sidechaincompress=threshold=0.05:ratio=3:attack=30:release=400[mus]")
        mix.append("[mus]")
        k += 1
    partes.append("".join(mix) + f"amix=inputs={len(mix)}:duration=first:normalize=0,"
                  "loudnorm=I=-14:TP=-1.5:LRA=11,aresample=48000[aout]")

    from .render import _executar
    _executar([entradas, ["-map", "[vout]", "-map", "[aout]", "-c:v", "libx264", "-crf", "18", "-preset", "medium",
                          "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", "-t", f"{dur:.3f}", "final.mp4"]],
              pasta, ";\n".join(partes))
    return pasta / "final.mp4"


def _ini_ass(linha):
    h, m, s = linha.split(",")[1].split(":")
    return int(h) * 3600 + int(m) * 60 + float(s)


def produzir(plano, base, pasta, estilo="estudio", **kw):
    if estilo == "auto":
        from . import visao
        diag = visao.analisar(base, Path(pasta) / "visao.json")["diagnostico"]
        estilo = visao.estilo_sugerido(diag, plano["preset"])
        kw["diagnostico"] = diag
    sfx_dir = kw.pop("sfx_dir", None)
    prod = dirigir(plano, estilo, **kw)
    salvar(prod, Path(pasta) / "producao.json")
    return prod, renderizar(prod, base, pasta, sfx_dir=sfx_dir)


def salvar(prod, caminho):
    Path(caminho).write_text(json.dumps(prod, ensure_ascii=False, indent=1), encoding="utf-8")
