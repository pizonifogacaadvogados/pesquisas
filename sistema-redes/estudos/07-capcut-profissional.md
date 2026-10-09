# E7: CapCut no nível profissional, mapa completo de recursos

> Complementa o E4. Este documento trata o CapCut como **editor de produção** (como um Premiere "leve"), não como app de legenda.
> **Plataforma:** desde 2026, o **CapCut Desktop é a versão completa**. O **Web** cobre o essencial (camadas, keyframes, chroma key, remoção de fundo, LUT, legendas), mas pode faltar ou limitar recursos avançados (gráfico de keyframes, curva de velocidade fina, estabilização, Auto Cut). A coluna "Web" abaixo diz o que foi **confirmado** por fonte; "?" significa conferir na tela. Quando faltar no Web, a receita traz alternativa, ou o Claude pode usar o CapCut Desktop via *computer use*.

## 1. Arquitetura de um projeto profissional (camadas)

Edição profissional é **edição em camadas**, não um clipe com efeitos por cima. Ordem de cima para baixo na timeline:

```
V7  Ajuste (adjustment layer): LUT + grão + vinheta, cobrindo o vídeo inteiro
V6  Textura/luz: light leaks, poeira, papel (modo de mesclagem Tela/Screen ou Sobrepor/Overlay)
V5  Gráficos: título, lower third, cartões, setas, destaques
V4  Legendas
V3  Pessoa recortada (cópia do A-roll com Remover fundo): "texto atrás da pessoa"
V2  B-roll / imagens / sobreposições (picture-in-picture)
V1  A-roll: a pessoa falando (vídeo principal)
V0  Fundo: estúdio virtual, cor ou fundo desfocado (quando há recorte ou chroma)
A1  Voz (diálogo)            A2  Ambiência / room tone
A3  Efeitos sonoros (SFX)    A4  Música (com ducking)
```

## 2. Recursos e onde ficam

| Recurso | Para que serve no nível pro | Caminho (PT / EN) | Web | Pro? |
|---|---|---|---|---|
| **Remover fundo (Auto cutout)** | recortar a pessoa sem fundo verde → estúdio virtual, texto atrás, fundo desfocado | clipe → Ferramentas inteligentes / Smart tools → Remover fundo → Remoção automática | ✅ | às vezes |
| **Recorte personalizado** | corrigir o recorte com pincel | Remover fundo → Recorte personalizado (pincel/borracha inteligente) | ? | pincel inteligente: sim |
| **Chroma key** | fundo verde real (melhor qualidade de borda) | Remover fundo → Chroma key → conta-gotas → **Intensidade** e **Sombra** | ✅ | não |
| **Máscaras** (linear, espelho, círculo, retângulo, coração, estrela) com **difusão** (*feather*) | vinheta localizada, revelar/esconder, transição por máscara, dividir tela, recorte manual | clipe → Vídeo → Máscara | ? | não |
| **Modos de mesclagem** (Normal, Tela, Sobrepor, Multiplicar, Clarear, Escurecer, Luz suave...) | light leak (Tela), textura de papel (Multiplicar/Sobrepor), brilho | clipe sobreposto → Básico → Mesclagem | ? | não |
| **Keyframes** (posição, escala, rotação, opacidade, máscara, cor) | todo movimento de câmera virtual e animação de gráfico | ◆ ao lado da propriedade | ✅ | não |
| **Gráfico de keyframes / easing** | movimento suave (entrada e saída lentas): o que separa amador de profissional | selecionar keyframe → curva (Ease in/out, personalizada) | ? (Desktop ✅) | não |
| **Velocidade → Curva** (Montagem, Herói, Bullet, Jump cut, Flash in/out, Personalizada) + **Fluxo óptico** | speed ramp em B-roll, câmera lenta suave | clipe → Velocidade → Curva | ? | fluxo óptico: às vezes |
| **Congelar quadro** | apresentar pessoa/nome, pausa dramática | clipe → botão Congelar | ✅ | não |
| **Rastreamento de movimento / câmera** | texto ou emoji que segue a pessoa; reenquadrar seguindo o rosto | clipe → Rastreamento / Camera tracking | ? | sim |
| **Estabilizar** | tremedeira de câmera na mão | clipe → Estabilizar | ? (Desktop ✅) | não |
| **Auto reframe** | horizontal → vertical seguindo o assunto | Ferramentas inteligentes → Auto reframe | ? | às vezes |
| **Ajustar**: Básico (exposição, contraste, realces, sombras, branco, preto, temperatura, matiz, saturação, nitidez, vinheta), **HSL**, **Curvas**, **Rodas de cor** | correção e gradação | clipe ou camada de ajuste → Ajustar | ✅ básico; ? HSL/curvas | não |
| **LUT** (.cube/.3dl) com intensidade | look de cinema consistente | Ajustar → LUT → Importar | ✅ (online confirma .CUBE/.3DL) | não |
| **Camada de ajuste** | aplicar grade/efeito no vídeo inteiro de uma vez | Ajustar → Adicionar camada de ajuste (ou Efeito como faixa) | ? | não |
| **Relight (IA)** | luz de estúdio sobre o rosto, recuperar rosto escuro | Ferramentas inteligentes → Relight | ? | sim |
| **Retoque** | pele, olheiras, brilho | Retoque / Retouch | ✅ | parcial |
| **Color match** | igualar cor de clipes diferentes | Ajustar → Color match | ? | sim |
| **Efeitos de vídeo** (Lente, Desfoque, Retrô, Luz, Distorção, Partículas) | grão de filme, vazamento de luz, flash, tremor de câmera, zoom com desfoque | Efeitos → Efeitos de vídeo | ✅ | parcial |
| **Transições** (Zoom, Puxar/Pull in, Desfoque, Deslizar, Glitch, Flash, Mistura) | troca entre blocos de ideia | Transições | ✅ | parcial |
| **Texto**: modelos, animação (entrada/saída/loop), curvar, contorno, sombra, fundo, espaçamento | tipografia profissional | Texto | ✅ | modelos: parcial |
| **Legendas automáticas** + estilos (destaque/karaokê) | legenda | Legendas | ✅ | estilos: parcial |
| **Áudio**: Melhorar voz, Redução de ruído, Isolar voz, Normalizar volume, Fade, Detecção de batida, Ducking | som profissional | clipe de áudio → Áudio | parcial | parcial |
| **Sobreposição / PIP** | B-roll em quadro, tela dividida, comentário sobre notícia | arrastar para faixa acima | ✅ | não |
| **Fundo do quadro (Canvas)**: cor, imagem, desfoque | preencher laterais de vídeo horizontal | Proporção → Fundo | ✅ | não |
| **Importar mídia com transparência (PNG)** | lower third, molduras, texturas, emojis | Mídia → Importar | ✅ | não |

