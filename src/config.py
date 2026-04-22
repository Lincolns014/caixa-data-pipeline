import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

CAMINHO_DADOS = os.path.join(BASE_DIR, "dados")
CAMINHO_DB = os.path.join(BASE_DIR, "caixa.db")