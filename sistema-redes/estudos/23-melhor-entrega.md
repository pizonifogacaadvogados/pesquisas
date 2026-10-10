# 23. A melhor forma de entregar um vídeo editado pelo Claude (Fase 12)

Pedido: "não se limite aos exemplos que dei, pesquise, aprofunde, e veja qual melhor forma de me entregar um vídeo editado".
Base: R16 (ecossistema, 90 entradas), R17 (blocos open-source testados em CPU), R18 (ofício de retenção e entrega, 69 entradas),
mais os testes deste repositório (R08.39-R08.42) e o diário (`memoria/DIARIO.md`).

## 1. Como a pesquisa foi feita (método)
- Três frentes paralelas, cada uma com um agente pesquisador: (a) **ecossistema** — quem edita com Claude/Codex/agentes e com
  que ferramenta; (b) **blocos técnicos** — o que roda em CPU, sem nuvem, e melhora som/imagem/transcrição, testado de verdade
  neste servidor; (c) **ofício** — o que editores de retenção fazem, com dados das plataformas, e o que uma agência entrega.
- Cada busca, leitura e teste virou uma linha de registro (consulta exata, fontes, achado, confiabilidade A-D), inclusive as falhas.
- Limite do ambiente: o proxy bloqueou quase todo WebFetch (403/DNS); funcionaram buscas, GitHub raw/releases, PyPI e npm. Por
  isso muitos achados vêm de resumos de busca (marcados B/C) e estrelas do GitHub são aproximadas.

## 2. O que descobrimos (as 8 conclusões)
1. **A arquitetura certa já é a nossa.** O padrão de 2026 é "corte pela transcrição palavra a palavra → lista de cortes (EDL) →
   ffmpeg → motion em HTML (HyperFrames/Remotion)". É o que video-use, claude-shorts, as skills oficiais do HyperFrames e os
   criadores (inclusive o BR "Rafa Voz") fazem. O "Claude editor" dos anúncios é isso: não existe mágica escondida.
2. **Ninguém "assiste" o vídeo.** Os agentes leem a transcrição e olham quadros só nos pontos de decisão. O que separa o bom do
   ruim são **regras duras de correção** (fade de 30 ms, nunca cortar dentro de palavra, retomadas, legenda por último) e
   **autoavaliação do render** — medida por código, não pela palavra do modelo (R16.83: o modelo "acha" que acertou e erra contas).
3. **Editores gráficos com MCP (DaVinci, Premiere, After Effects, CapCut) não servem para editar sozinho aqui**: exigem o programa
   aberto, licença e Windows/Mac. Servem como **saída** para um humano refinar (rascunho CapCut por pyCapCut; XML por auto-editor).
4. **SaaS (Opus Clip, Submagic, Captions, Klap, Descript, ElevenLabs) são proibidos para material de cliente** (sigilo): só benchmark.
5. **Não existe estudo controlado de "corte a cada X s".** Os números de cadência são heurísticas de mercado. Dados sólidos vêm das
   plataformas: TikTok — 63 % dos anúncios de maior CTR põem a mensagem-chave nos 3 primeiros segundos; Meta — legenda dá +12 % de
   tempo assistido; Reels 9:16 com som e pelo menos um elemento extra (pessoa, texto, gancho) tem +56 % de CTR. 45-60 s é a faixa
   de maior engajamento em Reels (base de 31 milhões de posts).
6. **Jurídico e político pedem ritmos diferentes.** Jurídico: planos de 2-5 s, legenda frase a frase, dúvida cotidiana respondida
   "sem juridiquês" (padrão Janaína Bastos, Educa Direito); político: troca visual a cada 1,5-3 s, fala direta, contraste — mas o
   vídeo de maior alcance (Nikolas Ferreira, Pix, 300 mi) era talking head quase puro. **Conteúdo > efeito.**
7. **A barra do Reels cresceu no fim de 2025**: legenda a ≥ 480 px da base, ≤ 32 caracteres por linha, 2 linhas.
8. **Entrega profissional é um pacote, não um arquivo**: prévia para aprovar, versões por rede, `.srt`, capas, variações de gancho,
   texto de publicação, nota de entrega com o que medir e ficha de QC — com versão que só sobe.

## 3. A melhor forma de te entregar um vídeo (o fluxo adotado)
```
gravação (checklist estudo 20)
  → executar <pauta>             análise · plano (retomadas e vícios fora) · produção v3 · efeitos da pauta
  → QC automático (qc.py)        som (−14 LUFS, pico ≤ −1), pretos, congelados, rosto visível, rosto sob a interface,
                                 ritmo (mudança de plano a cada X s, maior trecho parado) + folha de quadros
  → revisão do Claude            olha a folha de quadros e o QC; corrige; repete
  → exportação por rede          13 destinos de vídeo, bitrate pelo limite de cada rede
  → pacote PUBLICAR.md           arquivo certo + texto + horário + conformidade OAB/TSE/LGPD
  → entrega/vNN                  prévia 720p com marca d'água "NÃO PUBLICAR", legendas.srt, QC.md, folha de quadros,
                                 ENTREGA.md (como aprovar em 2 rodadas, como publicar, o que medir em 24-48 h)
  → você aprova no celular (com e sem som) → publica → `metricas` → o sistema aprende
```
**O que medir em 24-48 h:** taxa de pulo (< 35 % bom, > 50 % alarme → publicar a variação B de gancho), retenção média
(> 50 % bom), envios e salvamentos, comentários com dúvida (viram pautas).

## 4. O que foi implementado nesta fase
| Achado | Implementação | Arquivo |
|---|---|---|
| Autoavaliação por código (R16 #1, R18 checklist de QC) | QC automático no `executar` e comando `qc` | `redes/video/qc.py` |
| Pacote de entrega (R18 §c) | entrega versionada: prévia com marca d'água, `.srt` (≤ 32 car.), QC, nota de entrega | `redes/gestao/entrega.py` |
| Retomadas (R16: video-use, cut-video) | frase que recomeça igual a uma das 3 seguintes é cortada (fica a última tomada) | `redes/video/momentos.py`, `plano.py` |
| Rubrica de cortes (claude-shorts) | gancho 0,30 · sentido sozinho 0,25 · conteúdo 0,35 · fecho 0,10 | `redes/video/cortes.py` |
| Barra do Reels maior (R18) | legenda premium a 500 px da base; linhas ≤ 32 caracteres | `redes/video/graficos.py` |
| Ritmo jurídico × político (R18) | regras na skill `videomaker`; QC avisa > 5 s por mudança e > 10 s parado | skill, `qc.py` |
| Fade nas fronteiras, zoom 1,18-1,30 (R16) | já existiam (20/30 ms; punch 1,22) — conferido | `render.py`, `producao.py` |

## 5. O que ainda falta (e por quê) — ver `ESTADO.md` §3
Vídeo real do usuário; cadeia de limpeza de voz do R17; versão "limpa" sem legenda; 2 capas; WhisperX; mãos no HUD (libegl1);
rascunho CapCut/XML validado no computador do escritório; regras das skills oficiais do HyperFrames; subagente crítico.
