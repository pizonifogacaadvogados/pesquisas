"""Gera o RELATÓRIO + MANUAL completo do sistema em uma página HTML única (imagens embutidas).

Fonte de verdade: o próprio repositório — registros de pesquisa (R01…), estudos, skills, docstrings dos módulos,
perfis e plataformas. Rode de novo sempre que o sistema evoluir:
    python3 tools/gerar_relatorio.py --saida RELATORIO.html [--imagens pasta_com_png]
"""
import argparse
import ast
import base64
import html
import io
import re
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
REPO = RAIZ.parent
sys.path.insert(0, str(RAIZ))


# ------------------------------------------------------------------ markdown mínimo → HTML
def inline(t):
    t = html.escape(t, quote=False)
    t = re.sub(r"`([^`]+)`", r"<code>\1</code>", t)
    t = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", t)
    t = re.sub(r"(?<![\w*])\*([^*\n]+?)\*(?!\w)", r"<em>\1</em>", t)
    t = re.sub(r"\[([^\]]+)\]\((https?://[^)\s]+)\)", r'<a href="\2" target="_blank" rel="noopener">\1</a>', t)
    return t


def md(texto):
    out, tabela, lista, codigo = [], [], [], None
    def fecha_tab():
        if tabela:
            cab, *corpo = [r for r in tabela if not re.fullmatch(r"\|?\s*:?-{2,}.*", r.replace(" ", ""))]
            cel = lambda r: [c.strip() for c in r.strip().strip("|").split("|")]  # noqa: E731
            h = "".join(f"<th>{inline(c)}</th>" for c in cel(cab))
            b = "".join("<tr>" + "".join(f"<td>{inline(c)}</td>" for c in cel(r)) + "</tr>" for r in corpo)
            out.append(f'<div class="tab"><table><thead><tr>{h}</tr></thead><tbody>{b}</tbody></table></div>')
            tabela.clear()
    def fecha_lista():
        if lista:
            out.append("<ul>" + "".join(f"<li>{inline(i)}</li>" for i in lista) + "</ul>")
            lista.clear()
    for linha in texto.splitlines():
        if codigo is not None:
            if linha.startswith("```"):
                out.append(f"<pre><code>{html.escape(chr(10).join(codigo))}</code></pre>")
                codigo = None
            else:
                codigo.append(linha)
            continue
        if linha.startswith("```"):
            fecha_tab(); fecha_lista(); codigo = []
            continue
        if linha.startswith("|"):
            fecha_lista(); tabela.append(linha); continue
        fecha_tab()
        m = re.match(r"^\s*[-*] (.*)", linha)
        if m:
            lista.append(m.group(1)); continue
        fecha_lista()
        m = re.match(r"^(#{1,4}) (.*)", linha)
        if m:
            n = min(len(m.group(1)) + 2, 6)
            out.append(f"<h{n}>{inline(m.group(2))}</h{n}>")
        elif linha.startswith(">"):
            out.append(f"<blockquote>{inline(linha.lstrip('> '))}</blockquote>")
        elif linha.strip():
            out.append(f"<p>{inline(linha)}</p>")
    fecha_tab(); fecha_lista()
    return "\n".join(out)


# ------------------------------------------------------------------ coleta
def registros():
    rs = []
    for f in sorted((RAIZ / "pesquisa" / "registro").glob("R[0-9]*.md")):
        t = f.read_text(encoding="utf-8")
        titulo = t.splitlines()[0].lstrip("# ").strip()
        rs.append({"arq": f.name, "titulo": titulo, "texto": t, "entradas": len(re.findall(r"^\| R\d", t, re.M)),
                   "fontes": len(set(re.findall(r"https?://[^)\s|]+", t)))})
    return rs


def estudos():
    out = []
    for f in sorted((RAIZ / "estudos").glob("*.md")):
        linhas = f.read_text(encoding="utf-8").splitlines()
        titulo = linhas[0].lstrip("# ").strip()
        secoes = [l.lstrip("# ").strip() for l in linhas if l.startswith("## ")][:8]
        out.append({"arq": f.name, "titulo": titulo, "secoes": secoes, "texto": "\n".join(linhas[1:])})
    return out


