# Estado do projeto e passagem de bastão (10/10/2026)

Documento para **outra sessão continuar de onde paramos**. Leia nesta ordem: este arquivo → `CLAUDE.md` (raiz) →
`MANUAL.md` → `00-cronograma.md` → `memoria/DIARIO.md` → skill `gestor-redes`.

- Repositório: `pizonifogacaadvogados/pesquisas` · branch de trabalho `claude/admiring-allen-ii0fmx` (sem PR aberto; não abrir sem pedido).
- Relatório completo publicado (artefato privado): https://claude.ai/artifact/SAEthvVnoriDzMDPwQLXMX — gerado por
  `python3 tools/gerar_relatorio.py --saida RELATORIO.html --imagens <pasta>`; cópia em `RELATORIO.html`.
- Cliente/usuário: escritório Pizoni Fogaça Advogados (advocacia, conteúdo jurídico e campanhas políticas), fala português.

## 1. Regras permanentes (não negociáveis)
1. **Nunca publicar** nas redes em nome do usuário: o sistema entrega o pacote; quem publica é ele.
2. **Nunca enviar material sigiloso de cliente** a serviços externos (CapCut nuvem — ToS de 12/06/2025 dá licença perpétua —, Opus Clip, Submagic, Runway, ElevenLabs, IA de terceiros).
3. **Política:** nada de IA em rosto/voz de pessoa real; rótulo de IA em conteúdo sintético; janela de 72 h antes a 24 h depois de cada turno sem conteúdo sintético novo; dia da eleição é crime postar novo conteúdo; impulsionamento até 01/10 e 22/10 (datas em `redes/nucleo/conformidade.py`). Não organizar "concurso de cortes" pago (caso Marçal, R18).
4. **OAB (Prov. 205/2021):** sem promessa de resultado, preço/captação, superlativo, ostentação, caso concreto de cliente.
5. Rodar `REDES_RAPIDO=1 python3 -m unittest discover -s tests` (≈ 2,5 min) antes de cada commit de código; a suíte completa (sem `REDES_RAPIDO`) leva ≈ 8 min.
6. Toda pesquisa nova vai para `pesquisa/registro/` (tabela ID | Ferramenta | Consulta | Fontes | Achados | Conf.); todo aprendizado para `memoria/DIARIO.md`.

## 2. Linha do tempo dos pedidos do usuário (resumo fiel)
| Fase | Pedido do usuário | Resultado |
|---|---|---|
| 1-2 | Pesquisar como editar vídeo com o Claude; criar especialista | skill `editor-de-video`, R01, estudos 01-06 |
| 3-5 | Editor viral e cinematográfico para advocacia/política, operando CapCut Pro; registrar toda pesquisa | motor v1, roteiro CapCut, R02-R07, estudos 07-14 |
| 6-8 | Skill-mãe e filhas, react, áudio, carrosséis | videomaker + 6 filhas, react, carrossel, R08-R10 |
| 9 | "Ainda está muito amador… recorte visonho… fundo bem ruim" + estudar criadores com IA (Tiago Lemos @tiagolemosx) e comparar | motor v3 (RVM, cor casada, light wrap, HyperFrames), estudos 18-21, R11 |
| 10 | "Desenvolva de forma contínua… sistema de produção de conteúdo… vídeos e fotos… manual e relatório/artefato" | pacote `redes` completo, 26 destinos, conformidade, gestão, manual, relatório |
| 11 | Capturas de André Nunes, castilho.ia, Tiago Lemos, edicaomia, Runway, slayer.vfx: "talvez a estratégia seja o próprio Claude editar" | estudo 22, R15, motor de efeitos IA, cortes, variações, carrossel editorial, demo v4 |
| 12 | "Não se limite aos exemplos… pesquise, aprofunde… melhor forma de me entregar um vídeo editado… registre tudo no artefato" | R16, R17, R18, QC automático, entrega versionada, tomadas repetidas, estudo 23, relatório integral |
| 12 (fim) | "Registre tudo… tarefas feitas e não feitas… para outra sessão continuar" | este arquivo + relatório |

