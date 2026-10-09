#!/usr/bin/env python3
"""Transcreve um vídeo/áudio para .srt e .txt (com tempos) ao lado do arquivo.

Uso: transcrever.py ENTRADA [--modelo small] [--idioma pt]
Requer: pip install faster-whisper   (ou openai-whisper como alternativa)
"""
import argparse
import sys
from pathlib import Path


def ts(seg):
    h, r = divmod(seg, 3600)
    m, s = divmod(r, 60)
    return f"{int(h):02d}:{int(m):02d}:{int(s):02d},{int((s % 1) * 1000):03d}"


def segmentos(entrada, modelo, idioma):
    try:
        from faster_whisper import WhisperModel
        segs, _ = WhisperModel(modelo, compute_type="int8").transcribe(entrada, language=idioma, vad_filter=True)
        return [(s.start, s.end, s.text.strip()) for s in segs]
    except ImportError:
        pass
    try:
        import whisper
        res = whisper.load_model(modelo).transcribe(entrada, language=idioma)
        return [(s["start"], s["end"], s["text"].strip()) for s in res["segments"]]
    except ImportError:
        sys.exit("Instale um transcritor: pip install faster-whisper")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("entrada")
    p.add_argument("--modelo", default="small")
    p.add_argument("--idioma", default="pt")
    a = p.parse_args()

    segs = segmentos(a.entrada, a.modelo, a.idioma)
    base = Path(a.entrada).with_suffix("")
    srt = "\n".join(f"{n}\n{ts(i)} --> {ts(f)}\n{t}\n" for n, (i, f, t) in enumerate(segs, 1))
    Path(f"{base}.srt").write_text(srt, encoding="utf-8")
    Path(f"{base}.txt").write_text("\n".join(f"[{ts(i)[:8]}] {t}" for i, _, t in segs), encoding="utf-8")
    print(f"{len(segs)} segmentos -> {base}.srt / {base}.txt")


if __name__ == "__main__":
    main()
