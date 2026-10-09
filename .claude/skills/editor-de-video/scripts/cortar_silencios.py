#!/usr/bin/env python3
"""Remove trechos de silêncio de um vídeo usando ffmpeg silencedetect.

Uso: cortar_silencios.py ENTRADA SAIDA [--ruido -30dB] [--min 0.6] [--folga 0.15]
"""
import argparse
import re
import subprocess
import sys


def duracao(arquivo):
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", arquivo],
        capture_output=True, text=True, check=True,
    ).stdout
    return float(out.strip())


def silencios(arquivo, ruido, minimo):
    log = subprocess.run(
        ["ffmpeg", "-i", arquivo, "-af", f"silencedetect=noise={ruido}:d={minimo}", "-f", "null", "-"],
        capture_output=True, text=True,
    ).stderr
    inicios = [float(x) for x in re.findall(r"silence_start: ([\d.]+)", log)]
    fins = [float(x) for x in re.findall(r"silence_end: ([\d.]+)", log)]
    return list(zip(inicios, fins + [None] * (len(inicios) - len(fins))))


def main():
    p = argparse.ArgumentParser()
    p.add_argument("entrada")
    p.add_argument("saida")
    p.add_argument("--ruido", default="-30dB")
    p.add_argument("--min", type=float, default=0.6, help="silêncio mínimo em segundos")
    p.add_argument("--folga", type=float, default=0.15, help="segundos mantidos em volta da fala")
    a = p.parse_args()

    total = duracao(a.entrada)
    trechos, cursor = [], 0.0
    for ini, fim in silencios(a.entrada, a.ruido, a.min):
        fim = total if fim is None else fim
        corte_ini = min(ini + a.folga, total)
        if corte_ini > cursor:
            trechos.append((cursor, corte_ini))
        cursor = max(fim - a.folga, 0)
    if cursor < total:
        trechos.append((cursor, total))
    trechos = [(i, f) for i, f in trechos if f - i > 0.05]

    if not trechos:
        sys.exit("Nenhum trecho com som encontrado.")

    sel = "+".join(f"between(t,{i:.3f},{f:.3f})" for i, f in trechos)
    subprocess.run([
        "ffmpeg", "-y", "-loglevel", "error", "-i", a.entrada,
        "-vf", f"select='{sel}',setpts=N/FRAME_RATE/TB",
        "-af", f"aselect='{sel}',asetpts=N/SR/TB",
        "-c:v", "libx264", "-crf", "20", "-pix_fmt", "yuv420p", "-c:a", "aac", "-movflags", "+faststart",
        a.saida,
    ], check=True)

    mantido = sum(f - i for i, f in trechos)
    print(f"{len(trechos)} trechos mantidos: {total:.1f}s -> {mantido:.1f}s ({total - mantido:.1f}s removidos)")


if __name__ == "__main__":
    main()
