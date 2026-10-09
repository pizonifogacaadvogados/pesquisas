# 19. Ferramentas profissionais × CapCut Pro × nosso motor (Fase 9, B3 + B4)

Lente: **editor de cinema**. Pergunta para cada técnica: o profissional faz em quê? o CapCut Pro chega lá? nosso motor (Claude + código) chega lá?
Legenda: ✅ igual ao profissional · 🟡 aceitável em vídeo curto, abaixo do profissional · ❌ não faz.
Bases: `estudos/13` e `14` (CapCut), `estudos/18` (referências), registros R07, R09 e R11.

## 1. Quem usa o quê
| Ferramenta | Papel no mercado | Força |
|---|---|---|
| **Premiere Pro** | montagem (YouTube, agências) | timeline, integração com After Effects (Dynamic Link) |
| **After Effects** (+ plugins: Element 3D, Trapcode, GeoLayers, Deep Glow, Saber; Motion Array/Envato para templates) | motion graphics, composição, VFX 2D | curvas de easing (graph editor), máscaras, tracking, expressões |
| **DaVinci Resolve** (Edit, **Color**, Fusion, Fairlight) | cor de cinema, cada vez mais montagem | correção primária e secundária por nós, **Magic Mask** (recorte de vídeo por IA), Fusion para composição |
| **Final Cut Pro** | montagem rápida (criadores Apple) | desempenho, Magnetic Timeline |
| **Nuke** | composição de cinema (VFX) | keyers, light wrap, profundidade, multicanal |
| **Blender** | 3D, títulos 3D, cenários virtuais | gratuito, renderização física |
| **CapCut Pro** | vídeo curto, criadores | velocidade, legenda automática, templates, efeitos prontos, IA (EditPilot, remover fundo, retocar) |
| **Nosso motor** (Claude + ffmpeg + RVM + HyperFrames) | automação com decisão editorial | escolher momentos e cortes, regras jurídicas e de plataforma, aprendizado, motion por código |

