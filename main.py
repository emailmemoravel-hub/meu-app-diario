import streamlit as st
import pandas as pd
import json
import fitz  # Biblioteca para ler o PDF (PyMuPDF)
import re

st.set_page_config(page_title="Scanner PMSP Oficial", layout="wide")
st.title("🔎 Busca Integrada: Excel + JSON + PDF")

# Menu Lateral com os 3 campos obrigatórios
st.sidebar.header("Upload dos Arquivos")
file_excel = st.sidebar.file_uploader("1. Lista de Servidores (Excel)", type=['xlsx'])
file_json = st.sidebar.file_uploader("2. Diário Oficial (JSON)", type=['json'])
file_pdf = st.sidebar.file_uploader("3. Diário Oficial (PDF)", type=['pdf'])

if file_excel and file_json and file_pdf:
    try:
        # 1. Lendo a lista de servidores do Excel
        df_servidores = pd.read_excel(file_excel)
        # Considera Coluna 0 como Nome e Coluna 1 como RF
        lista_servidores = df_servidores.iloc[:, [0, 1]].values 

        # 2. Abrindo o PDF para identificar as páginas
        doc_pdf = fitz.open(stream=file_pdf.read(), filetype="pdf")
        
        # 3. Lendo o JSON para busca textual
        dados_json = json.load(file_json)
        publicacoes = dados_json.get('edicao', [])

        resultados = []

        with st.spinner('Cruzando dados...'):
            # Primeiro, buscamos no JSON (que é mais preciso para o texto)
            for pub in publicacoes:
                conteudo_json = str(pub.get('conteudo', '')).upper()
                orgao = pub.get('orgao', 'Não informado')

                for serv in lista_servidores:
                    nome = str(serv[0]).upper().strip()
                    rf = str(serv[1]).strip()
                    
                    # Se o nome ou RF estiver no texto do JSON desta publicação
                    if nome in conteudo_json or rf in conteudo_json:
                        # Agora buscamos em qual página do PDF esse servidor aparece
                        pagina_encontrada = "Não localizada no PDF"
                        for num_pag in range(len(doc_pdf)):
                            texto_pdf = doc_pdf.load_page(num_pag).get_text().upper()
                            if nome in texto_pdf or rf in texto_pdf:
                                pagina_encontrada = num_pag + 1
                                break # Achou a página, para de procurar no PDF
                        
                        resultados.append({
                            "Nome": nome,
                            "RF": rf,
                            "Órgão": orgao,
                            "Página": pagina_encontrada
                        })

        if resultados:
            st.success(f"Busca finalizada! Encontradas {len(resultados)} ocorrências.")
            df_final = pd.DataFrame(resultados).drop_duplicates()
            st.table(df_final)
        else:
            st.warning("Nenhum servidor da lista foi encontrado nos arquivos de hoje.")

    except Exception as e:
        st.error(f"Erro ao processar: {e}")
else:
    st.info("Aguardando o upload dos 3 arquivos para iniciar o cruzamento.")warning("Nada encontrado.")
