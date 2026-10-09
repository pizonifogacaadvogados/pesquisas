# Videomaker Viral

Sistema que transforma um **vídeo bruto** num **vídeo curto viral** (Reels/TikTok/Shorts), no estilo dinâmico: legenda palavra a palavra, zoom no rosto, emojis com pop, efeitos sonoros e título de gancho. Funciona de dois jeitos:

1. **Sozinho:** gera o `final.mp4` pronto (ffmpeg).
2. **No seu CapCut Web:** gera um roteiro passo a passo que o Claude executa no seu Chrome logado (extensão Claude in Chrome), para você continuar ajustando no CapCut.

> Veja `exemplo/`: `bruto.mp4` (entrada de teste com voz sintética) → `juridico_final.mp4` e `politico_final.mp4` (saídas), `roteiro_capcut_juridico.md` (roteiro gerado) e `juridico_quadros.png` (quadros dos momentos com efeito).

## Como funciona

```
vídeo bruto
   │  1. ANÁLISE     transcrição palavra a palavra + energia da voz
   ▼
   │  2. MOMENTOS    nota 0-100 por frase (gancho, dado, energia, vícios) → melhor janela de 20-60s
   ▼
   │  3. PLANO       corta silêncios e vícios ("éé", "hã", repetições) · cold open · punch-in a cada corte
   │                 · snap zoom nas palavras-chave · emoji + SFX · zoom lento + riser/hit no clímax
   │                 · título do gancho · legenda em blocos com destaque → plano.json
   ▼
   ├── 4A. RENDER    base.mp4 (só cortes, 9:16) e final.mp4 (completo)
   └── 4B. CAPCUT    roteiro_capcut.md → Claude in Chrome executa no CapCut Web
```

O plano (`plano.json`) é revisado pelo Claude antes da execução. A skill `videomaker-viral` (em `.claude/skills/`) obriga essa revisão editorial: gancho, sentido preservado, adequação dos emojis e alertas OAB/TSE.

## Presets

| Preset | Para | Estilo |
|---|---|---|
| `juridico` | advocacia (padrão do escritório) | sóbrio: zoom suave, poucos emojis neutros, sem 💰/🏆, alertas do Provimento 205/2021 |
| `politico` | política / opinião | intenso: CAIXA ALTA, destaque vermelho, snap zoom forte, riser/hit, alertas TSE |
| `dinamico` | viral máximo | estilo Hormozi: cortes a cada pausa, emojis frequentes, todos os SFX |

As regras (intensidade de zoom, intervalo entre emojis, cores, dicionário palavra → emoji) ficam em `videomaker/regras.py` e podem ser ajustadas.

## Instalação (no seu computador)

1. **Python 3.10+** e **ffmpeg**
   - Windows: `winget install Python.Python.3.12 Gyan.FFmpeg`
   - Mac: `brew install python ffmpeg`
2. Dependências:
   ```bash
   cd videomaker-viral
   pip install -r requirements.txt
   ```
   O `faster-whisper` baixa o modelo de transcrição (~500 MB) na primeira execução.
3. Para o modo CapCut: **Claude Code** + extensão **Claude in Chrome**, com o Chrome logado no CapCut Web.

## Uso

### Pedindo ao Claude (recomendado)
No Claude Code, dentro deste repositório:
> "Edita o vídeo `C:/videos/gravacao.mp4` no estilo jurídico, 30-45s, e depois executa no meu CapCut."

O Claude usa a skill `videomaker-viral`: roda o motor, revisa o plano, mostra o resultado e, se você pedir, opera o CapCut.

### Pela linha de comando
```bash
python -m videomaker tudo gravacao.mp4 --preset juridico --dur 30-45 --saida saida/video1
python -m videomaker tudo gravacao.mp4 --preset politico --srt legenda_do_capcut.srt   # sem transcrição local
python -m videomaker tudo gravacao.mp4 --musica trilha.mp3 --sfx-dir meus_sons/          # trilha e sons próprios

# etapas separadas
python -m videomaker analisar gravacao.mp4 --saida saida/video1
python -m videomaker planejar saida/video1/analise.json --preset dinamico --dur 20-30
python -m videomaker renderizar saida/video1/plano.json
python -m videomaker capcut saida/video1/plano.json --modo bruto
```

### No CapCut Web
1. Rode o pipeline e suba o **`base.mp4`** na Mídia do CapCut. Se quiser os mesmos sons e emojis, suba também a pasta `assets/`.
2. Peça ao Claude: *"executa o roteiro `saida/video1/roteiro_capcut.md` no meu CapCut"*.
3. O Claude segue as etapas R0 a R12 com verificação por print, exporta em 1080p e **para antes de publicar**.

### Teste
```bash
python tests/teste_pipeline.py      # gera vídeo sintético e valida os 3 presets
```

## Estrutura

```
videomaker-viral/
  00-cronograma.md        plano de estudos e desenvolvimento
  estudos/                base de conhecimento (cinema, viral, estilo, CapCut, nichos, automação)
  videomaker/
    analise.py            D1 transcrição (Whisper ou SRT) + energia da voz
    momentos.py           D2 pontuação de frases e escolha da janela
    plano.py              D3 plano de edição (cortes, zooms, emojis, SFX, legendas)
    render.py             D4 render ffmpeg (base.mp4 e final.mp4)
    capcut.py             D5 roteiro para o CapCut Web
    assets.py             emojis PNG e efeitos sonoros sintetizados
    regras.py             presets e regras editoriais
  tests/teste_pipeline.py
  exemplo/                saídas de exemplo
../.claude/skills/videomaker-viral/SKILL.md   D6 instruções do "videomaker" para o Claude
```

## Limitações conhecidas

- **Vídeos de referência do Instagram:** não foi possível abri-los (o Instagram exige login). O estilo foi reconstruído a partir da sua descrição e da pesquisa. Prints ou a legenda dos posts permitem calibrar.
- **CapCut Web:** não foi possível testar a execução real no CapCut a partir do servidor (sem acesso ao site). O roteiro funciona por intenção e com verificação visual, mas o **primeiro uso real deve ser acompanhado**.
- **Enquadramento:** assume o rosto no centro do quadro. Para outros casos, use `--enquadramento desfoque` ou ajuste no CapCut.
- **Emojis no CapCut:** o roteiro pede o sticker equivalente. Para garantir o mesmo visual, suba os PNG de `assets/emojis/`.
- **Efeitos sonoros:** os sintetizados são funcionais, mas simples. Para qualidade profissional, use `--sfx-dir` com sons de banco licenciado ou os sons do próprio CapCut.
- **O Claude não vê expressão facial nem estética com segurança:** sempre assista ao vídeo antes de publicar.
