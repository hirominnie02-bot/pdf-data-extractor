import streamlit as st 

st.title("請求書PDF情報抽出ツール")

uploaded_file = st.file_uploader("PDFを選択してください")

st.write(uploaded_file)
st.write(type(uploaded_file))
st.write(uploaded_file.name)

st.write(type(uploaded_file.getvalue()))