Fontes: veja o fim do documento. Planos e créditos de IA mudaram em 2025-2026 (Standard US$ 9,99, Pro US$ 19,99, cerca de 1.200 créditos de IA/mês no Pro). Os recursos de IA consomem créditos.

## 3. Técnicas profissionais passo a passo

### T1. Estúdio virtual (sem fundo verde)
1. V1: vídeo da pessoa → **Remover fundo → Automático**. Conferir a borda do cabelo; se falhar, use Recorte personalizado.
2. V0 (abaixo): fundo do estúdio (imagem gerada pelo sistema ou foto de biblioteca/escritório).
3. Fundo: **Ajustar → desfoque 15-25%** (profundidade de campo), exposição −0,3, levemente mais frio que a pessoa (separação).
4. Pessoa: **Relight** suave ou Ajustar → realces −10, sombras +8; leve "luz de recorte" (efeito Glow/Brilho bem baixo).
5. Escala da pessoa entre 95 e 110%, ombros na base do quadro, olhos no terço superior.
6. Camada de ajuste com LUT por cima de tudo, para "colar" pessoa e fundo na mesma cor. **Este é o passo que faz parecer real.**

### T2. Chroma key de qualidade
- Na gravação: fundo verde liso e bem iluminado, pessoa a 1,5-2 m dele, sem roupa verde.
- No CapCut: Chroma key → conta-gotas no verde **perto do cabelo** → Intensidade até sumir o verde (~20-40) → Sombra (~10-30) até tirar o halo. Exagerar corta detalhes.
- Depois: o mesmo acabamento do T1 (fundo desfocado + LUT).

### T3. Texto atrás da pessoa (efeito de capa de revista)
1. V1: vídeo original. V3: **cópia** do mesmo clipe, exatamente alinhada → Remover fundo (só a pessoa).
2. V2 (entre os dois): texto grande (60-80% da largura), fonte display grossa ou serifada elegante, posicionado atrás da cabeça.
3. Animação do texto: entrada com subida e desfoque ou escala 90→100% com easing; duração 2-3s no gancho.
4. Resultado: o texto parece estar "no cenário", atrás da pessoa.

### T4. Movimento de câmera virtual (o "aproxima a tela" profissional)
- **Push-in lento:** escala 100→106-110% ao longo de uma frase inteira (4-8s), com **ease in/out**. É o movimento mais "cinema" que existe.
- **Punch-in no corte:** 100% ↔ 112-118% (corte seco, sem animação), alternando a cada corte.
- **Snap zoom:** 0,2-0,3s até 125-135% com easing de saída, só em 1-2 momentos do vídeo inteiro.
- **Deriva (drift):** posição X ±1-2% lenta para dar vida a planos parados.
- Sempre ancorar no rosto (ponto de interesse), nunca no centro geométrico.

