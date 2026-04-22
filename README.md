
# 🚀 Caixa Data Pipeline

Pipeline em Python para processamento de arquivos CNAB da CAIXA com controle incremental (idempotência).

---

## 📌 Problema

Processar arquivos de retorno CNAB garantindo que arquivos já tratados não sejam reprocessados, evitando duplicidade e inconsistência nos dados.

---

## ⚙️ Solução

O sistema foi desenvolvido para:

* 📂 Ler arquivos CNAB automaticamente
* 🔁 Evitar reprocessamento (controle incremental)
* 💾 Armazenar dados em banco SQLite
* 📊 Gerar relatórios em Excel
* 📈 Atualizar status de registros

---

## 🧠 Conceitos aplicados

* Data Pipeline
* ETL (Extract, Transform, Load)
* Idempotência
* Processamento incremental
* Persistência de dados

---

## 🛠️ Tecnologias

* Python
* Pandas
* SQLite
* Openpyxl

---

## ▶️ Como executar

```bash
py -m src.main
```

---

## 📊 Resultados

* +200.000 registros processados
* 170+ arquivos controlados automaticamente
* Pipeline eficiente e escalável

---

## 📁 Estrutura do projeto

```
src/
 ├── main.py
 ├── database.py
 ├── processador_retorno.py
 └── config.py
```

---

## 🚀 Próximos passos

* Logging estruturado
* Integração com Airflow
* Dashboard com Power BI

---

## 👨‍💻 Autor

Desenvolvido por Lincolns Rocha
