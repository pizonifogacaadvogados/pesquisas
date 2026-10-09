"""Calendário editorial: distribui as pautas do perfil pela semana, por rede e horário.

Regras (estudos 11, 17 e R13):
  - frequência por rede/formato vem do perfil (`redes.<rede>.semana`);
  - horários do perfil (`horarios`), alternando entre os dias úteis e o fim de semana;
  - o mesmo tema desdobra: Reels primeiro (alcance), carrossel 1-3 dias depois (salvamentos);
  - vídeo vertical é publicado nas redes irmãs (TikTok, Shorts, Kwai, Facebook) no mesmo dia, 1-3 h depois do Reels
    (evita disputa de atenção; a originalidade do Instagram exige versão sem marca d'água de outra rede);
  - perfil político: nada de conteúdo novo nos dias de eleição (04/10 e 25/10/2026) — crime eleitoral (R13.03).
Saídas: `calendario.md` (leitura), `calendario.json` (máquina) e `calendario.ics` (Google Agenda/Outlook).
"""
import json
from datetime import date, datetime, timedelta
from pathlib import Path

from ..nucleo import conformidade, plataformas
from ..nucleo import perfis as _perfis
from . import pautas as _pautas

DIAS = ["seg", "ter", "qua", "qui", "sex", "sab", "dom"]
IRMAS_VIDEO = {"tiktok": ("video", 60), "youtube": ("shorts", 120), "kwai": ("video", 150), "facebook": ("reels", 180)}


def _horarios(perfil, dia):
    h = perfil.get("horarios", {})
    nome = DIAS[dia.weekday()]
    if nome in h:
        return h[nome]
    if dia.weekday() < 5:
        return h.get("seg-sex", ["12:00", "19:00"])
    return h.get("sab" if nome == "sab" else "dom", h.get("fds", []))


def _proibido(perfil, dia):
    return perfil.get("tipo") == "politico" and dia in conformidade.ELEICAO_2026["turnos"]


