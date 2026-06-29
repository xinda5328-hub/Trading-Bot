​import yfinance as yf
import pandas as pd
import requests
import os
import sys

def send_telegram_msg(message):
    token = os.environ.get('TOKEN')
    chat_id = os.environ.get('CHAT_ID')
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    params = {'chat_id': chat_id, 'text': message}
    try:
        response = requests.get(url, params=params, timeout=10)
        print(f"Telegram 响应码: {response.status_code}")
    except Exception as e:
        print(f"发送消息异常: {e}")

def run_strategy():
    print("开始运行策略...")
    try:
        # 使用更稳妥的数据下载方式
        data = yf.download("QQQ", period="1y", progress=False)
        if data.empty:
            raise Exception("未能下载到数据")
           
        price = data['Close'].iloc[-1]
        msg = f"【系统运行正常】QQQ 最新收盘价: {price:.2f}"
        print(msg)
        send_telegram_msg(msg)
    except Exception as e:
        error_msg = f"【运行错误】: {str(e)}"
        print(error_msg)
        send_telegram_msg(error_msg)

if __name__ == "__main__":
    run_strategy()
 
