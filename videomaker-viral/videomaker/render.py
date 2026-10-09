"""D4: renderiza o plano com ffmpeg.

Gera:
  base.mp4   cortes + enquadramento 9:16, sem efeitos. É o arquivo para subir no CapCut:
             os tempos do roteiro do CapCut batem com ele.
  final.mp4  versão completa: zoom (punch/snap/lento), emojis com pop, legendas
             palavra a palavra, título do gancho, SFX e áudio normalizado.
"""
import platform
import re
import shutil
import subprocess
from pathlib import Path

from . import assets, regras

W, H, FPS = 1080, 1920, 30
FONTES_PREFERIDAS = ["Montserrat ExtraBold", "Montserrat Black", "Poppins Black", "Anton", "Arial Black",
                     "Montserrat", "Poppins", "Arial", "Liberation Sans", "DejaVu Sans"]


# ------------------------------------------------------------------ utilidades
def fonte_legenda():
    if shutil.which("fc-list"):
        nomes = subprocess.run(["fc-list", ":", "family"], capture_output=True, text=True).stdout
        for f in FONTES_PREFERIDAS:
            if f.lower() in nomes.lower():
                return f
    return "Arial Black" if platform.system() in ("Windows", "Darwin") else "DejaVu Sans"


def _versao_ffmpeg():
    out = subprocess.run(["ffmpeg", "-version"], capture_output=True, text=True).stdout
    m = re.search(r"version (\d+)", out)
    return int(m.group(1)) if m else 6


def _executar(args, cwd, script):
    """Roda ffmpeg passando o filtro por arquivo (expressões longas)."""
    (Path(cwd) / "filtro.txt").write_text(script, encoding="utf-8")
    flag = ["-/filter_complex", "filtro.txt"] if _versao_ffmpeg() >= 7 else ["-filter_complex_script", "filtro.txt"]
    cmd = ["ffmpeg", "-y", "-v", "error", "-stats"] + args[0] + flag + args[1]
    r = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError("ffmpeg falhou:\n" + r.stderr[-3000:])


def _cortes_e_enquadramento(plano, tem_audio, enquadramento):
    """Filtro: corta os segmentos, concatena e reenquadra para 1080x1920 -> [vb][ab]."""
    partes, rotulos = [], []
    for n, s in enumerate(plano["segmentos"]):
        d = s["fim"] - s["ini"]
        partes.append(f"[0:v]trim=start={s['ini']:.3f}:end={s['fim']:.3f},setpts=PTS-STARTPTS[v{n}]")
        if tem_audio:
            partes.append(f"[0:a]atrim=start={s['ini']:.3f}:end={s['fim']:.3f},asetpts=PTS-STARTPTS,"
                          f"afade=t=in:d=0.02,afade=t=out:st={max(d - 0.03, 0):.3f}:d=0.03[a{n}]")
            rotulos.append(f"[v{n}][a{n}]")
        else:
            rotulos.append(f"[v{n}]")
    n = len(plano["segmentos"])
    partes.append("".join(rotulos) + f"concat=n={n}:v=1:a={1 if tem_audio else 0}[vc]" + ("[ab]" if tem_audio else ""))
    if not tem_audio:
        partes.append(f"anullsrc=r=48000:cl=stereo,atrim=0:{plano['duracao_final']:.3f}[ab]")

    li, al = plano["fonte_info"].get("largura") or W, plano["fonte_info"].get("altura") or H
    if li / al > 9 / 16 + 0.01 and enquadramento == "desfoque":
        partes.append(f"[vc]split[f0][f1];[f0]scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},"
                      f"boxblur=25:2[fundo];[f1]scale={W}:-2[frente];[fundo][frente]overlay=(W-w)/2:(H-h)/2,"
                      f"fps={FPS},setsar=1[vb]")
    elif li / al > 9 / 16 + 0.01:
        # corte vertical ancorado no centro (rosto costuma estar no centro em vídeo falado)
        partes.append(f"[vc]crop=w=ih*9/16:h=ih:x=(iw-ih*9/16)/2:y=0,scale={W}:{H},fps={FPS},setsar=1[vb]")
    else:
        partes.append(f"[vc]scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},fps={FPS},setsar=1[vb]")
    return partes


# ------------------------------------------------------------------ zoom
def _nivel_punch(plano, t):
    for e in plano["eventos"]:
        if e["tipo"] == "zoom" and e["modo"] == "punch" and e["ini"] <= t < e["fim"]:
            return e["escala"]
    return 1.0


