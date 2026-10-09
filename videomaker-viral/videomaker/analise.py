"""D1: análise do vídeo bruto -> analise.json

Saída:
{
  "fonte": "...", "duracao": 62.4, "largura": 1920, "altura": 1080, "fps": 30.0,
  "palavras": [{"w": "Você", "ini": 0.52, "fim": 0.71, "energia": 0.8}, ...],
  "origem_transcricao": "faster-whisper" | "whisper" | "srt" | "json"
}
"""
import json
import re
import subprocess
from pathlib import Path

import numpy as np


def sonda(video):
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration:stream=codec_type,width,height,r_frame_rate",
         "-of", "json", str(video)],
        capture_output=True, text=True, check=True,
    ).stdout
    info = json.loads(out)
    v = next((s for s in info["streams"] if s["codec_type"] == "video"), {})
    num, _, den = v.get("r_frame_rate", "30/1").partition("/")
    return {
        "duracao": float(info["format"]["duration"]),
        "largura": v.get("width"), "altura": v.get("height"),
        "fps": round(float(num) / float(den or 1), 3),
        "tem_audio": any(s["codec_type"] == "audio" for s in info["streams"]),
    }


# ------------------------------------------------------------------ transcrição
def _whisper(video, modelo, idioma):
    erros = []
    try:
        from faster_whisper import WhisperModel
        segs, _ = WhisperModel(modelo, compute_type="int8").transcribe(
            str(video), language=idioma, word_timestamps=True, vad_filter=True)
        pal = [{"w": w.word.strip(), "ini": w.start, "fim": w.end} for s in segs for w in (s.words or [])]
        return pal, "faster-whisper"
    except Exception as e:  # pacote ausente ou modelo sem download
        erros.append(f"faster-whisper: {type(e).__name__}: {e}")
    try:
        import whisper
        res = whisper.load_model(modelo).transcribe(str(video), language=idioma, word_timestamps=True)
        pal = [{"w": w["word"].strip(), "ini": w["start"], "fim": w["end"]}
               for s in res["segments"] for w in s.get("words", [])]
        return pal, "whisper"
    except Exception as e:
        erros.append(f"openai-whisper: {type(e).__name__}: {e}")
    raise RuntimeError(
        "Não foi possível transcrever:\n  " + "\n  ".join(erros)
        + "\nInstale `pip install faster-whisper` (baixa o modelo na 1ª vez) "
        "ou passe a legenda pronta com --srt (ex.: legenda exportada do CapCut).")


def _tempo_srt(s):
    h, m, rest = s.strip().replace(".", ",").split(":")
    seg, ms = rest.split(",")
    return int(h) * 3600 + int(m) * 60 + int(seg) + int(ms) / 1000


def ler_srt(caminho):
    """Lê SRT e distribui o tempo de cada bloco entre as palavras, proporcional ao tamanho."""
    texto = Path(caminho).read_text(encoding="utf-8-sig")
    palavras = []
    for bloco in re.split(r"\n\s*\n", texto.strip()):
        linhas = [l for l in bloco.splitlines() if l.strip()]
        idx = next((i for i, l in enumerate(linhas) if "-->" in l), None)
        if idx is None:
            continue
        a, b = linhas[idx].split("-->")
        ini, fim = _tempo_srt(a), _tempo_srt(b.split()[0])
        ws = " ".join(linhas[idx + 1:]).split()
        if not ws:
            continue
        pesos = [len(w) + 2 for w in ws]
        total, t = sum(pesos), ini
        for w, p in zip(ws, pesos):
            d = (fim - ini) * p / total
            palavras.append({"w": w, "ini": round(t, 3), "fim": round(t + d * 0.92, 3)})
            t += d
    return palavras


# ------------------------------------------------------------------ energia da voz
def _audio_mono(video, sr=16000):
    raw = subprocess.run(
        ["ffmpeg", "-v", "error", "-i", str(video), "-vn", "-ac", "1", "-ar", str(sr), "-f", "f32le", "-"],
        capture_output=True, check=True,
    ).stdout
    return np.frombuffer(raw, dtype=np.float32), sr


def anotar_energia(palavras, video):
    """energia = RMS da palavra normalizado (0..1) pelo percentil 95 do vídeo."""
    try:
        sinal, sr = _audio_mono(video)
    except subprocess.CalledProcessError:
        for p in palavras:
            p["energia"] = 0.5
        return
    rms = []
    for p in palavras:
        a, b = int(p["ini"] * sr), max(int(p["fim"] * sr), int(p["ini"] * sr) + 1)
        trecho = sinal[a:b]
        rms.append(float(np.sqrt(np.mean(trecho ** 2))) if trecho.size else 0.0)
    ref = np.percentile(rms, 95) if rms else 1.0
    for p, r in zip(palavras, rms):
        p["energia"] = round(min(r / ref, 1.0), 3) if ref > 0 else 0.5


def analisar(video, saida, srt=None, transcricao=None, modelo="small", idioma="pt"):
    info = sonda(video)
    if transcricao:
        dados = json.loads(Path(transcricao).read_text(encoding="utf-8"))
        palavras, origem = dados.get("palavras", dados), "json"
    elif srt:
        palavras, origem = ler_srt(srt), "srt"
    else:
        palavras, origem = _whisper(video, modelo, idioma)
    palavras = [p for p in palavras if p["w"]]
    if info["tem_audio"]:
        anotar_energia(palavras, video)
    else:
        for p in palavras:
            p["energia"] = 0.5
    res = {"fonte": str(Path(video).resolve()), **info, "palavras": palavras, "origem_transcricao": origem}
    Path(saida).write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
    return res
