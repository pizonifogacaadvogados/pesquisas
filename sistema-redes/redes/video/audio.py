"""Design de som (estudos/15): clima da música, automação de volume e batidas.

- humor_do_video(): decide o clima da trilha pelo conteúdo, preset e estilo
- escolher_musica(): pega uma faixa da biblioteca local nomeada "<humor>__titulo.mp3"
- automacao(): curva de volume da música ao longo do vídeo (em dB), como um editor faria à mão:
      abertura cheia → abaixa sob a fala → sobe nas pausas → stopdown antes do clímax
      → volta → sobe no fim → fade
- batidas(): detecta batidas da música para alinhar cortes e transições
"""
import re
import subprocess
from pathlib import Path

import numpy as np

from ..nucleo import regras

HUMORES = {
    "confiante": "jurídico educativo, dicas, direitos do dia a dia",
    "sobrio": "autoridade, estúdio, tema sério",
    "tensao": "alerta, golpe, direito violado, crime",
    "investigativo": "documental, lei, decisão, história",
    "dramatico": "política: denúncia, contradição",
    "esperanca": "política: proposta, futuro",
    "urgente": "resposta, react firme",
    "leve": "humor, bastidores",
}
GATILHOS_HUMOR = [
    ("tensao", r"golpe|crime|ilegal|fraude|preso|pol[ií]cia|cuidado|aten[cç][aã]o|perig|abus"),
    ("dramatico", r"mentira|contradi|esc[aâ]ndalo|vergonha|absurdo|corrup"),
    ("esperanca", r"futuro|proposta|vamos|juntos|mudar|esperan"),
    ("investigativo", r"lei |artigo|decis[aã]o|stf|tribunal|hist[oó]ria|em 19|em 20"),
    ("confiante", r"direito|pode|sabia|dica|passo|como fazer"),
]


def humor_do_video(texto, preset, estilo):
    t = regras.sem_acento(texto.lower())
    for humor, padrao in GATILHOS_HUMOR:
        if re.search(regras.sem_acento(padrao), t):
            if humor == "confiante" and estilo == "estudio":
                return "sobrio"
            if humor in ("dramatico", "esperanca") and preset != "politico":
                continue
            return humor
    return {"politico": "urgente", "juridico": "confiante"}.get(preset, "leve")


def escolher_musica(biblioteca, humor):
    """Biblioteca local de faixas LICENCIADAS, nomeadas '<humor>__titulo.ext'."""
    if not biblioteca or not Path(biblioteca).is_dir():
        return None
    faixas = sorted(p for p in Path(biblioteca).iterdir() if p.suffix.lower() in (".mp3", ".wav", ".m4a", ".ogg"))
    preferidas = [p for p in faixas if p.name.lower().startswith(humor + "__")]
    return str((preferidas or faixas or [None])[0]) if (preferidas or faixas) else None


def automacao(palavras, duracao, climax_ini=None, base_db=-21.0):
    """Pontos (t, dB) da música. Interpolação linear entre os pontos."""
    pts = [(0.0, -9.0), (0.35, -9.0), (0.9, base_db)]
    # pausas entre palavras ≥ 0,45s: a música "respira" (sobe 6 dB)
    for a, b in zip(palavras, palavras[1:]):
        gap = b["ini"] - a["fim"]
        if gap >= 0.45 and a["fim"] > 1.0:
            m = a["fim"] + gap / 2
            pts += [(a["fim"] + 0.08, base_db), (m, base_db + 6), (b["ini"] - 0.05, base_db)]
    # stopdown: a música some 0,6s antes do clímax e volta logo depois
    if climax_ini and climax_ini > 2:
        pts += [(climax_ini - 0.9, base_db), (climax_ini - 0.6, -60.0), (climax_ini + 0.05, -60.0),
                (climax_ini + 0.25, base_db + 2)]
    # fim: sobe e faz fade
    fim_fala = palavras[-1]["fim"] if palavras else duracao
    pts += [(fim_fala + 0.1, base_db), (min(fim_fala + 0.6, duracao - 0.2), -11.0), (duracao, -60.0)]
    pts = sorted(p for p in pts if 0 <= p[0] <= duracao)
    limpos = []
    for t, db in pts:
        if limpos and t - limpos[-1][0] < 0.02:
            limpos[-1] = (t, db)
        else:
            limpos.append((t, db))
    return limpos


