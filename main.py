import streamlit as st
import pandas as pd
import fitz  # PyMuPDF

st.set_page_config(page_title="Busca Diário Oficial", layout="wide")
st.title("🔎 Busca de Servidores PMSP")

st.sidebar.header("Upload dos Arquivos")
file_excel = st.sidebar.file_uploader("1. Lista de Servidores (Excel)", type=['xlsx'])
file_pdf = st.sidebar.file_uploader("2. Diário Oficial (PDF)", type=['pdf'])

if file_excel and file_pdf:
    df = pd.read_excel(file_excel)
    doc = fitz.open(stream=file_pdf.read(), filetype="pdf")
    res = []

    for num in range(len(doc)):
        txt = doc.load_page(num).get_text().upper()
        for _, s in df.iterrows():
            nome, rf = str(s[0]).upper(), str(s[1])
            if nome in txt or rf in txt:
                res.append({"Nome": nome, "RF": rf, "Página": num + 1})

    if res:
        st.table(pd.DataFrame(res).drop_duplicates())
    else:
        st.warning("Nada encontrado.")
