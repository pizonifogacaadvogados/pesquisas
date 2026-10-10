"""Detecção de rosto compartilhada (vídeo e foto).

Preferência: YuNet (OpenCV, modelo ONNX de 232 KB, licença MIT, `modelos/face_detection_yunet_2023mar.onnx`),
mais preciso que o Haar e disponível no OpenCV 4.8+ e 5.x. Reserva: Haar cascade (`CascadeClassifier`), que o
OpenCV 5 removeu do módulo principal — por isso a versão 2 do `visao` quebrou no OpenCV 5 (auditoria S1).
"""
import numpy as np

from . import caminhos

YUNET = caminhos.MODELOS / "face_detection_yunet_2023mar.onnx"
HAAR = caminhos.MODELOS / "haarcascade_frontalface_default.xml"


class Detector:
    """`Detector()(rgb)` → lista de (x, y, w, h, confiança), do maior rosto para o menor."""

    def __init__(self, confianca=0.75):
        import cv2
        try:
            cv2.utils.logging.setLogLevel(cv2.utils.logging.LOG_LEVEL_ERROR)   # aviso inofensivo do backend DNN
        except Exception:
            pass
        self.cv2 = cv2
        self.motor = None
        if hasattr(cv2, "FaceDetectorYN") and YUNET.exists():
            self._yn = cv2.FaceDetectorYN.create(str(YUNET), "", (320, 320), confianca, 0.3, 5000)
            self._tam = None
            self.motor = "yunet"
        elif hasattr(cv2, "CascadeClassifier") and HAAR.exists():
            self._haar = cv2.CascadeClassifier(str(HAAR))
            self.motor = "haar"
        else:
            raise RuntimeError("nenhum detector de rosto disponível (instale opencv-python-headless>=4.8)")

    def __call__(self, rgb):
        cv2 = self.cv2
        h, w = rgb.shape[:2]
        if self.motor == "yunet":
            if self._tam != (w, h):
                self._yn.setInputSize((w, h))
                self._tam = (w, h)
            _, faces = self._yn.detect(cv2.cvtColor(np.ascontiguousarray(rgb), cv2.COLOR_RGB2BGR))
            res = [] if faces is None else [(int(f[0]), int(f[1]), int(f[2]), int(f[3]), float(f[14])) for f in faces]
        else:
            cinza = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)
            res = [(int(x), int(y), int(a), int(b), 1.0) for x, y, a, b in
                   self._haar.detectMultiScale(cinza, scaleFactor=1.15, minNeighbors=5, minSize=(w // 12, w // 12))]
        res = [(max(x, 0), max(y, 0), min(a, w - max(x, 0)), min(b, h - max(y, 0)), c) for x, y, a, b, c in res]
        return sorted([r for r in res if r[2] > 0 and r[3] > 0], key=lambda r: -r[2] * r[3])

    def marcos(self, rgb):
        """Maior rosto com pontos: {"caixa", "olho_d", "olho_e", "nariz", "boca_d", "boca_e", "conf"} ou None.
        Só com YuNet (o Haar não dá pontos)."""
        if self.motor != "yunet":
            r = self(rgb)
            return {"caixa": r[0][:4], "conf": r[0][4]} if r else None
        cv2 = self.cv2
        h, w = rgb.shape[:2]
        if self._tam != (w, h):
            self._yn.setInputSize((w, h))
            self._tam = (w, h)
        _, faces = self._yn.detect(cv2.cvtColor(np.ascontiguousarray(rgb), cv2.COLOR_RGB2BGR))
        if faces is None or not len(faces):
            return None
        f = max(faces, key=lambda r: r[2] * r[3])
        pt = lambda i: (float(f[i]), float(f[i + 1]))  # noqa: E731
        return {"caixa": tuple(float(v) for v in f[:4]), "olho_d": pt(4), "olho_e": pt(6), "nariz": pt(8),
                "boca_d": pt(10), "boca_e": pt(12), "conf": float(f[14])}
