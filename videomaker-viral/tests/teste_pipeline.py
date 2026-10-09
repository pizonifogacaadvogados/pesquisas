"""Teste ponta a ponta: gera um vídeo sintético + SRT, roda o pipeline e confere as saídas.

Uso: python3 tests/teste_pipeline.py [pasta_temporaria]
Não precisa de microfone, voz sintética nem transcrição: a "fala" são tons nos tempos do SRT.
"""
import json
import subprocess
import sys
import tempfile
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
FRASES = [
    ("Bom, éé, hoje eu vou falar sobre um assunto.", 0.6, 3.2),
    ("Você sabia que pode cancelar uma compra feita pela internet?", 1.0, 4.0),
    ("hã", 0.9, 0.5),
    ("O artigo 49 do Código de Defesa do Consumidor garante o direito de arrependimento.", 0.8, 5.5),
    ("O prazo é de sete dias, contados do recebimento do produto.", 1.3, 4.0),
    ("E atenção, a loja não pode cobrar multa por isso.", 0.5, 3.5),
    ("Muita gente acha que precisa explicar o motivo, mas isso é mito.", 1.1, 4.2),
    ("E o pior: tem loja que se recusa a devolver o dinheiro.", 0.7, 3.8),
    ("Isso é ilegal, e você pode reclamar no Procon.", 0.9, 3.4),
    ("Salve esse vídeo e compartilhe com quem precisa saber disso.", 0.6, 3.6),
]


def ts(x):
    return f"{int(x // 3600):02d}:{int(x % 3600 // 60):02d}:{int(x % 60):02d},{int(round(x % 1 * 1000)) % 1000:03d}"


def montar(pasta):
    t, srt, expr = 0.5, [], []
    for n, (txt, pausa, dur) in enumerate(FRASES, 1):
        srt.append(f"{n}\n{ts(t)} --> {ts(t + dur)}\n{txt}\n")
        expr.append(f"between(t,{t:.2f},{t + dur:.2f})")
        t += dur + pausa
    (pasta / "bruto.srt").write_text("\n".join(srt), encoding="utf-8")
    fala = "+".join(expr)
    subprocess.run([
        "ffmpeg", "-y", "-v", "error",
        "-f", "lavfi", "-i", f"color=c=0x1d2b3a:s=1920x1080:r=30:d={t:.2f}",
        "-f", "lavfi", "-i", f"aevalsrc='0.4*sin(2*PI*220*t)*sin(2*PI*3*t)*({fala})':s=48000:d={t:.2f}",
        "-vf", "drawbox=x=810:y=180:w=300:h=380:color=0xe0b090:t=fill",
        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-c:a", "aac", "-shortest", str(pasta / "bruto.mp4"),
    ], check=True)
    return t


def duracao(f):
    return float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(f)],
                                capture_output=True, text=True, check=True).stdout)


def main():
    pasta = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(tempfile.mkdtemp(prefix="videomaker_"))
    pasta.mkdir(parents=True, exist_ok=True)
    total = montar(pasta)
    falhas = []
    for preset in ("juridico", "politico", "dinamico"):
        saida = pasta / preset
        r = subprocess.run([sys.executable, "-m", "videomaker", "tudo", str(pasta / "bruto.mp4"), "--srt",
                            str(pasta / "bruto.srt"), "--preset", preset, "--dur", "20-45", "--saida", str(saida)],
                           cwd=RAIZ, capture_output=True, text=True)
        if r.returncode != 0:
            falhas.append(f"{preset}: pipeline falhou\n{r.stderr[-1500:]}")
            continue
        plano = json.loads((saida / "plano.json").read_text(encoding="utf-8"))
        for arq in ("base.mp4", "final.mp4", "roteiro_capcut.md", "roteiro_capcut.json", "legendas.ass"):
            if not (saida / arq).exists():
                falhas.append(f"{preset}: falta {arq}")
        d_final = duracao(saida / "final.mp4")
        if abs(d_final - plano["duracao_final"]) > 0.15:
            falhas.append(f"{preset}: duração {d_final:.2f} ≠ plano {plano['duracao_final']:.2f}")
        if not plano["duracao_final"] < total:
            falhas.append(f"{preset}: não cortou nada")
        if "hã" in plano["texto"].split():
            falhas.append(f"{preset}: vício 'hã' não foi removido")
        if not plano["texto"].startswith("Você sabia"):
            falhas.append(f"{preset}: gancho inesperado: {plano['texto'][:40]}")
        tipos = {e["tipo"] for e in plano["eventos"]}
        for t in ("zoom", "emoji", "sfx", "titulo"):
            if t not in tipos:
                falhas.append(f"{preset}: nenhum evento {t}")
        if preset == "juridico" and any(e.get("emoji") == "💰" for e in plano["eventos"]):
            falhas.append("juridico: usou 💰 (bloqueado pelo preset)")
        print(f"✔ {preset:9s} {plano['duracao_final']:5.1f}s de {total:.1f}s, {plano['cortes_removidos']} cortes, "
              f"{len(plano['eventos'])} eventos")
    if falhas:
        print("\nFALHAS:\n- " + "\n- ".join(falhas))
        return 1
    print(f"\nTudo certo. Arquivos em {pasta}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
