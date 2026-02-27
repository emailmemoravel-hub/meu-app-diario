import streamlit as st
import pandas as pd
import json
import fitz  # PyMuPDF
import html
import unicodedata

st.set_page_config(page_title="Scanner PMSP Oficial", layout="wide")
st.title("🔎 Busca Combinada: Excel + JSON + PDF")

# Menu Lateral
st.sidebar.header("Arquivos Necessários")
file_excel = st.sidebar.file_uploader("1. Lista de Servidores (Excel)", type=['xlsx'])
file_json = st.sidebar.file_uploader("2. Diário Oficial (JSON)", type=['json'])
file_pdf = st.sidebar.file_uploader("3. Diário Oficial (PDF)", type=['pdf'])

def limpar_texto(t):
    if not t: 
        return ""
    texto = html.unescape(str(t)).replace('<p>', '').replace('</p>', '').upper().strip()
    # Remove acentos
    texto = ''.join(c for c in unicodedata.normalize('NFD', texto) if unicodedata.category(c) != 'Mn')
    return texto

if file_excel and file_json and file_pdf:
    try:
        # Excel
        df_servidores = pd.read_excel(file_excel)
        lista_servidores = df_servidores.iloc[:, [0, 1]].values 
        
        # JSON (objeto único)
        dados_json = json.load(file_json)

        # Se o JSON tiver chave 'edicao', usa; senão usa direto
        if isinstance(dados_json, dict):
            edicoes = dados_json.get('edicao', [])
        else:
            edicoes = dados_json
        
        # PDF
        pdf_bytes = file_pdf.read()
        doc_pdf = fitz.open(stream=pdf_bytes, filetype="pdf")
        
        resultados = []

        with st.spinner('Cruzando dados...'):
            for item in edicoes:
                conteudo_json = limpar_texto(item.get('conteudo', ''))
                orgao = item.get('orgao', 'Não informado')

                for serv in lista_servidores:
                    nome = limpar_texto(str(serv[0]))
                    rf = str(serv[1]).strip()
                    rf_curto = rf.split('-')[0].split('.')[0]

                    if nome in conteudo_json or rf_curto in conteudo_json:
                        pagina_final = "Verificar PDF"
                        for i in range(len(doc_pdf)):
                            texto_pag = limpar_texto(doc_pdf.load_page(i).get_text())
                            if nome in texto_pag or rf_curto in texto_pag:
                                pagina_final = i + 1
                                break
                        
                        resultados.append({
                            "Nome": nome,
                            "RF": rf,
                            "Órgão": orgao,
                            "Página": pagina_final
                        })

        if resultados:
            st.success(f"Encontradas {len(resultados)} ocorrências!")
            st.table(pd.DataFrame(resultados).drop_duplicates())
        else:
            st.warning("Nenhum servidor encontrado nos arquivos.")

    except Exception as e:
        st.error(f"Erro no processamento: {e}")
else:
    st.info("Aguardando upload dos 3 arquivos no menu lateral.")
