"""Caminhos do sistema (tudo relativo à raiz `sistema-redes/`)."""
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
FONTES = RAIZ / "fontes"
MODELOS = RAIZ / "modelos"
MEMORIA = RAIZ / "memoria"
PERFIS = RAIZ / "perfis"
DADOS = RAIZ / "dados"          # pautas, calendário, publicações (estado do gestor)
ESTUDOS = RAIZ / "estudos"
