import yfinance as yf
import os
import requests

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
        # 1. 明确指定只下载 QQQ
        df = yf.download("QQQ", period="1y", progress=False)
        if df.empty:
            raise Exception("下载数据为空")
       
        # 2. 提取并强制转换为 float，避免 Series 类型错误
        price = float(df['Close'].iloc[-1])
        ma50 = float(df['Close'].rolling(window=50).mean().iloc[-1])
        ma200 = float(df['Close'].rolling(window=200).mean().iloc[-1])
       
        # 计算当日涨跌幅
        daily_pct = float((df['Close'].iloc[-1] - df['Close'].iloc[-2]) / df['Close'].iloc[-2])
       
        # 3. 计算状态
        if daily_pct < -0.03:
            current_state = 0
        elif price > ma50 and price > ma200:
            current_state = 2
        elif price > ma200:
            current_state = 1
        else:
            current_state = 0

        # 4. 状态对比与推送
        last_state = -1
        if os.path.exists(STATE_FILE):
            with open(STATE_FILE, "r") as f:
                content = f.read().strip()
                last_state = int(content) if content else -1

        is_manual = os.environ.get('GITHUB_EVENT_NAME') == 'workflow_dispatch'
       
        if current_state != last_state or is_manual:
            state_names = {0: "清仓/避险 (State 0)", 1: "持有 QQQ (State 1)", 2: "混合仓位 (State 2)"}
            header = "【手动测试成功】" if is_manual else "【策略状态变更】"
            msg = f"{header}\n当前状态: {state_names[current_state]}\nQQQ价格: {price:.2f}"
            send_telegram_msg(msg)
           
            with open(STATE_FILE, "w") as f:
                f.write(str(current_state))
        else:
            print(f"状态未改变 (当前: {current_state})，无需推送。")

    except Exception as e:
        error_msg = f"策略运行出错: {str(e)}"
        print(error_msg)
        send_telegram_msg(error_msg)

if __name__ == "__main__":
    run_strategy()
 
