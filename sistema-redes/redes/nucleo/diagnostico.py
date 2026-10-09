"""Diagnóstico do ambiente: o que está instalado, o que falta e o que cada falta desliga."""
import importlib
import shutil
import subprocess

from . import caminhos


def _ok(cond, nome, efeito):
    return {"item": nome, "ok": bool(cond), "se_faltar": efeito}


def verificar():
    r = []
    ff = shutil.which("ffmpeg")
    r.append(_ok(ff, "ffmpeg/ffprobe", "TUDO do braço de vídeo"))
    if ff:
        v = subprocess.run(["ffmpeg", "-version"], capture_output=True, text=True).stdout.split("\n")[0]
        r[-1]["versao"] = v
    for mod, efeito in [("numpy", "tudo"), ("PIL", "imagens, legendas, carrosséis"),
                        ("onnxruntime", "recorte RVM (estúdio virtual, texto atrás, thumbnails)"),
                        ("cv2", "visão (rosto, enquadramento, capas)"),
                        ("rembg", "recorte reserva (opcional)"), ("faster_whisper", "transcrição local (opcional com --srt)")]:
        try:
            importlib.import_module(mod)
            r.append(_ok(True, mod, efeito))
        except Exception:
            r.append(_ok(False, mod, efeito))
    try:
        from ..foto.motor import achar_chrome
        r.append(_ok(achar_chrome(), "Chrome/Chromium", "carrosséis, posts, capas, thumbnails"))
    except RuntimeError:
        r.append(_ok(False, "Chrome/Chromium", "carrosséis, posts, capas, thumbnails"))
    node = shutil.which("node")
    nv = subprocess.run(["node", "-v"], capture_output=True, text=True).stdout.strip() if node else ""
    r.append(_ok(node and int(nv.lstrip("v").split(".")[0]) >= 22, f"Node.js ≥ 22 ({nv or 'ausente'})",
                 "motion graphics HyperFrames (volta para ASS/PNG)"))
    for arq, efeito in [("face_detection_yunet_2023mar.onnx", "detecção de rosto (YuNet)"),
                        ("rvm_mobilenetv3_fp32.onnx", "recorte RVM (baixa do GitHub na 1ª vez)")]:
        r.append(_ok((caminhos.MODELOS / arq).exists(), f"modelo {arq}", efeito))
    r.append(_ok(any(caminhos.PERFIS.glob("*.json")) if caminhos.PERFIS.exists() else False, "perfis configurados",
                 "o gestor precisa de pelo menos um perfil"))
    return r


def formatar(r):
    return "\n".join(f"{'✅' if x['ok'] else '❌'} {x['item']}" + (f"  ({x['versao']})" if x.get("versao") else "")
                     + ("" if x["ok"] else f"  → sem isso: {x['se_faltar']}") for x in r)
