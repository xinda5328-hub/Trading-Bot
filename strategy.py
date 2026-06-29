​import yfinance as yf
import pandas as pd
import requests
import os

def send_telegram_msg(message):
    token = os.environ.get('TOKEN')
    chat_id = os.environ.get('CHAT_ID')
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    params = {'chat_id': chat_id, 'text': message}
   
    print(f"DEBUG: Token={token[:5]}..., ChatID={chat_id}")
    try:
        response = requests.get(url, params=params, timeout=10)
        print(f"DEBUG: 响应码={response.status_code}, 内容={response.text}")
    except Exception as e:
        print(f"DEBUG: 异常={e}")

def run_strategy():
    # 1. 强制推送测试
    print("正在执行策略分析...")
    send_telegram_msg("【系统测试】猎人系统已启动，正在检查市场状态...")
   
    # 2. 数据分析
    try:
        data = yf.download(["QQQ"], period="1y")['Close']
        ma200 = data.rolling(window=200).mean().iloc[-1]
        price = data.iloc[-1]
        msg = f"【市场监控】当前价格: {price:.2f}, MA200: {ma200:.2f}"
        print(msg)
        send_telegram_msg(msg)
    except Exception as e:
        print(f"数据获取失败: {e}")
        send_telegram_msg(f"数据获取失败: {e}")

if __name__ == "__main__":
    run_strategy()
 
