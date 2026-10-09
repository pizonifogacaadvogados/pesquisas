"""Gera os recursos usados na edição: PNG de emojis e efeitos sonoros (WAV).

Os SFX são sintetizados (sem direitos autorais). Para usar sons profissionais,
coloque arquivos com o mesmo nome (whoosh.wav, pop.wav...) em --sfx-dir.
O mesmo pacote serve para subir no CapCut (Mídia), se quiser usar os mesmos sons lá.
"""
import platform
import wave
from pathlib import Path

import numpy as np

SR = 44100
FONTES_EMOJI = [
    ("/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf", 109),
    ("/usr/share/fonts/noto/NotoColorEmoji.ttf", 109),
    ("C:/Windows/Fonts/seguiemj.ttf", 160),
    ("/System/Library/Fonts/Apple Color Emoji.ttc", 160),
]


def nome_emoji(emoji):
    return "-".join(f"{ord(c):x}" for c in emoji if ord(c) != 0xFE0F) + ".png"


def emoji_png(emoji, pasta, tamanho=256):
    """Renderiza o emoji colorido em PNG transparente. Reaproveita se já existir."""
    from PIL import Image, ImageDraw, ImageFont
    destino = Path(pasta) / nome_emoji(emoji)
    if destino.exists():
        return destino
    for caminho, px in FONTES_EMOJI:
        if not Path(caminho).exists():
            continue
        try:
            fonte = ImageFont.truetype(caminho, px)
        except OSError:
            continue
        im = Image.new("RGBA", (px * 3, px * 2), (0, 0, 0, 0))
        ImageDraw.Draw(im).text((px // 2, px // 4), emoji, font=fonte, embedded_color=True)
        caixa = im.getbbox()
        if not caixa:
            continue
        im = im.crop(caixa)
        lado = max(im.size)
        quadro = Image.new("RGBA", (lado, lado), (0, 0, 0, 0))
        quadro.paste(im, ((lado - im.width) // 2, (lado - im.height) // 2))
        destino.parent.mkdir(parents=True, exist_ok=True)
        quadro.resize((tamanho, tamanho), Image.LANCZOS).save(destino)
        return destino
    raise RuntimeError(
        f"Nenhuma fonte de emoji colorida encontrada ({platform.system()}). "
        "Linux: apt install fonts-noto-color-emoji. Ou coloque PNGs em assets/emojis/<codigo>.png")


# ------------------------------------------------------------------ SFX
def _lowpass(x, alpha):
    """Filtro passa-baixa de 1 polo com alpha variável (array) para varredura."""
    y = np.zeros_like(x)
    acc = 0.0
    alpha = np.broadcast_to(alpha, x.shape)
    for i in range(len(x)):
        acc += alpha[i] * (x[i] - acc)
        y[i] = acc
    return y


def _norm(x, pico=0.8):
    m = np.max(np.abs(x)) or 1
    return x / m * pico


def sintetizar():
    rng = np.random.default_rng(7)
    sons = {}
    # whoosh: ruído com varredura de filtro, sobe e desce (0,4s)
    n = int(SR * 0.4)
    t = np.linspace(0, 1, n)
    forma = np.sin(np.pi * t) ** 2
    sons["whoosh"] = _norm(_lowpass(rng.standard_normal(n), 0.02 + 0.35 * forma) * forma, 0.7)
    # pop: senoide com queda de altura, bem curta (0,09s)
    n = int(SR * 0.09)
    t = np.arange(n) / SR
    freq = 950 * np.exp(-t * 28) + 280
    sons["pop"] = _norm(np.sin(2 * np.pi * np.cumsum(freq) / SR) * np.exp(-t * 45), 0.75)
    # hit: grave + estalo (0,8s)
    n = int(SR * 0.8)
    t = np.arange(n) / SR
    grave = np.sin(2 * np.pi * (48 + 30 * np.exp(-t * 12)) * t) * np.exp(-t * 4.5)
    estalo = rng.standard_normal(n) * np.exp(-t * 60) * 0.5
    sons["hit"] = _norm(grave + estalo, 0.9)
    # riser: ruído + senoide subindo, crescendo (1,2s)
    n = int(SR * 1.2)
    t = np.arange(n) / SR
    f = 180 + 1100 * (t / t[-1]) ** 2
    sobe = (t / t[-1]) ** 2.2
    sons["riser"] = _norm((np.sin(2 * np.pi * np.cumsum(f) / SR) * 0.5
                           + _lowpass(rng.standard_normal(n), 0.05 + 0.4 * sobe) * 0.8) * sobe, 0.6)
    # ding: sino (0,9s)
    n = int(SR * 0.9)
    t = np.arange(n) / SR
    sons["ding"] = _norm((np.sin(2 * np.pi * 1568 * t) + 0.4 * np.sin(2 * np.pi * 3136 * t)
                          + 0.2 * np.sin(2 * np.pi * 4704 * t)) * np.exp(-t * 5), 0.55)
    # buzzer: onda quadrada grave (0,45s)
    n = int(SR * 0.45)
    t = np.arange(n) / SR
    sons["buzzer"] = _norm(np.sign(np.sin(2 * np.pi * 140 * t)) * np.minimum(1, (0.45 - t) * 20) * np.minimum(1, t * 200), 0.4)
    for k, v in sons.items():  # fade de 5ms nas pontas (evita estalo)
        f = min(int(SR * 0.005), len(v) // 2)
        v[:f] *= np.linspace(0, 1, f)
        v[-f:] *= np.linspace(1, 0, f)
    return sons


def gerar_sfx(pasta):
    pasta = Path(pasta)
    pasta.mkdir(parents=True, exist_ok=True)
    caminhos = {}
    for nome, sinal in sintetizar().items():
        destino = pasta / f"{nome}.wav"
        if not destino.exists():
            with wave.open(str(destino), "wb") as w:
                w.setnchannels(1)
                w.setsampwidth(2)
                w.setframerate(SR)
                w.writeframes((sinal * 32767).astype(np.int16).tobytes())
        caminhos[nome] = destino
    return caminhos


def sfx(nome, pasta_padrao, pasta_usuario=None):
    if pasta_usuario:
        for ext in ("wav", "mp3", "m4a", "ogg"):
            p = Path(pasta_usuario) / f"{nome}.{ext}"
            if p.exists():
                return p
    return gerar_sfx(pasta_padrao)[nome]
