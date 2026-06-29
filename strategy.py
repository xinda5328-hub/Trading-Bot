import yfinance as yf
import pandas as pd
import numpy as np
import requests
import os
import sys

def send_telegram_msg(message):
    token = os.environ.get('TOKEN')
    chat_id = os.environ.get('CHAT_ID')
    if not token or not chat_id:
        print("未检测到环境变量，无法发送 Telegram 消息")
        return
    url = f"https://api.telegram.org/bot{token}/sendMessage?chat_id={chat_id}&text={message}"
    try:
        requests.get(url, timeout=10)
    except Exception as e:
        print(f"发送消息失败: {e}")

def run_strategy():
    print("开始获取数据...")
    data = yf.download(["QQQ", "TQQQ"], period="1y")['Close']
    df = data.dropna()
   
    # 计算指标
    df['MA200'] = df['QQQ'].rolling(window=200).mean()
    df['SMA50'] = df['QQQ'].rolling(window=50).mean()
    df['daily_pct'] = df['QQQ'].pct_change()
   
    # 取最新的状态
    curr = df.iloc[-1]
    prev = df.iloc[-2]
   
    price = curr['QQQ']
    drop = curr['daily_pct']
   
    # 状态逻辑 (0: 空仓, 1: 试仓, 2: 混合)
    def get_state(p, d, ma50, ma200):
        if d < -0.04: return 0
        if p > ma50: return 2
        if p > ma200: return 1
        return 0

    curr_state = get_state(price, drop, curr['SMA50'], curr['MA200'])
    prev_state = get_state(prev['QQQ'], prev['daily_pct'], prev['SMA50'], prev['MA200'])
   
    # 信号触发判定
    msg = ""
    if curr_state == 1 and prev_state == 0:
        msg = "【猎人信号】趋势确认，建议买入 QQQ 试仓！"
    elif curr_state == 2 and prev_state != 2:
        msg = "【猎人信号】行情强势，建议加仓 TQQQ 混合模式！"
    elif curr_state == 0 and prev_state != 0:
        msg = "【猎人信号】趋势破坏或波动异常，建议清仓转入 SGOV！"
   
    if msg:
        print(msg)
        send_telegram_msg(msg)
    else:
        print("无状态变化，保持现状。")

if __name__ == "__main__":
    run_strategy()
 