## 3. Lista de tarefas (feitas e não feitas)
### Feitas (32)
| # | Tarefa | Onde está |
|---|---|---|
| 1 | Estudos de nível profissional (CapCut pro + produção) | `estudos/07-08, 14` |
| 2 | Módulo de estilos (looks) e LUT .cube | `redes/video/estilos.py`, `luts.py` |
| 3 | Recorte de pessoa e fundos (chroma, IA, estúdio virtual) | `recorte.py`, `fundos.py` |
| 4 | Gráficos profissionais e acabamento de filme | `graficos.py` |
| 5 | B-roll, design de som e diretor (plano v2) | `audio.py`, `producao.py` |
| 6 | Roteiro CapCut profissional e skill v2 | `capcut.py`, skill `videomaker-capcut` |
| 7 | Teste com vídeo de pessoa real e revisão visual | `exemplo/v2`, `v3`, R08 |
| 8 | Registro de pesquisa (R01…) | `pesquisa/registro/` |
| 9-11 | Pesquisas: react, algoritmos 2026, nichos político/advocacia | R04-R06, estudos 10-12 |
| 12 | Inventário completo do CapCut | R07, estudo 13 |
| 13 | Skill-mãe e skills-filhas | `.claude/skills/` (14 skills) |
| 14-18 | Fase 9: benchmark, referências, pro × CapCut, captação, motor v3 | estudos 18-21, R11 |
| 19 | Criadores que editam com IA (Tiago Lemos etc.) + paralelo | estudo 21 |
| 20-25 | Fase 10: auditoria, specs das redes (R12), arquitetura, testes, skills, manual + relatório | pacote `redes`, `MANUAL.md` |
| 26 | Motor de efeitos IA (titulo, pergunta, card, hud, camadas, lista, transcricao, pb) | `redes/video/efeitos.py` |
| 27 | Estudo 22 + R15 (análise imagem a imagem) | `estudos/22`, R15 |
| 28 | Carrossel editorial + cortes multi-clipe + variações de gancho | `foto/carrossel.py`, `video/cortes.py` |
| 29 | Integração da Fase 11 (CLI, skills, fluxo, testes, demo v4) | `exemplo/v4` |
| 30 | Pesquisa ampliada R16 (ecossistema, 90 entradas), R17 (blocos de qualidade, 36 entradas, ~20 testes reais) e R18 (ofício/entrega, 69 entradas) | `pesquisa/registro/` |
| 31 | Integração dos achados: QC automático (`qc`), entrega versionada (`entrega`), legenda ≥ 480 px e ≤ 32 caracteres, tomada repetida (fica a última), pesos de cortes | `video/qc.py`, `gestao/entrega.py`, `momentos.py`, `cortes.py` |
| 32 | Estudo 23, diário, este ESTADO, relatório integral (estudos, código, skills, registros) | `estudos/23`, `memoria/DIARIO.md` |

### Não feitas / pendentes (prioridade decrescente)
| P | Pendência | Por que ficou | Como fazer |
|---|---|---|---|
| 1 | **Re-teste com vídeo real do usuário** gravado pelo checklist (estudo 20) | depende do usuário | `python3 -m redes executar <pauta>` com o material; revisar `qc/` e `entrega/v01` |
| ~~2~~ | ✅ **FEITO (Fase 12b): cadeia de voz integrada em `redes/video/voz.py`, na produção e no comando `voz`** — registro original:: DeepFilterNet 3 (binário `deep-filter-0.5.6-x86_64-unknown-linux-musl` da release do GitHub; RTF 0,36; ruído nas pausas −44,6 → −66,4 dBFS sem distorcer) com fallback `arnndn=m=std.rnnn` (rápido, mas distorce: SI-SDR 18,8); depois `highpass=f=80,equalizer=f=250:t=q:w=1.2:g=-2,equalizer=f=3200:t=q:w=1:g=2.5,deesser=i=0.5,acompressor=threshold=-21dB:ratio=3:attack=8:release=120:makeup=3dB:knee=4` + `volume` medido + `alimiter=limit=-2dB` (deu −14,2 LUFS, TP −2,0) | testado, não integrado (créditos) | função `tratar_voz()` em `redes/video/audio.py`; scripts em `pesquisa/testes-r17/` (`cadeia_voz.py`, `metricas.py`) |
| 2b | **Transcrição neste servidor está quebrada**: faster-whisper não baixa modelo (proxy 403) → `analise._whisper` falha aqui; use `--srt`. Alternativa testada: sherpa-onnx (PyPI) com modelos das releases do GitHub — Whisper turbo int8 WER 5,4 % (sem tempo por palavra) + Parakeet v3 int8 (tempo por palavra, erro médio 104 ms) combinados por `difflib` | testado, não integrado | `redes/video/analise.py`: backend sherpa-onnx; scripts `asr_*.py` em `pesquisa/testes-r17/` |
| 2c | ✅ R19 fez: licenças de música (regra na conformidade), nitidez (`unsharp` é o melhor custo: 6,6 s × 5,6 s sem filtro em 41 s; `nlmeans` inviável: 120-568 s), batida (aubio/librosa descartados). ✅ `audio.batidas()` v2 (F 0,67 → 0,99, R08.50). **Pendente:** confirmar batidas com trilhas reais, opção `unsharp` leve na exportação, reenquadramento seguindo o rosto | créditos | `R19` §Síntese |
| ~~3~~ | ✅ FEITO (Fase 12b): **versão limpa** `final_sem_legenda.mp4` no `executar` e na `entrega` (pauta `versao_limpa`, padrão ligado) — registro original: | precisa de render sem a camada ASS | em `producao.py`, flag para pular `subtitles=`; chamar em `entrega.preparar` |
| ~~4~~ | ✅ FEITO (Fase 12b): **duas opções de capa** (`capa_reels.png` e `capa_reels_B.png`, estilos diferentes) — registro original: | não implementado | `capas.capa_reels` com 2 quadros de `melhor_quadro` |
| 5 | **WhisperX / alinhamento fino de palavras** (R16: Whisper erra 100-300 ms) | Hugging Face bloqueado neste servidor | testar no computador do escritório; fallback `--srt` |
| 6 | **Mãos no HUD** (MediaPipe Hands) | falta `libegl1` no sistema | `apt install libegl1` onde houver permissão; modelo já baixa |
| 7 | **Exportar a edição para o CapCut** (pyCapCut gerou rascunho no Linux, R16) e XML Premiere/Resolve (auto-editor) | falta validar abrindo no CapCut do escritório | módulo `capcut_rascunho.py`; validar com o usuário |
| 8 | Regras das skills oficiais do HyperFrames (talking-head-recut, embedded-captions: palavra atrás da pessoa, cards ×1,3 no vertical) e subir para 0.8.145 | tempo | ler R16 §Síntese; aplicar em `efeitos.py`/`motion.py` |
| 9 | Revisor crítico separado (um subagente que assiste os quadros e reprova) antes da entrega | tempo | skill `videomaker` etapa 6: subagente com a folha de quadros + `QC.md` |
| 10 | Perfil real `escritorio-pizoni` (OAB, handles, cores, horários) | depende do usuário | `python3 -m redes perfil criar escritorio-pizoni` |
| 11 | Biblioteca de trilhas/SFX licenciadas do escritório | depende do usuário | pasta + `--biblioteca-musica` |
| 12 | Conector do Canva (falhou por proxy) e agendadores (Meta Business Suite) | ambiente | configurações do claude.ai |
| 14 | **Analisar os vídeos do @tiagolemosx** (incl. `IobZgb7ngz4`) | YouTube bloqueado aqui (R20) | baixar fora (yt-dlp) → `python3 -m redes referencia ref.mp4 --comparar nosso.mp4`; receita em `estudos/24` §1 |
| 15 | **Mapa do que falta + cronograma de 4 semanas** (luz, ambientes, técnicas de editor sênior, Claude × CapCut) | — | `estudos/24-mapa-do-que-falta.md` |
| 13 | Dados de retenção reais (taxa de pulo, curva) para calibrar o ritmo | depende de publicação | `metricas` + `feedback` |

