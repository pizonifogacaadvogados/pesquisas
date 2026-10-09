# E4: CapCut Web, funcionalidades e como executar cada edição

> **Atenção:** não consegui abrir o CapCut a partir deste servidor, e os rótulos mudam com as versões. O mapa abaixo junta documentação oficial, tutoriais e a interface conhecida do CapCut desktop, que é praticamente igual à web. Por isso o executor trabalha por **intenção**: o Claude lê a tela, encontra o botão equivalente e confirma visualmente cada passo. Os nomes aparecem em PT-BR / EN porque o idioma da interface pode variar.

## 1. Mapa da interface

```
┌─────────────────────────────────────────────────────────────────────┐
│ Topo: nome do projeto · Proporção (Ratio) · Desfazer · [Exportar]   │
├────────────┬─────────────────────────────────┬──────────────────────┤
│ Barra      │                                 │ Painel de            │
│ lateral    │        PRÉ-VISUALIZAÇÃO         │ propriedades         │
│ esquerda:  │        (player 9:16)            │ (do item             │
│ Mídia      │                                 │ selecionado):        │
│ Modelos    │                                 │ Básico, Animação,    │
│ Elementos  │                                 │ Velocidade, Áudio,   │
│ Texto      │                                 │ Ajustar, Ferramentas │
│ Legendas   │                                 │ inteligentes         │
│ Áudio      │                                 │                      │
│ Efeitos    │                                 │                      │
│ Transições │                                 │                      │
│ Filtros    │                                 │                      │
├────────────┴─────────────────────────────────┴──────────────────────┤
│ Barra da timeline: dividir ✂ · excluir · keyframe ◆ · zoom timeline │
│ TIMELINE: [texto/legenda] [sticker] [vídeo principal] [áudio/SFX]   │
└─────────────────────────────────────────────────────────────────────┘
```

| Menu (PT / EN) | Para que o sistema usa |
|---|---|
| **Mídia / Media** | vídeo bruto e assets que você subiu (emojis PNG, SFX, B-roll) |
| **Modelos / Templates** | não usamos (o sistema monta a edição do zero) |
| **Elementos / Elements** (Stickers) | emojis e stickers animados; busca por "emoji", "fire", "warning" |
| **Texto / Text** | título do gancho, listas, referência legal; modelos de texto animado |
| **Legendas / Captions** | **Legendas automáticas (Auto captions)**, idioma Português; estilos com destaque e karaokê |
| **Áudio / Audio** | música e **efeitos sonoros (Sound effects)**: busca por "whoosh", "pop", "swoosh", "hit", "riser", "ding" |
| **Efeitos / Effects** | efeitos de vídeo (zoom blur, shake, flash, glitch) e efeitos de corpo |
| **Transições / Transitions** | entre clipes: "Zoom", "Pull in", "Blur", "Whip", "Flash" |
| **Filtros / Filters** | look de cor |

## 2. Painel de propriedades (clipe de vídeo selecionado)

| Aba | Controles usados |
|---|---|
| **Básico / Basic** | Posição X/Y, **Escala (Scale)**, Rotação, Opacidade, **◆ keyframe** ao lado de cada propriedade |
| **Animação / Animation** | Entrada (In), Saída (Out), Combo; para stickers e textos: "Pop", "Zoom in", "Bounce" |
| **Velocidade / Speed** | normal ou curva |
| **Áudio / Audio** | volume, fade in/out, **Melhorar voz / Enhance voice**, **Redução de ruído / Noise reduction**, normalizar loudness |
| **Ajustar / Adjust** | brilho, contraste, saturação, temperatura, vinheta |
| **Ferramentas inteligentes / Smart tools / AI** | Remover fundo, **Auto reframe** (reenquadrar para 9:16), detecção de silêncio, remoção de vícios (quando existir na versão), aprimorar imagem |

## 3. Receitas passo a passo (o que o executor faz)

### R0. Preparar o projeto
1. Abrir o CapCut Web → **Criar novo / Create new** → vídeo em branco.
2. **Proporção / Ratio → 9:16**.
3. **Mídia** → localizar o vídeo bruto que você subiu → arrastar para a timeline (ou "Adicionar à timeline").
4. Se o vídeo é horizontal: selecionar o clipe → **Auto reframe**, ou Básico → Escala até cobrir o quadro, com o rosto centralizado.

### R1. Cortar (jump cut / remover silêncio)
1. Mover o *playhead* para o tempo exato (clique na régua ou digite no contador de tempo, quando disponível).
2. **Dividir / Split** (ícone de tesoura ou Ctrl+B / Cmd+B; o atalho pode variar).
3. Mover para o fim do trecho → Dividir.
4. Selecionar o pedaço do meio → **Excluir / Delete**.
5. Conferir que a timeline "fechou o buraco" (*ripple*); se não fechou, arrastar o clipe seguinte.

> **Otimização:** se a versão tiver "Remover silêncios / Remove pauses" ou "Remover vícios / Remove filler words" em Ferramentas inteligentes, use primeiro e só depois faça os cortes editoriais.

> **Ordem importa:** execute os cortes **do fim para o começo** do vídeo. Assim os tempos do plano continuam válidos depois de cada exclusão.