def skills():
    out = []
    for f in sorted((REPO / ".claude" / "skills").glob("*/SKILL.md")):
        t = f.read_text(encoding="utf-8")
        nome = re.search(r"^name: (.+)$", t, re.M).group(1)
        desc = re.search(r"^description: (.+)$", t, re.M).group(1)
        corpo = t.split("---", 2)[2] if t.startswith("---") else t
        out.append({"nome": nome, "desc": desc, "texto": corpo})
    return out


def modulos():
    out = []
    for pac in ("nucleo", "video", "foto", "gestao"):
        for f in sorted((RAIZ / "redes" / pac).glob("*.py")):
            if f.name == "__init__.py":
                continue
            src = f.read_text(encoding="utf-8")
            doc = (ast.get_docstring(ast.parse(src)) or "").strip().split("\n\n")[0].replace("\n", " ")
            out.append({"pac": pac, "mod": f.stem, "doc": doc, "linhas": src.count("\n")})
    return out


def codigo():
    """Todo o código-fonte do sistema (pacote, ferramentas e testes), para o apêndice."""
    out = []
    for pasta in ("redes", "tools", "tests"):
        for f in sorted((RAIZ / pasta).rglob("*.py")):
            src = f.read_text(encoding="utf-8")
            out.append({"arq": str(f.relative_to(RAIZ)), "linhas": src.count("\n"), "src": src})
    return out


def img64(caminho, largura=1400, qualidade=78):
    from PIL import Image
    im = Image.open(caminho).convert("RGB")
    if im.width > largura:
        im = im.resize((largura, int(im.height * largura / im.width)), Image.LANCZOS)
    buf = io.BytesIO()
    im.save(buf, "JPEG", quality=qualidade, optimize=True)
    return "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode()


