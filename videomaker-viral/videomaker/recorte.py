"""Recorte da pessoa (matte) para estúdio virtual, fundo desfocado e texto atrás da pessoa.

Dois caminhos:
  - IA (sem fundo verde): rembg (modelo u2net_human_seg), quadro a quadro, com suavização
    temporal para não "tremer" a borda. Equivale ao "Remover fundo → Automático" do CapCut.
  - Chroma key (fundo verde/azul): filtros chromakey + despill do ffmpeg.

Saída: vídeo em tons de cinza (branco = pessoa) com a mesma duração e fps do vídeo de entrada.
"""
import subprocess
from pathlib import Path

import numpy as np


def _sonda(video):
    out = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
                          "stream=width,height,r_frame_rate", "-of", "csv=p=0", str(video)],
                         capture_output=True, text=True, check=True).stdout.strip().split(",")
    num, _, den = out[2].partition("/")
    return int(out[0]), int(out[1]), float(num) / float(den or 1)


def matte_ia(video, destino, lado=384, suavizar=0.45, modelo="u2net_human_seg"):
    """Gera o matte por IA. `lado` = resolução de inferência (maior = borda melhor e mais lento)."""
    try:
        from rembg import new_session, remove
        from PIL import Image
    except ImportError as e:
        raise RuntimeError("Recorte por IA requer: pip install rembg onnxruntime pillow") from e
    destino = Path(destino)
    if destino.exists():
        return destino
    destino.parent.mkdir(parents=True, exist_ok=True)
    w, h, fps = _sonda(video)
    ew, eh = (lado, int(lado * h / w) // 2 * 2) if w <= h else (int(lado * w / h) // 2 * 2, lado)
    sessao = new_session(modelo)
    leitor = subprocess.Popen(["ffmpeg", "-v", "error", "-i", str(video), "-vf", f"scale={ew}:{eh}",
                               "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
    escritor = subprocess.Popen(["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "gray",
                                 "-s", f"{ew}x{eh}", "-r", f"{fps}", "-i", "-",
                                 "-vf", f"scale={w}:{h}:flags=bicubic,gblur=sigma=1.2",
                                 "-c:v", "libx264", "-crf", "12", "-pix_fmt", "yuv420p", str(destino)],
                                stdin=subprocess.PIPE)
    anterior = None
    tam = ew * eh * 3
    try:
        while True:
            buf = leitor.stdout.read(tam)
            if len(buf) < tam:
                break
            quadro = Image.fromarray(np.frombuffer(buf, np.uint8).reshape(eh, ew, 3))
            m = np.asarray(remove(quadro, session=sessao, only_mask=True, post_process_mask=False),
                           dtype=np.float32) / 255.0
            # curva de contraste no matte: borda mais definida, sem halo
            m = np.clip((m - 0.12) / 0.76, 0, 1)
            if anterior is not None:
                # suavização assimétrica: onde a pessoa SAIU (máscara caiu), segue rápido (sem rastro);
                # onde ficou/entrou, suaviza para a borda não tremer
                m = np.where(m < anterior, 0.15 * anterior + 0.85 * m, suavizar * anterior + (1 - suavizar) * m)
            anterior = m
            escritor.stdin.write((m * 255).astype(np.uint8).tobytes())
    finally:
        leitor.stdout.close()
        leitor.wait()
        escritor.stdin.close()
        escritor.wait()
    if escritor.returncode != 0:
        raise RuntimeError("falha ao gravar o matte")
    return destino


def matte_chroma(video, destino, cor="0x00FF00", similaridade=0.14, mistura=0.08):
    """Matte a partir de fundo verde (ou outra cor sólida)."""
    destino = Path(destino)
    destino.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", str(video), "-vf",
                    f"format=yuva444p,chromakey={cor}:{similaridade}:{mistura},alphaextract,gblur=sigma=0.8",
                    "-c:v", "libx264", "-crf", "12", "-pix_fmt", "yuv420p", str(destino)], check=True)
    return destino
