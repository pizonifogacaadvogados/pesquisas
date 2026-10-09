"""Linha de comando.

  python -m videomaker tudo VIDEO --preset juridico            # análise → plano → render → roteiro
  python -m videomaker analisar VIDEO [--srt legenda.srt]
  python -m videomaker planejar saida/analise.json --preset politico --dur 20-45
  python -m videomaker renderizar saida/plano.json [--musica trilha.mp3]
  python -m videomaker capcut saida/plano.json [--modo base|bruto]
"""
import argparse
import json
import sys
from pathlib import Path

from . import analise, capcut, estilos, plano, producao, regras, render


def _dur(txt):
    a, _, b = txt.partition("-")
    return float(a), float(b or a)


def _resumo(p):
    s = p["selecao"]
    tipos = {}
    for e in p["eventos"]:
        k = e["tipo"] + (f":{e['modo']}" if "modo" in e else "")
        tipos[k] = tipos.get(k, 0) + 1
    print(f"  trecho do bruto : {s['trecho_bruto'][0]:.1f}s → {s['trecho_bruto'][1]:.1f}s")
    print(f"  duração final   : {p['duracao_final']:.1f}s, {p['cortes_removidos']} cortes")
    print(f"  gancho          : {s['gancho']}{'  (cold open)' if s['cold_open'] else ''}")
    print(f"  eventos         : " + ", ".join(f"{k}={v}" for k, v in sorted(tipos.items())))
    for a in p["alertas"]:
        print(f"  ⚠ {a}")


