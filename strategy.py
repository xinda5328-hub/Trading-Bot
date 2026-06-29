import yfinance as yf
import pandas as pd
import requests
import os

def send_telegram_msg(message):
    token = os.environ.get('TOKEN')
    chat_id = os.environ.get('CHAT_ID')
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    params = {'chat_id': chat_id, 'text': message}
    try:
        requests.get(url, params=params, timeout=10)
    except Exception as e:
        print(f"发送消息异常: {e}")

def run_strategy():
    try:
        # 1. 下载 QQQ (用于判断趋势) 和 TQQQ (用于展示价格)
        # 增加数据下载容错
        data = yf.download(["QQQ", "TQQQ"], period="1y", progress=False)
       
        # 2. 计算 QQQ 的 200 日均线
        qqq_close = data['Close']['QQQ']
        ma200 = qqq_close.rolling(window=200).mean().iloc[-1]
        current_qqq = float(qqq_close.iloc[-1])
       
        # 3. 获取 TQQQ 当前价格
        current_tqqq = float(data['Close']['TQQQ'].iloc[-1])
       
        # 4. 策略逻辑判断
        if current_qqq > ma200:
            signal = "【持有信号】QQQ 处于 MA200 之上，多头趋势。"
        else:
            signal = "【清仓/避险】QQQ 跌破 MA200，风险区域。"
           
        # 5. 拼接消息
        msg = (f"【监控报告】\n"
               f"QQQ 最新价: {current_qqq:.2f}\n"
               f"QQQ MA200: {ma200:.2f}\n"
               f"TQQQ 最新价: {current_tqqq:.2f}\n"
               f"------------------\n"
               f"{signal}")
       
        print(msg)
        send_telegram_msg(msg)
       
    except Exception as e:
        error_msg = f"【运行错误】: {str(e)}"
        print(error_msg)
        send_telegram_msg(error_msg)

if __name__ == "__main__":
    run_strategy()
 