# ------------------------------------------------------------------ página
CSS = """
:root{
  /* Layout: coluna de leitura de 72ch com índice lateral fixo no desktop; tabelas largas rolam dentro do bloco */
  --papel:#F5F6F8; --folha:#FFFFFF; --tinta:#16202E; --tinta2:#4A5566; --linha:#DADFE7; --acento:#8A6A2F;
  --acento2:#1E4E79; --verde:#2E7D4F; --amarelo:#A86B00; --vermelho:#B3261E; --codigo:#EEF1F5;
  --f-tit:"Source Serif 4", Georgia, "Times New Roman", serif; --f-txt:"IBM Plex Sans", system-ui, -apple-system, "Segoe UI", sans-serif;
  --f-mono:"IBM Plex Mono", ui-monospace, Menlo, Consolas, monospace;
}
@media (prefers-color-scheme: dark){:root:not([data-theme="light"]){--papel:#0F141B;--folha:#151C25;--tinta:#E6EAF0;--tinta2:#A7B1BF;
  --linha:#2A3441;--acento:#D2AE6A;--acento2:#7FB2E5;--verde:#6BC08E;--amarelo:#E3A93B;--vermelho:#EF7B72;--codigo:#1C2531;color-scheme:dark}}
:root[data-theme="dark"]{--papel:#0F141B;--folha:#151C25;--tinta:#E6EAF0;--tinta2:#A7B1BF;--linha:#2A3441;--acento:#D2AE6A;
  --acento2:#7FB2E5;--verde:#6BC08E;--amarelo:#E3A93B;--vermelho:#EF7B72;--codigo:#1C2531;color-scheme:dark}
*{box-sizing:border-box}
body{background:var(--papel);color:var(--tinta);font:16px/1.62 var(--f-txt);margin:0}
.casca{display:grid;grid-template-columns:260px minmax(0,1fr);gap:40px;max-width:1240px;margin:0 auto;padding-inline:24px;padding-block:32px 80px}
nav.indice{position:sticky;top:calc(env(safe-area-inset-top,0px) + 24px);align-self:start;max-height:calc(100vh - 48px);overflow:auto;font-size:14px}
nav.indice b{display:block;font:600 12px/1 var(--f-txt);letter-spacing:.12em;text-transform:uppercase;color:var(--tinta2);margin:0 0 12px}
nav.indice a{display:block;color:var(--tinta);text-decoration:none;padding:5px 0 5px 12px;border-left:2px solid var(--linha)}
nav.indice a:hover,nav.indice a:focus-visible{border-left-color:var(--acento);color:var(--acento2)}
main{min-width:0}
header.capa{border-bottom:1px solid var(--linha);padding-bottom:28px;margin-bottom:12px}
.selo{font:600 12px/1 var(--f-txt);letter-spacing:.14em;text-transform:uppercase;color:var(--acento)}
h1{font:600 clamp(32px,5vw,48px)/1.08 var(--f-tit);margin:14px 0 14px;text-wrap:balance;letter-spacing:-.01em}
.lead{font-size:19px;color:var(--tinta2);max-width:68ch;margin:0}
.meta{display:flex;flex-wrap:wrap;gap:8px 22px;margin-top:20px;font-size:14px;color:var(--tinta2)}
.meta span strong{color:var(--tinta)}
section{padding-top:36px;scroll-margin-top:16px}
h2{font:600 30px/1.2 var(--f-tit);margin:0 0 6px;text-wrap:balance}
h2 + .sub{color:var(--tinta2);margin:0 0 18px}
h3{font:600 21px/1.3 var(--f-tit);margin:28px 0 8px}
h4,h5,h6{font:600 16px/1.4 var(--f-txt);margin:22px 0 6px}
p,li{max-width:76ch}
a{color:var(--acento2)}
code{font:13.5px/1.4 var(--f-mono);background:var(--codigo);padding:1px 5px;border-radius:4px;overflow-wrap:anywhere}
pre{background:var(--codigo);border:1px solid var(--linha);border-radius:8px;padding:14px 16px;overflow-x:auto;font:13.5px/1.55 var(--f-mono)}
pre code{background:none;padding:0}
.tab{overflow-x:auto;margin:14px 0 18px;border:1px solid var(--linha);border-radius:8px;background:var(--folha)}
table{border-collapse:collapse;width:100%;font-size:14px}
th{text-align:left;font-weight:600;background:var(--codigo);position:sticky;top:0}
th,td{padding:9px 12px;border-bottom:1px solid var(--linha);vertical-align:top}
td{min-width:90px}
tr:last-child td{border-bottom:0}
.numeros{display:grid;grid-template-columns:repeat(auto-fill,minmax(150px,1fr));gap:12px;margin:22px 0}
.numeros div{background:var(--folha);border:1px solid var(--linha);border-radius:8px;padding:14px 16px}
.numeros strong{display:block;font:600 30px/1.1 var(--f-tit);font-variant-numeric:tabular-nums;color:var(--acento2)}
.numeros span{font-size:13px;color:var(--tinta2)}
figure{margin:18px 0 26px}
figure img{width:100%;border-radius:8px;border:1px solid var(--linha);display:block}
figcaption{font-size:14px;color:var(--tinta2);margin-top:8px;max-width:76ch}
details{background:var(--folha);border:1px solid var(--linha);border-radius:8px;margin:10px 0;padding:0 16px}
details[open]{padding-bottom:10px}
summary{cursor:pointer;padding:12px 0;font-weight:600;list-style-position:outside}
summary small{font-weight:400;color:var(--tinta2);margin-left:6px}
.sinal{display:inline-block;font:600 12px/1 var(--f-txt);padding:4px 8px;border-radius:999px;border:1px solid currentColor}
.sinal.v{color:var(--verde)}.sinal.a{color:var(--amarelo)}.sinal.r{color:var(--vermelho)}
.aviso{border-left:3px solid var(--acento);background:var(--folha);padding:12px 16px;border-radius:0 8px 8px 0;margin:16px 0;max-width:80ch}
blockquote{border-left:3px solid var(--linha);margin:12px 0;padding:2px 14px;color:var(--tinta2)}
.mermaid{background:var(--folha);border:1px solid var(--linha);border-radius:8px;padding:16px;overflow-x:auto}
:focus-visible{outline:2px solid var(--acento2);outline-offset:2px}
@media (max-width:900px){.casca{grid-template-columns:minmax(0,1fr);padding-inline:16px}nav.indice{position:static;max-height:none;border-bottom:1px solid var(--linha);padding-bottom:12px}}
@media (prefers-reduced-motion:reduce){*{scroll-behavior:auto!important}}
html{scroll-behavior:smooth}
"""


