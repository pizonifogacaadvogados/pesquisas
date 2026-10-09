# E17: Carrosséis e posts de texto (Fase 8, gestor de redes)

> Base: R10 (+ R05, R06, R04 para conformidade). Carrossel é o formato que mais **gera engajamento e salvamentos** no Instagram; Reels é o que mais **alcança** contas pequenas. **A estratégia é combinar os dois**: o vídeo atrai, o carrossel aprofunda e é salvo.

## 1. Especificações

| Rede | Formato | Tamanho | Limites |
|---|---|---|---|
| Instagram carrossel | **4:5 = 1080×1350** (padrão) ou **3:4 = 1080×1440** (preenche a grade sem corte) | PNG/JPG sRGB | até **20** slides (10 via agendador); mesma proporção em todos |
| Instagram post único | 4:5 ou 3:4 | idem | — |
| TikTok Modo Foto | **9:16 = 1080×1920** | JPG/PNG ~20 MB | 2-35 imagens |
| LinkedIn documento | PDF 4:5 ou 1:1 | PDF | ~300 páginas (usar 8-12) |
| Stories | 9:16 | — | — |

O sistema exporta o mesmo carrossel em **4:5 (Instagram)**, **9:16 (TikTok)** e **PDF (LinkedIn)**.

## 2. Estrutura que engaja (texto)

| Slide | Função | Regra |
|---|---|---|
| **1. Capa** | **gancho**, não título | pergunta que só o deslize responde, número específico, "o erro que…", contradição; ≤ 10 palavras; elemento visual forte (foto do autor ou ícone) |
| **2. Promessa** | por que continuar | "Em 6 slides você vai saber…" |
| **3** | **melhor ponto** | o mais forte até aqui (muita gente para no 3) |
| 4-8 | desenvolvimento | **uma ideia por slide**, 12-25 palavras; numerar (1/5, 2/5…) |
| penúltimo | resumo / prova | lista-resumo ou dado com fonte |
| **último** | **CTA** específico | "Salve para consultar", "Envie para quem precisa", "Comente SEU CASO"; com identidade (foto, nome, @) |

Tamanho ideal: **7-10 slides**. Legenda do post complementa (não repete) e traz a palavra-chave de busca.

### Tipos de carrossel que funcionam
- **Educativo em lista** ("5 direitos que você tem quando…").
- **Passo a passo** ("o que fazer se o voo for cancelado").
- **Mito × verdade** (um mito por slide, com selo).
- **Texto-manifesto** (político): frases fortes, uma por slide, tipografia grande, fundo sóbrio. É o formato de "carrossel escrito" que engaja muito.
- **Notícia explicada** (print da manchete no slide 1, depois "o que muda pra você").
- **Antes × depois / comparação** (lei antiga × nova; promessa × entrega).
- **Pergunta de seguidor** (resposta geral, nunca consulta individual: CED art. 42, I).
- **Thread/citação** (estilo tweet, com foto e @ do autor: alta compartilhabilidade).

## 3. Design profissional (o oposto da "cachorreira")

| Princípio | Regra prática |
|---|---|
| **Sistema fixo** | margens de 88px, grade de 12 colunas, logo/@ e paginação **sempre no mesmo lugar** |
| **Tipografia** | 1-2 famílias: título serifado elegante (Playfair/DM Serif) **ou** grotesca forte (Inter Black/Bebas) + texto em Inter; título 72-110px, texto 40-52px (em 1080px de largura); entrelinha 1,25-1,4 |
| **Hierarquia** | 1 destaque por slide (marca-texto, cor de acento ou peso) |
| **Cor** | fundo neutro (off-white, grafite, azul-marinho) + **1 cor de acento**; contraste WCAG ≥ 4,5:1 |
| **Respiro** | ≥ 35% de área livre; nada de texto encostado na borda |
| **Imagem** | foto real e bem tratada (do autor, do lugar, do documento), não banco genérico; recorte limpo; mesma gradação de cor em todas (usar o mesmo LUT dos vídeos) |
| **Ícones** | um estilo só (linha ou sólido); nada de clipart e emojis em excesso |
| **Consistência** | todo carrossel do perfil "parece da mesma marca" |
| **Evitar** | gradientes berrantes, sombras pesadas, 3+ fontes, texto em cima de foto poluída, montagens com recorte serrilhado, letras em caixa alta com contorno amarelo (estética "panfleto") |

### Identidades visuais prontas (o sistema implementa)
- `juridico_classico`: off-white + azul-marinho + dourado discreto; Playfair Display + Inter.
- `juridico_moderno`: grafite + branco + acento verde-água; Inter (Black/Regular).
- `politico_sobrio`: branco + azul-escuro + acento da cor do partido; Inter Black + Inter.
- `manifesto`: fundo escuro + texto branco enorme; Bebas/Anton + Inter.

## 4. Tratamento de imagem e prints

- **Fotos do autor:** luz frontal suave; recorte (rembg) sobre fundo da identidade; mesma LUT dos vídeos (`luts.py`); nitidez leve.
- **Prints (manchete, tweet, documento):** capturar em alta resolução (zoom do navegador 150-200%); recortar só o essencial; **cantos arredondados + sombra suave**; nunca esticar; anonimizar dados pessoais (LGPD); fonte e data abaixo do print.
- **Documentos/lei:** cartão com o texto oficial e **marca-texto** no trecho-chave (como no vídeo documental).
- Exportar em **PNG** (texto nítido) e sRGB.

## 5. Ferramentas

| Ferramenta | Uso | Status |
|---|---|---|
| **Gerador do sistema (HTML → PNG)** | carrosséis por código com as identidades acima; exporta 4:5, 9:16 e PDF | implementado (`redes/foto/carrossel.py`) |
| **Canva (conector oficial do Claude)** | autofill de modelos do escritório, Brand Kit, edição fina, exportação | ⚠️ conector falhou neste ambiente (proxy); habilitar nas configurações de conectores |
| **CapCut Design Studio 2.0** | canvas infinito com agente de design | alternativa |
| Cowork / pasta do projeto | fotos e prints que o usuário entrega | fluxo de entrada |

## 6. Mix vídeo × carrossel (calendário)
- Para cada tema forte: **Reel** (alcance) → **carrossel** aprofundando (salvamentos), 1-3 dias depois → **Stories** com enquete.
- Proporção sugerida: 60% vídeo, 40% carrossel/post no jurídico; em campanha, carrossel-manifesto nos dias de pauta forte.
- Medir: carrossel por **salvamentos e envios**; vídeo por **taxa de pulo e envios**.

## 7. Conformidade
As mesmas regras dos vídeos (E10 §8): OAB (sem captação, promessa ou caso de cliente; sem consulta individual), TSE (fonte e data; sem descontextualização; IA rotulada), direito autoral (print com fonte; foto de terceiros só com direito de uso), LGPD (anonimizar prints).
