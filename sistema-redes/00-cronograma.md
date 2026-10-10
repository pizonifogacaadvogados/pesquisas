# Cronograma: Videomaker Viral (Claude + CapCut Web)

**Status (09/10/2026):** Fases 1 a 3 concluídas; T1 e T2 concluídos; **T3 (teste real no seu CapCut) pendente**.

**Objetivo final:** um sistema em que você deixa um vídeo bruto à disposição e o Claude:
1. Assiste por meio da transcrição e dos frames.
2. Escolhe os melhores momentos.
3. Monta um plano de edição viral: cortes, zooms, emojis, legendas, efeitos sonoros, transições.
4. Executa esse plano dentro do CapCut Web, no seu Chrome logado.
5. Também consegue renderizar uma versão automática por ffmpeg, para garantir o resultado se o CapCut falhar ou mudar a interface.

## Fase 1: Estudos (base de conhecimento)

| # | Estudo | Pergunta que responde | Entregável |
|---|---|---|---|
| ✅ E1 | Linguagem cinematográfica | O que faz um corte "funcionar"? Ritmo, tipos de corte, enquadramento, som | `estudos/01-cinema.md` |
| ✅ E2 | Anatomia do vídeo viral curto | Como prender nos primeiros 3s e manter a retenção até o fim | `estudos/02-viral.md` |
| ✅ E3 | Estilo de edição "dinâmico" | Zoom punch-in, emojis, legendas palavra a palavra, SFX, B-roll: quando e quanto usar | `estudos/03-estilo-edicao.md` |
| ✅ E4 | CapCut Web: todas as funcionalidades | Onde fica cada ferramenta e como fazer cada edição passo a passo | `estudos/04-capcut-web.md` |
| ✅ E5 | Nichos: advocacia e política | Formatos que viralizam, ganchos, tom, e os limites legais (OAB e TSE) | `estudos/05-nicho-juridico-politico.md` |
| ✅ E6 | Automação do navegador | Como o Claude opera o CapCut Web no Chrome com segurança e o que pode dar errado | `estudos/06-automacao.md` |

## Fase 2: Projeto do sistema

| # | Etapa | Entregável |
|---|---|---|
| ✅ P1 | Arquitetura e formato do "plano de edição" (JSON) | `estudos/06-automacao.md` §3 + formato do plano na skill |
| ✅ P2 | Regras de decisão (quando dar zoom, emoji, SFX, cortar) extraídas dos estudos | `redes/nucleo/regras.py` |

## Fase 3: Desenvolvimento

| # | Módulo | Função |
|---|---|---|
| ✅ D1 | `analise` | Lê o vídeo, transcreve palavra a palavra, detecta silêncios e energia da voz |
| ✅ D2 | `momentos` | Pontua e escolhe os melhores trechos (gancho, clímax, frase de efeito) |
| ✅ D3 | `plano` | Gera o plano de edição completo (EDL) aplicando as regras |
| ✅ D4 | `render` | Renderiza o plano com ffmpeg: cortes, zoom, emojis, legenda animada, SFX |
| ✅ D5 | `capcut` | Converte o plano num roteiro passo a passo para o CapCut Web |
| ✅ D6 | Skill do Claude | Orquestra tudo e opera o CapCut no Chrome (Claude in Chrome) |

## Fase 4: Testes e entrega

| # | Etapa |
|---|---|
| ✅ T1 | Teste ponta a ponta com vídeo sintético (aqui no servidor) |
| ✅ T2 | Guia de uso: como instalar no seu computador e rodar com o seu CapCut |
| ⏳ T3 | Teste real no seu computador, com seu vídeo e seu CapCut (depende de você) |

## Limitações já conhecidas

- **Instagram:** não consegui abrir os dois vídeos de referência porque o Instagram exige login. O estilo foi reconstruído a partir da sua descrição ("aproxima a tela, coloca emoji, várias edições") e da pesquisa. Se você mandar prints ou a legenda, eu calibro.
- **CapCut Web:** não abre a partir deste servidor. A execução no CapCut acontece no seu computador, com a extensão Claude in Chrome.
- **Transcrição:** os modelos de transcrição não baixam neste servidor. No seu computador funcionam.

