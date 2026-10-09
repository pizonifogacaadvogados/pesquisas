---
name: videomaker-publicacao
description: Skill-filha do videomaker para publicar e medir - formato por rede (Instagram Reels, TikTok), capa (grade 3:4), legenda do post com palavra-chave, até 5 hashtags, Trial Reels para testar ganchos, horário, e o ciclo de métricas (taxa de pulo, retenção, envios) que alimenta o aprendizado do sistema. Use na etapa 9 do videomaker ou quando o usuário perguntar como postar ou como foi o desempenho.
---

# Publicação e métricas

Base: `videomaker-viral/estudos/11-algoritmos-engajamento.md` e registro `R05`.

## 1. Pacote de publicação (gere para o usuário)
- **Arquivo:** 1080×1920, 30fps, H.264, sem marca d'água.
- **Capa:** título curto legível dentro do centro **3:4** (1080×1440), rosto + 3-6 palavras. Pode ser um quadro do vídeo com o título do gancho.
- **Legenda do post:** 1ª linha = gancho + **palavra-chave de busca** ("direito de arrependimento"); 2-4 linhas de valor; CTA permitido ("salve", "envie para quem precisa", "comente sua dúvida"; nada de captação).
- **Hashtags:** até **5**, específicas (Instagram limita a 5 desde dez/2025); no TikTok, palavras-chave naturais na legenda e no texto da tela.
- **Duração por rede:** Instagram ≤ 3 min (recomendação a não seguidores); TikTok > 60s se o objetivo for monetização.
- **Teste de gancho:** no Instagram, publique 2-3 versões como **Trial Reels** (só não seguidores) e compare a taxa de pulo em 24-48h.
- **Música:** se não estiver embutida, adicionar no app com a biblioteca liberada (ver `videomaker-audio`).

## 2. Medir (24-72h depois) e ensinar o sistema
Peça ao usuário os números (ou prints dos Insights) e registre:
```bash
python3 -m videomaker metricas <id> --plataforma instagram --views 12000 --taxa-pulo 0.38 \
   --retencao-media 0.52 --envios 310 --salvamentos 180 --comentarios 45
python3 -m videomaker licoes      # ranking de estilos e ganchos que funcionaram
```
Interprete para o usuário: **taxa de pulo** alta → gancho/1º quadro; **retenção** baixa no meio → ritmo/clareza; **envios** altos → tema compartilhável (repita o formato); salvamentos → conteúdo de referência (vire carrossel).

## 3. Calendário (sugestão)
Pauta única por dia em época de campanha; no jurídico, 3-5 vídeos/semana alternando formatos (educativo, react "isso pode?", decisão explicada) e intercalando com carrosséis (Fase 8).
