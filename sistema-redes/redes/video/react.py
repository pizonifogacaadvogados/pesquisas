"""React profissional (estudos/10): monta o vídeo a partir de um ROTEIRO de passos.

Entradas: o vídeo ORIGINAL (de terceiro, em alta) e a REAÇÃO (sua gravação comentando).
O roteiro (react.json) é escrito pelo Claude a partir das transcrições dos dois vídeos:

{
  "layout": "dividida" | "pip" | "greenscreen" | "tela_cheia",
  "credito": "@perfil · 08/10/2026 · TikTok",
  "passos": [
    {"tipo": "original", "ini": 3.2, "fim": 6.0,
       "congelar": {"x": 0.55, "y": 0.35, "escala": 1.6, "destaque": "circulo"}},   # opcional
    {"tipo": "comentario", "ini": 0.0, "fim": 7.5, "carimbo": "FALSO"},              # trecho da reação
    {"tipo": "replay", "ini": 4.0, "fim": 5.5, "velocidade": 0.6, "rotulo": "DE NOVO"},
    {"tipo": "comentario", "ini": 7.5, "fim": 15.0}
  ]
}

Regras de segurança aplicadas (art. 46, III LDA; Hosseinzadeh v. Klein): trechos do original
curtos, comentário domina o tempo, crédito sempre visível no original. O módulo calcula a
proporção comentário/original e alerta se o comentário ficar abaixo de 50% do tempo.
"""
import json
import subprocess
from pathlib import Path

from . import assets, graficos, recorte

W, H, FPS = 1080, 1920, 30
ENC = ["-c:v", "libx264", "-crf", "18", "-preset", "medium", "-pix_fmt", "yuv420p", "-r", str(FPS),
       "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2"]