---

# Fase 5+ (pedido de 09/10/2026): nível profissional, esgotar CapCut Pro, gestor de redes

## Fase 5: Pesquisa aprofundada (registrada em `pesquisa/registro/`)
| # | Estudo | Status |
|---|---|---|
| ✅ E7 | CapCut como editor profissional (camadas, chroma, máscaras, keyframes, LUT) | `estudos/07` |
| ✅ E8 | Produção profissional (cor, tipografia, som, profundidade) | `estudos/08` |
| ✅ E9 | Estilos de produção (autêntico, estúdio, documental, noticiário, cinemático, viral) | `estudos/09` |
| ✅ E10 | **React**: 16 formatos, layouts, técnicas, velocidade, direito autoral, OAB, TSE | `estudos/10` |
| ✅ E11 | Algoritmos e engajamento Instagram/TikTok 2026 | `estudos/11` |
| ✅ E12 | Nichos político-eleitoral e advocacia (aprofundado) | `estudos/12` |
| ✅ E13 | Inventário do CapCut menu a menu | `estudos/13` |
| ✅ E14 | **CapCut Pro esgotado**: cada recurso Pro, modelos/templates, tipos de legenda, efeitos de IA (VFX), aplicabilidade prática | `estudos/14` |
| ✅ E15 | **Áudio e música**: bancos de música, sons em alta, dinâmica (voz × música × original × impacto), automação de volume | `estudos/15` |
| ✅ E16 | **Matriz de decisão**: para cada tipo de vídeo/momento, qual recurso usar (fundo, zoom, emoji, react, transição, música) | `estudos/16` |

## Fase 6: Motor v2 (código)
| # | Módulo | Status |
|---|---|---|
| ✅ | `estilos`, `luts` (LUT .cube p/ render e CapCut), `fundos` (estúdio virtual), `recorte` (IA/chroma), `graficos` (legenda premium/forte/viral, aberturas, lower third, cartões, carimbos, light leak) | feito |
| ✅ | `producao` (diretor + render em camadas) | feito e testado |
| ✅ | `visao` – análise quadro a quadro (cenas, rosto, posição, brilho, movimento) para decidir a edição | |
| ✅ | `audio` – design de som (música por energia, ducking, momentos de impacto, áudio original × música) | |
| ✅ | `react` – layouts de react (dividida, PIP, green screen, pausa-e-comenta, carimbos, replay) | |
| ✅ | `aprendizado` – memória de decisões + feedback + métricas → o sistema se aperfeiçoa a cada uso | |
| ✅ | `capcut` v2 – roteiro profissional por camadas (Pro) | |

## Fase 7: Skills
| # | Skill | Papel |
|---|---|---|
| ✅ | `videomaker` (**mãe**) | orquestra: entende o material, escolhe formato/estilo, chama as filhas, revisa, entrega |
| ✅ | `videomaker-analise` | assiste (transcrição + quadros), decide momentos e a edição de cada trecho |
| ✅ | `videomaker-react` | reacts e manifestações sobre vídeos em alta |
| ✅ | `videomaker-audio` | trilha, efeitos, mixagem |
| ✅ | `videomaker-capcut` | operação do CapCut (Web/Desktop/Pro) |
| ✅ | `social-conformidade` | direito autoral, imagem, OAB, TSE, LGPD |
| ✅ | `social-publicacao` | formatos, capa, legenda do post, hashtags, horários, métricas |

## Fase 8 (depois dos vídeos): Gestor de redes – posts e carrosséis

Primeira versão entregue: `estudos/17`, `pesquisa/registro/R10`, `redes/foto/carrossel.py`, skill `social-carrossel`. Próximos passos: Canva (quando o conector estiver ativo), mais identidades, tratamento automático de prints.

