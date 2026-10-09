# R08: Testes técnicos e de ambiente (09/10/2026)

| ID | Teste | Resultado | Implicação |
|---|---|---|---|
| R08.01 | ffmpeg 6.1 disponível | ✅ | render local viável |
| R08.02 | corte + legenda + 9:16 em vídeo sintético | ✅ | base do pipeline |
| R08.03 | remoção de silêncios (silencedetect) | ✅ 15s → 9,6s | `cortar_silencios.py` |
| R08.04 | faster-whisper / openai-whisper (download de modelo) | ❌ Hugging Face e OpenAI bloqueados (403) | transcrição só no computador do usuário; alternativa `--srt` |
| R08.05 | espeak-ng (voz sintética pt-BR) | ✅ via apt | vídeos de teste com fala |
| R08.06 | acesso a capcut.com, instagram.com, tse.jus.br | ❌ bloqueados | execução no CapCut só no computador do usuário; leituras via busca |
| R08.07 | zoom por quadro: `scale=eval=frame` + `crop` | ✅ | zoom animado no render |
| R08.08 | overlay de emoji com escala animada | ✅ | pop de emoji |
| R08.09 | fonte de emoji colorida (Noto Color Emoji) + Pillow | ✅ (apt) | PNG de emoji |
| R08.10 | pipeline completo v1 (3 presets) | ✅ teste automatizado | versão 1 entregue |
| R08.11 | raw.githubusercontent.com | ✅ acessível | fontes do Google Fonts e vídeos de amostra |
| R08.12 | rembg (u2net_human_seg, 176 MB) | ✅ baixou e carregou | recorte de pessoa por IA testável |
| R08.13 | mediapipe 1.1.0 | ⚠️ sem a API legada `solutions` (exige modelo externo) | descartado; usar rembg |
| R08.14 | vídeo de amostra com pessoa real (intel-iot-devkit/sample-videos, 768×432, 12 fps, sem áudio) | ✅ | teste de recorte, estúdio e texto atrás |
| R08.15 | Google Fonts (Inter, Playfair, Bebas, Montserrat, Courier Prime, DM Serif, Oswald, Anton) | ✅ (Libre Baskerville falhou) | tipografia profissional embutida (OFL) |
| R08.16 | LUTs .cube gerados (6 looks) aplicados em quadro real | ✅ cor sutil e profissional | `luts.py` |
| R08.17 | Fundos de estúdio procedurais (5) | ✅ após 2ª iteração (1ª: bokeh exagerado, corrigido) | `fundos.py` |
| R08.18 | Recorte por IA (rembg) em pessoa real, 8s 1080×1920 | ✅ ~53s; borda boa no cabelo | `recorte.py` |
| R08.19 | Render v2 estilo estúdio (texto atrás, cartão, lower third, light leak, LUT, halation, grão) | ✅ 41s; −14,3 LUFS; pico de memória ~1,2 GB | `producao.py` |
| R08.20 | Defeitos visuais encontrados na revisão | light leak sobre o rosto → movido para as bordas; lower third pequeno → aumentado; **"rastro" do matte** (suavização temporal) → suavização assimétrica | correções aplicadas |
| R08.21 | Detecção "artigo quarenta e nove do Código de Defesa do Consumidor" → cartão "Art. 49 · CDC" | ✅ | `producao.referencias_legais` |
| R08.22 | Análise de quadros (OpenCV 5 + Haar) | ✅ 3,8s para 54s; diagnóstico correto (fundo liso → estúdio; plano estático → mais movimento) | `visao.py` |
| R08.23 | OpenCV 5 sem modelos Haar embutidos | ⚠️ baixado do repositório oficial (BSD) para `modelos/` | — |
| R08.24 | Detecção de batidas em trilha de 120 BPM | ✅ batidas a cada ~0,5s | `audio.batidas` |
| R08.25 | React em tela dividida (congelar + círculo, carimbo, replay "DE NOVO", crédito) | ✅ 57s de render; comentário = 61% do tempo; círculo saiu preenchido → corrigido | `react.py` |
| R08.26 | Aprendizado: feedback em linguagem natural → ajustes; métricas → ranking | ✅ "zoom demais / legenda pequena / light leak forte" → 3 ajustes | `aprendizado.py` |
| R08.27 | Reinício do servidor durante o render (exit 137) | ⚠️ não era falta de memória do código (pico 1,2 GB de 16 GB); o render foi refeito | — |
| R08.28 | Recorte com suavização assimétrica + curva de matte | ✅ rastro eliminado (cabeça virando sem "cúpula" de fundo) | `recorte.py` |
| R08.29 | Carrossel HTML→PNG via Chrome headless (9 slides, 2 identidades, 4:5 e 9:16, PDF) | ✅ ~16s; rodapé cortado na 1ª versão → render com folga e recorte | `carrossel.py` |
| R08.30 | Contraste WCAG das identidades | ✅ 14,3:1 (clássico), 19,3:1 (manifesto) | — |
| R08.31 | Recorte RVM (modelo de vídeo, ONNX do GitHub) × rembg (foto), 12 s 768×432 | ✅ tremor médio na borda **0,059 × 0,093 (−37%)**; fim do halo branco da parede no cabelo; ~1m40 para os dois em CPU | `recorte.matte_rvm` |
| R08.32 | Composição v3 (casar cor + light wrap) 1ª versão | ⚠️ borda natural, mas **rosto azulado e enevoado** (ganho por canal batendo no limite de ±15%, wrap largo) → regra de compositor: tinta nas sombras (±8%), pele ±4%, wrap σ 7 e 35% | `composicao.py` |
| R08.33 | HyperFrames 0.8.143 neste servidor | ✅ npm e Chrome headless OK; ❌ CDN do GSAP bloqueado → GSAP local via `npm pack`; overlay 9,5 s 1080×1920 ProRes 4444 com alfa em ~1 min (4 núcleos) | `motion.py` |
| R08.34 | HuggingFace (SAM 2, MatAnyone, BiRefNet) | ❌ bloqueado pelo proxy; RVM é o melhor modelo de vídeo baixável daqui | — |
| R08.35 | v3 completo (RVM + cor casada v2 + light wrap + overlay HyperFrames) na amostra de 41 s | ✅ pele natural, borda sem franja clara, lower third e cartão animados; lower third subido para não encostar na legenda; pico 1,4 GB no ffmpeg (o pico de 6 GB anterior veio do render do overlay) | `exemplo/v3` |
