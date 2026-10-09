---
name: social-publicacao
description: Skill-filha do gestor-redes para publicar e medir em todas as redes - pacote de publicação por rede (arquivos no tamanho certo, legenda com gancho e palavra-chave, assinatura OAB/eleitoral, até 5 hashtags, título do YouTube, texto alternativo, horário), passo a passo de postagem (Instagram, TikTok, YouTube, Facebook, LinkedIn, X, Kwai, Threads, Pinterest, WhatsApp), Trial Reels, e o ciclo de métricas que alimenta o aprendizado. Use quando o usuário perguntar como postar, pedir legenda, ou trouxer números de desempenho.
---

# Publicação e métricas

Trabalhe em `sistema-redes/`. Bases: `estudos/11` (algoritmos), R12 (especificações por rede), R13 (assinaturas obrigatórias), R05.

## 1. Pacote (gerado pelo `executar`)
`dados/producao/<pauta>/pacote/`:
- `PUBLICAR.md` → semáforo de conformidade, tabela destino × arquivo × horário × alertas, passo a passo por rede, checklist;
- `<destino>/` → arquivo final no tamanho da rede + `legenda.txt` (+ `TÍTULO` no YouTube) + `texto_alternativo.txt` nas imagens;
- `pacote.json` → tudo em formato de máquina.
Sem pauta (avulso): `python3 -m redes exportar final.mp4 --perfil <id>` + `python3 -m redes legenda <perfil> <destino> "gancho" --corpo "…" --hashtags a b c`.

## 2. Legenda (regras embutidas no código)
- **1ª linha = gancho com a palavra-chave de busca** (só ~125 caracteres aparecem no Instagram; ~55 nos Reels).
- Corpo curto (2-4 linhas de valor) + **um** CTA permitido do perfil (salvar, enviar, comentar dúvida; nada de captação).
- **Assinatura obrigatória:** advocacia → nome · cargo · OAB; político impulsionado → "Propaganda Eleitoral" + CNPJ; IA → "Conteúdo gerado/alterado com IA".
- Hashtags: as do tema primeiro, depois as do perfil; **máximo 5** (Instagram e TikTok), 1-2 no X, 1 tópico no Threads.
- X: versão curta (≤ 280). YouTube: título ≤ 70 caracteres (limite 100), descrição em **bytes** (5.000).
Escreva o `legenda_corpo` da pauta com o tom do perfil; o código monta o resto por rede.

## 3. Passo a passo e qualidade de upload
Está no `PUBLICAR.md`. Pontos que derrubam qualidade: no Instagram ligar "Enviar na qualidade mais alta"; no TikTok "Permitir uploads em alta qualidade"; nunca reenviar vídeo baixado de outra rede (marca d'água derruba a originalidade). **Trial Reels** para testar 2-3 ganchos com não seguidores.

## 4. Medir (48-72 h) e ensinar o sistema
```bash
python3 -m redes metricas <id_video> --plataforma instagram --views 12000 --taxa-pulo 0.38 \
   --retencao-media 0.52 --envios 310 --salvamentos 180 --comentarios 45
python3 -m redes feedback <id_video> "zoom demais, legenda pequena"
python3 -m redes pauta status <pauta> medido
python3 -m redes relatorio --perfil <perfil> --saida relatorio.md
```
Leitura: taxa de pulo alta → gancho/1º quadro; retenção cai no meio → ritmo; envios altos → repita o tema; salvamentos → vire carrossel; comentários com dúvida → nova pauta (formato "você pergunta").
