# Cronograma: Videomaker Viral (Claude + CapCut Web)

**Objetivo final:** um sistema em que você deixa um vídeo bruto à disposição e o Claude:
1. Assiste por meio da transcrição e dos frames.
2. Escolhe os melhores momentos.
3. Monta um plano de edição viral: cortes, zooms, emojis, legendas, efeitos sonoros, transições.
4. Executa esse plano dentro do CapCut Web, no seu Chrome logado.
5. Também consegue renderizar uma versão automática por ffmpeg, para garantir o resultado se o CapCut falhar ou mudar a interface.

## Fase 1: Estudos (base de conhecimento)

| # | Estudo | Pergunta que responde | Entregável |
|---|---|---|---|
| E1 | Linguagem cinematográfica | O que faz um corte "funcionar"? Ritmo, tipos de corte, enquadramento, som | `estudos/01-cinema.md` |
| E2 | Anatomia do vídeo viral curto | Como prender nos primeiros 3s e manter a retenção até o fim | `estudos/02-viral.md` |
| E3 | Estilo de edição "dinâmico" | Zoom punch-in, emojis, legendas palavra a palavra, SFX, B-roll: quando e quanto usar | `estudos/03-estilo-edicao.md` |
| E4 | CapCut Web: todas as funcionalidades | Onde fica cada ferramenta e como fazer cada edição passo a passo | `estudos/04-capcut-web.md` |
| E5 | Nichos: advocacia e política | Formatos que viralizam, ganchos, tom, e os limites legais (OAB e TSE) | `estudos/05-nicho-juridico-politico.md` |
| E6 | Automação do navegador | Como o Claude opera o CapCut Web no Chrome com segurança e o que pode dar errado | `estudos/06-automacao.md` |

## Fase 2: Projeto do sistema

| # | Etapa | Entregável |
|---|---|---|
| P1 | Arquitetura e formato do "plano de edição" (JSON) | `docs/arquitetura.md` + `schema` |
| P2 | Regras de decisão (quando dar zoom, emoji, SFX, cortar) extraídas dos estudos | `videomaker/regras.py` |

## Fase 3: Desenvolvimento

| # | Módulo | Função |
|---|---|---|
| D1 | `analise` | Lê o vídeo, transcreve palavra a palavra, detecta silêncios e energia da voz |
| D2 | `momentos` | Pontua e escolhe os melhores trechos (gancho, clímax, frase de efeito) |
| D3 | `plano` | Gera o plano de edição completo (EDL) aplicando as regras |
| D4 | `render` | Renderiza o plano com ffmpeg: cortes, zoom, emojis, legenda animada, SFX |
| D5 | `capcut` | Converte o plano num roteiro passo a passo para o CapCut Web |
| D6 | Skill do Claude | Orquestra tudo e opera o CapCut no Chrome (Claude in Chrome) |

## Fase 4: Testes e entrega

| # | Etapa |
|---|---|
| T1 | Teste ponta a ponta com vídeo sintético (aqui no servidor) |
| T2 | Guia de uso: como instalar no seu computador e rodar com o seu CapCut |
| T3 | Teste real no seu computador, com seu vídeo e seu CapCut (depende de você) |

## Limitações já conhecidas

- **Instagram:** não consegui abrir os dois vídeos de referência porque o Instagram exige login. O estilo foi reconstruído a partir da sua descrição ("aproxima a tela, coloca emoji, várias edições") e da pesquisa. Se você mandar prints ou a legenda, eu calibro.
- **CapCut Web:** não abre a partir deste servidor. A execução no CapCut acontece no seu computador, com a extensão Claude in Chrome.
- **Transcrição:** os modelos de transcrição não baixam neste servidor. No seu computador funcionam.
