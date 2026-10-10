"""Entrega profissional de um vídeo (R18: o que um editor de agência entrega ao cliente).

`preparar(...)` monta `<pasta>/entrega/vNN/` (a versão só sobe; nunca sobrescreve uma entrega anterior):
  previa_720p.mp4     prévia leve com marca d'água "PRÉVIA vNN · NÃO PUBLICAR" para aprovação no celular
  legendas.srt        legenda frase a frase (≤ 32 caracteres por linha, 2 linhas) para subir separada (YouTube, LinkedIn)
                      e para revisar o texto antes de aprovar
  QC.md + folha_quadros.png   ficha de controle de qualidade automática (redes/video/qc.py)
  ENTREGA.md          nota de entrega: o que está incluído, como aprovar (feedback consolidado, 2 rodadas),
                      como publicar e O QUE MEDIR em 24-48 h (taxa de pulo < 35 %, retenção, envios, salvamentos)
Os arquivos finais por rede, capa e textos continuam no pacote (`pacote/PUBLICAR.md`).
Prévia e entrega ficam no computador: nada sobe para serviço de terceiros (material de cliente).
"""
import shutil
import subprocess
from pathlib import Path

from ..nucleo import caminhos


def _proxima_versao(base):
    base.mkdir(parents=True, exist_ok=True)
    ns = [int(p.name[1:]) for p in base.glob("v[0-9]*") if p.name[1:].isdigit()]
    return f"v{(max(ns) + 1) if ns else 1:02d}"


def _t_srt(s):
    ms = int(round(max(s, 0) * 1000))
    return f"{ms // 3600000:02d}:{ms // 60000 % 60:02d}:{ms // 1000 % 60:02d},{ms % 1000:03d}"


def srt(palavras, caminho, max_chars=32, max_linhas=2, pausa=0.6):
    """Palavras com tempo ({w, ini, fim}) → SRT em blocos de frase."""
    blocos, atual = [], []
    for p in palavras:
        texto = " ".join(x["w"] for x in atual + [p])
        quebra = atual and (len(texto) > max_chars * max_linhas or p["ini"] - atual[-1]["fim"] > pausa)
        if quebra:
            blocos.append(atual)
            atual = []
        atual.append(p)
        if p["w"].rstrip().endswith((".", "?", "!")):
            blocos.append(atual)
            atual = []
    if atual:
        blocos.append(atual)
    out = []
    for n, b in enumerate(blocos, 1):
        linhas, linha = [], ""
        for x in b:
            if linha and len(linha) + 1 + len(x["w"]) > max_chars:
                linhas.append(linha)
                linha = x["w"]
            else:
                linha = f"{linha} {x['w']}".strip()
        linhas.append(linha)
        out += [str(n), f"{_t_srt(b[0]['ini'])} --> {_t_srt(b[-1]['fim'])}", "\n".join(linhas), ""]
    Path(caminho).write_text("\n".join(out), encoding="utf-8")
    return caminho


def previa(video, saida, rotulo):
    fonte = caminhos.FONTES / "Inter.ttf"
    ff = f":fontfile='{fonte}'" if fonte.exists() else ""
    vf = (f"scale=720:-2,drawtext=text='{rotulo}'{ff}:fontsize=30:fontcolor=white@0.55:x=(w-tw)/2:y=h*0.06:"
          "box=1:boxcolor=black@0.35:boxborderw=10")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(video), "-vf", vf, "-c:v", "libx264", "-crf", "28",
                    "-preset", "veryfast", "-c:a", "aac", "-b:a", "96k", "-movflags", "+faststart", str(saida)],
                   check=True)
    return saida


METRICAS = """## O que medir em 24-48 h (Instagram Insights / TikTok Analytics / YouTube Studio)
| Métrica | Bom | Alarme | Se der alarme |
|---|---|---|---|
| Taxa de pulo (saiu antes de 3 s) | < 35 % | > 50 % | troque o gancho: publique a variação B como Trial Reel |
| Retenção média | > 50 % da duração | < 30 % | corte o trecho onde a curva cai (mande o print da curva) |
| Envios (compartilhamentos) e salvamentos | crescendo com o alcance | zero | conteúdo útil demais para ser só assistido: vire carrossel |
| Comentários com dúvida | qualquer | — | viram as próximas pautas (formato pergunta → resposta) |
Registre: `python3 -m redes metricas <id> --views … --taxa-pulo … --envios … --salvamentos …`
"""


def preparar(pasta, final, palavras=None, qc=None, publicar_md=None, titulo="", destinos=()):
    pasta = Path(pasta)
    v = _proxima_versao(pasta / "entrega")
    dst = pasta / "entrega" / v
    dst.mkdir(parents=True)
    previa(final, dst / "previa_720p.mp4", f"PRÉVIA {v} · NÃO PUBLICAR")
    if palavras:
        srt(palavras, dst / "legendas.srt")
    if qc:
        for nome in ("QC.md", "folha_quadros.png"):
            orig = Path(qc["folha"]).parent / nome
            if orig.exists():
                shutil.copy(orig, dst / nome)
    sinal = {"verde": "🟢", "amarelo": "🟡", "vermelho": "🔴"}.get((qc or {}).get("sinal"), "—")
    linhas = [f"# Entrega {v}{' — ' + titulo if titulo else ''}", "",
              "## O que está incluído",
              "- `previa_720p.mp4`: prévia para aprovar no celular (com marca d'água; **não publique esta**)",
              "- `legendas.srt`: texto da legenda para revisar e para subir separado (YouTube, LinkedIn)" if palavras else "",
              f"- `QC.md` + `folha_quadros.png`: controle de qualidade automático {sinal}" if qc else "",
              f"- Arquivos finais por rede ({', '.join(destinos)}), capa e textos: `{publicar_md}`" if publicar_md else "",
              "", "## Como aprovar",
              "1. Assista a prévia **no celular, com som e depois sem som**, do início ao fim.",
              "2. Mande **um único retorno consolidado** com o minuto e o segundo de cada ajuste (ex.: \"0:12 trocar a palavra X\").",
              "3. Estão incluídas 2 rodadas de ajuste; cada rodada gera uma nova versão (v02, v03…), nunca sobrescreve.",
              "", "## Como publicar",
              "Siga o `PUBLICAR.md` do pacote (arquivo certo para cada rede, texto, horário, rótulo de IA quando houver).",
              "Publique as variações de gancho como **Trial Reels** e mantenha a de menor taxa de pulo.", "", METRICAS]
    (dst / "ENTREGA.md").write_text("\n".join(x for x in linhas if x is not None) + "\n", encoding="utf-8")
    return {"versao": v, "pasta": str(dst)}
