"""D5: converte o plano num roteiro passo a passo para o CapCut Web.

O roteiro é lido pelo Claude (com a extensão Claude in Chrome) e executado no CapCut
logado do usuário. Cada etapa tem uma verificação visual. As receitas (R0..R12)
estão detalhadas em estudos/04-capcut-web.md e na skill.

Modos:
  base  (recomendado) o usuário sobe o base.mp4 (já cortado e em 9:16). Os tempos do
        roteiro são os da timeline do CapCut.
  bruto o usuário sobe o vídeo original; o roteiro inclui os cortes (do fim para o começo).
"""
import json
from pathlib import Path

from . import regras

NOME_SFX = {"whoosh": "whoosh", "pop": "pop", "hit": "impact / hit", "riser": "riser", "ding": "ding / bell",
            "buzzer": "buzzer / wrong"}


def tc(s):
    """Tempo no formato mm:ss.cc (e segundos entre parênteses)."""
    s = max(s, 0)
    return f"{int(s // 60):02d}:{s % 60:05.2f}"


def etapas(plano, modo="base"):
    cfg = regras.PRESETS[plano["preset"]]
    ev = plano["eventos"]
    out = []

    out.append({"id": "R0", "titulo": "Preparar o projeto", "acoes": [
        {"acao": "abrir", "detalhe": "CapCut Web → Criar novo → vídeo em branco"},
        {"acao": "proporcao", "valor": "9:16"},
        {"acao": "importar", "arquivo": "base.mp4" if modo == "base" else Path(plano["fonte"]).name,
         "detalhe": "Mídia → localizar o arquivo que o usuário já subiu → adicionar à timeline em 00:00"},
    ], "verificar": "Timeline com 1 clipe começando em 00:00; player em formato vertical."})

    if modo == "bruto":
        segs = plano["segmentos"]
        remover = []
        corpo = [s for s in segs if s["papel"] == "corpo"]
        fim_total = plano["fonte_info"].get("duracao") or corpo[-1]["fim"]
        if corpo[-1]["fim"] < fim_total:
            remover.append((corpo[-1]["fim"], fim_total))
        for a, b in zip(corpo[:-1], corpo[1:]):
            if b["ini"] - a["fim"] > 0.01:
                remover.append((a["fim"], b["ini"]))
        if corpo[0]["ini"] > 0:
            remover.append((0, corpo[0]["ini"]))
        remover.sort(reverse=True)
        out.append({"id": "R1", "titulo": f"Cortes ({len(remover)} trechos) — DO FIM PARA O COMEÇO", "acoes": [
            {"acao": "excluir_trecho", "ini": round(a, 3), "fim": round(b, 3),
             "detalhe": f"dividir em {tc(a)} e em {tc(b)}, excluir o pedaço do meio"} for a, b in remover
        ], "verificar": f"Duração da timeline ≈ {tc(sum(s['fim'] - s['ini'] for s in corpo))}."})
        gancho = [s for s in segs if s["papel"] == "gancho"]
        if gancho:
            out.append({"id": "R1b", "titulo": "Gancho no início (cold open)", "acoes": [
                {"acao": "duplicar_para_inicio", "detalhe":
                 f"localizar a frase \"{plano['selecao']['gancho']}\", duplicar o trecho e colocar em 00:00"}],
                "verificar": "O vídeo começa com a frase de gancho."})
        out.append({"id": "R0b", "titulo": "Reenquadrar", "acoes": [
            {"acao": "auto_reframe", "detalhe": "se o vídeo for horizontal: Ferramentas inteligentes → Auto reframe "
             "(ou Básico → Escala até preencher, rosto no terço superior)"}],
            "verificar": "Sem barras pretas; rosto visível no terço superior."})

    punch = [e for e in ev if e["tipo"] == "zoom" and e["modo"] == "punch"]
    if punch:
        out.append({"id": "R2", "titulo": f"Punch-in nos cortes ({len(punch)})", "acoes": [
            {"acao": "dividir", "t": t} for t in sorted({e["ini"] for e in punch} | {e["fim"] for e in punch})
            if 0 < t < plano["duracao_final"] - 0.05] + [
            {"acao": "escala_clipe", "ini": e["ini"], "fim": e["fim"], "escala_pct": round(e["escala"] * 100),
             "detalhe": f"clipe {tc(e['ini'])}–{tc(e['fim'])}: Básico → Escala {round(e['escala'] * 100)}%"}
            for e in punch],
            "verificar": "Ao passar pelos cortes o enquadramento alterna (normal ↔ mais fechado)."})

    snaps = [e for e in ev if e["tipo"] == "zoom" and e["modo"] in ("snap", "lento")]
    if snaps:
        acoes = []
        for e in snaps:
            base_pct = 100
            for p in punch:
                if p["ini"] <= e["ini"] < p["fim"]:
                    base_pct = round(p["escala"] * 100)
            if e["modo"] == "snap":
                acoes.append({"acao": "keyframe_escala", "pontos": [
                    [e["ini"], base_pct], [round(e["ini"] + 0.18, 3), round(e["escala"] * 100)],
                    [round(e["fim"] - 0.15, 3), round(e["escala"] * 100)], [e["fim"], base_pct]],
                    "detalhe": f"snap zoom na palavra \"{e.get('palavra', '')}\" em {tc(e['ini'])}"})
            else:
                acoes.append({"acao": "keyframe_escala", "pontos": [[e["ini"], base_pct],
                                                                    [e["fim"], round(base_pct * e["escala"])]],
                              "detalhe": f"zoom lento do clímax {tc(e['ini'])}–{tc(e['fim'])}"})
        out.append({"id": "R3", "titulo": f"Zooms animados ({len(snaps)})", "acoes": acoes,
                    "verificar": "Os zooms acontecem nas palavras certas, suaves, sem cortar a cabeça."})

    emojis = [e for e in ev if e["tipo"] == "emoji"]
    if emojis:
        out.append({"id": "R5", "titulo": f"Emojis ({len(emojis)})", "acoes": [
            {"acao": "emoji", "emoji": e["emoji"], "ini": e["ini"], "fim": e["fim"], "lado": e.get("lado"),
             "arquivo_png": "assets/emojis/" + _nome_png(e["emoji"]),
             "detalhe": f"{e['emoji']} em {tc(e['ini'])} por {e['fim'] - e['ini']:.1f}s, lado {e.get('lado')}, "
                        f"altura {round(e.get('y', 0.24) * 100)}% da tela, "
                        f"animação de entrada Pop (palavra \"{e.get('palavra', '')}\")"} for e in emojis],
            "verificar": "Emojis aparecem perto da cabeça, sem cobrir boca nem legenda."})

    sons = [e for e in ev if e["tipo"] == "sfx"]
    if sons:
        out.append({"id": "R6", "titulo": f"Efeitos sonoros ({len(sons)})", "acoes": [
            {"acao": "sfx", "som": e["som"], "t": e["t"], "busca_capcut": NOME_SFX.get(e["som"], e["som"]),
             "arquivo": f"assets/sfx/{e['som']}.wav",
             "detalhe": f"{e['som']} em {tc(e['t'])} ({e.get('motivo', '')})"} for e in sons],
            "verificar": "Cada zoom/emoji tem som; volume dos efeitos abaixo da voz."})

    destaques = sorted({p["w"].strip(".,!?;:") for b in plano["legendas"] for p in b["palavras"] if p.get("destaque")})
    out.append({"id": "R7", "titulo": "Legendas dinâmicas", "acoes": [
        {"acao": "legenda_auto", "idioma": "Português"},
        {"acao": "revisar_texto", "referencia": plano["texto"]},
        {"acao": "estilo_legenda", "detalhe":
         f"fonte grossa, branco com contorno preto, palavra atual em destaque (karaokê), "
         f"{cfg['palavras_legenda']} palavras por bloco, {'CAIXA ALTA' if cfg['caixa_alta'] else 'caixa normal'}, "
         f"posição ~65% da altura, aplicar a todas"},
        {"acao": "destacar_palavras", "palavras": destaques},
    ], "verificar": "Legenda sincronizada, sem erros de grafia, fora da zona dos botões do Instagram."})

    tit = next((e for e in ev if e["tipo"] == "titulo"), None)
    if tit:
        out.append({"id": "R8", "titulo": "Título do gancho", "acoes": [
            {"acao": "texto", "texto": tit["texto"], "ini": tit["ini"], "fim": tit["fim"],
             "detalhe": "Texto → adicionar, topo (~20% da altura), fonte grossa, caixa com fundo, entrada Pop"}],
            "verificar": "Título legível nos 3 primeiros segundos."})

    out.append({"id": "R11", "titulo": "Voz e cor", "acoes": [
        {"acao": "audio_voz", "detalhe": "clipe principal → Áudio → Melhorar voz + Redução de ruído"},
        {"acao": "cor", "detalhe": "Ajustar → contraste +5" if plano["preset"] == "juridico"
         else "Ajustar → contraste +8, saturação +5, temperatura +3, vinheta 10"}],
        "verificar": "Voz limpa, pele natural."})
    out.append({"id": "R12", "titulo": "Exportar", "acoes": [
        {"acao": "exportar", "detalhe": "Exportar → 1080p, 30 fps, MP4, qualidade alta → Baixar"}],
        "verificar": "Download concluído."})
    return out


