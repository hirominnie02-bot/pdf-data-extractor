import streamlit as st #Streamlitをインポートします。

#関数達-------------------------------------

# 引数はPDFファイルのパスを受け取ります。
def extract_information_from_pdf(pdf_bytes):
    #PDFファイルを開く
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")

    # PDFの各ページについて処理を行います。
    for page in doc:
        # 現在のページからテキストを取得します。get_text() - HTMLタグの中の“文字だけ”取り出すメソッド
        text = page.get_text()
        # 取得したテキストを改行ごとに分割し、リストにします。
        lines = text.split('\n')
        company = extract_company(lines)
        date = extract_date(lines)
        # 確認用
        # print("変換前：" + date)
        date = normalize_date(date)
        # 確認用
        # print("変換後：" + date)
        money = extract_money(lines)

        return {
            "company": company,
            "date": date,
            "money": money
        }
    

# Streamlit-------------------------------------

st.title("請求書PDF情報抽出ツール")

uploaded_file = st.file_uploader("PDFを選択してください")



if uploaded_file: #ファイルがアップロードされた場合の処理を行います。
    st.write(uploaded_file.name)

    pdf_bytes = uploaded_file.getvalue()