## 2. Matriz técnica
| Técnica | Pro (ferramenta) | CapCut Pro | Nosso motor | Observação de editor |
|---|---|---|---|---|
| Corte por fala, remover silêncio e vícios | Premiere (Text-Based Editing), Descript | ✅ | ✅ (transcrição + regras) | empate; nosso diferencial é **escolher** o trecho |
| Escolha do gancho e dos melhores momentos | editor humano | 🟡 (IA de "highlights") | ✅ pontuação + regras do nicho | ponto forte do motor |
| Legenda animada por palavra | AE / Premiere (MOGRT) | ✅ (muitas prontas) | ✅ ASS (3 estilos) | CapCut tem **mais variedade pronta** |
| **Motion graphics** (títulos, lower third, cartões, dados) | **After Effects** | 🟡 (texto com keyframes e templates; easing limitado, sem graph editor) | ✅ **HyperFrames + GSAP** (curvas expo/power/back, máscara, stagger) | antes ❌ (ASS); agora no nível AE para tipografia 2D |
| Mapa animado, colagem de papel (Johnny Harris, Vox) | AE + GeoLayers, ilustração | ❌ | 🟡 HTML/SVG + textura (possível; ainda não implementado) | próximo passo do motor |
| Gráficos de dados animados | AE, Flourish | 🟡 | ✅ (blocos de gráfico HyperFrames) | |
| **Recorte de pessoa** (sem fundo verde) | Resolve **Magic Mask**, AE **Roto Brush 3**, Nuke | 🟡 "Remover fundo" (rápido, borda instável) | 🟡→✅ **RVM** (vídeo); MatAnyone/SAM 2 quando houver rede/GPU | **evitar trocar o fundo inteiro**: profissional filma no lugar |
| Chroma key | Keylight/Primatte (AE), Ultra Key, Resolve, Nuke | ✅ (com controles de borda) | ✅ (`matte_chroma`) | qualidade = **iluminação do verde** |
| Light wrap, casar cor da pessoa com o fundo | AE / Nuke (nativo) | ❌ | ✅ (`composicao.py`) | é o que separa "colado" de "filmado" |
| Correção de cor primária (balanço, exposição) | **Resolve** | ✅ (básico) | 🟡 (automático por estatística) | |
| Grade de cinema (LUT, curvas, pele protegida) | **Resolve** (nós, qualificadores) | 🟡 (LUT importado, ajustes globais) | 🟡 (LUT por estilo, sem secundária) | **pele protegida** só no Resolve |
| Correção secundária (só céu, só pele) | Resolve | ❌ | ❌ | fora do escopo |
| Estabilização | Warp Stabilizer, Resolve | ✅ | 🟡 (ffmpeg vidstab, não ativado) | |
| Reenquadrar 16:9 → 9:16 seguindo o rosto | Premiere Auto Reframe | ✅ | ✅ (visão + recorte) | |
| Câmera virtual (push-in, punch, snap) com easing | AE / Premiere | ✅ keyframes (curva simples) | ✅ (smoothstep) | |
| Speed ramp | todas | ✅ (curvas prontas) | ❌ ainda | fácil de implementar no ffmpeg |
| Motion blur real | AE (pixel motion), ReelSmart | 🟡 | ✅ nos gráficos (subquadros) | |
| Transições motivadas (whip, match cut) | montagem + captação | ✅ prontas | 🟡 | a boa transição **nasce na captação** |
| Desenho de som (SFX por movimento) | Premiere / Fairlight + bibliotecas pagas | ✅ biblioteca grande | 🟡 sintetizados (melhor com `--sfx-dir`) | |
| Mixagem (ducking, −14 LUFS, stopdown) | Fairlight, Audition | 🟡 (auto-ducking) | ✅ (automação + loudnorm) | |
| Redução de ruído e "voz de estúdio" | iZotope RX, Resolve Voice Isolation, Adobe Enhance | ✅ ("Melhorar voz") | 🟡 (afftdn) | CapCut forte aqui |
| Música licenciada | Artlist, Musicbed, Epidemic | ✅ (biblioteca comercial) | 🟡 (sua biblioteca) | |
| 3D, partículas, VFX ("um carro cai") | Blender, AE + Element, Houdini | 🟡 efeitos prontos | ❌ | uso raro no nicho |
| IA generativa (b-roll, imagem) | Runway, Veo, Kling, Firefly | 🟡 (IA do CapCut) | ❌ aqui (rede bloqueada) | **vedado** em rosto e voz de pessoa real (política: TSE) |

## 3. Gap analysis: nosso teste v2 × referência profissional
| Item avaliado | Profissional | v2 | v3 (agora) | O que fecha o gap |
|---|---|---|---|---|
| Recorte | borda estável, cabelo fino preservado | halo branco no cabelo, tremor | RVM: sem halo, −37% de tremor | MatAnyone/SAM 2 + **filmar em fundo que contraste** |
| Integração pessoa-fundo | luz e cor coerentes | pessoa clara e chapada sobre fundo escuro | cor casada + light wrap | **luz na captação coerente com o fundo** |
| Fundo | real, com profundidade | procedural (bokeh desenhado) | foto real com desfoque de lente (`--fundo-foto`) | **gravar no escritório** com fundo iluminado |
| Gráficos | AE: easing, máscara, ritmo | fade + subida linear | GSAP com curvas expo, máscara, stagger | biblioteca de cenas (dados, documento, mapa) |
| Material | 1080p-4K, 24/25 fps, 180° | 768×432 | idem (sem material melhor aqui) | **seu vídeo real** (B7) |

## 4. Divisão de trabalho recomendada
1. **Captação bem feita** (`estudos/20`): a maior alavanca.
2. **Nosso motor**: decisão editorial, cortes, legenda, motion graphics (HyperFrames), mixagem, conformidade e aprendizado. Exporta o vídeo pronto **e** o pacote CapCut.
3. **CapCut Pro**: retoques rápidos que o usuário queira fazer com o dedo (trocar um efeito, uma música da biblioteca comercial, "Melhorar voz").
4. **Quando um vídeo pedir cinema de verdade** (campanha, institucional): DaVinci Resolve (gratuito) para cor e Magic Mask; o motor entrega o corte e os gráficos em camadas (overlay com alfa importa em qualquer editor).
