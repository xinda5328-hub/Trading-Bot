import yfinance as yf
import os
import requests

# 状态文件名
STATE_FILE = "last_state.txt"

def send_telegram_msg(message):
    token = os.environ.get('TOKEN')
    chat_id = os.environ.get('CHAT_ID')
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    try:
        requests.get(url, params={'chat_id': chat_id, 'text': message}, timeout=10)
    except Exception as e:
        print(f"推送失败: {e}")

def run_strategy():
    try:
        # 1. 下载数据
        qqq = yf.download("QQQ", period="1y", progress=False)['Close']
        ma200 = qqq.rolling(window=200).mean().iloc[-1]
        ma50 = qqq.rolling(window=50).mean().iloc[-1]
        daily_pct = qqq.pct_change().iloc[-1]
        price = qqq.iloc[-1]

        # 2. 计算当前状态
        if daily_pct < -0.04: current_state = 0
        elif price > ma50 and price > ma200: current_state = 2
        elif price > ma200: current_state = 1
        else: current_state = 0

        # 3. 读取上次状态
        last_state = -1 # 默认值
        if os.path.exists(STATE_FILE):
            with open(STATE_FILE, "r") as f:
                last_state = int(f.read().strip())

        # 4. 判断逻辑：状态改变则推送，或手动触发测试时推送
        is_manual = os.environ.get('GITHUB_EVENT_NAME') == 'workflow_dispatch'
       
        if current_state != last_state or is_manual:
            state_names = {0: "清仓/避险 (State 0)", 1: "持有 QQQ (State 1)", 2: "混合仓位 (State 2)"}
            header = "【手动测试成功】" if is_manual else "【策略状态变更】"
            msg = f"{header}\n当前状态: {state_names[current_state]}\n价格: {price:.2f}"
            send_telegram_msg(msg)
           
            # 保存新状态
            with open(STATE_FILE, "w") as f:
                f.write(str(current_state))
        else:
            print("状态未改变，无需推送。")

    except Exception as e:
        send_telegram_msg(f"策略异常: {str(e)}")

if __name__ == "__main__":
    run_strategy()
 
