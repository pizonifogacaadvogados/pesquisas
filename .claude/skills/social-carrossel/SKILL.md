---
name: social-carrossel
description: Skill-filha do braço de foto (social-foto) para CARROSSÉIS (Instagram 4:5/3:4, TikTok Modo Foto 9:16, LinkedIn PDF, Facebook, Threads) com design minimalista profissional para advocacia e política - roteiro de texto (gancho, promessa, uma ideia por slide, CTA), identidades visuais, tratamento de fotos e prints, e geração automática de PNG/PDF. Use quando o usuário pedir carrossel, "conteúdo escrito" em slides ou transformar um vídeo/tema em carrossel (posts de imagem única: social-foto).
---

# Carrossel (gestor de redes)

Base: `sistema-redes/estudos/17-carrosseis.md` (especificações, estrutura, design, tratamento de imagem, mix com vídeo) e registro `pesquisa/registro/R10-carrosseis.md`. Conformidade: skill `social-conformidade` (mesmas regras dos vídeos).

## 1. Roteiro do texto (a parte que mais pesa)
Escreva **antes** de pensar no visual:
1. **Capa = gancho**, não título (≤ 10-12 palavras): pergunta que só o deslize responde, número específico, "o erro que…", contradição.
2. **Slide 2 = promessa** ("em 5 slides você vai saber…").
3. **Melhor ponto até o slide 3.**
4. **Uma ideia por slide**, 12-25 palavras, com 1 destaque (`==marca-texto==` ou `**negrito**`).
5. Penúltimo: resumo ou dado com **fonte**.
6. **Último = CTA** específico (salvar / enviar para alguém / comentar). Advocacia: sem captação nem consulta individual.
Total: **7-10 slides**. Legenda do post: complementa, traz a palavra-chave de busca, até 5 hashtags.

Tipos de slide disponíveis: `capa`, `promessa`, `item`, `dado`, `mito`, `texto` (manifesto), `citacao`, `print`, `lista`, `cta` e, para a identidade editorial (estilo de revista, R15/castilho.ia), `fluxo` (de → meio → para + cartões), `grade` (cartões com ícone), `terminal` (modelo de texto/mensagem), `antes_depois` e `cta_palavra` ("COMENTE 'PRAZO'"). Destaque em itálico colorido: `__palavra__`. Campo `kicker` em cada slide aparece no cabeçalho ("02 / 06 · COMO FUNCIONA").

## 2. Identidade visual
| Identidade | Quando |
|---|---|
| `juridico_classico` | padrão do escritório (off-white, azul-marinho, dourado; Playfair + Inter) |
| `juridico_moderno` | temas atuais, tecnologia, trabalho (grafite + verde-água; Inter) |
| `politico_sobrio` | política institucional, propostas (branco + azul; Inter Black) |
| `manifesto` | frases fortes, carrossel-texto político/opinião (preto + amarelo; Bebas) |
| `editorial_juridico` | estilo revista (papel, Playfair pesada + itálico dourado, cabeçalho 02/06): explicações passo a passo, modelos de mensagem |
| `editorial` | o mesmo com acento laranja/azul (castilho.ia) |
Mantenha **a mesma identidade** no perfil inteiro. Para outra paleta (cor do partido, marca), acrescente uma entrada em `IDENTIDADES`, sempre com contraste ≥ 4,5:1.

## 3. Imagens
- Foto do autor: recorte limpo, luz frontal; mesma cor dos vídeos (LUT).
- Prints: alta resolução, recorte do essencial, **fonte e data** no slide, dados pessoais **anonimizados** (LGPD).
- Nada de banco de imagem genérico nem clipart.

## 4. Gerar
Pelo gestor (recomendado): `python3 -m redes pauta criar <perfil> "Tema" --formato carrossel --material carrossel.json`
e `python3 -m redes executar <pauta>` → artes ajustadas para cada rede do perfil + PDF do LinkedIn + legendas + texto
alternativo + pacote. A identidade vem do perfil (`identidade_foto` + `cores`).
Avulso:
```bash
cd sistema-redes
python3 -m redes carrossel pasta/carrossel.json --formato 4x5 9x16 --saida pasta/saida
```
Saída: `slide_NN_4x5.png` (Instagram), `slide_NN_9x16.png` (TikTok), `carrossel_*.pdf` (LinkedIn), `mosaico_*.png` (revisão) e `relatorio_*.json` (alertas de excesso de palavras, número de slides, CTA e contraste).
**Revise o mosaico e 2-3 slides em tamanho real** (leia com Read) antes de entregar.

## 5. Canva (opcional)
Se o conector oficial do Canva estiver ativo (Configurações → Conectores; servidor `mcp.canva.com/mcp`), use-o para: preencher modelos do escritório (autofill), aplicar o Brand Kit e exportar. Neste ambiente ele **falhou ao conectar** (proxy); o gerador próprio cobre o fluxo sem depender dele.

## 6. Mix com vídeo
Para cada tema forte: Reel (alcance) → carrossel aprofundando (salvamentos), 1-3 dias depois. Registre o desempenho com `social-publicacao` (salvamentos e envios são as métricas do carrossel).