def main(argv=None):
    ap = argparse.ArgumentParser(prog="videomaker", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    def comuns_analise(p):
        p.add_argument("video")
        p.add_argument("--srt", help="legenda pronta (ex.: exportada do CapCut) em vez de transcrever")
        p.add_argument("--transcricao", help="JSON com palavras [{w, ini, fim}]")
        p.add_argument("--modelo", default="small", help="modelo Whisper (tiny/base/small/medium)")

    def comuns_plano(p):
        p.add_argument("--preset", choices=sorted(regras.PRESETS), default="dinamico")
        p.add_argument("--dur", type=_dur, default=(25, 60), help="duração alvo em segundos, ex.: 20-45")
        p.add_argument("--sem-cold-open", action="store_true", help="não repetir o gancho no início")

    def comuns_render(p):
        p.add_argument("--musica", help="trilha de fundo (mp3/wav)")
        p.add_argument("--sfx-dir", help="pasta com seus próprios whoosh.wav, pop.wav, hit.wav...")
        p.add_argument("--enquadramento", choices=["corte", "desfoque"], default="corte")

    p = sub.add_parser("tudo", help="pipeline completo")
    comuns_analise(p); comuns_plano(p); comuns_render(p)
    p.add_argument("--saida", default="saida")
    p.add_argument("--modo-capcut", choices=["base", "bruto"], default="base")
    p.add_argument("--sem-render", action="store_true", help="só análise, plano e roteiro")

    p = sub.add_parser("produzir", help="produção profissional (v2): estilos, estúdio virtual, cor, gráficos")
    comuns_analise(p); comuns_plano(p)
    p.add_argument("--estilo", choices=sorted(estilos.ESTILOS), default="estudio")
    p.add_argument("--nome", help="nome para o lower third (ex.: 'Dra. Ana Souza')")
    p.add_argument("--cargo", help="qualificação (ex.: 'Advogada · OAB/RS 00.000')")
    p.add_argument("--titulo", help="texto da abertura (padrão: derivado do gancho)")
    p.add_argument("--broll-dir", help="pasta de B-roll nomeado por tema (contrato.mp4, stf.jpg…)")
    p.add_argument("--musica"); p.add_argument("--sfx-dir")
    p.add_argument("--enquadramento", choices=["corte", "desfoque"], default="corte")
    p.add_argument("--saida", default="saida")
    p = sub.add_parser("rerender", help="re-renderiza a partir de producao.json editado")
    p.add_argument("producao"); p.add_argument("--sfx-dir")

    p = sub.add_parser("analisar"); comuns_analise(p); p.add_argument("--saida", default="saida")
    p = sub.add_parser("planejar"); p.add_argument("analise"); comuns_plano(p); p.add_argument("--saida", default=None)
    p = sub.add_parser("renderizar"); p.add_argument("plano"); comuns_render(p)
    p.add_argument("--so-base", action="store_true"); p.add_argument("--sem-base", action="store_true")
    p = sub.add_parser("capcut"); p.add_argument("plano"); p.add_argument("--modo", choices=["base", "bruto"], default="base")

    a = ap.parse_args(argv)
    try:
        if a.cmd == "produzir":
            pasta = Path(a.saida); pasta.mkdir(parents=True, exist_ok=True)
            print("1/5 analisando…")
            an = analise.analisar(a.video, pasta / "analise.json", srt=a.srt, transcricao=a.transcricao, modelo=a.modelo)
            print("2/5 planejando cortes…")
            pl = plano.gerar(an, a.preset, *a.dur, cold_open=not a.sem_cold_open)
            plano.salvar(pl, pasta / "plano.json")
            _resumo(pl)
            print("3/5 base (cortes + 9:16)…")
            render.renderizar(pl, pasta, enquadramento=a.enquadramento, base=True, final=False)
            print(f"4/5 produção, estilo '{a.estilo}' (recorte por IA pode levar alguns minutos)…")
            prod, final = producao.produzir(pl, pasta / "base.mp4", pasta, a.estilo, nome=a.nome, cargo=a.cargo,
                                            titulo=a.titulo, broll_dir=a.broll_dir, musica=a.musica, sfx_dir=a.sfx_dir)
            print(f"  final: {final}")
            print("5/5 roteiro do CapCut…")
            print(f"  {capcut.salvar_v2(prod, pl, pasta)}")
            return 0
        if a.cmd == "rerender":
            prod = json.loads(Path(a.producao).read_text(encoding="utf-8"))
            pasta = Path(a.producao).parent
            print(producao.renderizar(prod, pasta / "base.mp4", pasta, sfx_dir=a.sfx_dir))
            return 0
        if a.cmd in ("tudo", "analisar"):
            pasta = Path(a.saida); pasta.mkdir(parents=True, exist_ok=True)
            print("1/4 analisando…")
            an = analise.analisar(a.video, pasta / "analise.json", srt=a.srt, transcricao=a.transcricao, modelo=a.modelo)
            print(f"  {len(an['palavras'])} palavras, {an['duracao']:.1f}s (transcrição: {an['origem_transcricao']})")
            if a.cmd == "analisar":
                return 0
        if a.cmd in ("tudo", "planejar"):
            if a.cmd == "planejar":
                an = json.loads(Path(a.analise).read_text(encoding="utf-8"))
                pasta = Path(a.saida or Path(a.analise).parent)
                pasta.mkdir(parents=True, exist_ok=True)
            print("2/4 planejando…")
            pl = plano.gerar(an, a.preset, *a.dur, cold_open=not a.sem_cold_open)
            plano.salvar(pl, pasta / "plano.json")
            _resumo(pl)
            if a.cmd == "planejar":
                return 0
        if a.cmd == "renderizar":
            pl = json.loads(Path(a.plano).read_text(encoding="utf-8")); pasta = Path(a.plano).parent
        if a.cmd == "capcut":
            pl = json.loads(Path(a.plano).read_text(encoding="utf-8"))
            print(capcut.salvar(pl, Path(a.plano).parent, a.modo)); return 0
        if a.cmd == "renderizar" or (a.cmd == "tudo" and not a.sem_render):
            print("3/4 renderizando (pode levar alguns minutos)…")
            base = not getattr(a, "sem_base", False)
            final = not getattr(a, "so_base", False)
            for k, v in render.renderizar(pl, pasta, sfx_dir=a.sfx_dir, musica=a.musica,
                                          enquadramento=a.enquadramento, base=base, final=final).items():
                print(f"  {k}: {v}")
        if a.cmd == "tudo":
            print("4/4 roteiro do CapCut…")
            print(f"  {capcut.salvar(pl, pasta, a.modo_capcut)}")
    except RuntimeError as e:
        print(f"ERRO: {e}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