## 4. O que existe (mapa rápido)
- **Pacote `redes`** (`python3 -m redes <comando>`, rode dentro de `sistema-redes/`):
  `nucleo/` caminhos, regras, perfis, plataformas (26 destinos), conformidade (OAB/TSE/LGPD), rosto (YuNet), aprendizado, diagnostico ·
  `video/` voz (limpeza DeepFilterNet/RNNoise), analise, momentos (frases, gancho, **retomadas**), plano, render, producao (motor v3), estilos, luts, fundos, recorte (RVM), composicao,
  graficos, motion (HyperFrames), audio, assets, visao, react, capcut, exportar, **efeitos**, **cortes**, **qc** ·
  `foto/` motor, carrossel (15 tipos, 6 identidades), post, capas, tratamento ·
  `gestao/` pautas, calendario, publicacao, fluxo (`executar`), relatorio, **entrega**.
- **Comandos novos (Fases 11-13):** `efeitos`, `cortes`, `variacoes`, `qc`, `entrega`, `voz`, `referencia`.
- **Fluxo `executar` de vídeo:** análise → plano → produção v3 → efeitos da pauta → **QC** → exportação por rede → capa/thumbnail → conformidade → pacote `PUBLICAR.md` → **entrega/vNN** (prévia 720p com marca d'água, `.srt`, QC, nota com o que medir).
- **Testes:** `tests/test_sistema.py` (26 testes; suíte completa OK em 11m46s em 10/10/2026; 4 pulados no modo rápido).
- **Exemplos:** `exemplo/v3` (motor v3), `exemplo/v4` (demo dos 8 efeitos + carrossel editorial), `exemplo/sistema` (posts, calendário, pacote).
- **Conhecimento:** estudos 01-24, registros R01-R20, `memoria/DIARIO.md` (como cada coisa foi descoberta).

## 5. Limites do ambiente desta sessão (para a próxima não perder tempo)
- Proxy: Hugging Face, YouTube, Instagram, TikTok, jsDelivr (GSAP) e a maioria dos sites via WebFetch bloqueados (403/DNS); funcionam PyPI, npm, GitHub raw/releases, Google Fonts. WebSearch funciona.
- CPU 4 núcleos, sem GPU: `camadas` ≈ 6-10 min por 4 s; demo de 8 efeitos ≈ 6-7 min; `executar` completo ≈ 13 min.
- OpenCV 5 (sem Haar) → YuNet; GSAP servido local por `npm pack`.
- Arquivos de trabalho da sessão ficam no scratchpad (efêmero): o que importa já está em `exemplo/v4`.

## 6. Como retomar (receita)
```bash
cd sistema-redes
python3 -m redes diagnostico                       # dependências
REDES_RAPIDO=1 python3 -m unittest discover -s tests
python3 -m redes qc exemplo/v4/demo_efeitos.mp4    # ver o QC funcionando
# próximo passo de maior valor: pendência P1 (vídeo real) ou P2 (cadeia de áudio do R17)
python3 tools/gerar_relatorio.py --saida RELATORIO.html   # regenerar o relatório ao fim de cada fase
```
