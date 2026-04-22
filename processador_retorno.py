import pandas as pd
import os
import datetime
from database import (
    atualizar_status,
    inserir_pagamento,
    arquivo_ja_processado,
    salvar_arquivo_processado
)

def processar_retorno():

    print("\n🚀 MOTOR CAIXA – ANALISADOR COMPLETO POR ARQUIVO\n")

    base_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dados")

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
        "30": "ENCERRAMENTO_CALENDARIO"
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
    nome_saida = f"ANALISE_CAIXA_{timestamp}.xlsx"

    caminho_excel = os.path.join(os.path.dirname(os.path.abspath(__file__)), nome_saida)

    with pd.ExcelWriter(caminho_excel, engine="openpyxl") as writer:

        houve_dados = False

        for raiz, dirs, arquivos in os.walk(base_dir):

            for arquivo in arquivos:

                caminho = os.path.join(raiz, arquivo)

                if not os.path.isfile(caminho):
                    continue

                # 🔥 padroniza caminho (resolve problema de maiúscula/minúscula)
                nome_arquivo = caminho.lower().strip()

                # 🔥 CONTROLE INCREMENTAL
                if arquivo_ja_processado(nome_arquivo):
                    print(f"⏭️ Ignorado: {arquivo}")
                    continue

                print("📄 Processando:", caminho)

                dados = []

                try:
                    with open(caminho, "r", encoding="latin-1") as f:
                        linhas = f.readlines()
                except Exception as e:
                    print("❌ Erro ao ler arquivo:", e)
                    continue

                nome_upper = arquivo.upper()

                if nome_upper.startswith("CNT"):

                    for linha in linhas:
                        if linha.startswith("2"):
                            try:
                                cpf = linha[2:13].strip()
                                codigo_pagamento = linha[27:45].strip()
                                parcela = linha[79:81].strip()
                                valor = int(linha[45:57]) / 100
                                competencia = linha[57:63].strip()

                                inserir_pagamento(cpf, codigo_pagamento, parcela, valor, competencia)

                                dados.append({
                                    "CPF": cpf,
                                    "Código": codigo_pagamento,
                                    "Valor": valor
                                })

                            except:
                                pass

                elif "I02" in nome_upper:

                    for linha in linhas:
                        if linha.startswith("2"):
                            try:
                                codigo = linha[44:46].strip()
                                descricao = linha[46:96].strip()
                                codigo_pagamento = linha[26:44].strip()

                                status = classificar_rejeicao(codigo, descricao)
                                atualizar_status(codigo_pagamento, status)

                                dados.append({
                                    "Código": codigo_pagamento,
                                    "Status": status
                                })

                            except:
                                pass

                elif "I03" in nome_upper:

                    for linha in linhas:
                        if linha.startswith("2"):
                            try:
                                status_codigo = linha[83:85].strip()
                                codigo_pagamento = linha[15:33].strip()

                                status = classificar_status(status_codigo)
                                atualizar_status(codigo_pagamento, status)

                                dados.append({
                                    "Código": codigo_pagamento,
                                    "Status": status
                                })

                            except:
                                pass

                if dados:
                    houve_dados = True
                    df = pd.DataFrame(dados)
                    df.to_excel(writer, sheet_name=arquivo[:25], index=False)

                # 🔥 SEMPRE salva
                try:
                    salvar_arquivo_processado(nome_arquivo)
                except Exception as e:
                    print("Erro ao salvar controle:", e)

        if not houve_dados:
            pd.DataFrame({"Aviso": ["Nenhum dado"]}).to_excel(writer, sheet_name="SEM_DADOS", index=False)

    print("\n✅ Processamento finalizado!")