def gerar(perfil, inicio=None, semanas=1, pasta=None):
    p = _perfis.carregar(perfil)
    inicio = date.fromisoformat(inicio) if isinstance(inicio, str) else (inicio or date.today())
    fila = {f: [x for x in _pautas.listar(p["id"]) if x["formato"] == f and x["status"] not in ("publicado", "medido")]
            for f in _pautas.FORMATOS}
    itens, avisos = [], []
    ig = p.get("redes", {}).get("instagram", {}).get("semana", {})
    for s in range(semanas):
        dias = [inicio + timedelta(days=7 * s + i) for i in range(7)]
        uteis = [d for d in dias if not _proibido(p, d)]
        _it = lambda *a, s=s, **k: _item(*a, semana=s, **k)  # noqa: E731
        for d in dias:
            if _proibido(p, d):
                avisos.append(f"{d.isoformat()}: dia de eleição — sem publicações novas (Lei 9.504 art. 39 §5º IV)")
        # 1) vídeos-âncora (Reels) espalhados nos dias úteis, horário nobre
        n_reels = ig.get("reels", 0) or p.get("redes", {}).get("tiktok", {}).get("semana", {}).get("video", 0)
        passo = max(1, len(uteis) // max(n_reels, 1))
        for k in range(n_reels):
            d = uteis[min(k * passo, len(uteis) - 1)]
            hora = _horarios(p, d)[-1] if _horarios(p, d) else "19:00"
            pauta = fila["reels"].pop(0) if fila["reels"] else (fila["react"].pop(0) if fila["react"] else None)
            itens.append(_it(d, hora, "instagram", "reels", pauta))
            for rede, (fmt, atraso) in IRMAS_VIDEO.items():
                if p.get("redes", {}).get(rede, {}).get("semana", {}).get(fmt):
                    hh = (datetime.combine(d, datetime.strptime(hora, "%H:%M").time()) + timedelta(minutes=atraso))
                    itens.append(_it(d, hh.strftime("%H:%M"), rede, fmt, pauta, irmao=True))
            # 2) desdobramento em carrossel 2 dias depois (mesmo tema)
            if ig.get("carrossel") and sum(1 for i in itens if i["formato"] == "carrossel" and i["semana"] == s) < ig["carrossel"]:
                d2 = d + timedelta(days=2)
                if d2 in uteis:
                    pc = fila["carrossel"].pop(0) if fila["carrossel"] else None
                    item = _it(d2, (_horarios(p, d2) or ["12:00"])[0], "instagram", "carrossel", pc)
                    item["desdobra"] = pauta["id"] if pauta else None
                    itens.append(item)
        # 3) posts e stories
        for k in range(ig.get("post", 0)):
            d = uteis[(k * 3 + 1) % len(uteis)]
            itens.append(_it(d, (_horarios(p, d) or ["12:00"])[0], "instagram", "post",
                               fila["post"].pop(0) if fila["post"] else None))
        for k in range(ig.get("stories", 0)):
            d = uteis[k % len(uteis)]
            itens.append(_it(d, "09:00", "instagram", "stories", fila["stories"].pop(0) if fila["stories"] else None))
        # 4) LinkedIn
        li = p.get("redes", {}).get("linkedin", {}).get("semana", {})
        k_li = 0
        for fmt, n in li.items():
            for _ in range(n):
                dias_uteis = [x for x in uteis if x.weekday() < 5] or uteis
                d = dias_uteis[(1 + 2 * k_li) % len(dias_uteis)]
                k_li += 1
                itens.append(_it(d, "08:30", "linkedin", fmt, None))
    itens.sort(key=lambda i: (i["data"], i["hora"]))
    vazios = sum(1 for i in itens if not i["pauta"] and not i.get("irmao"))
    if vazios:
        avisos.append(f"{vazios} espaços sem pauta: rode `pauta sugerir` e crie as pautas que faltam")
    cal = {"perfil": p["id"], "inicio": inicio.isoformat(), "semanas": semanas, "itens": itens, "avisos": avisos}
    if pasta:
        salvar(cal, pasta)
    return cal


def _item(d, hora, rede, formato, pauta, irmao=False, semana=0):
    dest = plataformas.FORMATO_DO_PERFIL.get((rede, formato))
    return {"data": d.isoformat(), "dia": DIAS[d.weekday()], "hora": hora, "rede": rede, "formato": formato,
            "destino": dest, "pauta": pauta["id"] if pauta else None, "tema": pauta["tema"] if pauta else "(a definir)",
            "irmao": irmao, "semana": semana}


def salvar(cal, pasta):
    pasta = Path(pasta)
    pasta.mkdir(parents=True, exist_ok=True)
    (pasta / "calendario.json").write_text(json.dumps(cal, ensure_ascii=False, indent=1), encoding="utf-8")
    md = [f"# Calendário editorial · {cal['perfil']} · a partir de {cal['inicio']} ({cal['semanas']} semana(s))", ""]
    md += ["| Data | Dia | Hora | Rede | Formato | Pauta | Tema |", "|---|---|---|---|---|---|---|"]
    for i in cal["itens"]:
        md.append(f"| {i['data']} | {i['dia']} | {i['hora']} | {i['rede']} | {i['formato']}{' (mesmo vídeo)' if i['irmao'] else ''}"
                  f" | {i['pauta'] or '—'} | {i['tema']} |")
    if cal["avisos"]:
        md += ["", "## Avisos"] + [f"- {a}" for a in cal["avisos"]]
    (pasta / "calendario.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    ics = ["BEGIN:VCALENDAR", "VERSION:2.0", "PRODID:-//sistema-redes//calendario//PT"]
    for n, i in enumerate(cal["itens"]):
        ini = datetime.fromisoformat(f"{i['data']}T{i['hora']}")
        fim = ini + timedelta(minutes=15)
        ics += ["BEGIN:VEVENT", f"UID:{cal['perfil']}-{i['data']}-{n}@sistema-redes",
                f"DTSTART:{ini.strftime('%Y%m%dT%H%M%S')}", f"DTEND:{fim.strftime('%Y%m%dT%H%M%S')}",
                f"SUMMARY:[{i['rede']}] {i['formato']}: {i['tema']}".replace(",", "\\,"),
                f"DESCRIPTION:pauta {i['pauta'] or 'a definir'}", "END:VEVENT"]
    ics.append("END:VCALENDAR")
    (pasta / "calendario.ics").write_text("\r\n".join(ics) + "\r\n", encoding="utf-8")
    return pasta / "calendario.md"
