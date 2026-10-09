# Manual do Sistema de Redes Sociais
**Pizoni Fogaça Advogados · advocacia, conteúdo jurídico e política · versão 1.0 (10/2026)**

> O sistema produz e organiza conteúdo para as redes; **quem publica é sempre você**. O Claude opera o sistema pelas
> skills (comece pela `gestor-redes`); tudo também pode ser feito pela linha de comando abaixo.

---

## 1. O que o sistema faz
```
                    ┌───────────────────── GESTÃO ─────────────────────┐
  perfis ─► pautas ─► calendário ─► executar ─► conformidade ─► pacote PUBLICAR.md ─► métricas ─► aprendizado
                                     │                                                       ▲
                     ┌───────────────┴───────────────┐                                       │
               BRAÇO DE VÍDEO                   BRAÇO DE FOTO                                │
  análise · plano · produção v3 · react   carrossel · post · stories · capa                  │
  áudio · motion · CapCut · exportação    thumbnail · tratamento · prints                    │
  (11 destinos de vídeo)                  (13 destinos de imagem/documento)        feedback ─┘
```
- **Perfis**: cada conta (escritório, advogado, político, mandato) com identidade, assinatura, redes, frequência, horários, pilares.
- **Pautas**: backlog do tema à publicação (ideia → roteiro → material → produzido → aprovado → publicado → medido).
- **Calendário**: semana por rede e horário (md + json + .ics para Google Agenda), com as regras eleitorais.
- **Braço de vídeo**: transforma a gravação bruta em vídeo profissional (cortes, legenda, recorte de vídeo por IA, estúdio virtual, cor de cinema, motion graphics, som) e exporta para cada rede.
- **Braço de foto**: carrosséis, posts de imagem única, stories, capas de Reels, thumbnails do YouTube, tratamento de fotos.
- **Conformidade**: semáforo automático OAB, TSE (calendário 2026), LGPD e direito autoral em toda peça.
- **Publicação**: legenda por rede (gancho, CTA, assinatura obrigatória, hashtags no limite), arquivos no tamanho certo, passo a passo.
- **Aprendizado**: feedback e métricas reais ajustam o sistema e geram o arquivo de lições.

## 2. Instalação (uma vez)
Requisitos: Python 3.10+, **ffmpeg**, **Google Chrome/Chromium**, **Node.js 22+** (motion graphics; opcional).
```bash
cd sistema-redes
pip install -r requirements.txt
python3 -m redes diagnostico          # mostra o que está ok e o que cada falta desliga
```
Na primeira execução o sistema baixa do GitHub o modelo de recorte RVM (15 MB) e o GSAP (motion). O detector de rosto (YuNet) já vem no repositório.

## 3. Rotina em 5 comandos
```bash
python3 -m redes perfil criar escritorio-pizoni --tipo advocacia      # 1x; depois edite perfis/escritorio-pizoni.json
python3 -m redes pauta criar escritorio-pizoni "Direito de arrependimento" --formato reels \
    --gancho "Você sabia que pode cancelar uma compra online?" --material gravacao.mp4 --srt gravacao.srt \
    --data 2026-10-20 --hora 19:00 --hashtags direitodoconsumidor cdc
python3 -m redes calendario escritorio-pizoni --semanas 2 --saida planejamento/
python3 -m redes executar p0001                                     # peças + pacote
python3 -m redes metricas v0001 --views 12000 --taxa-pulo 0.38 --envios 310   # 48-72 h depois
```
O resultado do `executar` fica em `dados/producao/p0001/pacote/PUBLICAR.md`: arquivos por rede, legendas, horários, semáforo de conformidade, passo a passo e checklist.

