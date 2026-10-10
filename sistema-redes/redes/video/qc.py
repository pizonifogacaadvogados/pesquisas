"""Controle de qualidade (QC) automático antes da entrega: o Claude revisa o próprio corte.

Mede no arquivo final o que um editor de agência confere antes de mandar ao cliente (R18):
  técnico   resolução, fps, codec, duração, áudio presente
  som       loudness integrado (alvo −14 LUFS ±1), pico verdadeiro (≤ −1 dBTP), silêncios longos (> 1,2 s)
  imagem    quadros pretos, imagem congelada (> 1 s)
  rosto     % do tempo com rosto visível; rosto fora da zona segura (sob a interface das redes);
            TOM DE PELE no vetorscópio (linha de pele ≈ 123°; desvio > 12° = cor errada) — estudo 24 §4
  ritmo     tempo médio entre mudanças de plano (corte/zoom) e maior trecho parado — R18: jurídico 2-5 s,
            político 1,5-3 s, nunca mais de 8-10 s sem mudança visual (heurística de mercado, não estudo controlado)
E gera a FOLHA DE QUADROS (um quadro a cada N s) para a revisão humana, que continua obrigatória.
Uso: `python3 -m redes qc final.mp4 [--saida pasta]` → qc.json + QC.md + folha_quadros.png.
"""
import json
import re
import subprocess
from pathlib import Path

from ..nucleo import plataformas

ALVO_LUFS, TOL_LUFS, MAX_TP = -14.0, 1.0, -1.0


def _ff(args):
    return subprocess.run(["ffmpeg", "-hide_banner", "-nostats", *args], capture_output=True, text=True).stderr


def _probe(video):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", str(video)],
                       capture_output=True, text=True, check=True)
    d = json.loads(r.stdout)
    v = next((s for s in d["streams"] if s["codec_type"] == "video"), {})
    a = next((s for s in d["streams"] if s["codec_type"] == "audio"), None)
    num, _, den = v.get("r_frame_rate", "0/1").partition("/")
    return {"w": v.get("width"), "h": v.get("height"), "fps": round(float(num) / float(den or 1), 2),
            "codec": v.get("codec_name"), "dur": round(float(d["format"]["duration"]), 2), "audio": a is not None,
            "mb": round(int(d["format"]["size"]) / 1e6, 1)}


def _loudness(video):
    s = _ff(["-i", str(video), "-af", "ebur128=peak=true", "-f", "null", "-"])
    bloco = s[s.rfind("Summary:"):]
    i = re.search(r"I:\s+(-?[\d.]+) LUFS", bloco)
    tp = re.search(r"Peak:\s+(-?[\d.]+) dBFS", bloco)
    return (float(i.group(1)) if i else None), (float(tp.group(1)) if tp else None)


def _intervalos(saida, chave):
    ini = [float(x) for x in re.findall(chave + r"_start:\s*(-?[\d.]+)", saida)]
    fim = [float(x) for x in re.findall(chave + r"_end:\s*(-?[\d.]+)", saida)]
    return [(round(a, 2), round(b, 2)) for a, b in zip(ini, fim)]


def _silencios(video, minimo=1.2):
    return _intervalos(_ff(["-i", str(video), "-af", f"silencedetect=n=-40dB:d={minimo}", "-f", "null", "-"]), "silence")


def _pretos_e_congelados(video):
    s = _ff(["-i", str(video), "-vf", "blackdetect=d=0.25:pix_th=0.08,freezedetect=n=0.003:d=1", "-an", "-f", "null", "-"])
    pretos = [(round(float(a), 2), round(float(b), 2))
              for a, b in re.findall(r"black_start:(-?[\d.]+)\s+black_end:(-?[\d.]+)", s)]
    cong_i = [float(x) for x in re.findall(r"freeze_start:\s*(-?[\d.]+)", s)]
    cong_f = [float(x) for x in re.findall(r"freeze_end:\s*(-?[\d.]+)", s)]
    return pretos, [(round(a, 2), round(b, 2)) for a, b in zip(cong_i, cong_f)]


