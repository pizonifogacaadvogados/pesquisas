"""Publicação: legenda por rede + pacote pronto para postar (o sistema NUNCA publica sozinho).

legenda(...)  monta o texto de cada destino a partir da pauta e do perfil:
  - 1ª linha = gancho com a palavra-chave (é o que aparece antes do "mais" e o que a busca do Instagram lê);
  - corpo (escrito pelo Claude ou vindo da pauta) + CTA permitido do perfil;
  - assinatura obrigatória: advocacia → nome + OAB (Prov. 205/2021); político impulsionado → "Propaganda
    Eleitoral" + CNPJ; IA → rótulo (R13);
  - hashtags: base do perfil + do tema, sem repetir, no limite de cada rede (Instagram e TikTok: 5 — R12);
  - X: versão curta (280); YouTube: título (≤ 70 ideal) + descrição + tags.
pacote(...)   organiza `pacote/<destino>/` (arquivo final + legenda.txt + texto alternativo) e `PUBLICAR.md`
              com data/hora do calendário, passo a passo por rede, semáforo de conformidade e checklist.
"""
import json
import re
import shutil
from pathlib import Path

from ..nucleo import conformidade, plataformas
from ..nucleo import perfis as _perfis

PASSOS = {
    "instagram": "App → + → Reel/Post → selecione o arquivo → cole a legenda → capa: 'Adicionar da galeria' (capa_reels.png) "
                 "→ Configurações avançadas: 'Enviar na qualidade mais alta' ligado → Compartilhar. Teste de gancho: 'Trial Reel'.",
    "tiktok": "App → + → Carregar → arquivo → legenda (até 5 hashtags) → capa: selecionar quadro → 'Permitir uploads em alta "
              "qualidade' ligado → Publicar. Sem marca d'água de outra rede.",
    "youtube": "YouTube Studio/app → Criar → Shorts (vertical ≤ 3 min) ou Vídeo → título + descrição → miniatura (thumbnail.jpg, "
               "só vídeo longo) → Público.",
    "linkedin": "Começar publicação → Vídeo ou Documento (PDF do carrossel, dê um título) → texto → Publicar.",
    "facebook": "Página → Reel/Foto → arquivo → texto → Publicar (ou cruzar do Instagram pela Central de Contas).",
    "kwai": "App → + → Upload → arquivo → descrição → Publicar.",
    "x": "Postar → mídia → texto curto (280) → Postar.",
    "threads": "Novo thread → mídia → texto (500) → Publicar.",
    "pinterest": "Criar Pin → imagem/vídeo 2:3 ou 9:16 → título + descrição + link do site → Publicar.",
    "whatsapp": "Status → mídia → enviar (trechos de até 60 s, na ordem).",
}


def _hashtags(perfil, extras, limite):
    vistos, out = set(), []
    for h in list(extras or []) + list(perfil.get("hashtags_base", [])):   # tema primeiro (mais específico)
        h = "#" + re.sub(r"[^\wÀ-ÿ]", "", h.lstrip("#"))
        if len(h) > 1 and h.lower() not in vistos:
            vistos.add(h.lower())
            out.append(h)
    return out[:limite] if limite else []


def assinatura(perfil, peca=None):
    peca = peca or {}
    linhas = []
    a = perfil.get("assinatura", {})
    if perfil.get("tipo") in ("advocacia", "juridico"):
        linhas.append(" · ".join(x for x in (a.get("nome"), a.get("cargo"), a.get("registro")) if x))
    if perfil.get("tipo") == "politico" and peca.get("impulsionar"):
        linhas.append(f"Propaganda Eleitoral · {a.get('nome', '')} · CNPJ {perfil.get('cnpj_campanha') or '(INFORMAR)'}")
    if peca.get("usa_ia"):
        linhas.append("Conteúdo gerado/alterado com IA.")
    return "\n".join(linhas)


def legenda(perfil, destino, gancho, corpo="", hashtags=None, cta=None, peca=None):
    """Texto final de um destino + alertas (limites da rede e gancho fora da área visível)."""
    p = _perfis.carregar(perfil)
    d = plataformas.destino(destino)
    peca = peca or {}
    cta = cta if cta is not None else (p.get("cta_permitidos") or [""])[0]
    tags = _hashtags(p, hashtags, d.get("hashtags", 0))
    al = []
    if d.get("legenda") == 0:
        return {"texto": "", "hashtags": [], "alertas": []}
    if d["rede"] == "x":
        texto = gancho
        if len(texto) + sum(len(t) + 1 for t in tags) > d["legenda"]:
            tags = tags[:1]
        texto = (texto + " " + " ".join(tags)).strip()[: d["legenda"]]
        return {"texto": texto, "hashtags": tags, "alertas": plataformas.validar_texto(destino, texto, tags)}
    partes = [gancho.strip(), corpo.strip(), cta.strip(), assinatura(p, peca), " ".join(tags)]
    texto = "\n\n".join(x for x in partes if x)
    if d.get("visivel") and len(gancho) > d["visivel"]:
        al.append(f"{destino}: gancho com {len(gancho)} caracteres; só ~{d['visivel']} aparecem antes do 'mais'")
    if d.get("legenda") and len(texto.encode("utf-8") if d.get("bytes") else texto) > d["legenda"]:
        corte = d["legenda"] - 1
        texto = texto[:corte]
        al.append(f"{destino}: legenda cortada no limite de {d['legenda']}")
    al += plataformas.validar_texto(destino, texto, tags)
    out = {"texto": texto, "hashtags": tags, "alertas": al}
    if d["rede"] == "youtube":
        titulo = re.sub(r"\s+", " ", gancho)[: d.get("titulo", 100)]
        out["titulo"] = titulo
        out["alertas"] += plataformas.validar_texto(destino, "", (), titulo)
        out["tags"] = [t.lstrip("#") for t in tags]
    return out


