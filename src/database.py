import sqlite3
from src.config import CAMINHO_DB


def conectar():
    return sqlite3.connect(CAMINHO_DB)


def criar_tabelas():
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS pagamentos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        cpf TEXT,
        codigo_pagamento TEXT UNIQUE,
        parcela TEXT,
        valor REAL,
        competencia TEXT,
        status TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS arquivos_processados (
        nome_arquivo TEXT PRIMARY KEY
    )
    """)

    conn.commit()
    conn.close()


def inserir_pagamento(cpf, codigo_pagamento, parcela, valor, competencia):
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
    INSERT OR IGNORE INTO pagamentos 
    (cpf, codigo_pagamento, parcela, valor, competencia, status)
    VALUES (?, ?, ?, ?, ?, ?)
    """, (cpf, codigo_pagamento, parcela, valor, competencia, "ENVIADO"))

    conn.commit()
    conn.close()


def atualizar_status(codigo_pagamento, status):
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
    UPDATE pagamentos
    SET status = ?
    WHERE codigo_pagamento = ?
    """, (status, codigo_pagamento))

    conn.commit()
    conn.close()


def arquivo_ja_processado(nome_arquivo):
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT 1 FROM arquivos_processados WHERE nome_arquivo = ?
    """, (nome_arquivo,))

    resultado = cursor.fetchone()
    conn.close()

    return resultado is not None


def salvar_arquivo_processado(nome_arquivo):
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
    INSERT OR IGNORE INTO arquivos_processados (nome_arquivo)
    VALUES (?)
    """, (nome_arquivo,))

    conn.commit()
    conn.close()