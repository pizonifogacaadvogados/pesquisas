---
name: videomaker-analise
description: Skill-filha do videomaker. "Assiste" o material bruto (transcrição palavra a palavra + análise quadro a quadro) e decide formato, estilo, melhores momentos e a edição de cada trecho. Use na etapa 2 do videomaker ou quando o usuário pedir para analisar um vídeo, achar os melhores cortes ou dizer o que dá para fazer com um material.
---

# Análise (os olhos e ouvidos do videomaker)

Trabalhe em `videomaker-viral/`. Base: `estudos/16-matriz-decisao.md` (§1-§5), `estudos/02-viral.md` §4.

## 1. Ouvir: transcrição e momentos
```bash
python3 -m videomaker analisar VIDEO --saida saida/NOME            # Whisper local
python3 -m videomaker analisar VIDEO --srt legenda.srt --saida …    # sem Whisper (legenda do CapCut)
python3 -m videomaker planejar saida/NOME/analise.json --preset juridico --dur 30-60
```
Leia `plano.json` → `selecao` (trecho, gancho, clímax, notas por frase). **Releia a transcrição inteira você mesmo**: a pontuação automática é pré-seleção; você entende ironia, contexto e sentido.

## 2. Ver: análise de quadros
```bash
python3 -m videomaker visao VIDEO
```
Dá: presença e posição do rosto, deriva, luz do rosto × fundo, textura do fundo, movimento, trocas de cena e **recomendações** (estúdio virtual, reenquadrar no rosto, relight, estabilizar, rastreamento, color match, mais movimento).

Depois **olhe você mesmo**: extraia 6-10 quadros espalhados e nos momentos-chave.
```bash
ffmpeg -ss T -i VIDEO -frames:v 1 -vf scale=360:-1 q_T.png      # e leia com Read
```
Pergunte-se: o fundo ajuda ou atrapalha? A luz é boa? A expressão combina com a fala? Há gesto ou objeto que mereça zoom ou destaque?

## 3. Decidir (registre as decisões em 5-10 linhas para o usuário)
1. **Formato** (E16 §2): educativo, autoridade, notícia explicada, react, resposta, cortes.
2. **Estilo** (`autentico`, `estudio`, `documental`, `noticiario`, `cinematico`, `viral`): use a recomendação da visão + o nicho + `memoria/LICOES.md` (ranking real).
3. **Duração** por rede (E11): Instagram 30-60s; TikTok 20-35s (alcance) ou 61-90s (monetização).
4. **Momentos**: gancho (primeiros 3s), clímax, trechos a cortar, pausa dramática a manter.
5. **Mapa trecho → edição** (E16 §3): onde vai cartão de lei, B-roll, lower third, transição, stopdown.
6. **Fundo** (E16 §4): manter, desfocar ou estúdio virtual.

Passe essas decisões para `videomaker-producao` (ou `videomaker-react`).
