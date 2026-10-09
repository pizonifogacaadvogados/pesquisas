---
name: videomaker-react
description: Skill-filha do videomaker para reacts - reagir ou se manifestar sobre um vídeo em alta (dueto, stitch, remix, green screen, tela dividida, PIP, pausa e comenta, checagem, nota de realismo, resposta). Use quando o usuário quiser comentar, responder, checar ou analisar um vídeo de terceiro, notícia ou fala viral, em advocacia ou política.
---

# React (reagir a vídeo em alta)

Base obrigatória: `videomaker-viral/estudos/10-react.md` (formatos F1-F16, layouts, técnicas, velocidade, checklists) e registro `pesquisa/registro/R04-react.md`.
**Regra de ouro:** o react precisa **transformar** o original (crítica/análise real). Sem isso ele é ilegal (art. 46, III LDA), antiético (OAB) e não tem alcance (originalidade do Instagram desde 30/04/2026 e do TikTok).

## 1. Triagem (antes de qualquer coisa) → `videomaker-conformidade`
- Advocacia: o caso está **sob patrocínio de outro advogado**? → falar só da tese em abstrato (CED art. 42, II).
- Política: risco de descontextualização? período eleitoral? impulsionamento (negativo não pode)?
- Pessoa comum no vídeo? → desfocar o rosto ou não usar.
- Música no original? → será silenciada sob o comentário.

## 2. Escolher formato e layout (E10 §2-3)
| Situação | Formato | Layout |
|---|---|---|
| Situação cotidiana viral ("isso pode?") | F5 pausa e comenta | `dividida` |
| Notícia/decisão (print) | F1 green screen | `greenscreen` (fundo = print) ou CapCut |
| Fala de político | F8 checagem / F12 tradução | `dividida` + carimbos |
| Cena de série/novela | F10 nota de realismo | `dividida` ou `pip` |
| Ataque recebido | F6 stitch / F13 resposta | publicar via Stitch no app, ou `tela_cheia` |
| Velocidade máxima (30 min-4 h) | Dueto/Remix nativo | no app |

## 3. Escrever o roteiro `react.json` (você escreve, a partir das duas transcrições)
```json
{"layout": "dividida", "credito": "@perfil · 08/10/2026 · TikTok",
 "passos": [
  {"tipo": "original", "ini": 3.2, "fim": 6.0, "congelar": {"x": 0.55, "y": 0.35, "escala": 1.6}},
  {"tipo": "comentario", "ini": 0.0, "fim": 7.5, "carimbo": "FORA DE CONTEXTO"},
  {"tipo": "replay", "ini": 4.0, "fim": 5.5, "velocidade": 0.6, "rotulo": "OLHA ISSO"},
  {"tipo": "comentario", "ini": 7.5, "fim": 15.0}
 ]}
```
Regras: gancho = trecho mais forte do original (1-2s) + reação; trechos do original de 2-8s; **comentário ≥ 50-60% do tempo**; `congelar` no detalhe que você vai explicar; carimbo só com fonte confirmada; terminar com veredito.

## 4. Renderizar e revisar
```bash
python3 -m videomaker react ORIGINAL.mp4 REACAO.mp4 react.json --saida saida_react/NOME
```
Leia `react_relatorio.json` (proporção de comentário e alertas). Extraia quadros (congelamentos, carimbos, replay) e olhe. Legendas: rode a reação pelo CapCut (Legendas automáticas) ou passe o vídeo final por `videomaker analisar … --srt` + `producao` com estilo `autentico`.

## 5. Gravação da reação (oriente o usuário)
Fone de ouvido (o original não vaza no microfone); rosto grande no quadro; frases curtas; olhe para a câmera nos vereditos; grave já sabendo os 3 pontos que vai comentar.
