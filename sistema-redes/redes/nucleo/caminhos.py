"""Caminhos do sistema (tudo relativo à raiz `sistema-redes/`)."""
import os
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
FONTES = RAIZ / "fontes"
MODELOS = RAIZ / "modelos"
MEMORIA = Path(os.environ.get("REDES_MEMORIA", RAIZ / "memoria"))   # testes usam outra pasta
PERFIS = RAIZ / "perfis"
DADOS = Path(os.environ.get("REDES_DADOS", RAIZ / "dados"))          # pautas, calendário, publicações
ESTUDOS = RAIZ / "estudos"
