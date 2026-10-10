# R20: Acesso aos vídeos do @tiagolemosx e ferramenta de dissecação de referências (10/10/2026)

Pedido do usuário: analisar todos os vídeos do canal https://www.youtube.com/@tiagolemosx (ex.: https://www.youtube.com/watch?v=IobZgb7ngz4) para aprender as edições. Resultado: **bloqueado neste servidor**; receita para destravar em `estudos/24-mapa-do-que-falta.md` §1.

| ID | Ferramenta | Consulta | Fontes | Achados | Conf. |
|---|---|---|---|---|---|
| R20.01 | curl | `https://www.youtube.com/@tiagolemosx/videos` | — | sem conexão (código 000): proxy bloqueia o YouTube | — |
| R20.02 | curl | feed RSS `youtube.com/feeds/videos.xml?user=tiagolemosx` | — | sem conexão | — |
| R20.03 | yt-dlp 2026.8.19 (wheel do PyPI, sem instalar) | `--flat-playlist -I 1:5 @tiagolemosx/videos` | — | `Tunnel connection failed: 403 Forbidden` (3 tentativas) | — |
| R20.04 | curl | oEmbed e noembed do vídeo `IobZgb7ngz4` | — | sem conexão | — |
| R20.05 | curl | miniaturas `i.ytimg.com` / `img.youtube.com` do vídeo | — | sem conexão | — |
| R20.06 | curl | espelhos Invidious (yewtu.be, inv.nadeko.net) e r.jina.ai | — | sem conexão | — |
| R20.07 | WebSearch | `"IobZgb7ngz4" OR "Tiago Lemos" tiagolemosx youtube Claude edição vídeo` | [Wikipedia: Tiago Lemos (futebolista)](https://en.wikipedia.org/wiki/Tiago_Lemos), [Red Bull: Tiago Lemos skatista](https://www.redbull.com/br-pt/lançamento-do-documentario-guerreiro-sobre-tiago-lemos), [Fast Company Brasil: prompts do Claude](https://fastcompanybrasil.com/?p=283838) | o canal e o vídeo não estão indexados; homônimos (skatista, futebolista). Nada sobre as edições | D |
| R20.08 | código | `redes/video/referencia.py` + comando `referencia` testado: demo v4 × base | local | dissecação em 49 s: cortes/min (2,9 × 0), plano médio, mudança visual a cada 2,0 × 2,9 s, LUFS −14,3 × −20,5, enquadramento close, brilho/contraste/saturação, folha de planos. Pronto para os vídeos do Tiago quando forem baixados fora deste servidor | A (medido) |

## Síntese
Nenhuma rota ao YouTube funciona daqui. A análise depende de baixar os vídeos no computador do escritório (yt-dlp ou gravação de tela, só para estudo) e rodar `python3 -m redes referencia`. A ferramenta está pronta e testada.
