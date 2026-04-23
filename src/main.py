from src.database import criar_tabelas
from src.processador_retorno import processar_retorno


def main():
    criar_tabelas()
    processar_retorno()


if __name__ == "__main__":
    main()

    # python -m src.main