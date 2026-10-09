---
name: videomaker-producao
description: Skill-filha do videomaker. Produz o vídeo profissional (talking head) com o motor v3 - recorte de vídeo por IA (RVM) com light wrap e casamento de cor, motion graphics HyperFrames/GSAP, estilos, estúdio virtual, texto atrás da pessoa, câmera com easing, LUT, cartões de lei, lower third, light leak, legenda premium - e faz a revisão editorial e visual. Use na etapa 4 do videomaker para vídeos de pessoa falando.
---

# Produção (motor v3)

Trabalhe em `videomaker-viral/`. Base: `estudos/08` (produção), `09` (estilos), `07` (técnicas), `16` (matriz), **`18` (referências), `19` (pro × CapCut), `20` (captação), `21` (criadores com IA)**.

## 0. Antes de tudo: o material
O padrão de cinema se decide na captação (`estudos/20`). Se o material for fraco (parede branca colada, luz de teto, < 1080p), **diga ao usuário** e mande o checklist de 1 minuto do `estudos/20` §1 junto com a entrega. Prefira `--estilo autentico` (sem trocar o fundo) quando o ambiente gravado já for bom: profissional filma no lugar, não recorta.

## 1. Rodar
```bash
python3 -m videomaker produzir VIDEO --preset juridico --dur 30-60 --estilo auto \
   --nome "Dra. Fulana" --cargo "Advogada · OAB/UF 00.000" --saida saida/NOME \
   [--srt legenda.srt] [--broll-dir broll/] [--biblioteca-musica musicas/] [--musica faixa.mp3] [--titulo "Você sabia?"] \
   [--fundo-foto foto_do_escritorio.jpg]
```
- **Recorte:** `recorte.matte_auto` usa o RVM (modelo de vídeo, baixado do GitHub na 1ª vez) e cai para o rembg só se faltar. O motor usado fica em `producao.json → composicao.recorte`.
- **Fundo:** com `--fundo-foto`, a foto real do ambiente vira placa com desfoque de lente (muito melhor que o fundo desenhado). Peça ao usuário uma foto do escritório na mesma luz da gravação.
- **Composição:** cor da pessoa casada com o fundo (sombras puxam para o ambiente, pele quase intacta) + light wrap. Medidas em `composicao.cor`.
- **Motion graphics:** lower third, cartões de norma e chamada saem de uma composição **HyperFrames + GSAP** (`videomaker/motion.py`, Node 22+), renderizada como overlay com alfa. Sem Node/HyperFrames, volta aos gráficos ASS/PNG. Desligar: `"motion": false` no `producao.json`. Para novas cenas de motion, use as skills `hyperframes-animation` (regras de easing, máscara, stagger) e siga o contrato `hyperframes-core`.
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
- recorte limpo (sem halo nem "rastro" de fundo); **pele sem tom azulado/arroxeado** depois da composição; se houver problema, ajuste ou troque para `autentico`;
- gráficos: entram e saem com movimento (não "pulam"); o lower third não cobre a legenda;
- cor natural na pele; luz não estourada;
- texto legível no tamanho de celular.
Confira o áudio: `ffmpeg -i final.mp4 -af ebur128 -f null -` (≈ −14 LUFS) e escute os pontos de música e SFX.

## 4. Entregar
Resumo: estilo, duração, gancho, recursos usados (cartões, B-roll, transições), trilha (clima e licença), alertas. Peça feedback para o aprendizado.
