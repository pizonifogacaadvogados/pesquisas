"""Exporta um vídeo final para cada rede (registro R12; `nucleo/plataformas.py`).

Entrada: o master vertical 9:16 (final.mp4 da produção) e, opcionalmente, um master horizontal 16:9.
Para cada destino de vídeo:
  - 9:16 (Reels, TikTok, Shorts, Kwai, Stories, Status, Threads, Pinterest): reencoda no padrão de entrega
    (H.264 High, 30 fps, 10-16 Mbps, AAC 48 kHz 192 kbps, −14 LUFS / −1 dBTP, faststart), corta no máximo da rede.
  - 4:5 (LinkedIn, Facebook feed): recorte central y 285-1635 do 9:16 — o mesmo bloco que a grade 3:4 mostra,
    onde o motor já mantém rosto e legenda.
  - 16:9 (YouTube longo, X): usa o master horizontal se houver; senão, o vertical sobre o próprio vídeo
    desfocado (pillarbox de fundo desfocado, padrão de TV para material vertical).
  - WhatsApp Status: divide em trechos de até 60 s.
Saída: `<pasta>/<destino>.mp4` + `exportacao.json` (arquivos e alertas por destino).
"""
import json
import math
import shutil
import subprocess
from pathlib import Path

from ..nucleo import plataformas


def _dur(arq):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(arq)],
                         capture_output=True, text=True).stdout.strip()
    return float(out or 0)


def _tem_audio(arq):
    return bool(subprocess.run(["ffprobe", "-v", "error", "-select_streams", "a", "-show_entries", "stream=index",
                                "-of", "csv=p=0", str(arq)], capture_output=True, text=True).stdout.strip())


def _filtro_video(d, horizontal):
    w, h = d["w"], d["h"]
    if w == 1080 and h == 1920:
        return "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920"
    if (w, h) == (1080, 1350):
        return "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,crop=1080:1350:0:285"
    if w > h and horizontal:
        return f"scale={w}:{h}:force_original_aspect_ratio=increase,crop={w}:{h}"
    # vertical sobre fundo desfocado
    return (f"split[a][b];[a]scale={w}:{h}:force_original_aspect_ratio=increase,crop={w}:{h},gblur=sigma=40,"
            f"eq=brightness=-0.08:saturation=0.9[fundo];[b]scale=-2:{h}[frente];[fundo][frente]overlay=(W-w)/2:0")


def _bitrate(d, dur):
    """Bitrate (alvo, teto) em Mbps: padrão de entrega, reduzido para caber no limite de arquivo da rede."""
    alvo, teto = d.get("bitrate", plataformas.EXPORT["bitrate"])
    if d.get("max_mb") and dur > 0:
        cabe = d["max_mb"] * 8 * 0.9 / dur - plataformas.EXPORT["audio_kbps"] / 1000
        alvo, teto = min(alvo, cabe), min(teto, cabe * 1.15)
    if alvo < 2:
        raise RuntimeError(f"vídeo longo demais para o limite de {d['max_mb']} MB da rede")
    return round(alvo, 2), round(teto, 2)


def _assinatura(nome, dur_total, master_16x9):
    """Destinos com a mesma assinatura recebem o MESMO arquivo (um encode, várias cópias)."""
    d = plataformas.destino(nome)
    dur = min(dur_total, d["dur"][1])
    return (d["w"], d["h"], round(dur, 2), _bitrate(d, dur), bool(d["w"] > d["h"] and master_16x9))


def exportar_um(master, nome, saida, master_16x9=None, ini=0.0, dur=None):
    d = plataformas.destino(nome)
    if d["tipo"] != plataformas.V:
        raise ValueError(f"{nome} não é destino de vídeo")
    horizontal = d["w"] > d["h"] and master_16x9
    fonte = master_16x9 if horizontal else master
    e = plataformas.EXPORT
    total = _dur(fonte)
    dur = min(dur or total, d["dur"][1], total - ini)
    br = _bitrate(d, dur)
    vf = f"{_filtro_video(d, horizontal)},fps={e['fps']},format=yuv420p,setsar=1"
    cmd = ["ffmpeg", "-y", "-v", "error", "-ss", f"{ini:.3f}", "-t", f"{dur:.3f}", "-i", str(fonte),
           "-filter_complex", f"[0:v]{vf}[v]", "-map", "[v]"]
    if _tem_audio(fonte):
        cmd += ["-map", "0:a:0", "-af", f"loudnorm=I={e['lufs']}:TP={e['true_peak']}:LRA=11,aresample={e['audio_hz']}",
                "-c:a", "aac", "-b:a", f"{e['audio_kbps']}k", "-ar", str(e["audio_hz"]), "-ac", "2"]
    cmd += ["-c:v", "libx264", "-profile:v", "high", "-preset", "medium", "-b:v", f"{br[0]}M",
            "-maxrate", f"{br[1]}M", "-bufsize", f"{br[1]}M", "-g", str(e["fps"] // 2), "-keyint_min", str(e["fps"] // 2),
            "-sc_threshold", "0", "-color_primaries", "bt709", "-color_trc", "bt709", "-colorspace", "bt709",
            "-movflags", "+faststart", str(saida)]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(f"exportação {nome} falhou:\n{r.stderr[-1500:]}")
    return Path(saida)


def exportar(master, pasta, destinos=None, master_16x9=None):
    """Exporta para cada destino; devolve o relatório (também salvo em `exportacao.json`)."""
    pasta = Path(pasta)
    pasta.mkdir(parents=True, exist_ok=True)
    destinos = destinos or ["instagram_reels", "tiktok_video", "youtube_shorts"]
    total = _dur(master)
    rel = {"master": str(master), "duracao": round(total, 2), "destinos": {}}
    feitos = {}
    for nome in destinos:
        d = plataformas.destino(nome)
        if d["tipo"] != plataformas.V:
            continue
        alertas = []
        if total > d["dur"][1] and nome != "whatsapp_status":
            alertas.append(f"vídeo de {total:.0f} s cortado no máximo da rede ({d['dur'][1]} s): revise o final")
        if nome == "whatsapp_status" and total > d["dur"][1]:
            n = math.ceil(total / d["dur"][1])
            arqs = [exportar_um(master, nome, pasta / f"{nome}_{i + 1}de{n}.mp4", ini=i * d["dur"][1], dur=d["dur"][1])
                    for i in range(n)]
            alertas.append(f"dividido em {n} trechos de até {d['dur'][1]} s")
        else:
            assin = _assinatura(nome, total, master_16x9)
            destino_arq = pasta / f"{nome}.mp4"
            if assin in feitos:
                shutil.copyfile(feitos[assin], destino_arq)
            else:
                exportar_um(master, nome, destino_arq, master_16x9=master_16x9)
                feitos[assin] = destino_arq
            arqs = [destino_arq]
        if d["w"] > d["h"] and not master_16x9:
            alertas.append("16:9 montado a partir do vertical (fundo desfocado); para YouTube longo, grave/edite em 16:9")
        for a in arqs:
            alertas += plataformas.validar_arquivo(a, nome)
        rel["destinos"][nome] = {"arquivos": [a.name for a in arqs], "alertas": alertas}
    (pasta / "exportacao.json").write_text(json.dumps(rel, ensure_ascii=False, indent=1), encoding="utf-8")
    return rel
