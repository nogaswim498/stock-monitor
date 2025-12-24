import os  
import sys  
from playwright.sync_api import sync_playwright  
import requests  
  
# 監視対象URL  
TARGET_URL = "https://www.iijmio.jp/device/oppo/findx9.html"  
  
def send_line(message):  
    token = os.environ["LINE_TOKEN"]  
    user_id = os.environ["LINE_USER_ID"]  
    url = "https://api.line.me/v2/bot/message/push"  
    headers = {  
        "Content-Type": "application/json",  
        "Authorization": f"Bearer {token}"  
    }  
    data = {  
        "to": user_id,  
        "messages": [{"type": "text", "text": message}]  
    }  
    requests.post(url, headers=headers, json=data)  
  
def check_stock():  
    with sync_playwright() as p:  
        # ブラウザを起動（ヘッドレスモード＝画面なしで高速動作）  
        browser = p.chromium.launch(headless=True)  
        page = browser.new_page()  
          
        # ページにアクセス  
        print(f"Checking: {TARGET_URL}")  
        page.goto(TARGET_URL)  
          
        # 重要なポイント：ページが完全に読み込まれるまで待つ  
        # 「カートに入れる」や「在庫切れ」などの要素が出るまで最大30秒待機  
        try:  
            page.wait_for_load_state("networkidle", timeout=30000)  
        except:  
            print("Time out waiting for page load")  
  
        # ページ内のテキストをすべて取得  
        content = page.content()  
          
        # 判定ロジック  
        # 1. 「一時在庫切れ」の文字があるか  
        is_out_of_stock = "一時在庫切れ" in content  
          
        # 2. 「お申し込み」ボタンが押せる状態か（classチェックなどは複雑なのでまずは文字で）  
        has_apply_text = "お申し込み" in content  
  
        print(f"Status - OutOfStockText: {is_out_of_stock}, ApplyText: {has_apply_text}")  
  
        # 「在庫切れ」の文字がなく、かつ「お申し込み」の文字がある場合  
        if not is_out_of_stock and has_apply_text:  
            print("Stock FOUND!")  
            send_line(f"🚨【IIJmio在庫復活】\nOPPO Find X9 の在庫が復活した可能性があります！\nブラウザで確認しました。\n\n{TARGET_URL}")  
        else:  
            print("Stock not available.")  
  
        browser.close()  
  
if __name__ == "__main__":  
    check_stock()  
