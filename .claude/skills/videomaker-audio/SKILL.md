---
name: videomaker-audio
description: Skill-filha do videomaker para som - escolha de trilha por clima, licença de música por rede (Meta Sound Collection, TikTok CML, bancos pagos, música por IA), automação de volume (ducking, pausas, stopdown, fade), efeitos sonoros e alternância entre áudio original, voz e música. Use na etapa 5 do videomaker ou quando o usuário perguntar sobre música, áudio ou efeitos.
---

# Áudio

Base: `sistema-redes/estudos/15-audio-musica.md` (camadas, clima por tipo de vídeo, dinâmica, fontes e licenças, paleta de SFX) e `pesquisa/registro/R09` (R09.09-14).

## 1. Clima
O motor sugere (`producao.json` → `humor_trilha`): confiante, sobrio, tensao, investigativo, dramatico, esperanca, urgente, leve. Confirme lendo o texto: a música **muda com a história** (tensa no problema, resolve na solução).

## 2. Licença (decida ANTES de escolher a faixa)
| Destino | Opção segura |
|---|---|
| Só Instagram | publicar sem música e adicionar no app (Meta Sound Collection), **ou** faixa de banco pago embutida |
| Só TikTok | adicionar no app (Commercial Music Library: vale só no TikTok) |
| Várias redes / WhatsApp | faixa de banco pago com licença multiplataforma, ou música por IA (confirmar termos) |
| Evitar | biblioteca do CapCut marcada "comercial: TikTok e CapCut"; músicas em alta em conta comercial; áudio extraído de vídeo de terceiros |

Biblioteca local do escritório: pasta com faixas licenciadas nomeadas `<humor>__titulo.mp3` → `--biblioteca-musica pasta/`.

## 3. Dinâmica (o motor aplica; confira e ajuste em `producao.json` → `camadas.musica.automacao_db`)
- Abertura: música presente (−9 dB) no primeiro segundo e logo abaixo da voz (−21 dB).
- Pausas ≥ 0,45s: sobe ~6 dB (respiro).
- **Stopdown** 0,6s antes do clímax (−60 dB) e volta com força.
- Fim: sobe e faz fade.
- React: original **cheio** quando só ele fala; sob o seu comentário, −15 a −20 dB; **música off** sob o original.
- Transições do vídeo caem nas **batidas** da música (o motor alinha automaticamente).

## 4. Conferir
- Voz clara no **alto-falante do celular**; loudness ≈ −14 LUFS; pico ≤ −1,5 dBTP.
- Nenhum SFX repetido 3 vezes seguidas; o pico do whoosh no corte.
- Feedback do usuário sobre música → `python3 -m redes feedback <id> "música alta"` (o sistema ajusta).

## Limpeza de voz (R17, Fase 12b)
- A produção limpa a voz sozinha (`redes/video/voz.py`): DeepFilterNet 3 (melhor; ~0,4 × tempo real em CPU) → reserva RNNoise → EQ de voz (−2 dB 250 Hz, +2,5 dB 3,2 kHz), de-esser, compressor 3:1; volume final −14 LUFS na mixagem.
- Avulso: `python3 -m redes voz VIDEO [--motor deepfilter|rnnoise|nenhum]`.
- **Sempre na voz bruta.** Em vídeo já mixado com música o compressor levanta a trilha nas pausas (medido: +19 dB de piso). O modo auto não limpa áudio que já está limpo (piso < −60 dBFS).
- Gravação ruim não vira boa: limpeza agressiva gera voz "metálica". Prefira regravar perto do microfone (estudo 20).