def gerar(saida, imagens=None):
    from redes.nucleo import plataformas
    regs, ests, sks, mods = registros(), estudos(), skills(), modulos()
    n_ent = sum(r["entradas"] for r in regs)
    todas = set()
    for r in regs:
        todas |= set(re.findall(r"https?://[^)\s|]+", r["texto"]))
    n_linhas = sum(m["linhas"] for m in mods) + sum(p.read_text().count("\n") for p in (RAIZ / "redes").glob("*.py"))
    imgs = {}
    if imagens:
        for f in Path(imagens).glob("*.*"):
            if f.suffix.lower() in (".png", ".jpg", ".jpeg"):
                imgs[f.stem] = img64(f)

    def fig(nome, legenda):
        return f'<figure><img src="{imgs[nome]}" alt="{html.escape(legenda)}"><figcaption>{legenda}</figcaption></figure>' \
            if nome in imgs else ""

    manual = (RAIZ / "MANUAL.md").read_text(encoding="utf-8")
    manual = manual.split("\n---\n", 1)[-1]
    cron = (RAIZ / "00-cronograma.md").read_text(encoding="utf-8")
    secoes = []

    secoes.append(("resumo", "Resumo executivo", "O que foi construído, em números", f"""
<p>O pedido evoluiu em seis movimentos: (1) pesquisar como editar vídeo com o Claude; (2) criar um especialista que
edite vídeos virais e cinematográficos para advocacia e política, operando o CapCut Pro; (3) elevar o padrão para
"edição de cinema", estudando os melhores criadores e quem já edita com IA; (4) transformar tudo num <strong>sistema de
produção e gestão de redes</strong> com dois braços (vídeo e foto) e uma camada de gestão; (5) estudar quem "deixa o
Claude editar sozinho" e reproduzir esse nível (motor de efeitos IA); (6) pesquisar além dos exemplos a <strong>melhor forma de
entregar um vídeo</strong> (QC automático, entrega versionada) e registrar tudo para a próxima sessão. Este relatório documenta
todas as etapas: o que foi pesquisado (com todas as fontes), o que foi construído, como usar, os resultados e os limites.</p>
<div class="numeros">
<div><strong>{len(regs)}</strong><span>registros de pesquisa (R01–R{len(regs):02d})</span></div>
<div><strong>{n_ent}</strong><span>buscas e testes registrados</span></div>
<div><strong>{len(todas)}</strong><span>fontes únicas citadas</span></div>
<div><strong>{len(ests)}</strong><span>estudos (base de conhecimento)</span></div>
<div><strong>{len(mods)}</strong><span>módulos de código</span></div>
<div><strong>{str(f'{n_linhas:,}').replace(',', '.')}</strong><span>linhas de Python</span></div>
<div><strong>{len(plataformas.DESTINOS)}</strong><span>destinos (rede × formato)</span></div>
<div><strong>{len(sks)}</strong><span>skills do Claude</span></div>
</div>
<div class="aviso"><strong>Princípio do sistema:</strong> o Claude planeja, produz, revisa e entrega pronto; <strong>quem publica é
sempre você</strong>. Nada de material sigiloso de cliente em serviços de terceiros; nada de IA em rosto ou voz de pessoa real
em conteúdo político.</div>
"""))

    est = (RAIZ / "ESTADO.md").read_text(encoding="utf-8").split("\n", 1)[1]
    secoes.append(("estado", "Estado atual, tarefas feitas e pendentes", "Passagem de bastão para a próxima sessão (ESTADO.md)", md(est)))

    secoes.append(("fase11", "Fases 11-12: o Claude como editor e a melhor entrega",
                   "Análise das referências, motor de efeitos, QC, entrega e pesquisa além dos exemplos", f"""
{fig("efeitos_demo", "Demo dos 8 efeitos (exemplo/v4) sobre a amostra de 41 s: camadas 3D, cartão da produção, pergunta, lista explicativa, HUD com rastreamento real, card SALVO, P&B com ATENÇÃO, transcrição ao vivo com forma de onda, título final. Nenhum efeito cobre o cartão da produção (função conflitos).")}
{fig("comparacao_denoise", "R17: limpeza de voz medida neste servidor (bruto com ruído × DeepFilterNet 3 × RNNoise × afftdn). DeepFilterNet: ruído nas pausas −44,6 → −66,4 dBFS sem distorcer a fala; testado, integração pendente.")}
{fig("capas_ab", "Duas opções de capa geradas para o mesmo vídeo (R18): A com degradê e título branco; B com manchete em caixa branca e rótulo na cor do perfil.")}
{fig("comparacao_imagem", "R19: filtros de imagem em CPU sobre a demo (sem filtro, unsharp, hqdn3d, cas, nlmeans). unsharp é o melhor custo-benefício para texto; nlmeans é inviável em CPU (120-568 s para 41 s).")}
{fig("carrossel_editorial", "Carrossel editorial (identidade editorial: fundo papel, itálico de ênfase, cabeçalho 03/07; slides fluxo, grade, terminal, antes/depois e CTA palavra).")}
""" + md((RAIZ / "estudos" / "23-melhor-entrega.md").read_text(encoding="utf-8").split("\n", 1)[1])
                   + "<h3>Estudo 22 — análise imagem a imagem das referências</h3>"
                   + md((RAIZ / "estudos" / "22-claude-editor.md").read_text(encoding="utf-8").split("\n", 1)[1])))

    secoes.append(("diario", "Diário de aprendizados", "Cada problema, como foi descoberto, a causa e o que mudou",
                   md((RAIZ / "memoria" / "DIARIO.md").read_text(encoding="utf-8").split("\n", 1)[1])))

    secoes.append(("arquitetura", "Arquitetura", "Dois braços de produção sobre uma camada de gestão", """
<pre class="mermaid">
flowchart LR
  P[Perfis] --> PA[Pautas] --> C[Calendário] --> E{executar}
  E -->|reels · react · vídeo longo| V[Braço de vídeo]
  E -->|carrossel · post · stories| F[Braço de foto]
  V --> X[Exportação por rede]
  F --> A[Artes por rede]
  X --> K[Conformidade OAB · TSE · LGPD]
  A --> K
  K --> PB[Pacote PUBLICAR.md]
  PB --> U((Você publica))
  U --> M[Métricas e feedback] --> L[Aprendizado] --> PA
</pre>
""" + md("| Pacote | Módulo | Função | Linhas |\n|---|---|---|---|\n" + "\n".join(
        f"| {m['pac']} | `{m['mod']}` | {m['doc'].replace('|', '/')} | {m['linhas']} |" for m in mods))))

    secoes.append(("manual", "Manual de uso", "Instalação, rotina e todos os comandos", md(manual)))

    secoes.append(("video", "Braço de vídeo: resultados", "Da versão 1 ao motor v3", f"""
<p>O motor passou por três gerações, cada uma motivada pela sua avaliação. A <strong>v1</strong> cortava e legendava com
regras de vídeo viral; você a achou "fora de uma edição cinematográfica". A <strong>v2</strong> trouxe estilos com LUT,
estúdio virtual, câmera com easing, cartões de lei e desenho de som; você a achou "amadora: o recorte ficou visonho, o fundo
ficou ruim". A <strong>v3</strong> atacou as causas com as técnicas de compositor profissional: recorte por modelo de
<em>vídeo</em> (RVM), cor casada entre pessoa e fundo, light wrap, e motion graphics de verdade (HyperFrames + GSAP).</p>
{fig("v2_x_v3", "Em cima, v2; embaixo, v3 (mesma amostra). Na v3: borda do cabelo sem franja clara, pele sem tom azulado, lower third e cartão animados com curvas de easing, lower third afastado da legenda.")}
{fig("recorte_rvm_x_rembg", "Recorte: RVM (modelo de vídeo, à esquerda) × rembg (modelo de foto, à direita). O rembg deixa o halo branco da parede no cabelo; o RVM reduziu o tremor da borda em 37% (0,059 × 0,093).")}
{fig("borda_v2_x_v3", "Detalhe da borda: v2 (esquerda) × v3 (direita).")}
<div class="aviso"><strong>O limite que nenhum código resolve:</strong> a amostra de teste tem 768×432, parede branca e luz
chapada. Os criadores de referência parecem caros porque <strong>gravam bem</strong> (luz a 45°, fundo com profundidade, 4K).
O sistema agora avisa quando o material é fraco e entrega o checklist de gravação (estudo 20). O próximo salto depende do seu
vídeo real.</div>
"""))

    secoes.append(("foto", "Braço de foto: resultados", "Posts, stories, capas e thumbnails", f"""
{fig("posts_mos", "Posts gerados pelo sistema (identidade jurídica clássica do perfil): dado, evento, foto com texto, frase, manchete e pergunta, em 4:5 e em stories 9:16 (zonas seguras respeitadas).")}
{fig("capa_thumb", "Capa de Reels (com prévia do corte da grade 3:4) e thumbnail do YouTube com a pessoa recortada; à direita, a thumbnail no tamanho em que o celular mostra.")}
{fig("carrossel_mos", "Carrossel gerado a partir de JSON (9 slides).")}
"""))

    cal = (RAIZ / "exemplo" / "sistema" / "calendario.md")
    pub = (RAIZ / "exemplo" / "sistema" / "PUBLICAR.md")
    secoes.append(("gestao", "Gestão: exemplo real", "Calendário e pacote de publicação gerados pelo sistema",
                   (md(cal.read_text(encoding="utf-8")) if cal.exists() else "") +
                   (md(pub.read_text(encoding="utf-8")) if pub.exists() else "")))

    secoes.append(("conformidade", "Conformidade automática", "Regras, fontes e o calendário eleitoral de 2026",
                   md((RAIZ / "pesquisa" / "registro" / "R13-conformidade-automatica.md").read_text(encoding="utf-8")
                      .split("\n", 2)[2])))

    secoes.append(("skills", "Skills do Claude", "Como o Claude opera o sistema (texto integral de cada skill)", md(
        "| Skill | Quando é usada |\n|---|---|\n" + "\n".join(f"| `{s['nome']}` | {s['desc'].replace('|', '/')} |" for s in sks))
        + "".join(f"<details><summary>{html.escape(s['nome'])} <small>SKILL.md</small></summary>{md(s['texto'])}</details>"
                  for s in sks)))

    secoes.append(("estudos", "Estudos", "A base de conhecimento (sistema-redes/estudos)", "".join(
        f"<details><summary>{html.escape(e['titulo'])} <small>{e['arq']}</small></summary>{md(e['texto'])}</details>"
        for e in ests)))

    secoes.append(("cronograma", "Cronograma e histórico", "Todas as fases, do primeiro pedido ao sistema", md(cron)))

    testes = (RAIZ / "exemplo" / "sistema" / "testes.txt")
    secoes.append(("testes", "Testes e auditoria", "O que foi verificado e corrigido", md("""
Auditoria do código existente (Fase 10, S1) — falhas encontradas e corrigidas:

| Falha | Causa | Correção |
|---|---|---|
| `visao` quebrava | OpenCV 5 removeu o Haar cascade | detector **YuNet** (ONNX 232 KB) com Haar de reserva (`nucleo/rosto.py`) |
| `--transcricao` com lista JSON falhava | código esperava dicionário | aceita lista `[{w, ini, fim}]` (formato documentado) |
| Capa com legenda queimada | quadro escolhido do vídeo final | capa usa `base.mp4` (sem gráficos) automaticamente |
| WhatsApp Status acima de 16 MB | 1080p em 60 s não cabe | Status em 720×1280, bitrate ajustado ao limite |
| Kwai acima de 50 MB | bitrate fixo | bitrate calculado pelo limite de arquivo de cada rede |
| 13 codificações repetidas na exportação | uma por rede | redes com a mesma especificação compartilham o arquivo (13 → 5) |
| Rosto azulado na composição v3 | ganho de cor por canal de ±15% | tinta forte só nas sombras, pele ±4% |
| Lower third encostando na legenda | posição fixa | subiu para fora da faixa de legenda |
| React com recorte de foto | `matte_ia` (rembg) | recorte de vídeo RVM |
""") + (f"<pre>{html.escape(testes.read_text(encoding='utf-8'))}</pre>" if testes.exists() else "")))

    secoes.append(("limites", "Limites e próximos passos", "O que depende de você e o que vem depois", md("""
**Para dar o próximo salto de qualidade (depende de você):**
- Um vídeo seu real, gravado com o checklist do estudo 20 (luz lateral, fundo com profundidade, 4K) — é o re-teste que falta.
- Uma foto do escritório na mesma luz (vira o fundo do estúdio virtual) e um retrato para capas e carrosséis.
- Preencher o perfil real (`perfil criar escritorio-pizoni`): OAB, handles, redes, frequência, horários.
- Responder sobre os vídeos do Tiago Lemos (estudo 21 §5) para reproduzir o fluxo dele.
- Habilitar o conector do Canva nas configurações (falhou por proxy nesta sessão) se quiser usar modelos do Canva.

**Limites técnicos honestos:**
- O sistema não publica nem lê métricas sozinho (você informa os números).
- Modelos de recorte mais novos (MatAnyone, SAM 2) ficam no Hugging Face, bloqueado neste ambiente; o RVM é o melhor baixável.
- YouTube, Instagram e TikTok não podem ser assistidos daqui: referências foram estudadas por bastidores, entrevistas e análises escritas.
- A operação do CapCut é guiada (roteiro + skill); a execução real no seu CapCut ainda não foi testada com você.
- Regras eleitorais e da OAB mudam: revisar `conformidade.py` a cada eleição.

**Próximos passos sugeridos:** re-teste com material real; biblioteca de SFX e trilhas licenciadas do escritório; cenas de motion
para dados e documentos (estilo Vox/Johnny Harris); integração com agendadores (Meta Business Suite) quando houver acesso.
""")))

    cods = codigo()
    licoes = (RAIZ / "memoria" / "LICOES.md")
    secoes.append(("codigo", "Apêndice: código-fonte completo",
                   f"{len(cods)} arquivos, {sum(c['linhas'] for c in cods):,} linhas — o sistema inteiro, como está no repositório".replace(",", "."),
                   (md(licoes.read_text(encoding="utf-8")) if licoes.exists() else "") + "".join(
                       f"<details><summary>{html.escape(c['arq'])} <small>{c['linhas']} linhas</small></summary>"
                       f"<pre><code>{html.escape(c['src'])}</code></pre></details>" for c in cods)))

    apend = "".join(
        f'<details><summary>{html.escape(r["titulo"])} <small>{r["entradas"]} entradas · {r["fontes"]} fontes · {r["arq"]}</small>'
        f"</summary>{md(r['texto'].split(chr(10), 1)[1] if chr(10) in r['texto'] else '')}</details>" for r in regs)
    secoes.append(("registro", "Apêndice: registro completo das pesquisas",
                   f"Todas as {n_ent} buscas e testes, com consultas, fontes, achados e confiabilidade (A oficial · B imprensa/estudo · C guia/blog · D fraco)",
                   md((RAIZ / "pesquisa" / "registro" / "README.md").read_text(encoding="utf-8")) + apend))

    indice = "".join(f'<a href="#{i}">{html.escape(t)}</a>' for i, t, _, _ in secoes)
    corpo = "".join(f'<section id="{i}"><h2>{html.escape(t)}</h2><p class="sub">{html.escape(s)}</p>{c}</section>'
                    for i, t, s, c in secoes)
    pagina = f"""<title>Sistema de Redes Pizoni Fogaça</title>
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500&family=IBM+Plex+Sans:wght@400;500;600&family=Source+Serif+4:opsz,wght@8..60,500;8..60,600&display=swap">
<style>{CSS}</style>
<script src="https://cdn.jsdelivr.net/npm/mermaid@10.9.1/dist/mermaid.min.js"></script>
<script>document.addEventListener("DOMContentLoaded",()=>{{try{{mermaid.initialize({{startOnLoad:false,theme:matchMedia("(prefers-color-scheme: dark)").matches?"dark":"neutral"}});mermaid.run({{querySelector:".mermaid"}})}}catch(e){{}}}});</script>
<div class="casca">
<nav class="indice" aria-label="Índice"><b>Índice</b>{indice}</nav>
<main>
<header class="capa"><div class="selo">Pizoni Fogaça Advogados · relatório e manual</div>
<h1>Sistema de produção e gestão de redes sociais</h1>
<p class="lead">Vídeo e foto para advocacia, conteúdo jurídico e política: o que foi pesquisado, o que foi construído,
como usar e o que vem depois.</p>
<div class="meta"><span><strong>Data</strong> 10/10/2026</span><span><strong>Versão</strong> 2.0</span>
<span><strong>Código</strong> pesquisas/sistema-redes (branch claude/admiring-allen-ii0fmx)</span></div>
</header>
{corpo}
</main></div>
"""
    Path(saida).parent.mkdir(parents=True, exist_ok=True)
    Path(saida).write_text(pagina, encoding="utf-8")
    return saida


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--saida", default=str(RAIZ / "RELATORIO.html"))
    ap.add_argument("--imagens")
    a = ap.parse_args()
    print(gerar(a.saida, a.imagens))
