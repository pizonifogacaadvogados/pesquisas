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
| ✅ P2 | Regras de decisão (quando dar zoom, emoji, SFX, cortar) extraídas dos estudos | `videomaker/regras.py` |

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
| ⏳ E14 | **CapCut Pro esgotado**: cada recurso Pro, modelos/templates, tipos de legenda, efeitos de IA (VFX), aplicabilidade prática | `estudos/14` |
| ⏳ E15 | **Áudio e música**: bancos de música, sons em alta, dinâmica (voz × música × original × impacto), automação de volume | `estudos/15` |
| ⏳ E16 | **Matriz de decisão**: para cada tipo de vídeo/momento, qual recurso usar (fundo, zoom, emoji, react, transição, música) | `estudos/16` |

## Fase 6: Motor v2 (código)
| # | Módulo | Status |
|---|---|---|
| ✅ | `estilos`, `luts` (LUT .cube p/ render e CapCut), `fundos` (estúdio virtual), `recorte` (IA/chroma), `graficos` (legenda premium/forte/viral, aberturas, lower third, cartões, carimbos, light leak) | feito |
| ✅ | `producao` (diretor + render em camadas) | feito; em teste |
| ⏳ | `visao` – análise quadro a quadro (cenas, rosto, posição, brilho, movimento) para decidir a edição | |
| ⏳ | `audio` – design de som (música por energia, ducking, momentos de impacto, áudio original × música) | |
| ⏳ | `react` – layouts de react (dividida, PIP, green screen, pausa-e-comenta, carimbos, replay) | |
| ⏳ | `aprendizado` – memória de decisões + feedback + métricas → o sistema se aperfeiçoa a cada uso | |
| ⏳ | `capcut` v2 – roteiro profissional por camadas (Pro) | |

## Fase 7: Skills
| # | Skill | Papel |
|---|---|---|
| ⏳ | `videomaker` (**mãe**) | orquestra: entende o material, escolhe formato/estilo, chama as filhas, revisa, entrega |
| ⏳ | `videomaker-analise` | assiste (transcrição + quadros), decide momentos e a edição de cada trecho |
| ⏳ | `videomaker-react` | reacts e manifestações sobre vídeos em alta |
| ⏳ | `videomaker-audio` | trilha, efeitos, mixagem |
| ⏳ | `videomaker-capcut` | operação do CapCut (Web/Desktop/Pro) |
| ⏳ | `videomaker-conformidade` | direito autoral, imagem, OAB, TSE, LGPD |
| ⏳ | `videomaker-publicacao` | formatos, capa, legenda do post, hashtags, horários, métricas |

## Fase 8 (depois dos vídeos): Gestor de redes – posts e carrosséis
| # | Etapa |
|---|---|
| ⬜ G1 | Pesquisa: carrosséis que mais engajam (texto, design, estrutura), formatos aceitos (Instagram/TikTok/LinkedIn), tratamento de imagem e prints |
| ⬜ G2 | Pesquisa: design minimalista profissional para advocacia e política (tipografia, grid, paleta, padrão visual) |
| ⬜ G3 | Ferramentas: Canva (conector/MCP), geração por código (HTML/Pillow → PNG), fluxo pelo Cowork |
| ⬜ G4 | Skill-filha `social-carrossel` (+ `social-imagem`) e templates do escritório |
| ⬜ G5 | Estratégia de mix: carrossel × vídeo, calendário editorial |