def _quadros(video, fps, largura=270):
    """Quadros RGB amostrados (ffmpeg → numpy), sem gravar em disco."""
    import numpy as np
    p = _probe(video)
    h = int(round(p["h"] * largura / p["w"] / 2) * 2)
    r = subprocess.run(["ffmpeg", "-v", "error", "-i", str(video), "-vf", f"fps={fps},scale={largura}:{h}",
                        "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], capture_output=True, check=True)
    n = len(r.stdout) // (largura * h * 3)
    return np.frombuffer(r.stdout[:n * largura * h * 3], np.uint8).reshape(n, h, largura, 3), (largura, h)


def tom_de_pele(rgb, caixa):
    """Ângulo de matiz (graus, no plano CbCr do vetorscópio) do centro do rosto. A "linha de pele" fica em ~123°
    (laranja-avermelhado) para todas as etnias; desvio > 12° indica pele esverdeada/azulada/magenta (cor errada)."""
    import numpy as np
    x, y, w, h = [int(v) for v in caixa[:4]]
    reg = rgb[max(0, y + h // 3): y + 2 * h // 3, max(0, x + w // 4): x + 3 * w // 4].reshape(-1, 3).astype(np.float32)
    if len(reg) < 20:
        return None
    r, g, b = reg[:, 0], reg[:, 1], reg[:, 2]
    yy = 0.299 * r + 0.587 * g + 0.114 * b
    cb, cr = (b - yy).mean(), (r - yy).mean()
    # vetorscópio: eixo horizontal = Cb, vertical = Cr; 0° no +Cb, sentido anti-horário
    return round(float(np.degrees(np.arctan2(cr, cb)) % 360), 1)


def _rosto_e_ritmo(video, destino="instagram_reels", fps=4):
    import numpy as np
    from ..nucleo import rosto
    qs, (w, h) = _quadros(video, fps)
    det = rosto.Detector()
    d = plataformas.destino(destino)
    topo, base, dir_, esq = (v * h / d["h"] for v in d["segura"])
    visivel, fora, centros, mudancas, peles = 0, [], [], [], []
    ant = None
    for k, q in enumerate(qs):
        f = [r for r in det(q) if r[2] > 0.15 * w]     # só o rosto principal (ignora a janela do apresentador)
        if f:
            x, y, fw, fh, _ = f[0]
            visivel += 1
            if k % 4 == 0:
                ang = tom_de_pele(q, f[0])
                if ang is not None:
                    peles.append(ang)
            cy = y + fh / 2
            centros.append((x + fw / 2, cy, fw))
            if y < topo * 0.6 or y + fh > h - base:
                fora.append(round(k / fps, 1))
        # mudança de plano: diferença grande de histograma entre quadros consecutivos
        g = (q[::4, ::4].mean(axis=2) // 16).astype(np.int32).ravel()
        hist = np.bincount(g, minlength=16) / g.size
        if ant is not None and np.abs(hist - ant).sum() > 0.35:
            mudancas.append(k / fps)
        ant = hist
    # zoom/punch-in também conta como mudança de plano: salto de > 12% no tamanho do rosto
    for k in range(1, len(centros)):
        if centros[k - 1][2] and abs(centros[k][2] / centros[k - 1][2] - 1) > 0.12:
            mudancas.append(k / fps)
    dur = len(qs) / fps
    mud = sorted(set(round(t, 1) for t in mudancas))
    marcos = [0.0] + mud + [dur]
    return {"rosto_visivel_pct": round(100 * visivel / max(1, len(qs))), "rosto_fora_zona_s": fora[:20],
            "pele_graus": round(float(np.median(peles)), 1) if peles else None,
            "maior_trecho_sem_mudanca": round(max(b - a for a, b in zip(marcos, marcos[1:])), 1),
            "mudancas_plano": len(mud), "seg_por_mudanca": round(dur / max(1, len(mud)), 1)}


def folha_quadros(video, saida, cada=3.0, colunas=8, largura=240):
    p = _probe(video)
    n = max(1, int(p["dur"] // cada))
    linhas = (n + colunas - 1) // colunas
    vf = (f"fps=1/{cada},scale={largura}:-2,drawtext=text='%{{pts\\:hms}}':x=6:y=6:fontsize=16:fontcolor=white:"
          f"box=1:boxcolor=black@0.6,tile={colunas}x{linhas}:padding=4:color=0x111111")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(video), "-vf", vf, "-frames:v", "1", str(saida)], check=True)
    return saida


def revisar(video, saida=None, destino="instagram_reels", rosto=True):
    """Roda o QC completo. Devolve {sinal, itens[], medidas{}} e grava qc.json/QC.md/folha_quadros.png."""
    video = Path(video)
    pasta = Path(saida) if saida else video.parent / "qc"
    pasta.mkdir(parents=True, exist_ok=True)
    m = _probe(video)
    itens = []

    def item(nivel, texto):
        itens.append({"nivel": nivel, "texto": texto})

    d = plataformas.destino(destino)
    if (m["w"], m["h"]) != (d["w"], d["h"]):
        item("amarelo", f"resolução {m['w']}×{m['h']} (o destino {destino} pede {d['w']}×{d['h']}; a exportação ajusta)")
    if m["fps"] < 24:
        item("vermelho", f"{m['fps']} fps: abaixo de 24 parece travado")
    if not m["audio"]:
        item("vermelho", "sem trilha de áudio")
    else:
        lufs, tp = _loudness(video)
        m.update(lufs=lufs, pico_dbtp=tp)
        if lufs is not None and abs(lufs - ALVO_LUFS) > TOL_LUFS:
            item("amarelo", f"loudness {lufs} LUFS (alvo {ALVO_LUFS} ±{TOL_LUFS}); a exportação normaliza, mas confira a mixagem")
        if tp is not None and tp > MAX_TP:
            item("amarelo", f"pico {tp} dBFS acima de {MAX_TP}: risco de distorção na conversão das redes")
        sil = _silencios(video)
        m["silencios"] = sil
        for a, b in sil:
            item("amarelo", f"silêncio de {b - a:.1f} s em {a:.1f}-{b:.1f} s (corte ou trilha?)")
    pretos, cong = _pretos_e_congelados(video)
    m.update(pretos=pretos, congelados=cong)
    for a, b in pretos:
        item("vermelho" if a > 0.1 else "amarelo", f"quadro preto em {a:.1f}-{b:.1f} s")
    for a, b in cong:
        item("amarelo", f"imagem parada em {a:.1f}-{b:.1f} s ({b - a:.1f} s)")
    if rosto:
        r = _rosto_e_ritmo(video, destino)
        m.update(r)
        if r["rosto_visivel_pct"] < 60:
            item("amarelo", f"rosto visível em só {r['rosto_visivel_pct']}% do vídeo (talking head pede > 80%)")
        if r["rosto_fora_zona_s"]:
            item("amarelo", f"rosto sob a interface da rede em {r['rosto_fora_zona_s'][:6]} s")
        if r["seg_por_mudanca"] > 5:
            item("amarelo", f"uma mudança de plano a cada {r['seg_por_mudanca']} s: lento para vídeo curto "
                            "(R18: jurídico 2-5 s, político 1,5-3 s)")
        if r.get("pele_graus") is not None and abs(r["pele_graus"] - 123) > 12:
            item("amarelo", f"tom de pele a {r['pele_graus']}° no vetorscópio (linha de pele ≈ 123°): "
                            f"{'esverdeado/amarelado' if r['pele_graus'] > 123 else 'magenta/avermelhado'} — revise o balanço de branco/LUT")
        if r.get("maior_trecho_sem_mudanca", 0) > 10:
            item("amarelo", f"{r['maior_trecho_sem_mudanca']} s sem nenhuma mudança visual (R18: nunca mais de 8-10 s)")
    folha_quadros(video, pasta / "folha_quadros.png")
    sinal = "vermelho" if any(i["nivel"] == "vermelho" for i in itens) else \
        "amarelo" if itens else "verde"
    r = {"video": str(video), "sinal": sinal, "itens": itens, "medidas": m, "folha": str(pasta / "folha_quadros.png")}
    (pasta / "qc.json").write_text(json.dumps(r, ensure_ascii=False, indent=1), encoding="utf-8")
    (pasta / "QC.md").write_text(formatar(r), encoding="utf-8")
    return r


def formatar(r):
    ic = {"verde": "🟢", "amarelo": "🟡", "vermelho": "🔴"}
    m = r["medidas"]
    linhas = [f"# QC {ic[r['sinal']]} {Path(r['video']).name}", "",
              f"{m['w']}×{m['h']} · {m['fps']} fps · {m['codec']} · {m['dur']} s · {m['mb']} MB"
              + (f" · {m.get('lufs')} LUFS · pico {m.get('pico_dbtp')} dBFS" if m.get("audio") else ""), ""]
    if "rosto_visivel_pct" in m:
        linhas.append(f"Rosto visível {m['rosto_visivel_pct']}% · {m['mudancas_plano']} mudanças de plano "
                      f"(uma a cada {m['seg_por_mudanca']} s) · pele {m.get('pele_graus')}° (ideal ≈ 123°)")
        linhas.append("")
    linhas += [f"- {ic[i['nivel']]} {i['texto']}" for i in r["itens"]] or ["- 🟢 nada a corrigir"]
    linhas += ["", "Revisão humana (obrigatória): assista no celular, com som, do início ao fim; confira a folha de quadros."]
    return "\n".join(linhas) + "\n"
