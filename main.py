# 必要なライブラリをインポートします。

import os  #ファイルやディレクトリの操作に使用します
import fitz  #PPyMuPDFライブラリをインポートします。PDFファイルの読み込みや操作に使用します。
import re # Pythonで正規表現（Regular Expression）を扱うための標準ライブラリ（reモジュール）を読み込む。
import csv # CSVファイルを扱うための道具箱を使います！

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
    
# 会社名を抽出する関数を定義します。
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

# 請求額を抽出する関数を定義します。
def extract_money(lines):
    # 請求金額を抽出(次の行が存在する時のみ処理)
    for i, line in enumerate(lines):
        #ルール1：請求金額と同じ行に金額がある場合
        if "請求金額" in line: 
            money = re.findall(r"\d[\d,]*", line) 
            return money
        
        #ルール2：請求金額の次の行に金額がある場合
        elif "請求金額" in line and i+1 < len(lines):
            target_text = lines[i+1]
            money = re.findall(r"\d[\d,]*",target_text) #正規表現を使用して、数字とカンマの組み合わせを抽出します。r"\d[\d,]*"は、数字で始まり、その後に数字やカンマが続くパターンを表しています。
            return money
        
        #ルール3：請求金額の前5行から最大値を探さないと金額が分からない場合
        elif "請求金額" in line and i+1 < len(lines):
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
        
# PDFファイルから特定のキーワードに続くテキストを抽出する関数を定義します。
# 引数はPDFファイルのパスを受け取ります。
def extract_information_from_pdf(file_path):
    #PDFファイルを開く
    doc = fitz.open(file_path)

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

#デバック用  
filename = "invoice-03.pdf"
pdf_path = os.path.join("PDF", filename)
doc = fitz.open(pdf_path)
for page in doc:
    text = page.get_text()
    lines = text.split("\n")

    for i, line in enumerate(lines):
        print(i, line)


# 抽出した情報を格納するための空のリストを作成します。
all_data = []

# 指定されたディレクトリ内のすべてのPDFファイルを処理します。
for filename in os.listdir("PDF"):
    # ファイルがPDFファイルであるかどうかを確認します。
    if filename.endswith(".pdf"):
        # PDFファイルのパスを作成します。os.path.join()は、複数のパス要素を結合して1つのパスを作成するための関数です。ここでは、"PDF"ディレクトリとファイル名を結合して、PDFファイルの完全なパスを作成しています。
        pdf_path = os.path.join("PDF", filename)

        # PDFファイルから情報を抽出する関数を呼び出します。
        result = extract_information_from_pdf(pdf_path)
        all_data.append(result)

#デバッグ用にファイル名と抽出結果を表示します。
print(all_data)




# PDFファイルから抽出した情報をCSVに書きだします。
# CSVファイルを開く。
with open("請求情報.csv","w",newline = "",encoding = "utf-8-sig") as f:
    writer = csv.writer(f) #CSVに書き込む係を作る(fで開いたファイルに対して書き込みを行う準備)
    writer.writerow(["会社名","請求日","請求金額"])
    for data in all_data:
        writer.writerow([
        data["company"],
        data["date"],
        data["money"]
        ])