def expressao_zoom(plano):
    termos = []
    for e in plano["eventos"]:
        if e["tipo"] != "zoom":
            continue
        a, b = e["ini"], e["fim"]
        if e["modo"] == "punch":
            termos.append(f"{e['escala'] - 1:.3f}*gte(t,{a:.3f})*lt(t,{b:.3f})")
        elif e["modo"] == "snap":
            amp = e["escala"] - _nivel_punch(plano, a)
            termos.append(f"{amp:.3f}*gte(t,{a:.3f})*lt(t,{b:.3f})*min(1,(t-{a:.3f})/0.18)*min(1,({b:.3f}-t)/0.15)")
        elif e["modo"] == "lento":
            termos.append(f"{e['escala'] - 1:.3f}*gte(t,{a:.3f})*lt(t,{b:.3f})*(t-{a:.3f})/{max(b - a, 0.1):.3f}")
    return "1+" + "+".join(termos) if termos else "1"


# ------------------------------------------------------------------ legendas (ASS)
def _t_ass(s):
    s = max(s, 0)
    return f"{int(s // 3600)}:{int(s % 3600 // 60):02d}:{s % 60:05.2f}"


def _esc(txt):
    return txt.replace("\\", "").replace("{", "(").replace("}", ")")


def gerar_ass(plano, caminho, fonte):
    cfg = regras.PRESETS[plano["preset"]]
    alta = cfg["caixa_alta"]
    tam = 104 if alta else 90
    branco = "&H00FFFFFF"
    linhas = [
        "[Script Info]", "ScriptType: v4.00+", f"PlayResX: {W}", f"PlayResY: {H}", "WrapStyle: 0",
        "ScaledBorderAndShadow: yes", "",
        "[V4+ Styles]",
        "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, "
        "Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, "
        "MarginR, MarginV, Encoding",
        f"Style: Legenda,{fonte},{tam},{branco},{branco},&H00000000,&H64000000,-1,0,0,0,100,100,0,0,1,7,3,2,90,90,600,1",
        f"Style: Titulo,{fonte},88,{branco},{branco},&H2E000000,&H00000000,-1,0,0,0,100,100,0,0,3,18,0,8,80,80,250,1",
        "", "[Events]", "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text",
    ]
    for e in plano["eventos"]:
        if e["tipo"] == "titulo":
            txt = _esc(e["texto"])
            linhas.append(f"Dialogue: 1,{_t_ass(e['ini'])},{_t_ass(e['fim'])},Titulo,,0,0,0,,"
                          f"{{\\fad(60,150)\\fscx70\\fscy70\\t(0,130,\\fscx100\\fscy100)}}{txt}")
    for bloco in plano["legendas"]:
        ps = bloco["palavras"]
        for k, atual in enumerate(ps):
            ini = bloco["ini"] if k == 0 else atual["ini"]
            fim = ps[k + 1]["ini"] if k + 1 < len(ps) else bloco["fim"]
            if fim - ini < 0.02:
                continue
            partes = []
            for m, p in enumerate(ps):
                w = _esc(p["w"].upper() if alta else p["w"])
                if m == k and k > 0:
                    partes.append(f"{{\\c{cfg['cor_atual']}&\\fscx110\\fscy110}}{w}{{\\c{branco}&\\fscx100\\fscy100}}")
                elif m == k:
                    partes.append(f"{{\\c{cfg['cor_atual']}&}}{w}{{\\c{branco}&}}")
                elif p.get("destaque"):
                    partes.append(f"{{\\c{cfg['cor_destaque']}&}}{w}{{\\c{branco}&}}")
                else:
                    partes.append(w)
            pop = "{\\fscx82\\fscy82\\t(0,90,\\fscx100\\fscy100)}" if k == 0 else ""
            linhas.append(f"Dialogue: 0,{_t_ass(ini)},{_t_ass(fim)},Legenda,,0,0,0,,{pop}{' '.join(partes)}")
    Path(caminho).write_text("\n".join(linhas) + "\n", encoding="utf-8")


