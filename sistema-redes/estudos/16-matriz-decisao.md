# E16: Matriz de decisão, a inteligência do videomaker

> Como o sistema decide **o que fazer** em cada vídeo e em cada momento. Resume E1-E15 em regras acionáveis. A skill-mãe segue esta matriz; o módulo `visao` (análise de quadros) e a transcrição fornecem os sinais; o módulo `aprendizado` ajusta as regras com o resultado real.

## 1. Diagnóstico do material (antes de editar)

| Sinal | Como medir | Decisão |
|---|---|---|
| **Proporção** | ffprobe | 16:9 → auto reframe/corte no rosto ou fundo desfocado; 9:16 → direto |
| **Rosto presente e posição** | detecção de rosto por quadro (`visao`) | centralizar no terço superior; se o rosto sai do quadro → rastreamento |
| **Fundo** | variância e brilho do fundo (área fora do rosto) | fundo liso/feio → estúdio virtual; fundo bonito → manter + leve desfoque; parede clara atrás de pessoa escura → relight/exposição |
| **Iluminação** | brilho médio do rosto × fundo | rosto escuro → relight/curvas; estourado → reduzir realces |
| **Movimento** | diferença entre quadros | câmera tremida → estabilizar; pessoa parada muito tempo → mais movimento virtual |
| **Cortes de cena** | detecção de troca de cena | múltiplas câmeras/clipes → color match; react → separar original e reação |
| **Áudio** | ruído de fundo (silêncios), clipping | ruído → reduzir ruído; eco → isolar voz; clipping → avisar |
| **Fala** | transcrição: ritmo, vícios, pausas | cortar vícios e pausas; manter a pausa dramática |
| **Conteúdo** | transcrição: tema, palavras-chave, normas, números | cartões de lei/dado; B-roll; tom da música |
| **Nicho/risco** | regras OAB/TSE/LDA | preset e alertas |

## 2. Escolha do formato e do estilo

| Material / objetivo | Formato | Estilo | Duração |
|---|---|---|---|
| Advogado explicando direito do dia a dia | educativo "você sabia" | `autentico` ou `estudio` | 30-60s (TikTok 61-90s p/ monetizar) |
| Advogado com autoridade (lançamento, tema sério) | autoridade | `estudio` | 45-75s |
| Lei nova / decisão de tribunal | notícia explicada | `documental` ou green screen | 45-90s |
| Vídeo viral de situação cotidiana | **react "Isso pode?"** | `autentico` + layout dividida/pausa | 30-60s |
| Série/novela com cena jurídica | **react "Nota de realismo"** | `autentico` + pausa e comenta | 45-90s |
| Discurso/fala de político | **react checagem/tradução** | `noticiario` | 30-60s |
| Ataque de adversário | **resposta (stitch)** | `autentico` (selfie premium) | 20-45s |
| Proposta de campanha | mensagem | `cinematico` ou `autentico` | 30-60s |
| Podcast/live longa | cortes | `viral` ou `noticiario` | 30-60s cada |
| Bastidores/humanização | selfie | `autentico` (quase sem efeito) | 15-30s |

## 3. Decisão por momento (dentro do vídeo)

| Momento detectado | Câmera | Gráfico | Som |
|---|---|---|---|
| **Gancho (0-3s)** | já em movimento (push-in) | abertura do estilo (texto atrás, cinética, manchete) | impacto suave + música entrando |
| Apresentação de quem fala | estável | **lower third** | whoosh suave |
| Frase longa explicativa | push-in lento (ease) | legenda | música sob a voz |
| Jump cut (corte de pausa) | **punch-in alternado** | — | (whoosh só se for troca de bloco) |
| Citação de lei / número | estável | **cartão** de lei/dado | pop/papel |
| Palavra-chave forte | snap zoom (só no estilo que permite) | destaque na legenda (emoji só no viral) | whoosh |
| Exemplo concreto (contrato, celular, dinheiro) | — | **B-roll** 1,5-3s (L-cut) | — |
| Mudança de bloco de ideia | transição do estilo | — | whoosh suave / flash |
| Antes do clímax | — | — | riser ou **stopdown** |
| Clímax / revelação | zoom lento ou snap | — | impacto grave |
| Trecho de terceiro (react) | **congelar + zoom + círculo** no detalhe | crédito "@perfil · data" | tape stop; original cheio, música off |
| Repetir o momento-chave (react) | **replay** em câmera lenta | "DE NOVO" | — |
| Afirmação falsa (checagem) | — | **carimbo** FALSO + fonte | buzzer/impacto |
| Fechamento / CTA | push-out leve | texto final limpo | música sobe + fade |

## 4. Fundo: quando trocar, como trocar

| Situação | Ação | Ferramenta |
|---|---|---|
| Parede lisa clara, sem graça | **estúdio virtual** escuro (escritório noturno, biblioteca) | `fundos` + `recorte` / CapCut Remover fundo |
| Ambiente bagunçado | estúdio virtual ou **desfoque de profundidade** | idem |
| Escritório bonito | manter; leve desfoque se houver distração | máscara + desfoque |
| Fundo verde | chroma key (melhor borda) | `recorte.matte_chroma` / CapCut Chroma |
| Externo (rua, evento) | manter (autenticidade) | — |
| React | original como fundo (green screen) ou layout dividido | `react` |
| **Nunca** | fundo que finge um lugar real (ex.: "dentro do STF") | — |

## 5. Emojis: quando usar
- **Estilo `viral`**: sim, 1 a cada 4-8s, só se ilustram a palavra.
- **Advocacia**: no máximo ícones neutros (⚖️ ✅ ❌ ⚠️ 📄), raros, ou nenhum. Nada de 💰 🏆.
- **Política**: raros; carimbos e cartões funcionam melhor.
- **Tema sensível** (violência, luto, vítimas): **nenhum**.

## 6. Checklist de qualidade final (o sistema confere)
1. Primeiro quadro: rosto + texto do gancho + movimento.
2. Nada parado por mais de ~12s sem mudança visual.
3. Legenda revisada, dentro da zona segura, palavra-chave destacada.
4. Música licenciada para a(s) rede(s) de destino; voz clara no alto-falante do celular.
5. Loudness ≈ −14 LUFS; sem clipping.
6. Conformidade: OAB / TSE / direito autoral / imagem (alertas resolvidos).
7. Sem marca d'água; 1080×1920; capa com título no centro 3:4.