def _nome_png(emoji):
    from .assets import nome_emoji
    return nome_emoji(emoji)


def roteiro_md(plano, modo="base"):
    ets = etapas(plano, modo)
    sel = plano["selecao"]
    l = [f"# Roteiro CapCut Web: preset `{plano['preset']}`", "",
         f"- **Duração final:** {tc(plano['duracao_final'])} ({plano['cortes_removidos']} cortes)",
         f"- **Trecho escolhido do bruto:** {tc(sel['trecho_bruto'][0])} → {tc(sel['trecho_bruto'][1])}",
         f"- **Gancho:** \"{sel['gancho']}\"" + (" (repetido no início: cold open)" if sel["cold_open"] else ""),
         f"- **Clímax:** \"{sel['climax']}\"",
         f"- **Modo:** `{modo}`: suba **{'base.mp4' if modo == 'base' else 'o vídeo bruto'}** "
         "(e, se quiser usar os mesmos sons/emojis, a pasta `assets/`) na Mídia do CapCut antes de começar.",
         ""]
    if plano["alertas"]:
        l += ["## ⚠️ Alertas de conformidade (revisar antes de publicar)", ""] + [f"- {a}" for a in plano["alertas"]] + [""]
    l += ["## Regras de execução", "",
          "1. Execute as etapas **na ordem**. Ao fim de cada uma, tire um print e confira o item **Verificar**.",
          "2. Para posicionar o cursor, prefira digitar/clicar no tempo exato; dê zoom na timeline para precisão.",
          "3. Se um botão não estiver onde o roteiro diz, procure o equivalente (o nome pode estar em inglês).",
          "4. Recurso Pro bloqueado → use a alternativa grátis mais próxima e anote no relatório.",
          "5. Não exclua nem altere nada fora do que está descrito. Em dúvida, pare e pergunte.", ""]
    for et in ets:
        l += [f"## {et['id']}. {et['titulo']}", ""]
        for n, a in enumerate(et["acoes"], 1):
            if "detalhe" in a:
                txt = a["detalhe"]
            elif a["acao"] == "dividir":
                txt = f"dividir em {tc(a['t'])}"
            elif a["acao"] == "proporcao":
                txt = f"Proporção → {a['valor']}"
            elif a["acao"] == "legenda_auto":
                txt = f"Legendas → Legendas automáticas → {a['idioma']} → Gerar"
            elif a["acao"] == "revisar_texto":
                txt = "comparar o texto gerado com a transcrição de referência (abaixo) e corrigir"
            elif a["acao"] == "destacar_palavras":
                txt = "destacar (cor/maior): " + ", ".join(a["palavras"])
            else:
                txt = json.dumps(a, ensure_ascii=False)
            if a["acao"] == "keyframe_escala":
                txt += " — keyframes de escala: " + ", ".join(f"{tc(t)} = {v}%" for t, v in a["pontos"])
            l.append(f"{n}. {txt}")
        l += ["", f"**Verificar:** {et['verificar']}", ""]
    l += ["## Transcrição de referência", "", "> " + plano["texto"], ""]
    return "\n".join(l)


def salvar(plano, pasta, modo="base"):
    pasta = Path(pasta)
    (pasta / "roteiro_capcut.md").write_text(roteiro_md(plano, modo), encoding="utf-8")
    (pasta / "roteiro_capcut.json").write_text(
        json.dumps({"modo": modo, "etapas": etapas(plano, modo)}, ensure_ascii=False, indent=1), encoding="utf-8")
    return pasta / "roteiro_capcut.md"
