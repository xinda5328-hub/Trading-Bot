import yfinance as yf
import os
import requests
import pandas as pd
import numpy as np
# 推送通知函数
def send_telegram_msg(message):
    token = os.environ.get('TOKEN')
    chat_id = os.environ.get('CHAT_ID')
    if not token or not chat_id:
        print("未检测到 Telegram 配置，跳过推送")
        return
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    try:
        requests.get(url, params={'chat_id': chat_id, 'text': message}, timeout=10)
    except Exception as e:
        print(f"推送失败: {e}")
def run_strategy():
    # 1. 获取数据 (获取过去 1 年数据用于计算指标)
    tickers = ["QQQ", "TQQQ", "SGOV"]
    df = yf.download(tickers, period="1y", progress=False)['Close'].dropna()
    
    # 2. 计算指标
    curr_qqq = float(df['QQQ'].iloc[-1])
    ma200 = float(df['QQQ'].rolling(window=200).mean().iloc[-1])
    
    # 计算当前波动率 (20日) 与 历史均值波动率 (200日)
    vol = df['QQQ'].pct_change().std()
    vol_ma = df['QQQ'].pct_change().rolling(window=200).mean().iloc[-1]
    
    # 3. 核心策略逻辑
    # State 0: 现金防御 (SGOV)
    # State 1: 降杠杆避险 (QQQ)
    # State 2: 激进进攻 (50% QQQ + 50% TQQQ)
    
    if curr_qqq < ma200:
        state = 0
        reason = "趋势破位 (跌破 MA200) -> 现金防御 (SGOV)"
    elif vol > vol_ma * 1.3:
        state = 1
        reason = "波动率异常 (超过1.3倍均值) -> 降杠杆 (持仓 QQQ)"
    else:
        state = 2
        reason = "环境平稳 -> 激进进攻 (混合仓)"
    
    # 4. 构建推送内容
    state_names = {0: "现金/避险", 1: "保守持仓 (QQQ)", 2: "激进进攻 (混合仓)"}
    msg = (
        f"【策略监控状态】\n"
        f"当前状态: {state_names[state]}\n"
        f"判定逻辑: {reason}\n"
        f"QQQ 当前价: {curr_qqq:.2f}\n"
        f"MA200 参考值: {ma200:.2f}"
    )
    
    print(msg) # 本地打印调试
    send_telegram_msg(msg) # 发送通知
if __name__ == "__main__":
    run_strategy()
