"""Limpeza e tratamento de voz (R17: testado em CPU neste servidor).

Cadeia (a mesma de um engenheiro de áudio de podcast, medida no R17):
  1. redução de ruído
       deepfilter  DeepFilterNet 3 (binário da release v0.5.6 do GitHub, MIT/Apache-2.0): ruído nas pausas
                   −44,6 → −66,4 dBFS sem distorcer a fala (SI-SDR 23,2); ~0,36 × o tempo real em CPU
       rnnoise     reserva: ffmpeg `arnndn` com o modelo std.rnnn (richardpl/arnndn-models): 20× mais rápido,
                   mas distorce mais a fala (SI-SDR 18,8) — por isso só quando o DeepFilterNet não existe
       (afftdn foi descartado: só −2 dB e atraso de 25 ms)
  2. voz de transmissão: passa-alta 80 Hz · −2 dB em 250 Hz (tira o "embolado") · +2,5 dB em 3,2 kHz (presença) ·
     de-esser (`i=0.5`: com o padrão i=0 o filtro não faz nada) · compressor 3:1 suave
  Aplique na VOZ BRUTA (a produção já faz isso no base.mp4). Em vídeo já mixado com música, o compressor levanta a
  música nas pausas (teste: −77 → −58 dBFS) — por isso, se o piso já está abaixo de −60 dBFS, o modo auto não limpa.
  3. o volume final (−14 LUFS, pico ≤ −1,5 dBTP) é feito na mixagem da produção / exportação.
Os binários e modelos são baixados uma vez para `modelos/` (fora do git). Nada sai do computador: o processamento é local.
Desligar: `REDES_SEM_LIMPEZA_VOZ=1` ou `prod["voz"] = {"limpar": false}`.
"""
import os
import shutil
import stat
import subprocess
import tempfile
import urllib.request
from pathlib import Path

import numpy as np

from ..nucleo import caminhos

DF_URL = ("https://github.com/Rikorose/DeepFilterNet/releases/download/v0.5.6/"
          "deep-filter-0.5.6-x86_64-unknown-linux-musl")
RNN_URL = "https://raw.githubusercontent.com/richardpl/arnndn-models/master/std.rnnn"
DF_BIN = caminhos.MODELOS / "bin" / "deep-filter"
RNN_MODELO = caminhos.MODELOS / "rnnoise" / "std.rnnn"

CADEIA = ("highpass=f=80:p=2,equalizer=f=250:t=q:w=1.2:g=-2,equalizer=f=3200:t=q:w=1.0:g=2.5,"
          "deesser=i=0.5:m=0.5:f=0.5,acompressor=threshold=-21dB:ratio=3:attack=8:release=120:makeup=3dB:knee=4")


def _baixar(url, destino, minimo):
    destino.parent.mkdir(parents=True, exist_ok=True)
    tmp = destino.with_suffix(".parcial")
    try:
        urllib.request.urlretrieve(url, tmp)
        if tmp.stat().st_size < minimo:          # o proxy às vezes devolve uma página de erro pequena
            raise OSError(f"download incompleto ({tmp.stat().st_size} bytes)")
        tmp.replace(destino)
        return destino
    except Exception:
        tmp.unlink(missing_ok=True)
        return None


def deepfilter(baixar=True):
    """Caminho do binário do DeepFilterNet (baixa na primeira vez) ou None."""
    achado = shutil.which("deep-filter")
    if achado:
        return Path(achado)
    if not DF_BIN.exists() and baixar:
        if _baixar(DF_URL, DF_BIN, 1_000_000):
            DF_BIN.chmod(DF_BIN.stat().st_mode | stat.S_IEXEC)
    return DF_BIN if DF_BIN.exists() else None


def rnnoise(baixar=True):
    if not RNN_MODELO.exists() and baixar:
        _baixar(RNN_URL, RNN_MODELO, 100_000)
    return RNN_MODELO if RNN_MODELO.exists() else None


def _wav_mono48(entrada, saida):
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(entrada), "-vn", "-ac", "1", "-ar", "48000",
                    "-c:a", "pcm_s16le", str(saida)], check=True)
    return saida


def piso_ruido(wav, janela=0.05, pct=10):
    """Nível (dBFS) das partes mais quietas — o ruído de fundo que sobra nas pausas."""
    r = subprocess.run(["ffmpeg", "-v", "error", "-i", str(wav), "-ac", "1", "-ar", "16000", "-f", "s16le", "-"],
                       capture_output=True, check=True)
    x = np.frombuffer(r.stdout, np.int16).astype(np.float32) / 32768
    n = int(16000 * janela)
    if len(x) < n:
        return None
    w = x[: len(x) // n * n].reshape(-1, n)
    rms = np.sqrt((w ** 2).mean(axis=1)) + 1e-9
    return round(float(20 * np.log10(np.percentile(rms, pct))), 1)


def tratar(entrada, saida, motor="auto", atenuacao_db=30):
    """Áudio de `entrada` (vídeo ou áudio) → `saida` .wav mono 48 kHz limpo e tratado.
    motor: auto | deepfilter | rnnoise | nenhum. Devolve {motor, piso_antes, piso_depois, saida}."""
    saida = Path(saida)
    saida.parent.mkdir(parents=True, exist_ok=True)
    tmp = Path(tempfile.mkdtemp(prefix="voz_"))
    try:
        bruto = _wav_mono48(entrada, tmp / "v.wav")
        limpo, usado = bruto, "nenhum"
        piso0 = piso_ruido(bruto)
        if motor == "auto" and piso0 is not None and piso0 < -60:
            motor = "nenhum"          # já limpo (gravação boa ou áudio já tratado): não mexe no ruído
        if motor in ("auto", "deepfilter"):
            df = deepfilter()
            if df:
                r = subprocess.run([str(df), "-D", "-a", str(atenuacao_db), "-o", str(tmp / "df"), str(bruto)],
                                   capture_output=True)
                if r.returncode == 0 and (tmp / "df" / "v.wav").exists():
                    limpo, usado = tmp / "df" / "v.wav", "deepfilter"
        filtro = CADEIA
        if usado == "nenhum" and motor in ("auto", "rnnoise"):
            m = rnnoise()
            if m:
                filtro = f"arnndn=m='{m}':mix=0.85," + CADEIA      # mix < 1 preserva um pouco do original (menos artefato)
                usado = "rnnoise"
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(limpo), "-af", filtro, "-ar", "48000",
                        "-c:a", "pcm_s16le", str(saida)], check=True)
        return {"motor": usado, "piso_antes": piso0, "piso_depois": piso_ruido(saida), "saida": str(saida)}
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def ativo(prod=None):
    return os.environ.get("REDES_SEM_LIMPEZA_VOZ") != "1" and (prod or {}).get("voz", {}).get("limpar", True)


def limpar_video(video, saida, motor="auto"):
    """Troca o áudio de um vídeo pela voz tratada (vídeo copiado sem recodificar) e normaliza a −14 LUFS."""
    saida = Path(saida)
    wav = saida.with_suffix(".voz.wav")
    r = tratar(video, wav, motor)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(video), "-i", str(wav), "-map", "0:v:0?", "-map", "1:a:0",
                    "-c:v", "copy", "-af", "loudnorm=I=-14:TP=-1.5:LRA=11,aresample=48000", "-c:a", "aac", "-b:a", "192k",
                    "-movflags", "+faststart", "-shortest", str(saida)], check=True)
    wav.unlink(missing_ok=True)
    return {**r, "saida": str(saida)}
