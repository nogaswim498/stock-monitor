import os  
from playwright.sync_api import sync_playwright  
import requests  
  
# テスト用に在庫があるReno11 AなどのURLのままにしてください  
TARGET_URL = "https://www.iijmio.jp/device/oppo/a79_5g.html"  
  
def send_line(message):  
    token = os.environ.get("LINE_TOKEN")  
    user_id = os.environ.get("LINE_USER_ID")  
      
    # トークンやIDが設定されているか確認  
    if not token:  
        print("Error: LINE_TOKEN is missing.")  
        return  
    if not user_id:  
        print("Error: LINE_USER_ID is missing.")  
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
      
    # エラーの詳細を確認する  
    try:  
        res = requests.post(url, headers=headers, json=data)  
        print(f"--- LINE API Response ---")  
        print(f"Status Code: {res.status_code}") # 200なら成功、400系なら失敗  
        print(f"Message: {res.text}")            # エラーの理由が表示されます  
        print(f"-------------------------")  
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
            pass  
  
        content = page.content()  
        is_out_of_stock = "一時在庫切れ" in content  
        has_apply_text = "お申し込み" in content  
  
        print(f"Status - OutOfStockText: {is_out_of_stock}, ApplyText: {has_apply_text}")  
  
        if not is_out_of_stock and has_apply_text:  
            print("Stock FOUND! Sending notification...")  
            send_line(f"🚨【IIJmio在庫復活】\n在庫あります！\n{TARGET_URL}")  
        else:  
            print("Stock not available.")  
  
        browser.close()  
  
if __name__ == "__main__":  
    check_stock()  