def _ff(args, cwd):
    r = subprocess.run(["ffmpeg", "-y", "-v", "error"] + args, cwd=cwd, capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError("ffmpeg (react) falhou:\n" + r.stderr[-2000:])


def _ass_credito(caminho, texto, dur, extra=None):
    est = [graficos.estilo("Cred", "Inter", 34, cor="&H00FFFFFF", fundo="&H80000000", borda=3, esp_contorno=10,
                           alinh=7, ml=40, mv=0)]
    lin = [graficos.dialogo(0, dur, "Cred", f"{{\\pos(40,140)}}{graficos.esc(texto)}", 2)] if texto else []
    if extra:
        est += extra[0]
        lin += extra[1]
    graficos.escrever_ass(caminho, est, lin)


def _preencher(entrada, saida):
    """Filtro: original 'contido' no quadro vertical, com fundo desfocado dele mesmo."""
    return (f"[{entrada}]split[o1][o2];[o1]scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},"
            f"boxblur=28:2,eq=brightness=-0.12[f];[o2]scale={W}:-2[c];[f][c]overlay=0:(H-h)/2*0.85[{saida}]")


def renderizar(original, reacao, roteiro, pasta):
    pasta = Path(pasta).resolve()
    pasta.mkdir(parents=True, exist_ok=True)
    shutil_fontes(pasta)
    lay = roteiro.get("layout", "dividida")
    cred = roteiro.get("credito", "")
    clipes, t_orig, t_com = [], 0.0, 0.0
    matte = recorte.matte_auto(reacao, pasta / "assets" / "matte_reacao.mp4")[0] if lay == "greenscreen" else None
    ultimo_quadro = None
    for n, p in enumerate(roteiro["passos"]):
        out = pasta / f"passo_{n:02d}.mp4"
        d = p["fim"] - p["ini"]
        if p["tipo"] in ("original", "replay"):
            vel = p.get("velocidade", 1.0) if p["tipo"] == "replay" else 1.0
            extra = None
            if p["tipo"] == "replay":
                extra = ([graficos.estilo("Rot", "Bebas Neue", 110, cor="&H0000E6FF", borda=1, esp_contorno=6, alinh=8, mv=330)],
                         [graficos.dialogo(0, d / vel, "Rot", f"{{\\fad(80,120)}}{graficos.esc(p.get('rotulo', 'DE NOVO'))}", 3)])
            _ass_credito(pasta / f"cred_{n}.ass", cred, d / vel + 2, extra)
            z = f"1+0.08*clip(t/{d / vel:.3f},0,1)" if p["tipo"] == "replay" else "1"
            vf = (_preencher("0:v", "pr") + f";[pr]scale=w='2*trunc({W}*({z})/2)':h='2*trunc({H}*({z})/2)':eval=frame,"
                  f"crop={W}:{H},setpts=PTS/{vel},subtitles=cred_{n}.ass:fontsdir=fontes,fps={FPS}[v]")
            af = f"[0:a]atempo={vel},aformat=channel_layouts=stereo:sample_rates=48000[a]" if vel != 1 else \
                "[0:a]aformat=channel_layouts=stereo:sample_rates=48000[a]"
            _ff(["-ss", f"{p['ini']:.3f}", "-t", f"{d:.3f}", "-i", str(original), "-filter_complex", vf + ";" + af,
                 "-map", "[v]", "-map", "[a]"] + ENC + [out.name], pasta)
            clipes.append(out)
            t_orig += d / vel
            ultimo_quadro = (p["fim"] - 0.05)
            if p.get("congelar"):
                clipes.append(_congelar(original, ultimo_quadro, p["congelar"], cred, pasta, n))
                t_orig += 1.4
        elif p["tipo"] == "comentario":
            clipes.append(_comentario(original, reacao, p, lay, ultimo_quadro, cred, pasta, n, matte))
            t_com += d
    lista = pasta / "lista.txt"
    lista.write_text("".join(f"file '{c.name}'\n" for c in clipes), encoding="utf-8")
    _ff(["-f", "concat", "-safe", "0", "-i", lista.name, "-af", "loudnorm=I=-14:TP=-1.5:LRA=11",
         "-movflags", "+faststart"] + ENC + ["react_final.mp4"], pasta)
    proporcao = t_com / max(t_com + t_orig, 0.01)
    relatorio = {"tempo_comentario": round(t_com, 2), "tempo_original": round(t_orig, 2),
                 "proporcao_comentario": round(proporcao, 2),
                 "alertas": (["Comentário abaixo de 50% do tempo: aumente a análise ou encurte os trechos do original "
                              "(art. 46, III LDA; originalidade Instagram/TikTok)."] if proporcao < 0.5 else [])
                 + ([] if cred else ["Sem crédito do original: indique autor e origem (art. 46, III LDA)."])}
    (pasta / "react_relatorio.json").write_text(json.dumps(relatorio, ensure_ascii=False, indent=1), encoding="utf-8")
    return pasta / "react_final.mp4", relatorio


def shutil_fontes(pasta):
    import shutil
    if not (pasta / "fontes").exists():
        shutil.copytree(graficos.FONTES_DIR, pasta / "fontes")


def _congelar(original, t, c, cred, pasta, n, dur=1.4):
    """Congela o quadro, dá zoom com easing até o ponto e desenha o destaque (círculo)."""
    out = pasta / f"passo_{n:02d}_cong.mp4"
    x, y, esc = c.get("x", 0.5), c.get("y", 0.4), c.get("escala", 1.5)
    p = "clip(t/0.45,0,1)"
    z = f"(1+{esc - 1:.3f}*(1-pow(1-{p},3)))"
    cx, cy = x * W, y * H
    # círculo desenhado em ASS (vetor), entra depois do zoom
    r = 130
    circ = (f"m {-r} 0 b {-r} {-r * 0.55:.0f} {-r * 0.55:.0f} {-r} 0 {-r} b {r * 0.55:.0f} {-r} {r} {-r * 0.55:.0f} {r} 0 "
            f"b {r} {r * 0.55:.0f} {r * 0.55:.0f} {r} 0 {r} b {-r * 0.55:.0f} {r} {-r} {r * 0.55:.0f} {-r} 0")
    est = [graficos.estilo("Circ", "Inter", 20, cor="&HFF000000", contorno="&H0000D5FF", borda=1, esp_contorno=9, alinh=7)]
    lin = [graficos.dialogo(0.5, dur, "Circ", f"{{\\pos({cx:.0f},{cy:.0f})\\p1\\1a&HFF&\\3a&HFF&\\fscx40\\fscy40"
                                              f"\\t(0,160,\\fscx100\\fscy100\\3a&H00&)}}{circ}{{\\p0}}", 3)]
    _ass_credito(pasta / f"cong_{n}.ass", cred, dur, (est, lin))
    vf = (f"[0:v]trim=end_frame=1,loop=loop={int(dur * FPS)}:size=1:start=0,setpts=N/{FPS}/TB[q];"
          + _preencher("q", "pr") +
          f";[pr]scale=w='2*trunc({W}*{z}/2)':h='2*trunc({H}*{z}/2)':eval=frame,"
          f"crop={W}:{H}:x='(iw-{W})*{x:.3f}':y='(ih-{H})*{y:.3f}',subtitles=cong_{n}.ass:fontsdir=fontes,fps={FPS}[v]")
    som = assets.sfx("tape_stop", pasta / "assets" / "sfx")
    _ff(["-ss", f"{t:.3f}", "-i", str(original), "-i", str(som), "-filter_complex",
         vf + f";[1:a]aformat=channel_layouts=stereo:sample_rates=48000,volume=0.45,apad,atrim=0:{dur}[a]",
         "-map", "[v]", "-map", "[a]", "-t", f"{dur}"] + ENC + [out.name], pasta)
    return out


def _comentario(original, reacao, p, lay, t_quadro, cred, pasta, n, matte):
    out = pasta / f"passo_{n:02d}.mp4"
    d = p["fim"] - p["ini"]
    t_q = t_quadro if t_quadro is not None else 0.0
    entradas = ["-ss", f"{t_q:.3f}", "-i", str(original), "-ss", f"{p['ini']:.3f}", "-t", f"{d:.3f}", "-i", str(reacao)]
    fundo_parado = (f"[0:v]trim=end_frame=1,loop=loop={int(d * FPS) + 2}:size=1:start=0,setpts=N/{FPS}/TB")
    extra_est, extra_lin = [], []
    if p.get("carimbo"):
        cores = {"FALSO": (230, 40, 40), "VERDADE": (40, 190, 90), "FORA DE CONTEXTO": (240, 150, 20),
                 "ENGANOSO": (240, 150, 20)}
        png = graficos.carimbo(p["carimbo"], pasta / "assets" / f"carimbo_{n}.png",
                               cores.get(p["carimbo"].upper(), (230, 40, 40)))
        entradas += ["-loop", "1", "-t", f"{d:.3f}", "-i", str(png)]
    if lay == "dividida":
        vf = (fundo_parado + f",scale={W}:{H // 2}:force_original_aspect_ratio=increase,crop={W}:{H // 2}[top];"
              f"[1:v]scale={W}:{H // 2}:force_original_aspect_ratio=increase,crop={W}:{H // 2}[bot];"
              f"[top][bot]vstack,drawbox=x=0:y={H // 2 - 3}:w={W}:h=6:color=white@0.9:t=fill[base]")
    elif lay == "pip":
        vf = (fundo_parado + "[fz];" + _preencher("fz", "fb") +
              f";[1:v]scale=440:440:force_original_aspect_ratio=increase,crop=440:440,format=rgba,"
              f"geq=lum='p(X,Y)':cb='p(X,Y)':cr='p(X,Y)':a='if(lte(hypot(X-220,Y-220),214),255,0)'[cam];"
              f"[fb][cam]overlay=60:{H - 440 - 420}[base]")
    elif lay == "greenscreen":
        entradas += ["-ss", f"{p['ini']:.3f}", "-t", f"{d:.3f}", "-i", str(matte)]
        k_m = 3 if p.get("carimbo") else 2
        vf = (fundo_parado + "[fz];" + _preencher("fz", "fb0") + ";[fb0]eq=brightness=-0.08,boxblur=3[fb];"
              f"[1:v]scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},format=yuva420p[pz];"
              f"[{k_m}:v]scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},format=gray,erosion,erosion[mz];"
              f"[pz][mz]alphamerge[pa];[pa]scale=iw*0.86:-2[ps];[fb][ps]overlay=(W-w)/2:H-h[base]")
    else:  # tela_cheia: só a reação
        vf = f"[1:v]scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H}[base]"
    atual = "base"
    if p.get("carimbo"):
        vf += (f";[2:v]scale=w='2*trunc(620*min(1,0.6+t/0.15*0.4)/2)':h=-2:eval=frame[cb];"
               f"[{atual}][cb]overlay=x=(W-w)/2:y={H * 0.16:.0f}:enable='lt(t,2.2)'[cbo]")
        atual = "cbo"
    _ass_credito(pasta / f"com_{n}.ass", cred if lay in ("dividida", "pip", "greenscreen") else "", d,
                 (extra_est, extra_lin))
    vf += f";[{atual}]subtitles=com_{n}.ass:fontsdir=fontes,fps={FPS}[v]"
    sons = "[1:a]aformat=channel_layouts=stereo:sample_rates=48000[a]"
    if p.get("carimbo"):
        som = assets.sfx("buzzer" if p["carimbo"].upper() != "VERDADE" else "ding", pasta / "assets" / "sfx")
        entradas += ["-i", str(som)]
        k_s = len([x for x in entradas if x == "-i"]) - 1
        sons = (f"[1:a]aformat=channel_layouts=stereo:sample_rates=48000[r];[{k_s}:a]aformat=channel_layouts=stereo:"
                f"sample_rates=48000,volume=0.35[s];[r][s]amix=inputs=2:duration=first:normalize=0[a]")
    _ff(entradas + ["-filter_complex", vf + ";" + sons, "-map", "[v]", "-map", "[a]", "-t", f"{d:.3f}"] + ENC + [out.name],
        pasta)
    return out