| # | Etapa |
|---|---|
| ✅ G1 | Pesquisa: carrosséis que mais engajam (texto, design, estrutura), formatos aceitos (Instagram/TikTok/LinkedIn), tratamento de imagem e prints |
| ✅ G2 | Pesquisa: design minimalista profissional para advocacia e política (tipografia, grid, paleta, padrão visual) |
| ✅ G3 | Ferramentas: Canva (conector/MCP), geração por código (HTML/Pillow → PNG), fluxo pelo Cowork |
| ✅ G4 | Skill-filha `social-carrossel` (+ `social-imagem`) e templates do escritório |
| ✅ G5 | Estratégia de mix: carrossel × vídeo, calendário editorial |

---

# Fase 9 (pedido de 09/10/2026): padrão de cinema, benchmark profissional

**Diagnóstico honesto da versão 2:** o resultado ainda é amador. Causas: (1) material de teste ruim (amostra 768×432, parede branca, luz chapada), (2) recorte por um modelo feito para fotos (sem coerência temporal), (3) composição sem "colagem" de luz e cor entre pessoa e fundo, (4) gráficos estáticos em vez de motion design. **Meta:** toda decisão com as lentes de um editor profissional de cinema; o CapCut é uma das ferramentas, não o teto.

| # | Etapa | Entregável | Status |
|---|---|---|---|
| B1 | **Levantamento de referências**: os vídeos e carrosséis tecnicamente mais bem produzidos (YouTube, TikTok, Instagram) em: cinematográfico geral, política (BR e internacional), advocacia; carrosséis minimalistas e ricos em elementos | `estudos/18-referencias.md` + registro R11 | ✅ |
| B1b | **Criadores que editam com IA / Claude Code** (Tiago Lemos @tiagolemosx, HyperFrames, Remotion, skills de motion e recorte) e paralelo "por que o deles é bom e o nosso não" (pedido de 09/10/2026) | `estudos/21-criadores-ia.md` + R11 §C | ✅ |
| B2 | **Decomposição técnica** de cada referência: captação (câmera, lente, luz, cenário), montagem, motion graphics, cor, som, tipografia | `estudos/18` (fichas) | ✅ |
| B3 | **Ferramentas dos profissionais** (Premiere, After Effects, DaVinci Resolve, Blender, Figma…) × **CapCut Pro**: o que dá, o que dá em parte, o que não dá | `estudos/19-ferramentas-pro-x-capcut.md` | ✅ |
| B4 | **Comparativo e gap analysis**: nosso teste × referências, item a item | `estudos/19` §gap | ✅ |
| B5 | **Guia de captação cinematográfica** (o que fazer ANTES de editar: luz, lente, cenário, áudio, enquadramento, celular × câmera) | `estudos/20-captacao.md` | ✅ |
| B6 | **Evolução técnica do motor**: recorte de vídeo profissional (matting temporal), motion graphics de verdade (HTML/GSAP, Remotion/HyperFrames), composição com light wrap e correspondência de cor | código + testes (`recorte.matte_rvm`, `composicao.py`, `motion.py`; R08.31-34) | ✅ 1ª rodada |
| B7 | **Re-teste com material decente** (seu vídeo real ou amostra 1080p+) e comparação lado a lado com as referências | `exemplo/v3` | 🟡 re-render da amostra feito; falta **o seu vídeo real** |

**Limitação:** este servidor não reproduz vídeos do YouTube, TikTok e Instagram (bloqueio de rede). O levantamento usa reportagens, entrevistas, bastidores, cursos e análises escritas sobre como cada peça foi feita. Os links ficam no estudo para você assistir.

---

# Fase 10 (pedido de 09/10/2026): o SISTEMA de redes, de ponta a ponta

Pedido: estruturar todo o código como um sistema de produção de conteúdo com dois braços (vídeo para todas as redes de vídeo; foto/carrossel/posts) e uma camada de gestão para manter redes de advocacia, conteúdo jurídico e política; auditar, corrigir, testar, arquitetar as skills e entregar manual + relatório completo.

