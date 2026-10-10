# 22. "O próprio Claude edita": análise das referências enviadas e estratégia (Fase 11)

Pedido de 10/10/2026: o usuário enviou ~30 capturas de tela (Instagram e o site edicaomia.com.br) de criadores que
dizem que o Claude edita "por si só, melhor que qualquer editor ou CapCut". Pediu análise **imagem a imagem**, o
nível da edição, e o que dá para fazer com isso. Registro das buscas: `pesquisa/registro/R15-claude-editor.md`.

> Método: as imagens são quadros parados. O que segue é a leitura técnica de cada quadro (tipografia, cor, camadas,
> movimento implícito, captação) com o nível de cada elemento e a ferramenta mais provável. Onde não dá para
> afirmar, está marcado como inferência.

---

## 1. Análise imagem a imagem

### 1.1 André Nunes (@oandrenuneu) — anúncio patrocinado
Números no quadro: 2.673 curtidas, **2.809 comentários**, 1.409 envios; seguido por 367 mil contas.

| Quadro | O que aparece | Técnica | Nível | Ferramenta provável |
|---|---|---|---|---|
| **Visão computacional** | Caixas com cantos em "L" no ROSTO (rótulo "ROSTO 0,94" = confiança do detector), OLHOS e BOCA com linhas-guia, duas caixas MÃO; cabeçalho mono "VISÃO COMPUTACIONAL · RECONHECENDO · QUADRO 0267"; "OBJETOS 05"; selo "EDITOR ANDRÉ" riscado → "EDITOR IA ✓"; legenda "foi um **IA**" com palavra-chave em lilás | HUD de **rastreamento real** (as caixas seguem o rosto e as mãos), tipografia mono técnica, contador de quadros, troca de "editor" como gancho narrativo | **Alto** (motion design com dado real) | detector de rosto/mãos (MediaPipe/YuNet) → coordenadas → HTML/GSAP ou Remotion; Claude Code orquestra |
| **Transcrição ao vivo** | Vídeo em janela arredondada no topo; "EDITANDO AO VIVO 00:13:27"; faixa de **blocos de palavras** com mini-ondas, palavra atual em roxo com cursor; "PALAVRA 46 / 179"; régua 0:00-1:10; forma de onda do áudio inteiro | **Interface de edição como conteúdo** (mostra a máquina trabalhando); dados reais da transcrição e do áudio | **Alto** | transcrição palavra a palavra (Whisper) + HTML/GSAP |
Captação: cenário com luz prática magenta lateral, fundo escuro, rosto bem iluminado; câmera estável. **Boa, não excepcional.**

### 1.2 castilho.ia — carrossel de 6 slides (patrocinado/sugestão)
Números: 1.114 curtidas, **2.171 comentários**, 1.213 envios (o volume de comentários vem do CTA "comenta EDITOR").

| Slide | O que aparece | Técnica | Nível |
|---|---|---|---|
| 02/06 "Conecte seu conteúdo ao *Claude.*" | Fluxo **vídeo bruto → Claude edita (8 tarefas em paralelo) → reel editado**; 8 cartões com ícone (corta silêncios, gera legendas, cria hook, efeitos de som, corrige cor, limpa o áudio, anima o vídeo, reel pronto) | **Infográfico editorial**: serifa condensada pesada + itálico colorido na palavra-chave, papel creme, ícones em quadrados suaves, linhas tracejadas | **Alto** (design de revista) |
| 03/06 "Você fala com ele como um *editor de vídeo.*" | Janela de **terminal** com o prompt: "Atue como um editor de vídeo profissional… Siga este processo: 1. Diagnóstico 2. Formato 9:16 3. Ritmo 4. Cortes 5. Áudio 6. Legendas"; rodapé itálico azul | Mostrar o **prompt** como prova; o processo é exatamente o nosso pipeline | Médio-alto |
| 04/06 "Você pede. *Ele edita tudo.*" | Casos: ① **podcast de 1 h → 10 clipes** (miniaturas com duração); ② **1 ideia → 5 testes de Reels** (gancho de pergunta, lista prática, exemplo pessoal, antes e depois, passo a passo) | Casos com números concretos | Alto |
| 05/06 "Um vídeo editado *em minutos.*" | Painel escuro: ANTES × DEPOIS (legenda "IDEIAS BOAS NÃO BASTAM. **É A EXECUÇÃO QUE CONTA.**" com tarja azul), lista "7 ajustes aplicados" e **linha do tempo multipista** (vídeo, legendas, efeitos, movimento, áudio) | Mockup de editor | Alto |
| 06/06 "COMENTA **"EDITOR"**" | CTA de palavra-chave + "te mando no DM ↓" | Funil de comentários → DM | — |
Observação: as fotos das pessoas nos slides parecem **geradas por IA** (inferência: estética e perfeição). Não usar isso em conteúdo político ou jurídico com pessoas reais.

