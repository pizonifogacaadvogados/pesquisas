# Orientação para o Claude neste repositório

- O sistema de redes fica em `sistema-redes/` (pacote Python `redes`; rode os comandos **de dentro** dessa pasta:
  `cd sistema-redes && python3 -m redes …`). Comece pela skill `gestor-redes`.
- Testes: `cd sistema-redes && REDES_RAPIDO=1 python3 -m unittest discover -s tests` (≈ 2 min); sem `REDES_RAPIDO`
  inclui produção de vídeo (≈ 6-8 min). Rode antes de commitar mudanças no código.
- Toda pesquisa nova vai para `sistema-redes/pesquisa/registro/` (tabela ID | Ferramenta | Consulta | Fontes | Achados | Conf.).
- Nunca publique nas redes em nome do usuário; nunca envie material sigiloso de cliente para serviços externos (CapCut, IA de terceiros).
- Conteúdo político: nada de IA em rosto/voz de pessoa real; datas eleitorais em `redes/nucleo/conformidade.py`.
