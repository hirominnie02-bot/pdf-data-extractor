# 必要なライブラリをインポートします。

import os  #ファイルやディレクトリの操作に使用します
import fitz  #PPyMuPDFライブラリをインポートします。PDFファイルの読み込みや操作に使用します。
import re # Pythonで正規表現（Regular Expression）を扱うための標準ライブラリ（reモジュール）を読み込む。

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
        # 請求先を抽出する
        # linesにカウンタを追加
        for i,line in enumerate(lines):
            if "御中" in line:
                # 御中の文字を削除
                billing_address=line.replace("御中", "").strip()
                # 分割したテキストの各行を出力します。
                print(billing_address)
            # 請求日を抽出(次の行が存在する時のみ処理)
            elif "請求日" in line and i+1 < len(lines):
                print(lines[i+1])
            # 請求金額を抽出(次の行が存在する時のみ処理)
            elif "請求金額" in line and i+1 < len(lines):
                # 全ての金額らしき数字をカンマ区切りで抽出
                money = re.findall(r"\d{1,3},\d{3}", text)
                # 請求金額を入れる空リスト
                numbers = []
                # カンマの除去
                numbers = money.replace(",","")
                # 数値型に変換
                numbers.append(int(money))
                # 一番大きな金額を抽出
                print(max(money))

    print(line)
        #print(lines)
# PDFファイルが格納されているディレクトリのパスを設定します。
directory_path = 'PDF'

# 処理対象のPDFファイル名を設定します。
filename = 'invoice-02.pdf'

# ディレクトリのパスとファイル名を結合して、PDFファイルのフルパスを作成します。os.path - ファイルの場所を扱う機能
pdf_path = os.path.join(directory_path, filename)
print(pdf_path)
# PDFファイルから情報を抽出する関数を呼び出します。
extract_information_from_pdf(pdf_path)