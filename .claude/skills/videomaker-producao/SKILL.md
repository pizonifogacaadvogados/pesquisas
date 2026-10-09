---
name: videomaker-producao
description: Skill-filha do videomaker. Produz o vídeo profissional (talking head) com o motor v2 - estilos, estúdio virtual, texto atrás da pessoa, câmera com easing, LUT, cartões de lei, lower third, light leak, legenda premium - e faz a revisão editorial e visual. Use na etapa 4 do videomaker para vídeos de pessoa falando.
---

# Produção (motor v2)

Trabalhe em `videomaker-viral/`. Base: `estudos/08` (produção), `09` (estilos), `07` (técnicas), `16` (matriz).

## 1. Rodar
```bash
python3 -m videomaker produzir VIDEO --preset juridico --dur 30-60 --estilo auto \
   --nome "Dra. Fulana" --cargo "Advogada · OAB/UF 00.000" --saida saida/NOME \
   [--srt legenda.srt] [--broll-dir broll/] [--biblioteca-musica musicas/] [--musica faixa.mp3] [--titulo "Você sabia?"]
```
Saídas: `base.mp4` (cortes 9:16), `producao.json` (decisões de direção), `final.mp4`, `roteiro_capcut_pro.md`, `capcut_assets/`. O recorte por IA pode levar alguns minutos; rode em segundo plano quando possível.

## 2. Revisão editorial (edite `producao.json` e rode `python3 -m videomaker rerender saida/NOME/producao.json`)
- `camadas.abertura.texto`: curto e forte (texto atrás da pessoa: 1-3 palavras).
- `camadas.cartoes`: confira **número e nome da norma** (o detector lê da fala; erro aqui é grave). Acrescente cartões de dado: `{"titulo": "7 dias", "subtitulo": "prazo de arrependimento", "ini": 12.7, "fim": 15.5}`.
- `camadas.camera`: tire zooms de momentos sensíveis; no máximo 1-2 snaps no vídeo todo.
- `camadas.transicoes`: 1 a cada 10-15s, só entre blocos de ideia.
- `camadas.broll`: só imagem que **mostra** o que a fala diz.
- `camadas.emojis`: vazio fora do estilo viral; nunca em tema sensível.
- `palavras`: corrija erros de transcrição (a legenda vem daqui).

## 3. Revisão visual (obrigatória)
Extraia quadros em: 0,5s (gancho), lower third, cada cartão, cada transição, clímax, final. Leia cada um e confira:
- rosto no terço superior; nada importante sob a legenda nem na coluna direita (botões);
- recorte limpo (sem halo nem "rastro" de fundo); se houver, ajuste ou troque para `autentico`;
- cor natural na pele; luz não estourada;
- texto legível no tamanho de celular.
Confira o áudio: `ffmpeg -i final.mp4 -af ebur128 -f null -` (≈ −14 LUFS) e escute os pontos de música e SFX.

## 4. Entregar
Resumo: estilo, duração, gancho, recursos usados (cartões, B-roll, transições), trilha (clima e licença), alertas. Peça feedback para o aprendizado.
