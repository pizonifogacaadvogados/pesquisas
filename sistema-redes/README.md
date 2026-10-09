# sistema-redes

Sistema de produção e gestão de redes sociais para advocacia, conteúdo jurídico e política.
**Leia o [MANUAL.md](MANUAL.md).** Skill de entrada: `gestor-redes`. Cronograma e histórico: [00-cronograma.md](00-cronograma.md).

```bash
pip install -r requirements.txt && python3 -m redes diagnostico
python3 -m redes --help
```

| Pasta | Conteúdo |
|---|---|
| `redes/nucleo` | perfis, especificações por rede, conformidade (OAB/TSE/LGPD), rosto, aprendizado, diagnóstico |
| `redes/video` | braço de vídeo: análise, plano, produção v3, motion, áudio, react, CapCut, exportação |
| `redes/foto` | braço de foto: carrossel, post/stories, capas, thumbnails, tratamento de imagem |
| `redes/gestao` | pautas, calendário, publicação, fluxo de ponta a ponta, relatório |
| `estudos/` | 21 estudos (cinema, viral, CapCut, nichos, react, algoritmos, áudio, carrosséis, referências, captação…) |
| `pesquisa/registro/` | R01-R14: todas as pesquisas com consultas, fontes, achados e confiabilidade |
| `perfis/` · `memoria/` · `dados/` | contas atendidas · aprendizado · estado do gestor (fora do git) |
| `exemplo/` | saídas de exemplo (v1, v2, v3) |
| `tests/` | suíte automatizada (`python3 -m unittest discover -s tests`) |