def expressao_volume(pontos):
    """Expressão do filtro volume (eval=frame) a partir dos pontos em dB."""
    if len(pontos) < 2:
        return "1"
    termos = []
    for (t0, d0), (t1, d1) in zip(pontos, pontos[1:]):
        if t1 <= t0:
            continue
        termos.append(f"between(t,{t0:.3f},{t1:.3f})*({d0:.2f}+({d1 - d0:.2f})*(t-{t0:.3f})/{t1 - t0:.3f})")
    db = "+".join(termos)
    return f"pow(10,({db})/20)"


def batidas(arquivo, max_seg=180, bpm_min=60, bpm_max=180):
    """Tempos (s) das batidas (o pulso, não todo ataque).
    v2 (R19): a v1 marcava todo ataque — inclusive o chimbal no contratempo (F=0,67 na faixa de teste a 112 BPM).
    Agora: fluxo espectral com peso no grave (bumbo/baixo) → andamento por autocorrelação (com preferência
    suave por ~110 BPM) → fase da grade pela soma do fluxo → cada batida da grade é ajustada ao pico mais próximo
    (±60 ms), seguindo pequenas variações de andamento."""
    sr = 11025
    raw = subprocess.run(["ffmpeg", "-v", "error", "-t", str(max_seg), "-i", str(arquivo), "-ac", "1", "-ar", str(sr),
                          "-f", "f32le", "-"], capture_output=True, check=True).stdout
    x = np.frombuffer(raw, np.float32)
    if x.size < sr * 2:
        return []
    hop, n = 128, 1024
    fps = sr / hop
    quadros = np.lib.stride_tricks.sliding_window_view(x, n)[::hop] * np.hanning(n)
    esp = np.log1p(np.abs(np.fft.rfft(quadros, axis=1)))
    d = np.maximum(np.diff(esp, axis=0), 0)
    corte = int(250 / (sr / n))                       # até ~250 Hz: bumbo e baixo
    fluxo = d[:, :corte].sum(axis=1) + 0.25 * d[:, corte:].sum(axis=1)
    fluxo = (fluxo - fluxo.mean()) / (fluxo.std() + 1e-9)
    fluxo = np.maximum(fluxo, 0)
    # andamento: autocorrelação nos atrasos de bpm_max..bpm_min, com preferência log-normal em torno de 110 BPM
    ac = np.correlate(fluxo, fluxo, "full")[len(fluxo) - 1:]
    lags = np.arange(int(fps * 60 / bpm_max), int(fps * 60 / bpm_min) + 1)
    peso = np.exp(-0.5 * (np.log2((60 * fps / lags) / 110) / 0.9) ** 2)
    lag = int(lags[np.argmax(ac[lags] * peso)])
    # refina o período (fracionário) pela média de 3 múltiplos
    per = lag
    for m in (2, 3, 4):
        j = np.arange(m * lag - 2, m * lag + 3)
        j = j[j < len(ac)]
        if len(j):
            per = (per + j[np.argmax(ac[j])] / m) / 2 if m == 2 else (per * (m - 1) + j[np.argmax(ac[j])] / m) / m
    fase = int(np.argmax([fluxo[f::lag].sum() for f in range(lag)]))
    viz = int(0.06 * fps)
    tempos, pos = [], float(fase)
    while pos < len(fluxo):
        i0, i1 = max(0, int(pos) - viz), min(len(fluxo), int(pos) + viz + 1)
        k = i0 + int(np.argmax(fluxo[i0:i1]))
        alvo = k if fluxo[k] > 0.5 else int(round(pos))      # sem pico claro: mantém a grade
        tempos.append(round((alvo * hop + n / 2) / sr + 0.035, 3))   # +35 ms: atraso da janela (medido, R08.50)
        pos = alvo + per
    return tempos


def alinhar_a_batidas(tempos_evento, tempos_batida, tolerancia=0.3):
    """Move cada evento para a batida mais próxima, se estiver dentro da tolerância."""
    if not tempos_batida:
        return tempos_evento
    b = np.array(tempos_batida)
    out = []
    for t in tempos_evento:
        j = int(np.abs(b - t).argmin())
        out.append(float(b[j]) if abs(b[j] - t) <= tolerancia else t)
    return out
