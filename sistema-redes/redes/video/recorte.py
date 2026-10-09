"""Recorte da pessoa (matte) para estúdio virtual, fundo desfocado e texto atrás da pessoa.

Três caminhos (o padrão é `matte_auto`):
  - IA de VÍDEO (padrão): Robust Video Matting (RVM, Lin et al., WACV 2022, licença GPL-3.0),
    modelo recorrente: lembra os quadros anteriores, então a borda e o cabelo não "tremem" e não
    há rastro. É a classe de modelo dos profissionais (MatAnyone, GVM e SAM2 são a geração seguinte,
    hospedados no Hugging Face, que é bloqueado neste servidor). Baixado do GitHub na 1ª vez.
  - IA de FOTO (reserva): rembg (u2net_human_seg), quadro a quadro, com suavização temporal.
    Foi a causa do "recorte visonho" da versão 2: cada quadro é recortado sem saber do anterior.
  - Chroma key (fundo verde/azul): filtros chromakey + despill do ffmpeg.

Saída: vídeo em tons de cinza (branco = pessoa) com a mesma duração e fps do vídeo de entrada.
"""
import subprocess
from pathlib import Path

import numpy as np
from ..nucleo import caminhos


def _sonda(video):
    out = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
                          "stream=width,height,r_frame_rate", "-of", "csv=p=0", str(video)],
                         capture_output=True, text=True, check=True).stdout.strip().split(",")
    num, _, den = out[2].partition("/")
    return int(out[0]), int(out[1]), float(num) / float(den or 1)


RVM_URL = "https://github.com/PeterL1n/RobustVideoMatting/releases/download/v1.0.0/rvm_mobilenetv3_fp32.onnx"
MODELOS = caminhos.MODELOS


def _modelo_rvm():
    alvo = MODELOS / "rvm_mobilenetv3_fp32.onnx"
    if not alvo.exists():
        import urllib.request
        MODELOS.mkdir(exist_ok=True)
        tmp = alvo.with_suffix(".part")
        urllib.request.urlretrieve(RVM_URL, tmp)
        tmp.rename(alvo)
    return alvo


def matte_rvm(video, destino, lado_ref=512, fundo_verde=False):
    """Matte por IA de vídeo (RVM). Inferência na resolução original; o modelo reduz internamente
    para ~`lado_ref` px (downsample_ratio) e refina a borda na resolução cheia.
    Se `fundo_verde`, grava também o primeiro plano 'despill' (fgr) — não usado por padrão."""
    import onnxruntime as ort
    destino = Path(destino)
    if destino.exists():
        return destino
    destino.parent.mkdir(parents=True, exist_ok=True)
    w, h, fps = _sonda(video)
    # inferência no máximo em 1920 no lado maior (RVM foi treinado até 4K; acima disso só custa tempo)
    esc = min(1.0, 1920 / max(w, h))
    ew, eh = int(w * esc) // 4 * 4, int(h * esc) // 4 * 4
    ratio = np.array([min(1.0, lado_ref / max(ew, eh))], dtype=np.float32)
    opc = ort.SessionOptions()
    opc.intra_op_num_threads = 0
    sessao = ort.InferenceSession(str(_modelo_rvm()), opc, providers=["CPUExecutionProvider"])
    rec = [np.zeros((1, 1, 1, 1), np.float32)] * 4
    leitor = subprocess.Popen(["ffmpeg", "-v", "error", "-i", str(video), "-vf", f"scale={ew}:{eh}",
                               "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
    escritor = subprocess.Popen(["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "gray",
                                 "-s", f"{ew}x{eh}", "-r", f"{fps}", "-i", "-",
                                 "-vf", f"scale={w}:{h}:flags=bicubic",
                                 "-c:v", "libx264", "-crf", "10", "-pix_fmt", "yuv420p", str(destino)],
                                stdin=subprocess.PIPE)
    tam = ew * eh * 3
    try:
        while True:
            buf = leitor.stdout.read(tam)
            if len(buf) < tam:
                break
            src = np.frombuffer(buf, np.uint8).reshape(eh, ew, 3).transpose(2, 0, 1)[None].astype(np.float32) / 255
            fgr, pha, *rec = sessao.run(None, {"src": src, "r1i": rec[0], "r2i": rec[1], "r3i": rec[2],
                                                "r4i": rec[3], "downsample_ratio": ratio})
            escritor.stdin.write((np.clip(pha[0, 0], 0, 1) * 255).astype(np.uint8).tobytes())
    finally:
        leitor.stdout.close()
        leitor.wait()
        escritor.stdin.close()
        escritor.wait()
    if escritor.returncode != 0:
        destino.unlink(missing_ok=True)
        raise RuntimeError("falha ao gravar o matte")
    return destino


def matte_auto(video, destino):
    """RVM (vídeo) quando possível; rembg (foto) como reserva. Devolve (caminho, motor)."""
    try:
        return matte_rvm(video, destino), "rvm"
    except Exception as e:  # sem rede para baixar o modelo, onnxruntime ausente etc.
        print(f"[recorte] RVM indisponível ({e}); usando rembg")
        return matte_ia(video, destino), "rembg"


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