## 4. Perfis (`perfis/<id>.json`)
| Campo | Para que serve |
|---|---|
| `tipo` | `advocacia`, `juridico` ou `politico` (muda regras de conformidade, presets e modelos de pauta) |
| `assinatura` | nome, cargo, **registro OAB**, handle → lower third, legenda (assinatura obrigatória) |
| `redes.<rede>.semana` | quantas peças por semana em cada formato (o calendário lê daqui) |
| `horarios` | `seg-sex`, `sab`, `dom` (ou dia específico) |
| `pilares` | temas fixos com pesos (somam 1); a sugestão de pautas equilibra por eles |
| `identidade_foto`, `cores` | identidade visual (juridico_classico, juridico_moderno, politico_sobrio, manifesto) e cores próprias |
| `estilo_video`, `preset_video` | estilo de produção (auto, autentico, estudio, documental, noticiario, cinematico, viral) e ritmo de cortes |
| `foto_autor`, `fundo_foto` | retrato (capas, carrosséis) e **foto real do ambiente** (fundo do estúdio virtual) |
| `cta_permitidos`, `hashtags_base`, `tom` | CTA sem captação, hashtags fixas, tom de voz |
| `candidato`, `cnpj_campanha` | político: assinatura "Propaganda Eleitoral" em conteúdo impulsionado |
`python3 -m redes perfil validar <id>` mostra o que falta.

## 5. Pautas
Formatos: `reels`, `carrossel`, `post`, `stories`, `react`, `video_longo`, `documento`.
Campos úteis (via `pauta editar <id> --campos '{…}'`): `legenda_corpo`, `hashtags`, `titulo_capa`, `thumb_texto`, `titulo_abertura`,
`estilo`, `dur` ("25-60"), `destinos` (lista para forçar redes), `spec` (carrossel/post), `react` ({original, reacao, roteiro, credito}),
`usa_ia`, `impulsionar`, `musica`, `musica_licenca`, `terceiro`, `credito`.
`pauta sugerir <perfil>` devolve esqueletos de pauta por nicho (ex.: "Mito ou verdade: …", "O que muda com …", "A proposta para …, explicada em 1 minuto").

## 6. Calendário
Regras: vídeo-âncora no horário nobre e repetido nas redes irmãs (TikTok +1 h, Shorts +2 h, Kwai +2,5 h, Facebook +3 h); carrossel do mesmo tema 2 dias depois; stories diários de manhã; LinkedIn em dias úteis às 8h30; **perfil político sem publicações nos dias de eleição**. Importe o `.ics` no Google Agenda.

## 7. Braço de vídeo
| Comando | O que faz |
|---|---|
| `produzir VIDEO --preset juridico --estilo auto --nome … --cargo … [--srt] [--fundo-foto] [--biblioteca-musica]` | pipeline completo v3: análise → cortes → base 9:16 → produção → roteiro CapCut |
| `rerender saida/producao.json` | refaz depois de editar as decisões (textos, cartões, câmera, trilha) |
| `react ORIGINAL REACAO react.json` | react (dividida, PIP, green screen, tela cheia) com crédito e proporção de comentário |
| `exportar final.mp4 --perfil <id>` | um arquivo por rede (tamanho, duração, bitrate, −14 LUFS) |
| `capa final.mp4 "Título"` / `thumbnail video.mp4 "Até 5 palavras"` | capa de Reels e thumbnail do YouTube |
| `visao VIDEO` | diagnóstico visual (rosto, luz, fundo, movimento, **qualidade da captação**) |
| `analisar`, `planejar`, `renderizar`, `tudo`, `capcut` | etapas avulsas e motor v1 (corte rápido + roteiro CapCut) |
Motor v3: recorte de vídeo **RVM** (modelo temporal) com **light wrap** e **cor casada** entre pessoa e fundo; **motion graphics HyperFrames + GSAP** (lower third, cartões de norma, chamada); 6 estilos com LUT; legendas premium/forte/viral; câmera virtual com easing; desenho de som e automação de trilha.
**A maior alavanca de qualidade é a gravação**: veja `estudos/20-captacao.md` (checklist de 1 minuto).

### Destinos de vídeo
`instagram_reels` · `instagram_stories` · `facebook_reels` · `facebook_feed_video` (4:5) · `tiktok_video` · `youtube_shorts` · `youtube_video` (16:9) · `kwai_video` · `linkedin_video` (4:5) · `x_video` (16:9) · `threads_video` · `pinterest_video` · `whatsapp_status` (720p, trechos de 60 s). Lista completa com limites: `python3 -m redes destinos`.

