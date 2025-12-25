import os  
import sys  
from playwright.sync_api import sync_playwright  
import requests  
  
# 監視対象URL  
TARGET_URL = "https://www.iijmio.jp/device/oppo/findx9.html"  
  
def send_line(message):  
    token = os.environ.get("LINE_TOKEN")  
    user_id = os.environ.get("LINE_USER_ID")  
      
    if not token or not user_id:  
        print("Error: LINE settings are missing.")  
        return  
  
    url = "https://api.line.me/v2/bot/message/push"  
    headers = {  
        "Content-Type": "application/json",  
        "Authorization": f"Bearer {token}"  
    }  
    data = {  
        "to": user_id,  
        "messages": [{"type": "text", "text": message}]  
    }  
    try:  
        requests.post(url, headers=headers, json=data)  
    except Exception as e:  
        print(f"Request Error: {e}")  
  
def check_stock():  
    with sync_playwright() as p:  
        browser = p.chromium.launch(headless=True)  
        page = browser.new_page()  
          
        print(f"Checking: {TARGET_URL}")  
        page.goto(TARGET_URL)  
          
        try:  
            page.wait_for_load_state("networkidle", timeout=30000)  
        except:  
            print("Time out waiting for page load")  
  
        content = page.content()  
          
        # --- 判定ロジックの修正 ---  
          
        # 1. 「一時在庫切れ」があるか？  
        is_out_of_stock = "一時在庫切れ" in content  
          
        # 2. 「販売再開予定」があるか？（←これを追加！これが今回の原因）  
        is_scheduled = "販売再開予定" in content  
          
        # 3. 「お申し込み」の文字があるか？  
        has_apply_text = "お申し込み" in content  
  
        print(f"Status - OutOfStock: {is_out_of_stock}, Scheduled: {is_scheduled}, ApplyText: {has_apply_text}")  
  
        # 【結論】  
        # 「在庫切れ」でもなく、かつ「再開予定」でもなく、かつ「お申し込み」がある場合のみ通知  
        if not is_out_of_stock and not is_scheduled and has_apply_text:  
            print("Stock FOUND!")  
            send_line(f"🚨【IIJmio在庫復活】\nOPPO Find X9 が購入可能になりました！\n\n{TARGET_URL}")  
        else:  
            print("Stock not available (Sold out or Scheduled).")  
  
        browser.close()  
  
if __name__ == "__main__":  
    check_stock()  