def texto_alternativo(slides_ou_texto):
    """Alt text (acessibilidade) a partir dos textos dos slides/post."""
    if isinstance(slides_ou_texto, str):
        return slides_ou_texto[:1000]
    partes = []
    for i, s in enumerate(slides_ou_texto, 1):
        t = " ".join(str(s.get(c, "")) for c in ("numero", "rotulo", "titulo", "subtitulo", "afirmacao", "veredito",
                                                   "texto", "legenda", "fonte") if s.get(c))
        t = (t + " " + "; ".join(s.get("itens", []))).replace("==", "").replace("**", "").strip()
        partes.append(f"Slide {i}: {t}")
    return " ".join(partes)[:1000]


def pacote(perfil, pasta, pecas, gancho, corpo="", hashtags=None, texto_peca="", peca=None, agenda=None, alt=None):
    """`pecas`: {destino: arquivo ou [arquivos]} — saída dos braços (exportar, carrossel, post, capas).
    `texto_peca`: tudo o que está escrito/falado na peça (roteiro, slides) para a conformidade.
    `agenda`: {destino: "AAAA-MM-DD HH:MM"} (do calendário). Devolve o resumo e grava PUBLICAR.md."""
    p = _perfis.carregar(perfil)
    pasta = Path(pasta)
    pasta.mkdir(parents=True, exist_ok=True)
    peca = dict(peca or {})
    agenda = agenda or {}
    resumo = {"perfil": p["id"], "destinos": {}, "conformidade": None}
    textos = [texto_peca]
    for dest, arqs in pecas.items():
        arqs = arqs if isinstance(arqs, (list, tuple)) else [arqs]
        sub = pasta / dest
        sub.mkdir(exist_ok=True)
        copiados = []
        for a in arqs:
            a = Path(a)
            if a.exists():
                alvo = sub / a.name
                if a.resolve() != alvo.resolve():
                    shutil.copyfile(a, alvo)
                copiados.append(alvo.name)
        if dest in agenda:
            peca["data"] = agenda[dest][:10]
        leg = legenda(p, dest, gancho, corpo, hashtags, peca=peca)
        textos.append(leg["texto"])
        (sub / "legenda.txt").write_text(leg["texto"] + ("\n\nTÍTULO: " + leg["titulo"] if leg.get("titulo") else ""),
                                         encoding="utf-8")
        if alt and plataformas.destino(dest)["tipo"] != plataformas.V:
            (sub / "texto_alternativo.txt").write_text(alt, encoding="utf-8")
        al = list(leg["alertas"])
        for c in copiados:
            if plataformas.destino(dest)["tipo"] == plataformas.V and c.endswith(".mp4"):
                al += plataformas.validar_arquivo(sub / c, dest)
        resumo["destinos"][dest] = {"arquivos": copiados, "legenda": leg, "agenda": agenda.get(dest), "alertas": al}
    conf = conformidade.checar("\n".join(textos), p, peca)
    resumo["conformidade"] = conf
    _publicar_md(p, pasta, resumo)
    (pasta / "pacote.json").write_text(json.dumps(resumo, ensure_ascii=False, indent=1), encoding="utf-8")
    return resumo


def _publicar_md(p, pasta, r):
    c = r["conformidade"]
    ic = {"verde": "🟢", "amarelo": "🟡", "vermelho": "🔴"}[c["sinal"]]
    md = [f"# Pacote de publicação · {p['nome']}", "",
          f"**Conformidade: {ic} {c['sinal'].upper()}** — {c['resumo']}", ""]
    if c["itens"]:
        md += ["```", conformidade.formatar(c), "```", ""]
    if c["sinal"] == "vermelho":
        md += ["> ⛔ **NÃO PUBLIQUE** antes de corrigir os pontos vermelhos.", ""]
    md += ["| Destino | Arquivos | Quando | Alertas |", "|---|---|---|---|"]
    for dest, d in r["destinos"].items():
        md.append(f"| {dest} | {', '.join(d['arquivos'])} | {d['agenda'] or 'ver calendário'} | "
                  f"{'; '.join(d['alertas']) or '—'} |")
    md += ["", "## Como publicar (manual: o sistema não posta por você)"]
    for rede in sorted({plataformas.destino(x)["rede"] for x in r["destinos"]}):
        md.append(f"- **{rede}**: {PASSOS.get(rede, '')}")
    md += ["", "## Checklist final",
           "- [ ] Assisti/olhei a peça inteira no celular (texto legível, nada sob os botões)",
           "- [ ] Legenda revisada (nomes, números, norma citada)",
           "- [ ] Música com licença da rede ou própria", "- [ ] Conteúdo de terceiro com crédito",
           "- [ ] Depois de 48 h: registrar métricas (`python -m redes metricas …`)"]
    (pasta / "PUBLICAR.md").write_text("\n".join(md) + "\n", encoding="utf-8")
