# 21. Quem edita com IA e Claude Code: paralelo com o nosso motor (Fase 9, B1b)

Pedido de 09/10/2026: estudar profissionais que usam Claude Code e IA para editar vídeo e produzir para redes, a partir de **Tiago Lemos (@tiagolemosx)**, e responder: *por que o deles está bom e o nosso não? o que evoluir?* Registro: `pesquisa/registro/R11-referencias-fase9.md` §C.

## 1. Mapa de quem faz e como
| Quem / o quê | Onde | Rota técnica | Ponto forte |
|---|---|---|---|
| **Tiago Lemos** (BR) | [Instagram](https://www.instagram.com/tiagolemosx/), [YouTube](https://www.youtube.com/@tiagolemosx), [TikTok](https://www.tiktok.com/@tiagolemosx); vídeos-chave: ["Como Editar Vídeos com IA no Claude AI (Sem Saber Editar)"](https://www.youtube.com/watch?v=a4YBW-pit3g), ["CLAUDE OPUS 5.5 = VÍDEOS DE R$100K"](https://www.youtube.com/watch?v=61u9wOT-Cds) | Sobe o **próprio material gravado** e pede ao Claude a edição; compara IAs de vídeo generativo (Runway, Hailuo, PixVerse, Midjourney) | **Ele grava bem** (rosto iluminado, enquadramento de criador), ritmo de Reels, ganchos fortes, e **mostra o processo** (o que vende é o "como") |
| **Danilo Gato** (@odanilogato), **@paulo.ia** (BR) | Instagram | IA para negócios e para vídeo e criatividade | Volume e didática |
| **HyperFrames** (HeyGen, aberto) | [GitHub](https://github.com/heygen-com/hyperframes), [conector no Claude](https://claude.com/connectors/hyperframes-heygen) | Claude escreve **HTML + GSAP**; o CLI renderiza quadro a quadro em MP4/MOV com alfa. Workflows prontos: `/talking-head-recut` (fala + títulos, lower thirds, dados), `/embedded-captions`, `/motion-graphics` | Motion de nível After Effects **por código**, com regras de animação embutidas (easing, máscara, stagger, seek-safe) |
| **Remotion** + plugin oficial do Claude Code | [remotion.dev](https://remotion.dev/docs/ai/claude-code-plugin) | React → vídeo | Ecossistema grande; **licença paga** para empresa com 4+ pessoas; tende a "apresentação animada" |
| **Barty-Bart/motion-graphics** | [GitHub](https://github.com/Barty-Bart/motion-graphics) | `motion-broll` (formas com **springs** e **motion blur 180°**, overlays ProRes 4444 pela transcrição) + `object-separation` (**SAM 2.1**, cliques no 1º quadro, máscara por quadro) | Recorte de **vídeo** com modelo de segmentação moderno; b-roll animado sincronizado |
| **howseen claude-motion-design** | [GitHub](https://github.com/howseen-ai/claude-motion-design) | HTML + Playwright + ffmpeg; `seek(t)` determinístico; **subquadros = motion blur**; molas; **mapa de batidas** (drop = momento visual); stills aprovados antes do render | Processo de estúdio: **brief → batidas → quadros-chave aprovados → render** |
| **claude-code-video-toolkit** | [GitHub](https://github.com/digitalsamba/claude-code-video-toolkit) | Remotion + ffmpeg + modelos em GPU na nuvem (voz, imagem, vídeo, música) | Kit completo, mas sem recorte |
| Guias de fluxo (MindStudio, japonês, PT) | [MindStudio](https://www.mindstudio.ai/blog/claude-code-video-editing-motion-graphics), [note.com](https://note.com/btl_glhfe/n/n327ef1290d90?hl=en), ["O Claude code agora edita meus vídeos"](https://videohighlight.com/v/tT5ya2HKazo) | Claude orquestra; ffmpeg corta; HyperFrames/Remotion animam; **acabamento final humano** (CapCut/Descript) | Divisão clara de papéis |

## 2. Por que o deles fica bom e o nosso ficou amador (diagnóstico honesto)
| # | Diferença | Eles | Nós (v2) | Peso |
|---|---|---|---|---|
| 1 | **Material de origem** | o criador grava **para** o vídeo: luz no rosto, fundo escolhido, 1080p+ | amostra pública 768×432, parede branca, luz chapada | **altíssimo** |
| 2 | **Não trocam o fundo** (quase nunca) | filmam no cenário certo; o recorte só aparece em efeito pontual (texto atrás) | estúdio virtual **o vídeo inteiro**, com recorte de modelo de foto | alto |
| 3 | **Motion** | HTML/GSAP ou After Effects: easing exponencial, máscara, stagger, movimento secundário | ASS e PNG com fade e subida linear | alto |
| 4 | **Recorte** (quando usam) | SAM 2/MatAnyone, modelos **de vídeo**, ou chroma bem iluminado | rembg (foto), quadro a quadro: halo e tremor | médio-alto |
| 5 | **Processo** | quadros-chave aprovados **antes** do render final; iteram 3-5 vezes | render direto e revisão depois | médio |
| 6 | **Humano no acabamento** | o criador ajusta no CapCut/Descript | 100% automático | médio |
| 7 | **Sem fingir** | mostram o processo; o "efeito IA" é o conteúdo | queríamos esconder a IA (conteúdo jurídico) | contexto diferente |

**Resumo:** nosso motor "pensa" bem (escolha de momentos, cortes, regras jurídicas e de plataforma, aprendizado), mas **pintava** como amador em três camadas: recorte, fundo e motion. E testamos com material que nenhum profissional aceitaria.

## 3. O que já mudou no motor (v3, esta fase)
| Mudança | Módulo | Efeito medido |
|---|---|---|
| **Recorte de vídeo RVM** (recorrente, com memória temporal) no lugar do rembg | `recorte.matte_rvm`, `matte_auto` | tremor de borda **−37%** (0,093 → 0,059) e fim do halo branco da parede no cabelo (R08/v3) |
| **Casar cor** pessoa × fundo (equilíbrio por canal em luz linear, nível de preto, exposição) | `composicao.casar_cor` | a pessoa deixa de "brilhar" sobre fundo escuro |
| **Light wrap** (luz do fundo abraçando a borda) | `composicao.light_wrap` | borda deixa de parecer recortada a tesoura |
| **Placa de fundo a partir de foto real** (desfoque de lente com bokeh, queda de luz) | `composicao.placa_de_fundo`, `--fundo-foto` | substitui o fundo desenhado quando houver foto do escritório |
| **Motion graphics HyperFrames + GSAP** (lower third com barra e máscara, cartão de norma com stagger e linha que se desenha, chamada de abertura), overlay com alfa | `motion.py` | animação com curvas de After Effects; texto nítido fora do LUT e do grão |

## 4. O que ainda falta (e por quê)
- **Modelos de recorte da geração seguinte** (MatAnyone 2, SAM 2.1, BiRefNet): hospedados no Hugging Face, **bloqueado neste servidor**. No computador do escritório (ou numa sessão com rede liberada) dá para trocar o RVM por eles; a interface `matte_auto` já está pronta para isso.
- **GPU**: RVM em CPU leva ~1,5 min para 12 s de vídeo 768p. Em 1080p, ~4-6 min por 40 s.
- **Processo de "stills aprovados"**: adotar no fluxo da skill (gerar 4 quadros-chave, você aprova, depois render).

## 5. Para você confirmar assistindo (não consegui ver daqui)
Nos vídeos do Tiago Lemos, observe e me diga:
1. Ele usa **Claude Code** (terminal, código, ffmpeg/HyperFrames/Remotion) ou o **Claude no chat** com upload?
2. O acabamento final é feito no Claude ou ele termina no CapCut/Premiere?
3. Legendas: animadas por palavra? fonte? posição?
4. Ele troca o fundo ou grava no cenário?
5. Que "prompt" ou skill ele mostra para a edição?
Com isso, ajusto o motor para reproduzir exatamente o fluxo dele.