| # | Etapa | Entregável | Status |
|---|---|---|---|
| S1 | Auditoria do código existente | bugs corrigidos: `visao` no OpenCV 5 (→ YuNet), `--transcricao` em lista, nome de variável no teste, exportação WhatsApp, capa com legenda queimada | ✅ |
| S2 | Especificações de todas as redes (vídeo e foto) | `R12` (48 buscas) → `redes/nucleo/plataformas.py` (26 destinos) | ✅ |
| S3 | Arquitetura: núcleo, braço de vídeo, braço de foto, gestão | pacote `redes` (perfis, pautas, calendário, exportação multirrede, posts, capas, thumbnails, tratamento, conformidade automática R13, publicação, fluxo, relatório, diagnóstico, CLI) | ✅ |
| S4 | Testes de ponta a ponta | `tests/test_sistema.py` (18 testes, todos passando em 7m42s, incluindo produção de vídeo completa) + `teste_pipeline.py` | ✅ |
| S5 | Skills | `gestor-redes` (mãe) → `social-planejamento`, `videomaker` (+5), `social-foto` (+ carrossel), `social-conformidade`, `social-publicacao` | ✅ |
| S6 | Manual e relatório | `MANUAL.md` + relatório completo (artefato) | ✅ |

# Fase 11 (pedido de 10/10/2026): o Claude como editor

Pedido: analisar imagem a imagem as referências enviadas (Tiago Lemos, André Nunes, castilho.ia, edicaomia, Runway, slayer.vfx), entender o nível de edição e o que dá para fazer com o Claude editando sozinho.

| # | Etapa | Entregável | Status |
|---|---|---|---|
| F11-1 | Motor de efeitos IA | `redes/video/efeitos.py`: título, pergunta, card, lista, camadas 3D, transcrição, HUD com rastreamento YuNet, P&B; cache de render; aviso de conflito com os cartões da produção | ✅ |
| F11-2 | Estudo e registro | `estudos/22-claude-editor.md` + `R15` (análise imagem a imagem, nível de edição, estratégia) | ✅ |
| F11-3 | Reutilização e carrossel editorial | `video/cortes.py` (cortes e variações de gancho), identidades editoriais e 5 tipos novos de slide, regra de conformidade do "comente X que te mando no DM" | ✅ |
| F11-4 | Integração | CLI (`efeitos`, `cortes`, `variacoes`), campo `efeitos` da pauta no `executar`, skill `videomaker-efeitos`, testes, demo `exemplo/v4`, relatório | ✅ |

# Fase 12 (pedido de 10/10/2026): além dos exemplos — a melhor forma de entregar

Pedido: "não se limite aos exemplos que dei, pesquise, aprofunde, e veja qual melhor forma de me entregar um vídeo editado; registre tudo no artefato". Depois: "registre tudo, feito e não feito, para outra sessão continuar".

| # | Etapa | Entregável | Status |
|---|---|---|---|
| F12-1 | Pesquisa ampliada em 3 frentes | R16 ecossistema (90 entradas), R18 ofício/entrega (69), R17 blocos open-source (ver o registro e as pendências) | ✅ (R17 parcial) |
| F12-2 | Integração | `qc` automático, `entrega` versionada, legenda ≥ 480 px e ≤ 32 car., retomadas, rubrica de cortes | ✅ |
| F12-3 | Registro integral | estudo 23, `memoria/DIARIO.md`, `ESTADO.md` (tarefas feitas/pendentes), relatório com estudos, skills, registros e código completos | ✅ |

# Fase 12b-13 (10/10/2026): fazer, medir e mapear o que falta
| # | Etapa | Entregável | Status |
|---|---|---|---|
| F12b | Integrações | limpeza de voz (`voz`), versão limpa, 2 capas, licença de música política, batidas v2 (F 0,99), cache de recorte/voz; suíte completa 26 testes OK | ✅ |
| F13-1 | Vídeos do @tiagolemosx | YouTube bloqueado (R20); ferramenta `referencia` pronta | ⏳ depende de baixar fora |
| F13-2 | Mapa do que falta + cronograma | `estudos/24` (cinema, luz, ambientes, técnicas sênior, Claude × CapCut, 4 semanas) | ✅ |