# ------------------------------------------------------------------ render
def renderizar(plano, pasta, sfx_dir=None, musica=None, enquadramento="corte", base=True, final=True):
    pasta = Path(pasta).resolve()
    pasta.mkdir(parents=True, exist_ok=True)
    fonte_video = plano["fonte"]
    dur = plano["duracao_final"]
    tem_audio = _tem_audio(fonte_video)
    saidas = {}

    if base:
        partes = _cortes_e_enquadramento(plano, tem_audio, enquadramento)
        partes.append("[vb]format=yuv420p[vout]")
        _executar([["-i", fonte_video], ["-map", "[vout]", "-map", "[ab]", "-c:v", "libx264", "-crf", "18",
                                         "-preset", "medium", "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart",
                                         "-t", f"{dur:.3f}", "base.mp4"]], pasta, ";\n".join(partes))
        saidas["base"] = pasta / "base.mp4"

    if not final:
        return saidas

    entradas = ["-i", fonte_video]
    partes = _cortes_e_enquadramento(plano, tem_audio, enquadramento)
    z = expressao_zoom(plano)
    partes.append(f"[vb]scale=w='2*trunc({W}*({z})/2)':h='2*trunc({H}*({z})/2)':eval=frame,"
                  f"crop={W}:{H}:(iw-{W})/2:(ih-{H})*0.38[vz]")

    # emojis
    atual, k_in = "vz", 1
    emo_dir = pasta / "assets" / "emojis"
    for n, e in enumerate([e for e in plano["eventos"] if e["tipo"] == "emoji"]):
        png = assets.emoji_png(e["emoji"], emo_dir)
        entradas += ["-loop", "1", "-framerate", str(FPS), "-t", f"{dur:.3f}", "-i", str(png)]
        a, b = e["ini"], e["fim"]
        x = 0.20 * W if e.get("lado") == "esquerda" else 0.80 * W
        y = e.get("y", 0.24) * H
        escala = (f"if(lt(t,{a:.3f}),0.01,if(lt(t-{a:.3f},0.12),0.6+(t-{a:.3f})/0.12*0.6,"
                  f"if(lt(t-{a:.3f},0.25),1.2-(t-{a:.3f}-0.12)/0.13*0.2,1)))")
        partes.append(f"[{k_in}:v]scale=w='2*trunc(230*{escala}/2)':h=-2:eval=frame[e{n}]")
        partes.append(f"[{atual}][e{n}]overlay=x='{x:.0f}-w/2':y='{y:.0f}-h/2':enable='between(t,{a:.3f},{b:.3f})'"
                      f":eval=frame[o{n}]")
        atual, k_in = f"o{n}", k_in + 1

    # legendas + título
    gerar_ass(plano, pasta / "legendas.ass", fonte_legenda())
    partes.append(f"[{atual}]subtitles=legendas.ass,format=yuv420p[vout]")

    # áudio: voz + SFX (+ música)
    sons = [e for e in plano["eventos"] if e["tipo"] == "sfx"]
    mix = ["[ab]aformat=sample_rates=48000:channel_layouts=stereo,highpass=f=70[voz]"]
    rot = ["[voz]"]
    vol = {"whoosh": 0.45, "pop": 0.5, "hit": 0.6, "riser": 0.35, "ding": 0.35, "buzzer": 0.3}
    for n, e in enumerate(sons):
        arq = assets.sfx(e["som"], pasta / "assets" / "sfx", sfx_dir)
        entradas += ["-i", str(arq)]
        ms = int(max(e["t"], 0) * 1000)
        mix.append(f"[{k_in}:a]aformat=sample_rates=48000:channel_layouts=stereo,volume={vol.get(e['som'], 0.4)},"
                   f"adelay={ms}|{ms}[s{n}]")
        rot.append(f"[s{n}]")
        k_in += 1
    if musica:
        entradas += ["-stream_loop", "-1", "-i", str(musica)]
        mix.append(f"[{k_in}:a]aformat=sample_rates=48000:channel_layouts=stereo,volume=0.10,"
                   f"atrim=0:{dur:.3f},afade=t=out:st={max(dur - 1.5, 0):.3f}:d=1.5[mus]")
        rot.append("[mus]")
        k_in += 1
    mix.append("".join(rot) + f"amix=inputs={len(rot)}:duration=first:normalize=0,"
               "loudnorm=I=-14:TP=-1.5:LRA=11,aresample=48000[aout]")
    partes += mix

    _executar([entradas, ["-map", "[vout]", "-map", "[aout]", "-c:v", "libx264", "-crf", "20", "-preset", "medium",
                          "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", "-t", f"{dur:.3f}", "final.mp4"]],
              pasta, ";\n".join(partes))
    saidas["final"] = pasta / "final.mp4"
    return saidas


def _tem_audio(video):
    out = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "a", "-show_entries", "stream=index",
                          "-of", "csv=p=0", str(video)], capture_output=True, text=True).stdout
    return bool(out.strip())
