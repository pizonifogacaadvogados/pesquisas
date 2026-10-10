"""Comandos do SISTEMA (gestão + braços de foto + exportação). Registrados no `python -m redes`."""
import json
from pathlib import Path

from .foto import capas, post, tratamento
from .gestao import calendario, fluxo, pautas, publicacao, relatorio
from .nucleo import conformidade, diagnostico, perfis, plataformas
from .video import exportar

COMANDOS = {"qc", "entrega", "efeitos", "cortes", "variacoes", "perfil", "pauta", "calendario", "executar", "exportar", "post", "capa", "thumbnail", "foto", "checar",
            "legenda", "relatorio", "diagnostico", "destinos"}


def registrar(sub):
    p = sub.add_parser("qc", help="controle de qualidade do vídeo final (som, imagem, rosto, ritmo) + folha de quadros")
    p.add_argument("video"); p.add_argument("--saida"); p.add_argument("--destino", default="instagram_reels")
    p.add_argument("--sem-rosto", action="store_true")
    p = sub.add_parser("entrega", help="entrega versionada: prévia 720p com marca d'água, .srt, QC e nota de entrega")
    p.add_argument("video"); p.add_argument("--producao", help="producao.json (palavras → legendas.srt)")
    p.add_argument("--saida", default="."); p.add_argument("--titulo", default="")
    p = sub.add_parser("efeitos", help="aplica efeitos de edição IA (titulo, pergunta, card, hud, camadas, lista, transcricao, pb)")
    p.add_argument("video"); p.add_argument("spec", help="JSON com a lista de efeitos (ver redes/video/efeitos.py)")
    p.add_argument("--saida"); p.add_argument("--tema", default=None, help="roxo | dourado | azul (padrão: cores do perfil)")
    p.add_argument("--perfil"); p.add_argument("--producao", help="producao.json (palavras para o efeito transcricao)")
    for nome, ajuda in (("cortes", "vídeo longo → N clipes curtos (podcast, live, palestra)"),
                        ("variacoes", "mesmo trecho com ganchos diferentes (teste A/B, Trial Reels)")):
        p = sub.add_parser(nome, help=ajuda)
        p.add_argument("video"); p.add_argument("--srt"); p.add_argument("--transcricao"); p.add_argument("--modelo", default="small")
        p.add_argument("-n", type=int, default=10 if nome == "cortes" else 3)
        p.add_argument("--preset", default="juridico"); p.add_argument("--dur", default="25-60")
        p.add_argument("--sem-render", action="store_true"); p.add_argument("--saida", default=nome)

    p = sub.add_parser("perfil", help="perfis (contas atendidas): listar | criar | mostrar | validar")
    p.add_argument("acao", choices=["listar", "criar", "mostrar", "validar"])
    p.add_argument("id", nargs="?")
    p.add_argument("--tipo", choices=sorted(perfis.MODELOS), default="advocacia")

    p = sub.add_parser("pauta", help="pautas: criar | listar | status | editar | sugerir | painel")
    p.add_argument("acao", choices=["criar", "listar", "status", "editar", "sugerir", "painel", "mostrar"])
    p.add_argument("args", nargs="*", help="criar: PERFIL TEMA · status: ID STATUS · editar/mostrar: ID · sugerir: PERFIL")
    p.add_argument("--formato", choices=pautas.FORMATOS, default="reels")
    p.add_argument("--gancho", default="")
    p.add_argument("--pilar", default="")
    p.add_argument("--material", default="", help="vídeo bruto, spec JSON de carrossel/post ou pasta")
    p.add_argument("--srt"); p.add_argument("--transcricao")
    p.add_argument("--data", help="data alvo AAAA-MM-DD"); p.add_argument("--hora")
    p.add_argument("--hashtags", nargs="*")
    p.add_argument("--perfil"); p.add_argument("--status")
    p.add_argument("--campos", help="editar: JSON com os campos (ex.: '{\"usa_ia\": true}')")

    p = sub.add_parser("calendario", help="calendário editorial (md + json + ics)")
    p.add_argument("perfil"); p.add_argument("--inicio"); p.add_argument("--semanas", type=int, default=1)
    p.add_argument("--saida")

    p = sub.add_parser("executar", help="executa uma pauta de ponta a ponta (material → peças → pacote)")
    p.add_argument("pauta"); p.add_argument("--saida")

    p = sub.add_parser("exportar", help="exporta um vídeo final para cada rede")
    p.add_argument("video"); p.add_argument("--destinos", nargs="+"); p.add_argument("--perfil")
    p.add_argument("--master-16x9"); p.add_argument("--saida", default="exportar")

    p = sub.add_parser("post", help="post de imagem única/stories a partir de post.json")
    p.add_argument("spec"); p.add_argument("--formatos", nargs="+", default=["4x5"]); p.add_argument("--perfil")
    p.add_argument("--saida")

    for nome, ajuda in (("capa", "capa de Reels/TikTok (melhor quadro + título na área da grade)"),
                        ("thumbnail", "thumbnail do YouTube (pessoa recortada + até 5 palavras)")):
        p = sub.add_parser(nome, help=ajuda)
        p.add_argument("fonte"); p.add_argument("texto"); p.add_argument("--perfil"); p.add_argument("--rotulo", default="")
        p.add_argument("--saida", default=nome)

    p = sub.add_parser("foto", help="tratamento de imagem: tratar | recortar | anonimizar | print")
    p.add_argument("acao", choices=["tratar", "recortar", "anonimizar", "print"])
    p.add_argument("imagem"); p.add_argument("--formatos", nargs="+", default=["4x5"]); p.add_argument("--perfil")
    p.add_argument("--look"); p.add_argument("--caixas", help="anonimizar: 'x,y,w,h;x,y,w,h' (px ou 0-1)")
    p.add_argument("--modo", choices=["desfoque", "tarja"], default="desfoque")
    p.add_argument("--fonte", default=""); p.add_argument("--data", default=""); p.add_argument("--saida", default="foto_saida")

    p = sub.add_parser("checar", help="conformidade (OAB, TSE, LGPD, autoral) de um texto ou arquivo")
    p.add_argument("texto", nargs="?"); p.add_argument("--arquivo"); p.add_argument("--perfil")
    p.add_argument("--data"); p.add_argument("--impulsionar", action="store_true"); p.add_argument("--usa-ia", action="store_true")

    p = sub.add_parser("legenda", help="legenda de um destino (gancho + corpo + CTA + assinatura + hashtags)")
    p.add_argument("perfil"); p.add_argument("destino"); p.add_argument("gancho"); p.add_argument("--corpo", default="")
    p.add_argument("--hashtags", nargs="*")

    p = sub.add_parser("relatorio", help="relatório de gestão (pautas, produção, desempenho, lições)")
    p.add_argument("--perfil"); p.add_argument("--saida")
    sub.add_parser("diagnostico", help="verifica dependências e o que cada falta desliga")
    p = sub.add_parser("destinos", help="lista as especificações por rede"); p.add_argument("--tipo")


