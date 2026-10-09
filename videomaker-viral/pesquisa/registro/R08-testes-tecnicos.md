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
