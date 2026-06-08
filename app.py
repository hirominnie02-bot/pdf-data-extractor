# 必要なライブラリをインポートします。

import streamlit as st #Streamlitをインポートします。
import fitz #fitzをインポート
import re # Pythonで正規表現（Regular Expression）を扱うための標準ライブラリ（reモジュール）を読み込む。


#関数達-------------------------------------

#会社名を抽出する関数を定義します。
def extract_company(lines):
    # linesにカウンタを追加
    for i,line in enumerate(lines):
        if "御中" in line:
            # 御中の文字を削除
            billing_address=line.replace("御中", "").strip()
            # 分割したテキストの各行を出力します。
            return billing_address
        #御中がない場合⇒様があるか探す 
        elif "様" in line:
            #その2行前を返す
            return lines[i - 2].strip() 
        
# 請求日を抽出する関数を定義します。
def extract_date(lines):
    for i, line in enumerate(lines):
        # パターン1: "請求日:"が行に含まれている場合、その行から請求日を抽出します。
        if "請求日:" in line:
            return line.replace("請求日:", "").strip()

        # パターン2: "請求日"の次の行に請求日があるパターン。
        elif "請求日" in line and i+1 < len(lines):
            return lines[i + 1].strip()    

# 日付を正規化する関数を定義します。
def normalize_date(date_text):
    if "年" in date_text:
        parts = re.findall(r"\d+", date_text)
        year = parts[0]
        month = parts[1]
        day = parts[2]
        return f"{year}-{month.zfill(2)}-{day.zfill(2)}"
    elif "/" in date_text:
        parts = re.findall(r"\d+", date_text)
        year = parts[2]
        month = parts[0]
        day = parts[1]
        return f"{year}-{month.zfill(2)}-{day.zfill(2)}"
    # yyyy-mm-ddが来た時にNoneが返るのを防ぐ
    return date_text 

# 請求額を抽出する関数を定義します。
def extract_money(lines):
    # 請求金額を抽出(次の行が存在する時のみ処理)
    for i, line in enumerate(lines):
        #ルール1：請求金額と同じ行に金額がある場合
        if "請求金額" in line: 
            money = re.findall(r"\d[\d,]*", line) #正規表現を使用して、数字とカンマの組み合わせを抽出します。r"\d[\d,]*"は、数字で始まり、その後に数字やカンマが続くパターンを表しています。
            if money:
                money = money[0].replace(",", "") #カンマを削除します。
                return int(money)
        
        #ルール2：請求金額の次の行に金額がある場合
            if i+1 < len(lines):
                target_text = lines[i+1]
                money = re.findall(r"\d[\d,]*",target_text)
                if money:
                    money = money[0].replace(",", "")
                    return int(money)

        #ルール3：請求金額の前5行から最大値を探さないと金額が分からない場合
                # 請求金額の近くの数字を抽出
                target_text = "\n".join(lines[i-5:i]) #請求金額の前5行を結合してテキストを作成
                money = re.findall(r"\d[\d,]*",target_text) 

                # デバッグ用に抽出したテキストを表示します。
                #print("抽出テキスト" + target_text)

                # 請求金額を入れる空リスト
                numbers = []

                # カンマの除去
                for m in money:
                    m = m.replace(",", "")
                    # 数値型に変換
                    numbers.append(int(m))
                    # 一番大きな金額を抽出
                
                if numbers:
                        # デバッグ用に抽出した数字を表示します。
                        #print("抽出した数字:", numbers)
                        return (max(numbers))    
                
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
st.write("PDFをアップロードすると会社名・請求日・請求金額を抽出します。")

uploaded_files = st.file_uploader(
    "PDFを選択してください（複数選択可能）",
    accept_multiple_files = True #複数ファイルを許可するパラメータ
    )


all_data = [] #抽出情報を貯めるリストを作る
if uploaded_files: #ファイルがアップロードされた場合の処理を行います。
    for uploaded_file in uploaded_files:
        st.caption(uploaded_file.name)
    
    # st.write(type(uploaded_files))
    # st.write(uploaded_files)

        pdf_bytes = uploaded_file.getvalue()

        result = extract_information_from_pdf(pdf_bytes)
        all_data.append(result)

        st.subheader("抽出結果")

        st.write("会社名:", result["company"])
        st.write("請求日:", result["date"])
        st.metric("請求金額", f"{result['money']:,}円") #数値をカンマ区切りで表示するために、f文字列と:,を使用しています。
        st.success("抽出完了！")

    st.write(all_data)
    
    #CSV形式のデータを作成する
    csv_data = f"""会社名,請求日,請求金額
    {result["company"]},{result["date"]},{result["money"]}
    """
    st.download_button(
    label="CSVダウンロード",
    data = csv_data.encode("utf-8-sig"),
    file_name="請求情報.csv"
    )