def _j(x):
    print(json.dumps(x, ensure_ascii=False, indent=1, default=str))


def executar(a):
    c = a.cmd
    if c == "qc":
        from .video import qc
        r = qc.revisar(a.video, a.saida, a.destino, rosto=not a.sem_rosto)
        print(qc.formatar(r))
        return {"verde": 0, "amarelo": 1, "vermelho": 2}[r["sinal"]]
    if c == "entrega":
        from .gestao import entrega
        from .video import qc
        r_qc = qc.revisar(a.video, Path(a.saida) / "qc")
        pal = json.loads(Path(a.producao).read_text(encoding="utf-8"))["palavras"] if a.producao else None
        r = entrega.preparar(a.saida, a.video, pal, r_qc, titulo=a.titulo)
        print(f"{r['versao']}: {r['pasta']} (QC {r_qc['sinal']})"); return 0
    if c == "efeitos":
        from .video import efeitos
        lista = json.loads(Path(a.spec).read_text(encoding="utf-8"))
        base = Path(a.spec).parent
        for e in lista:
            if e.get("imagem") and not Path(e["imagem"]).is_absolute():
                e["imagem"] = str((base / e["imagem"]).resolve())
        pal = json.loads(Path(a.producao).read_text(encoding="utf-8"))["palavras"] if a.producao else None
        saida = a.saida or str(Path(a.video).with_name(Path(a.video).stem + "_efeitos.mp4"))
        r = efeitos.aplicar(a.video, lista, saida, tema=a.tema, perfil=a.perfil, palavras=pal)
        for x in r["efeitos"]:
            print(f"  {x['efeito']:>12}: {x.get('status') or str(x.get('ini')) + '–' + str(x.get('fim')) + ' s'}")
        print(r["saida"]); return 0
    if c in ("cortes", "variacoes"):
        from .video import analise, cortes
        Path(a.saida).mkdir(parents=True, exist_ok=True)
        an = analise.analisar(a.video, Path(a.saida) / "analise.json", srt=a.srt, transcricao=a.transcricao, modelo=a.modelo)
        dmin, _, dmax = a.dur.partition("-")
        f = cortes.cortes if c == "cortes" else cortes.variacoes
        r = f(an, a.saida, a.n, a.preset, float(dmin), float(dmax or dmin), renderizar=not a.sem_render)
        _j(r); return 0
    if c == "perfil":
        if a.acao == "listar":
            print("\n".join(perfis.listar()) or "nenhum perfil (crie com: perfil criar <id> --tipo advocacia)")
        elif a.acao == "criar":
            p = perfis.criar(a.id, a.tipo)
            print(f"criado: perfis/{p['id']}.json — edite nome, assinatura, cores, redes e horários")
        elif a.acao == "mostrar":
            _j(perfis.carregar(a.id))
        else:
            al = perfis.validar(perfis.carregar(a.id))
            print("\n".join(f"⚠ {x}" for x in al) or "perfil completo")
        return 0
    if c == "pauta":
        if a.acao == "criar":
            perfil, tema = a.args[0], " ".join(a.args[1:])
            extra = {k: v for k, v in (("srt", a.srt), ("transcricao", a.transcricao), ("hora", a.hora),
                                       ("hashtags", a.hashtags)) if v}
            if a.material and a.material.endswith(".json") and a.formato in ("carrossel", "post", "stories"):
                extra["spec"] = json.loads(Path(a.material).read_text(encoding="utf-8"))
            p = pautas.criar(perfil, tema, a.formato, a.gancho, a.pilar, material=a.material, data_alvo=a.data, **extra)
            print(f"{p['id']} criada ({p['formato']}, {p['perfil']})")
        elif a.acao == "listar":
            for p in pautas.listar(a.perfil, a.status):
                print(f"{p['id']}  {p['status']:>9}  {p['formato']:>9}  {p['perfil']}  {p['tema']}")
        elif a.acao == "status":
            pautas.atualizar(a.args[0], status=a.args[1]); print("ok")
        elif a.acao == "editar":
            _j(pautas.atualizar(a.args[0], **json.loads(a.campos or "{}")))
        elif a.acao == "mostrar":
            _j(pautas.obter(a.args[0]))
        elif a.acao == "sugerir":
            _j(pautas.sugerir(a.args[0]))
        else:
            print(pautas.painel(a.perfil))
        return 0
    if c == "calendario":
        cal = calendario.gerar(a.perfil, a.inicio, a.semanas, a.saida or f"calendario_{a.perfil}")
        print(f"{len(cal['itens'])} publicações planejadas → {a.saida or 'calendario_' + a.perfil}/calendario.md (.json, .ics)")
        for x in cal["avisos"]:
            print("⚠", x)
        return 0
    if c == "executar":
        r = fluxo.executar(a.pauta, a.saida)
        print(f"pauta {r['pauta']} ({r['formato']}) → {len(r['destinos'])} destinos · conformidade {r['conformidade']}")
        print(f"abra: {r['publicar']}")
        return 0 if r["conformidade"] != "vermelho" else 2
    if c == "exportar":
        ds = a.destinos or (plataformas.destinos_do_perfil(perfis.carregar(a.perfil), plataformas.V) if a.perfil
                            else None)
        r = exportar.exportar(a.video, a.saida, ds, a.master_16x9)
        for d, v in r["destinos"].items():
            print(f"{d:>22}: {', '.join(v['arquivos'])}" + "".join(f"\n{'':>24}⚠ {x}" for x in v["alertas"]))
        return 0
    if c == "post":
        spec = json.loads(Path(a.spec).read_text(encoding="utf-8"))
        r = post.gerar(spec, a.saida or Path(a.spec).parent / "post_saida", a.formatos, a.perfil, base=Path(a.spec).parent)
        _j(r); return 0
    if c in ("capa", "thumbnail"):
        f = capas.capa_reels if c == "capa" else capas.thumbnail
        _j(f(a.fonte, a.texto, a.saida, a.perfil, rotulo=a.rotulo)); return 0
    if c == "foto":
        Path(a.saida).mkdir(parents=True, exist_ok=True)
        if a.acao == "tratar":
            _j(tratamento.tratar(a.imagem, a.saida, a.formatos, a.perfil, a.look))
        elif a.acao == "recortar":
            print(tratamento.recortar_pessoa(a.imagem, Path(a.saida) / (Path(a.imagem).stem + "_recorte.png")))
        elif a.acao == "anonimizar":
            caixas = [tuple(float(v) for v in cx.split(",")) for cx in (a.caixas or "").split(";") if cx]
            print(tratamento.anonimizar(a.imagem, caixas, Path(a.saida) / (Path(a.imagem).stem + "_anon.jpg"), a.modo))
        else:
            print(tratamento.moldura_print(a.imagem, Path(a.saida) / (Path(a.imagem).stem + "_print.jpg"), a.perfil,
                                           a.fonte, a.data))
        return 0
    if c == "checar":
        texto = Path(a.arquivo).read_text(encoding="utf-8") if a.arquivo else (a.texto or "")
        r = conformidade.checar(texto, perfis.carregar(a.perfil), {"data": a.data, "impulsionar": a.impulsionar,
                                                                  "usa_ia": a.usa_ia})
        print(conformidade.formatar(r))
        return {"verde": 0, "amarelo": 1, "vermelho": 2}[r["sinal"]]
    if c == "legenda":
        r = publicacao.legenda(a.perfil, a.destino, a.gancho, a.corpo, a.hashtags)
        print(r["texto"]); [print("⚠", x) for x in r["alertas"]]
        if r.get("titulo"):
            print("TÍTULO:", r["titulo"])
        return 0
    if c == "relatorio":
        print(relatorio.gerar(a.perfil, a.saida)); return 0
    if c == "diagnostico":
        r = diagnostico.verificar(); print(diagnostico.formatar(r))
        return 0 if all(x["ok"] for x in r) else 1
    if c == "destinos":
        for k, d in plataformas.DESTINOS.items():
            if a.tipo and d["tipo"] != a.tipo:
                continue
            dur = f" · {d['dur'][0]}-{d['dur'][1]} s (ideal {d['dur'][2][0]}-{d['dur'][2][1]})" if "dur" in d else ""
            print(f"{k:>22}: {d['w']}x{d['h']} {d['tipo']}{dur} · legenda {d.get('legenda', '—')} · hashtags "
                  f"{d.get('hashtags', '—')}" + (f" · {d['obs']}" if d.get("obs") else ""))
        return 0
    return 1
