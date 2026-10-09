"""D2: frases, pontuação e escolha dos melhores momentos (estudos/02-viral.md §4)."""
import re

from . import regras


def frases(palavras, pausa_frase=0.6):
    """Agrupa palavras em frases: quebra em pontuação final ou pausa longa."""
    out, atual = [], []
    for i, p in enumerate(palavras):
        atual.append(i)
        prox = palavras[i + 1] if i + 1 < len(palavras) else None
        fim_pont = re.search(r"[.!?…]$", p["w"])
        pausa = prox is not None and prox["ini"] - p["fim"] > pausa_frase
        if prox is None or fim_pont or pausa:
            out.append(atual)
            atual = []
    return [{"idx": f, "ini": palavras[f[0]]["ini"], "fim": palavras[f[-1]]["fim"],
             "texto": " ".join(palavras[i]["w"] for i in f)} for f in out]


def pontuar(frase, palavras):
    """Nota 0..100 de uma frase."""
    ws = [palavras[i] for i in frase["idx"]]
    texto = frase["texto"]
    dur = max(frase["fim"] - frase["ini"], 0.1)
    nota = 30.0
    nota += min(regras.eh_gatilho(texto) * 12, 36)                       # gatilhos de gancho
    nota += 8 if re.search(r"\?", texto) else 0                             # pergunta
    nota += 6 if re.search(r"!", texto) else 0
    nota += 8 if re.search(r"\d|\bartigo\b|\blei\b|%", texto, re.I) else 0  # dado / autoridade
    energia = sum(w.get("energia", 0.5) for w in ws) / len(ws)
    nota += (energia - 0.5) * 30                                            # voz firme
    pps = len(ws) / dur
    nota += 6 if 2.0 <= pps <= 4.5 else -6                                  # ritmo de fala
    vicios = sum(1 for w in ws if regras.limpa(w["w"]) in regras.VICIOS_SEMPRE)
    nota -= vicios * 8
    if len(ws) < 4:
        nota -= 12                                                          # fragmento solto
    return max(0.0, min(100.0, round(nota, 1)))


CONECTIVOS = {"e", "mas", "então", "entao", "porque", "isso", "também", "tambem", "aí", "ai", "daí", "dai", "ou"}


def _depende_do_anterior(frase):
    primeira = regras.limpa(frase["texto"].split()[0]) if frase["texto"].split() else ""
    return primeira in CONECTIVOS


def _eh_cta(frase):
    return bool(re.search(r"\b(salve|salva|compartilh|coment|segue|siga|manda pra)", frase["texto"], re.I))


def escolher_janela(fs, dur_min, dur_max):
    """Janela contínua de frases com maior nota média ponderada, dentro da duração alvo.

    A duração considera fala útil (sem pausas), que é o que sobra depois dos cortes.
    """
    melhor, melhor_nota = (0, len(fs) - 1), -1.0
    for i in range(len(fs)):
        if fs[i].get("descartavel"):
            continue
        fala = 0.0
        for j in range(i, len(fs)):
            if not fs[j].get("descartavel"):
                fala += fs[j]["fim"] - fs[j]["ini"]
            if fala > dur_max:
                break
            if fala < dur_min and j < len(fs) - 1:
                continue
            # frases que são só vício ("hã") serão cortadas: não entram na média
            notas = [f["nota"] for f in fs[i:j + 1] if not f.get("descartavel")] or [0]
            nota = (sum(notas) / len(notas)
                    + 0.25 * fs[i]["nota"] - (10 if _depende_do_anterior(fs[i]) else 0)  # começa forte e sozinho
                    + 0.10 * fs[j]["nota"] + (5 if _eh_cta(fs[j]) else 0)                # termina forte / CTA
                    + 10 * min(fala / dur_max, 1))                                       # contexto suficiente
            if nota > melhor_nota:
                melhor, melhor_nota = (i, j), nota
    return melhor


def selecionar(palavras, dur_min=25, dur_max=60):
    fs = frases(palavras)
    for f in fs:
        f["nota"] = pontuar(f, palavras)
        ws = [regras.limpa(palavras[k]["w"]) for k in f["idx"]]
        f["descartavel"] = all(w in regras.VICIOS_SEMPRE | regras.VICIOS_CONTEXTO for w in ws)
    i, j = escolher_janela(fs, dur_min, dur_max)
    janela = fs[i:j + 1]
    # gancho: melhor frase da janela; se não for a primeira e for bem melhor, vira "cold open"
    candidatos = [f for f in janela if not _depende_do_anterior(f)] or janela
    gancho = max(candidatos, key=lambda f: f["nota"])
    cold_open = gancho is not janela[0] and gancho["nota"] >= janela[0]["nota"] + 15 \
        and (gancho["fim"] - gancho["ini"]) <= 6.0
    if not cold_open:
        gancho = janela[0]
    # clímax: frase mais forte entre 55% e 95% da janela (para zoom lento / riser+hit)
    n = len(janela)
    meio = janela[int(n * 0.55):max(int(n * 0.95), int(n * 0.55) + 1)] or janela[-1:]
    climax = max(meio, key=lambda f: f["nota"])
    return {"frases": fs, "janela": (i, j), "gancho": gancho, "cold_open": cold_open, "climax": climax}