### T5. B-roll profissional
- Corte J/L: o B-roll entra **com a voz continuando** (L-cut); nunca corta a fala.
- **Ken Burns** em fotos: escala 100→112% + deslocamento leve, com easing, 2-4s.
- Speed ramp em vídeo de ação: curva Montagem/Herói, ou personalizada (100% → 30% → 100%).
- Mesma LUT do A-roll (camada de ajuste por cima).
- Ritmo: B-roll de 1,5-3s; 1 a cada 8-15s; casar o corte com uma batida da música.

### T6. Lower third (identificação)
- Nome + qualificação ("Dra. Fulana · Advogada · OAB/RS 00.000").
- Entrada: linha que se desenha (máscara linear animada) + texto que sobe 20px com fade (easing), 0,4-0,6s; fica 3-4s; sai em 0,3s.
- Posição: terço inferior, alinhado à esquerda, a 8% da margem; fora da zona das legendas.

### T7. Gradação de cor (o "look")
1. **Correção** (por clipe): exposição, balanço de branco, contraste neutro. Pele no tom natural.
2. **Look** (camada de ajuste): LUT a **50-70%** de intensidade.
3. **Ajuste fino**: HSL (laranja da pele com saturação −5 e luminância +5; azuis/verdes com saturação −10 no look documental), curvas em "S" suave.
4. **Acabamento de filme**: grão sutil (visível, mas sem distrair), halation leve nos realces (brilho alaranjado), vinheta 10-20%.

### T8. Transições que profissionais usam
- **Corte seco** é o padrão (≥ 80% dos cortes).
- Entre blocos: **zoom-through** (zoom rápido com desfoque de movimento, 8-12 frames) + whoosh; **light leak/flash** (sobreposição em modo Tela) + impacto; **transição por máscara** (objeto em primeiro plano revela a próxima cena); **whip pan**.
- Regra: 8-20 frames; esconder o corte com oclusão, luz ou desfoque; casar com a batida.

### T9. Design de som em camadas
1. Voz: Melhorar voz + Redução de ruído; normalizar (alvo das redes ≈ −14 LUFS integrado).
2. Room tone/ambiência por baixo de tudo: preenche os cortes, "sentido mais que ouvido".
3. SFX: cada movimento visual tem som; variações para não repetir; o pico do som coincide com o corte.
4. Música: entra por último; cortes do B-roll nas batidas; **ducking** (música desce ~10-15 dB quando há voz); sobe nos respiros e no final.

## Fontes
- [CapCut: Chroma key online (Smart tools → Remove background → Chroma key; Intensity/Shadow)](https://www.capcut.com/resource/chroma-key-online)
- [CapCut: Green screen video](https://www.capcut.com/resource/green-screen-video) · [Guide to green screen & AI backgrounds](https://www.capcut.com/resource/guide-to-green-screen)
- [Movavi: green screen no CapCut (Auto/Custom cutout)](https://www.movavi.com/learning-portal/how-to-use-green-screen-on-capcut) · [TourBox: cutout vs chroma](https://www.tourboxtech.com/en/news/how-to-use-green-screen-on-capcut.html)
- [Miracamp: remover fundo](https://www.miracamp.com/learn/capcut/how-to-remove-background) · [Miracamp: LUTs no CapCut](https://www.miracamp.com/learn/capcut/the-ultimate-guide-to-luts)
- [Sparklestock: importar LUT no CapCut Desktop](https://www.sparklestock.com/docs/import-luts-in-capcut-desktop/) · [CapCut: color grading online (.CUBE/.3DL)](https://www.capcut.com/tools/color-grading)
- [CapCut: keyframe animation](https://www.capcut.com/tools/keyframe-animation) · [VideoWizard: máscaras e keyframes](https://videowizardtools.com/capcut-mask-keyframes-guide/)
- [CapCut: how to use (keyframes, masks, blend, speed curve)](https://www.capcut.com/resource/how-to-use-capcut) · [CapCut: speed curve](https://www.capcut.com/tools/speed-ramp)
- [CapCut: Relight](https://www.capcut.com/tools/relight-videos-with-ai) · [ARWriter: recursos de IA 2026](https://arwriterai.com/en/blog/capcut-ai-features-complete-guide-2026/)
- [CapCut: transições em alta 2026](https://www.capcut.com/es-es/help/capcut-transitions) · [CapCut: epic transitions (8-20 frames)](https://www.capcut.com/resource/epic-transitions-template-tutorial)
- [CapCut: template Text behind Subject](https://www.capcut.com/template-detail/textbehindsubject/7507937836256070973)
- [BigVu: CapCut Free vs Pro 2026](https://bigvu.tv/blog/capcut-free-vs-pro-what-2026s-restructure-actually-gives-you/) · [AI After 40: Web vs Desktop 2026](https://www.aiafter40.com/capcut-web-vs-desktop-app-in-2026-which-platform-should-you-use/)