### 1.3 Tiago Lemos (@tiagolemosx) — anúncios e stories
Números: 473-828 curtidas, 157-354 envios, seguido por 1,5 mi contas.

| Quadro | O que aparece | Técnica | Nível |
|---|---|---|---|
| **"ALTO NÍVEL" em camadas** | O quadro do vídeo se abre em **5 placas de vidro** em perspectiva: CAMADA 01 VÍDEO, 02 RECORTE, 03 LEGENDA, 04 ÍCONES, 05 TÍTULO, com bordas lilás brilhantes, ícones em botões arredondados, legenda "aparecendo na hora" | **Composição 3D explicada** (desmonta a própria edição) | **Muito alto** (nível de After Effects) |
| **"AQUELE VÍDEO COM / EDIÇÃO INCRÍVEL"** | Kicker espaçado + título enorme em **gradiente branco→lilás com brilho**; **card flutuante** inclinado à direita mostrando um post salvo ("SALVO · Roteiro em 4 passos…"); legenda branca palavra a palavra no centro | Título cinético + B-roll em card | Alto |
| **"PERGUNTA"** | Card claro no topo: "PERGUNTA — Tiago, eu consigo editar uma VSL inteira só com inteligência artificial?" | Formato **"você pergunta, eu respondo"** | Médio (simples e eficaz) |
| **"E PENSOU:"** | Kicker mono espaçado no topo + card salvo | Ritmo: texto da fala vira título | Médio |
| **"Editor IA · meu_video.mov"** | Mockup do editor: vídeo à esquerda; "VOCÊ PEDE: 'edita meu v|'" (digitando); "A IA EDITA: ritmo dos cortes, transições, fontes, composição"; linha do tempo com VÍDEO / LEGENDA / EDIÇÃO (blocos "TÍTULO") / ÁUDIO e cursor | Interface de edição como conteúdo | Muito alto |
| Stories **"EDITAR UM VÍDEO DE / 20 MINUTOS"** | Título gigante sobre a cabeça | Título cinético | Médio-alto |
| Stories **"CORTE DE RESPIRAÇÃO"** | Vídeo **em preto e branco** + título lilás | Mudança de cor como ênfase | Médio |
| Stories **"LEGENDA / IMAGEM"** | Duas palavras empilhadas: uma condensada e alta, outra larga e branca, sobrepostas | Tipografia cinética que ecoa a fala | Alto |
Captação: **excelente**. Estante com profundidade, luz prática magenta/roxa no fundo, luz principal suave no rosto, lente clara (fundo levemente desfocado), microfone de lapela. A edição brilha porque a gravação é boa (confirma o estudo 18 §1).