### R2. Punch-in (zoom instantâneo no corte)
1. Selecionar o clipe que começa após o corte.
2. Básico → **Escala = 115–125%** (o plano diz o valor).
3. Ajustar Posição Y para manter o rosto no terço superior.

### R3. Snap zoom (zoom rápido animado)
1. Playhead em `t` (início da palavra-chave) → Básico → **◆ keyframe** em Escala (100%).
2. Avançar 0,2s → Escala **140%** (cria keyframe automático).
3. (Opcional) avançar até `t + duração` → Escala 100% para voltar.
4. Adicionar SFX "whoosh" em `t − 0,05s` (R6).

### R4. Zoom lento
1. Keyframe em Escala 100% no início, keyframe em 108% no fim do trecho.

### R5. Emoji / sticker
1. **Elementos / Stickers** → buscar o emoji (ex.: "warning", "money", "fire") ou usar a imagem PNG do emoji em Mídia.
2. Arrastar para a faixa acima do vídeo em `t`.
3. Duração: ajustar a borda direita até `t + 1,2s`.
4. Básico → Escala ~40–60%; posicionar perto da cabeça.
5. **Animação → Entrada → "Pop" / "Zoom in" / "Bounce"** (≈0,3s).
6. SFX "pop" em `t`.

### R6. Efeito sonoro (SFX)
1. **Áudio → Efeitos sonoros** → buscar ("whoosh", "pop", "swoosh", "hit", "riser", "ding").
2. Arrastar para uma faixa de áudio em `t`.
3. Volume do SFX: −6 a −12 dB.

### R7. Legendas dinâmicas
1. **Legendas → Legendas automáticas → Português → Gerar**.
2. Revisar o texto: corrigir nomes, termos jurídicos e números ("art. 49", "CDC").
3. Escolher estilo com **destaque/karaokê** (palavra atual colorida) ou configurar: fonte grossa, branco, contorno preto, destaque amarelo; **Aplicar a todas**.
4. Quebra: 2–4 palavras por bloco (dividir legendas longas).
5. Posição: ~65% da altura.
6. Palavras-chave do plano: selecionar o bloco → cor de destaque e escala maior.

### R8. Título do gancho
1. **Texto → Adicionar texto** em 0s, duração 2,5–3s.
2. Texto do plano, CAIXA ALTA, fonte grossa, topo (~20% da altura).
3. Animação de entrada "Pop" ou "Typewriter".

### R9. Transição entre blocos
1. Ponto entre dois clipes → **Transições** → "Zoom" / "Pull in" / "Blur" → duração 0,2–0,3s.
2. SFX whoosh no ponto.

### R10. Música de fundo
1. **Áudio → Música** → buscar por clima ("tense", "corporate", "inspiring") → faixa abaixo.
2. Volume −20 dB; fade-out de 1s no fim; ducking automático se disponível.

### R11. Áudio da voz e cor
1. Clipe principal → Áudio → **Melhorar voz** + **Redução de ruído**.
2. Ajustar → contraste +8, saturação +5, temperatura +3, vinheta 10 (preset jurídico: só contraste +5).

### R12. Exportar
1. **Exportar / Export** (canto superior direito) → resolução **1080p**, 30 fps, MP4, qualidade alta → **Baixar / Download**.

## 4. Atalhos (confirmar na versão, pois o navegador pode interceptar)

| Ação | Atalho comum |
|---|---|
| Dividir | Ctrl/Cmd + B |
| Excluir | Delete / Backspace |
| Play/Pause | Espaço |
| Desfazer | Ctrl/Cmd + Z |
| Mover playhead 1 frame | ← / → |

## 5. Limites do CapCut Web relevantes

- É mais lento que o desktop; projetos longos travam. **O sistema edita só o trecho selecionado (30–90s), não o bruto inteiro.** O corte inicial do bruto vem pronto do pipeline local, ou é feito primeiro no CapCut.
- Alguns estilos de legenda e efeitos são **Pro** (pagos). O plano marca alternativas grátis.
- A legenda automática erra em sotaque, fala rápida e termos técnicos: revisão obrigatória.

## Fontes

- [CapCut: Add captions with AI](https://www.capcut.com/resource/add-captions-with-ai)
- [CapCut: How to add subtitles (web/mobile/desktop)](https://www.capcut.com/resource/how-to-add-subtitle-in-capcut)
- [CapCut: Caption templates](https://www.capcut.com/resource/caption-template)
- [CapCut: Web editor template guide (export)](https://www.capcut.com/create/capcut-web-editor-template-guide)
- [Riverside: captions in CapCut](https://riverside.com/blog/how-to-add-captions-in-capcut)
- [CapCut cheat sheet (keyframes)](https://litcommerce.com/wp-content/uploads/2026/03/CapCut-ToolCheat-Sheet.pdf)
- [Skillademia: CapCut shortcuts](https://www.skillademia.com/shortcuts/capcut-shortcuts/)
- [AI After 40: CapCut Web vs Desktop 2026](https://www.aiafter40.com/capcut-web-vs-desktop-app-in-2026-which-platform-should-you-use/)
- [BigVu: CapCut Free vs Pro 2026](https://bigvu.tv/blog/capcut-free-vs-pro-what-2026s-restructure-actually-gives-you/)
