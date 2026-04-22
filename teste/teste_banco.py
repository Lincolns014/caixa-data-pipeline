import sqlite3

conn = sqlite3.connect("caixa.db")
cursor = conn.cursor()

cursor.execute("SELECT COUNT(*) FROM pagamentos")

resultado = cursor.fetchone()

print("📊 TOTAL DE REGISTROS NO BANCO:", resultado[0])

conn.close()

import sqlite3

conn = sqlite3.connect("caixa.db")
cursor = conn.cursor()

cursor.execute("SELECT COUNT(*) FROM arquivos_processados")
print("📂 ARQUIVOS PROCESSADOS:", cursor.fetchone()[0])

conn.close()