### 1.4 edicaomia.com.br — curso "Editor IA" (provavelmente do Tiago Lemos: mesmo apresentador e cenário)
| Tela | Conteúdo |
|---|---|
| Promessa | "NUNCA MAIS abra um Editor de Vídeos. A IA Faz Isso Por Você." "**Você usa o Codex ou o Claude Code e pede, em português, o que quer ver na tela.**" 10 aulas + 2 bônus; garantia de 7 dias |
| 10 estilos (carrossel do site) | 01 **Montagem em 3D** ("A IA monta a edição em camadas", 5 camadas); 02 **Motion explicativo** ("TRÊS PONTOS PARA SUA ROTINA": itens com ícone que acendem, apresentador em janela, legenda); 03 **Tutorial em 3D** ("Pronto pra postar": tela inclinada com chips "Título animado", "Legenda automática"); 04 **Bruto → editado** (carrossel 3D de vídeos); 05 **Perspectiva 3D** (01 fundo IA, 02 texto, 03 apresentador, 04 ícones, 05 moldura); 06 **Recorte de fundo**; 07-10 não visíveis |
| Demo "Editor IA" | "Silêncio encontrado: 1,6 s" → VOCÊ: "Corta as pausas e coloca legenda" → ① Retira o silêncio ② Aproxima os trechos ③ Insere as legendas → "Pronto: vídeo editado" (linha do tempo vídeo/legendas/áudio) |
| **Skills de edição** (bônus) | "Com as skills ligadas, a IA consulta **estilo, ritmo, legendas, movimento e composição** antes de editar." Exemplo: "Edita esse vídeo e deixa bonito" + Estilo: cor tratada, clima roxo; Ritmo: glitch no tempo da fala; Legendas: palavra-chave em destaque; Movimento: carrossel 3D dos meus vídeos |
| Método | **Prepare → Peça → Revise → Reutilize**; guia com comandos por aula, **modelo de briefing**, **pasta modelo para os arquivos**, **ficha de revisão** |
| Público | Ads (testar versões B/C/D de criativos), Conteúdo (pasta de gravações "aguardando edição"), Negócio (explicar a oferta) |

### 1.5 Runway (@runwayapp) — anúncio
"A Runway chegou ao Claude Opus 5.5. Uma foto do produto, uma descrição do comercial: o Claude planeja os planos, a Runway filma." Quadro: comercial fotorrealista (criança e torradeira). **Geração de vídeo por IA** dirigida pelo Claude (conector). Nível visual: cinema publicitário. Limite para nós: **não** usar com pessoas reais, candidatos ou clientes (TSE/deepfake, Súmula 403); possível para B-roll de objetos e cenários, sempre rotulado.

### 1.6 slayer.vfx — anúncio
"EDIÇÃO DE VÍDEO 100% COM IA · mesmo vídeo, outro resultado · este vídeo foi **89%** inteiramente editado · APENAS R$ 19". Comparação lado a lado com/sem. Engajamento baixo (15 curtidas). Infoproduto de entrada; útil só como formato "antes × depois".

---

## 2. O que é verdade e o que é marketing
| Afirmação | Leitura técnica |
|---|---|
| "O Claude edita sozinho, melhor que o CapCut" | **Verdade para motion graphics e automação**: o Claude Code escreve HTML/CSS/GSAP (HyperFrames, Remotion) e comanda o ffmpeg; isso faz animações com qualidade de After Effects, com **dados reais** (rastreamento, transcrição, forma de onda) que os modelos prontos do CapCut não fazem. **Exagero** em "sozinho": o resultado depende da direção (briefing, estilo, revisão: o próprio curso vende "skills" e "ficha de revisão") e da **gravação** (todos têm cenário e luz bons). |
| "Nunca mais abra um editor" | Para formatos repetíveis, sim (é o que o nosso `executar` faz). Para cor fina, VFX e decisões emocionais de montagem, o editor humano ainda vence. |
| Os números | Os maiores volumes de comentário vêm do **CTA de palavra-chave** ("comenta EDITOR"), não da edição. Vários posts são **patrocinados**: a distribuição é paga. |