## 8. Braço de foto
| Comando | O que faz |
|---|---|
| `carrossel spec.json --formato 4x5 9x16` | carrossel (10 tipos de slide, 4 identidades) + PDF |
| `post post.json --formatos 4x5 9x16 1x1 16x9 --perfil <id>` | post de imagem única: frase, manchete, dado, comunicado, evento, foto, pergunta |
| `foto tratar img.jpg --formatos 4x5 9x16` | enquadra pelo rosto, corrige cor e aplica o look do perfil |
| `foto recortar img.jpg` | pessoa com fundo transparente |
| `foto anonimizar img.png --caixas "x,y,w,h;…" --modo tarja` | oculta dados pessoais (LGPD) |
| `foto print img.png --fonte G1 --data 08/10/2026` | print em moldura com fonte |
Destinos de imagem: `instagram_feed`, `instagram_carrossel`, `instagram_stories_img`, `instagram_capa_reels`, `tiktok_foto`, `facebook_foto`, `linkedin_imagem`, `linkedin_documento` (PDF), `x_imagem`, `threads_imagem`, `pinterest_imagem` (2:3), `whatsapp_status_img`, `youtube_thumbnail`.

## 9. Conformidade
`python3 -m redes checar "texto" --perfil <id> [--data AAAA-MM-DD] [--impulsionar] [--usa-ia]` → 🟢 0 · 🟡 1 · 🔴 2.
Roda sozinha em todo pacote. Cobre: OAB (promessa de resultado, captação/preço, superlativos, especialista, ostentação, caso de cliente); TSE 2026 (pedido de voto antes de 16/08, dia da eleição, impulsionamento após 01/10 e 22/10, IA na janela de 72 h, rótulo de IA, deepfake); LGPD (CPF, CNPJ, processo, telefone, e-mail); autoral (música sem licença, terceiro sem crédito); limites de cada rede. **É a primeira barreira, não a decisão**: a skill `social-conformidade` traz o checklist humano.

## 10. Publicação, métricas e aprendizado
- `legenda <perfil> <destino> "gancho" --corpo "…" --hashtags a b` → texto pronto por rede.
- `metricas <id> --views … --taxa-pulo … --envios … --salvamentos …` e `feedback <id> "texto"` → ajustam o sistema.
- `licoes` e `relatorio --perfil <id>` → o que funcionou (ranking de estilos e ganchos), pautas pendentes, conformidade.

## 11. Estrutura de pastas
```
sistema-redes/
  MANUAL.md · README.md · 00-cronograma.md · requirements.txt
  redes/                      código (python -m redes)
    nucleo/   caminhos · regras · perfis · plataformas · conformidade · rosto · aprendizado · diagnostico
    video/    analise · momentos · plano · render · producao · estilos · luts · fundos · recorte · composicao
              graficos · motion · audio · assets · visao · react · capcut · exportar
    foto/     motor · carrossel · post · capas · tratamento
    gestao/   pautas · calendario · publicacao · fluxo · relatorio
  perfis/     um JSON por conta          dados/      pautas, produção, pacotes (fora do git)
  memoria/    LICOES.md e aprendizado    estudos/    01-21 base de conhecimento
  pesquisa/registro/  R01-R14 todas as pesquisas com fontes      fontes/ modelos/ exemplo/ tests/
```

## 12. Testes
```bash
REDES_RAPIDO=1 python3 -m unittest discover -s tests     # ≈ 2 min (núcleo, foto, exportação, gestão, CLI)
python3 -m unittest discover -s tests                    # + produção de vídeo e react (≈ 6-8 min)
```

## 13. Limites conhecidos
- Não publica nem lê métricas sozinho (as redes não dão acesso a este sistema); você informa os números.
- Recorte por IA: RVM é bom, mas a próxima geração (MatAnyone, SAM 2) depende do Hugging Face; trocar o fundo é remendo — grave no ambiente certo.
- Transcrição local (Whisper) baixa modelos na 1ª vez; sem rede, use `--srt` (legenda exportada do CapCut).
- O Kwai não publica especificações oficiais: valores conservadores (R12).
- A operação do CapCut é guiada (roteiro + skill `videomaker-capcut`); o acabamento automático é feito pelo próprio sistema.
- Regras eleitorais e da OAB mudam: atualize `redes/nucleo/conformidade.py` a cada eleição.
