"""Relatório de gestão: situação das pautas, o que foi produzido, conformidade e o que o sistema aprendeu."""
from datetime import datetime

from ..nucleo import aprendizado, caminhos
from . import pautas as _pautas


def gerar(perfil=None, destino=None):
    ps = _pautas.listar(perfil)
    md = [f"# Relatório de redes{' · ' + perfil if perfil else ''} · {datetime.now():%d/%m/%Y %H:%M}", "",
          "## Pautas por status", "```", _pautas.painel(perfil), "```", ""]
    prod = [p for p in ps if p.get("pecas", {}).get("pacote")]
    if prod:
        md += ["## Produzidas", "| Pauta | Formato | Tema | Conformidade | Pacote |", "|---|---|---|---|---|"]
        for p in prod:
            md.append(f"| {p['id']} | {p['formato']} | {p['tema']} | {p['pecas'].get('conformidade', '—')} | "
                      f"{p['pecas']['pacote']} |")
        md.append("")
    rk = aprendizado.ranking()
    if rk:
        md += ["## Desempenho por preset × estilo (aprendizado)", "| Preset | Estilo | Pontuação média | Publicações |",
               "|---|---|---|---|"]
        md += [f"| {preset} | {estilo} | {nota} | {n} |" for (preset, estilo), nota, n in rk[:10]]
        md.append("")
    aprendizado.escrever_licoes()
    lic = caminhos.MEMORIA / "LICOES.md"
    if lic.exists():
        md += ["## Lições aprendidas", lic.read_text(encoding="utf-8")]
    txt = "\n".join(md) + "\n"
    if destino:
        from pathlib import Path
        Path(destino).write_text(txt, encoding="utf-8")
    return txt
