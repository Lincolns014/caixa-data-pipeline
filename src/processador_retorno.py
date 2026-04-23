import pandas as pd
import os
import datetime

from src.database import (
    atualizar_status,
    inserir_pagamento,
    arquivo_ja_processado,
    salvar_arquivo_processado,
    buscar_cpf_por_codigo
)

from src.config import CAMINHO_DADOS, BASE_DIR


def processar_retorno():

    print("\n🚀 MOTOR CAIXA – ANALISADOR COMPLETO POR ARQUIVO\n")

    base_dir = CAMINHO_DADOS

    if not os.path.exists(base_dir):
        raise FileNotFoundError("❌ Pasta 'dados' não encontrada")

    print("📂 Pasta analisada:", base_dir)

    mapa_status = {
        "14": "AGENDADA_CREDITO_CONTA",
        "15": "ENVIADA_CREDITO_CONTA",
        "20": "PAGO",
        "32": "REJEITADO"
    }

    mapa_rejeicao_codigo = {
        "30": "ENCERRAMENTO_CALENDARIO",
        "40": "CPF_INVALIDO"
    }

    def classificar_rejeicao(codigo, descricao):
        desc = descricao.upper()

        if codigo in mapa_rejeicao_codigo:
            return mapa_rejeicao_codigo[codigo]

        if "SUSPENS" in desc:
            return "CPF_SUSPENSO"
        elif "FALECIDO" in desc:
            return "TITULAR_FALECIDO"
        elif "CANCEL" in desc:
            return "CPF_CANCELADO"
        elif "CALENDARIO" in desc:
            return "ENCERRAMENTO_CALENDARIO"

        return f"REJEICAO_NAO_MAPEADA_{codigo}"

    def classificar_status(codigo):
        if codigo in mapa_status:
            return mapa_status[codigo]

        if codigo == "30":
            return "ENCERRAMENTO_CALENDARIO"

        return f"STATUS_NAO_MAPEADO_{codigo}"

    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    caminho_excel = os.path.join(BASE_DIR, f"ANALISE_CAIXA_{timestamp}.xlsx")

    with pd.ExcelWriter(caminho_excel, engine="openpyxl") as writer:

        houve_dados = False

        for raiz, dirs, arquivos in os.walk(base_dir):

            for arquivo in arquivos:

                caminho = os.path.join(raiz, arquivo)

                if not os.path.isfile(caminho):
                    continue

                nome_arquivo = caminho.lower().strip()

                if arquivo_ja_processado(nome_arquivo):
                    print(f"⏭️ Ignorado: {arquivo}")
                    continue

                print(f"📄 Processando: {arquivo}")

                dados = []

                try:
                    with open(caminho, "r", encoding="latin-1") as f:
                        linhas = f.readlines()
                except Exception as e:
                    print("Erro leitura:", e)
                    continue

                nome_upper = arquivo.upper()

                # ================= CNT =================
                if nome_upper.startswith("CNT"):

                    for linha in linhas:
                        if linha.startswith("2"):
                            try:
                                cpf = linha[2:13].strip()
                                codigo = linha[27:45].strip()
                                parcela = linha[79:81].strip()
                                valor = int(linha[45:57]) / 100
                                comp = linha[57:63].strip()

                                inserir_pagamento(cpf, codigo, parcela, valor, comp)

                                dados.append({
                                    "CPF": cpf,
                                    "Código": codigo,
                                    "Valor": valor
                                })

                            except:
                                pass

                # ================= I02 =================
                elif "I02" in nome_upper:

                    for linha in linhas:
                        if linha.startswith("2"):
                            try:
                                codigo_pagamento = linha[26:44].strip()
                                codigo = linha[44:46].strip()
                                desc = linha[46:96].strip()

                                status = classificar_rejeicao(codigo, desc)
                                atualizar_status(codigo_pagamento, status)

                                cpf = buscar_cpf_por_codigo(codigo_pagamento)

                                dados.append({
                                    "CPF": cpf,
                                    "Código": codigo_pagamento,
                                    "Status": status
                                })

                            except:
                                pass

                # ================= I03 =================
                elif "I03" in nome_upper:

                    for linha in linhas:
                        if linha.startswith("2"):
                            try:
                                codigo_pagamento = linha[15:33].strip()
                                status_cod = linha[83:85].strip()

                                status = classificar_status(status_cod)
                                atualizar_status(codigo_pagamento, status)

                                cpf = buscar_cpf_por_codigo(codigo_pagamento)

                                dados.append({
                                    "CPF": cpf,
                                    "Código": codigo_pagamento,
                                    "Status": status
                                })

                            except:
                                pass

                # ================= SALVAR =================
                if dados:
                    houve_dados = True
                    pd.DataFrame(dados).to_excel(writer, sheet_name=arquivo[:25], index=False)

                salvar_arquivo_processado(nome_arquivo)

        if not houve_dados:
            pd.DataFrame({"Aviso": ["Nenhum dado"]}).to_excel(writer, sheet_name="SEM_DADOS")

    print("\n✅ Processamento finalizado!")