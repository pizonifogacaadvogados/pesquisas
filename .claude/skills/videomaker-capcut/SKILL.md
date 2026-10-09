---
name: videomaker-capcut
description: Skill-filha do videomaker para executar a edição dentro do CapCut (conta Pro) - Desktop via computer use (preferido, inclui EditPilot) ou Web via Claude in Chrome - seguindo o roteiro_capcut_pro.md, com recursos Pro, modelos, Skills do CapCut, chroma/remover fundo, keyframes com easing, LUT, legendas e áudio. Use quando o usuário pedir para editar "no CapCut", "no meu CapCut", ou abrir o projeto no CapCut.
---

# CapCut (execução)

Base: `sistema-redes/estudos/14-capcut-pro.md` (o que o Pro libera e quando usar), `13` (inventário menu a menu), `07` (técnicas T1-T9), `04` (receitas R0-R12), `06` (automação e riscos).

## 0. Pré-requisitos (o usuário faz)
- **Desktop (preferido):** CapCut PC aberto e logado (Pro) + computer use habilitado no app do Claude. Necessário para o **EditPilot** e o conjunto Pro completo.
- **Web:** Chrome com **Claude in Chrome** logado no CapCut Web.
- O usuário **sobe** a pasta `capcut_assets/` (gerada pelo motor) na Mídia, porque o upload pela extensão é instável.
- ⚠️ Nada sigiloso de cliente no CapCut (os termos dão licença perpétua sobre o conteúdo armazenado).

## 1. Carregar as ferramentas certas
- Desktop: skill `anthropic-skills:computer-use`.
- Web: skill `anthropic-skills:chrome-browser`.
Siga as regras de segurança delas (aba nova, não mexer em outros projetos, parar em diálogos sensíveis).

## 2. Executar `roteiro_capcut_pro.md`, etapa por etapa
1. **Estrutura:** opção A (EditPilot: cole as instruções do roteiro, uma por vez, e revise o resultado contra o texto de referência) **ou** opção B (importar `base.mp4`, que é mais preciso).
2. **Camadas**, de baixo para cima: fundo → pessoa (Remover fundo / Chroma) → texto atrás → B-roll → cartões → lower third → legendas → **camada de ajuste com `look.cube`** → luz (`trilha_luz.mp4` em modo Tela).
3. **Câmera:** keyframes de escala com curva **Ease in/out** (gráfico de keyframe no Desktop).
4. **Áudio:** Melhorar voz + Redução de ruído; música licenciada com os keyframes de volume do roteiro; SFX nos tempos.
5. **Exportar:** 1080p, 30 fps, sem marca d'água. **Nunca publicar.**
Depois de **cada** etapa: print → conferir o item "Verificar" → seguir. Dois erros seguidos na mesma etapa: pare e descreva ao usuário.

## 3. Padrão do escritório dentro do CapCut (fazer uma vez, reaproveitar sempre)
- Criar **modelos próprios** (Web/Mobile → Compartilhar como modelo): abertura, lower third com OAB, cartão de lei, encerramento.
- Salvar o look como **Skill do CapCut** (2026), se disponível na conta.
- Guardar `look.cube` e fontes do escritório na nuvem do CapCut (só material público).

## 4. Quando o roteiro não bate com a tela
Procure pelo **sentido** (PT/EN), descreva o que vê e adapte. Recurso Pro ausente: alternativa mais próxima + anotação no relatório. Mudanças de interface relevantes → acrescente em `sistema-redes/memoria/LICOES_MANUAIS.md`.
