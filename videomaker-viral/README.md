# Videomaker (advocacia e política)

Núcleo de vídeo profissional operado pelo Claude: assiste ao material bruto, decide a edição como um diretor, produz o vídeo final com acabamento de produção (estúdio virtual, cor de cinema, tipografia, câmera com easing, design de som) e/ou gera o roteiro para executar no **CapCut Pro**. Inclui **react** e um ciclo de **aprendizado** que melhora o sistema a cada vídeo.

## Mapa do projeto

```
.claude/skills/
  videomaker/                 SKILL-MÃE (orquestra tudo)
  videomaker-analise/         assiste: transcrição + quadros → formato, estilo, momentos
  videomaker-producao/        produz (motor v2) + revisão editorial e visual
  videomaker-react/           reacts (16 formatos, roteiro react.json)
  videomaker-audio/           trilha, licença, automação de volume, SFX
  videomaker-capcut/          execução no CapCut Pro (Desktop/EditPilot ou Web)
  videomaker-conformidade/    LDA, imagem, OAB, TSE, LGPD, termos do CapCut
  videomaker-publicacao/      capa, legenda, hashtags, Trial Reels, métricas
  social-carrossel/           carrosséis e posts (gestor de redes, Fase 8)
videomaker-viral/
  00-cronograma.md            plano de estudos e desenvolvimento (fases 1-9)
  estudos/01-21               base de conhecimento (ver índice abaixo)
  pesquisa/registro/          registro de TODAS as pesquisas (consultas, fontes, achados, confiabilidade)
  memoria/                    aprendizado: LICOES.md, ajustes.json, videos.json
  videomaker/                 código (Python)
  fontes/                     fontes profissionais (licença OFL)
  modelos/                    detector de rosto (BSD); RVM e GSAP baixados na 1ª execução (fora do git)
  exemplo/                    saídas de exemplo (v1, v2, v3)
```

## Estudos
| # | Tema | # | Tema |
|---|---|---|---|
| 01 | Linguagem cinematográfica | 09 | Estilos de produção |
| 02 | Anatomia do viral | **10** | **React (guia completo)** |
| 03 | Estilo dinâmico | 11 | Algoritmos e engajamento 2026 |
| 04 | CapCut Web (receitas) | 12 | Nichos (aprofundado) |
| 05 | Nichos (base) | 13 | Inventário do CapCut |
| 06 | Automação | **14** | **CapCut Pro esgotado** |
| 07 | CapCut profissional | **15** | **Áudio e música** |
| 08 | Produção profissional | **16** | **Matriz de decisão** |
| **17** | **Carrosséis** | **18** | **Referências de excelência** |
| **19** | **Ferramentas pro × CapCut × motor** | **20** | **Guia de captação** |
| **21** | **Criadores que editam com IA** | | |

## Motor (código)
| Módulo | Função |
|---|---|
| `analise` | transcrição palavra a palavra (Whisper ou SRT) + energia da voz |
| `visao` | análise quadro a quadro: rosto, luz, fundo, movimento, cenas → recomendações |
| `momentos`, `plano` | pontuação de frases, gancho, clímax, cortes (vícios, pausas) |
| `producao` | **diretor** (decisões de direção) + **render em camadas** |
| `estilos`, `luts` | 6 estilos (autêntico, estúdio, documental, noticiário, cinemático, viral) + LUT .cube |
| `recorte`, `fundos` | pessoa recortada por IA **de vídeo (RVM)**, rembg ou chroma + estúdios virtuais |
| `composicao` | casar cor pessoa × fundo, light wrap, placa de fundo a partir de foto real |
| `motion` | motion graphics HyperFrames + GSAP (lower third, cartões, chamada) em overlay com alfa |
| `graficos` | legendas (premium/forte/viral), aberturas (cinética, texto atrás, manchete), lower third, cartões, carimbos, light leak |
| `audio` | clima da trilha, automação de volume, stopdown, batidas |
| `react` | dividida, PIP, green screen, tela cheia; congelar + zoom + círculo, replay, carimbos, crédito |
| `capcut` | roteiro CapCut Pro por camadas + pacote de assets + instruções para o EditPilot |
| `aprendizado` | registro, feedback → ajustes, métricas → ranking |
| `carrossel` | carrosséis e posts: JSON → PNG (4:5, 3:4, 9:16) + PDF, 4 identidades visuais |

## Uso
```bash
pip install -r requirements.txt          # + ffmpeg instalado
python -m videomaker produzir gravacao.mp4 --preset juridico --estilo auto \
    --nome "Dra. Ana Souza" --cargo "Advogada · OAB/RS 00.000" --saida saida/video1
python -m videomaker react original.mp4 minha_reacao.mp4 react.json --saida saida/react1
python -m videomaker visao gravacao.mp4
python -m videomaker feedback v0001 "zoom demais, legenda pequena"
python -m videomaker metricas v0001 --views 12000 --taxa-pulo 0.38 --envios 310
python -m videomaker licoes
```
Ou simplesmente peça ao Claude ("edita esse vídeo no estilo do escritório") e a skill-mãe conduz tudo.

## Requisitos
Python 3.10+, ffmpeg, `numpy`, `pillow`, `onnxruntime` (recorte RVM), `rembg` (reserva), `opencv-python-headless` (visão), `faster-whisper` (transcrição; opcional com `--srt`). **Node 22+** para os motion graphics (`npx hyperframes`, baixado sob demanda; sem Node, volta aos gráficos ASS/PNG).

## Limitações conhecidas
- Execução real no CapCut ainda **não testada** (o servidor não acessa o CapCut): o primeiro uso deve ser acompanhado.
- Vídeos de referência do Instagram não puderam ser vistos (exigem login).
- O detector de normas lê a fala ("artigo 49 do CDC"): sempre conferir o cartão.
- Recorte por IA: RVM (vídeo) é bom, mas a geração seguinte (MatAnyone, SAM 2) fica no Hugging Face, bloqueado neste servidor. **Trocar o fundo é remendo**: o padrão profissional é gravar no ambiente certo (`estudos/20`).