## 3. Comparação com o nosso sistema
| Elemento das referências | Nosso sistema antes | Agora (Fase 11) |
|---|---|---|
| Claude Code + HTML/GSAP + ffmpeg como "editor" | ✅ é a nossa arquitetura (motor v3, HyperFrames) | — |
| Cortar silêncios, legendas palavra a palavra, ritmo, gancho, cor, áudio, SFX, formato 9:16 | ✅ (análise, plano, produção, áudio) | — |
| Skills de estilo/ritmo/legendas/movimento/composição | ✅ estilos, presets, legendas, motion; skills por etapa | mapa explícito no skill `videomaker-efeitos` |
| Título cinético com gradiente e brilho | 🟡 (abertura ASS/GSAP simples) | ✅ efeito `titulo` |
| Card de PERGUNTA | ❌ | ✅ efeito `pergunta` |
| Card flutuante (post salvo, print) | 🟡 (cartão de norma) | ✅ efeito `card` |
| HUD de visão computacional | ❌ | ✅ efeito `hud` (rosto, olhos, boca com YuNet; mãos: pendente, ver §5) |
| Transcrição ao vivo com forma de onda | ❌ | ✅ efeito `transcricao` |
| Camadas / perspectiva 3D | ❌ | ✅ efeito `camadas` (vídeo, recorte RVM, legenda, ícones, título) |
| Motion explicativo (itens que acendem + apresentador em janela) | ❌ | ✅ efeito `lista` |
| Preto e branco de ênfase | ❌ | ✅ efeito `pb` |
| Podcast 1 h → N clipes; 1 ideia → N variações de gancho | 🟡 (um trecho por vez) | ✅ comandos `cortes` e `variacoes` |
| Carrossel editorial (fluxo, terminal, casos, antes/depois, CTA palavra) | 🟡 4 identidades, 10 tipos de slide | ✅ identidade `editorial` + 5 tipos novos |
| Conformidade OAB/TSE, multirrede, calendário, aprendizado | ✅ (eles não têm) | — |

## 4. Estratégia recomendada
1. **Sim: o Claude é o editor.** O caminho principal do sistema passa a ser explicitamente o da referência: Claude Code + código (análise → cortes → legendas → cor → motion → efeitos → exportação), **sem abrir editor**. O CapCut fica como opcional para retoques manuais e para quem quiser mexer com o dedo (a skill `videomaker-capcut` continua).
2. **Repertório de efeitos com moderação por marca.** Para o escritório: `pergunta`, `lista` (motion explicativo de direitos), `card` (decisão, print, lei), `titulo`, `camadas` como abertura ocasional; tema dourado/azul do perfil. O HUD e a transcrição ao vivo são "meta" (falam da própria tecnologia): use em conteúdo sobre inovação, LGPD, IA no Direito; não em todo vídeo.
3. **Direção vale mais que efeito.** Adotamos o método deles no nosso fluxo: **Prepare** (pauta + material + checklist de gravação) → **Peça** (briefing na pauta: estilo, ritmo, legendas, movimento, composição, efeitos) → **Revise** (quadros-chave e ficha de revisão) → **Reutilize** (cortes, variações de gancho, carrossel do mesmo tema).
4. **Gravação no padrão deles**: cenário com estante, luz prática colorida no fundo (identidade do perfil: dourado no jurídico, azul no político), luz suave no rosto, lapela. Estudo 20.
5. **CTA de comentário com cuidado**: "comente DÚVIDA" é permitido (conteúdo informativo); "comenta X que te mando no DM" pode virar captação na advocacia: a conformidade agora sinaliza 🟡.
6. **IA generativa (Runway e similares)**: só para B-roll de objetos/cenários, rotulado; nunca pessoas reais, nunca em conteúdo eleitoral na janela proibida.

## 5. Limites honestos
- **Mãos**: o detector usado (YuNet) é de rosto; caixas de mão exigem MediaPipe Hands (modelo do Google; testar instalação no computador do escritório).
- **Fundo gerado por IA** ("01 FUNDO (IA)" do curso): depende de gerador de imagem (não disponível aqui); o sistema aceita qualquer imagem como fundo (`--fundo-foto`).
- Os efeitos 3D são renderizados em CPU: ~1-2 min por efeito de 4-8 s.
