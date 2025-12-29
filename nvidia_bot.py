import requests
import os
from datetime import datetime
import pytz

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

def get_nvidia_price():
    try:
        import yfinance as yf
        nvda = yf.Ticker("NVDA")
        data = nvda.history(period="2d")
        
        current_price = data['Close'].iloc[-1]
        previous_price = data['Close'].iloc[-2]
        change_percent = ((current_price - previous_price) / previous_price) * 100
        
        return {
            'current': round(current_price, 2),
            'previous': round(previous_price, 2),
            'change': round(change_percent, 2)
        }
    except Exception as e:
        print(f"Error: {e}")
        return None

def is_trading_hours():
    ny_tz = pytz.timezone('America/New_York')
    now = datetime.now(ny_tz)
    
    if now.weekday() >= 5:
        return False
    if now.hour < 9 or now.hour > 16:
        return False
    if now.hour == 9 and now.minute < 30:
        return False
    
    return True

def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {
        'chat_id': TELEGRAM_CHAT_ID,
        'text': message,
        'parse_mode': 'Markdown'
    }
    
    try:
        response = requests.post(url, data=data)
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def main():
    print(f"🤖 NVIDIA Alert Bot - {datetime.now()}")
    
    if not is_trading_hours():
        print("⏰ Not trading hours")
        return
    
    price_data = get_nvidia_price()
    if not price_data:
        print("Error getting price")
        return
    
    change = price_data['change']
    current = price_data['current']
    
    print(f"💰 NVIDIA: ${current} (Change: {change}%)")
    
    if abs(change) < 2:
        print("Normal movement")
        return
    
    emoji = "🔴" if change < 0 else "🟢"
    message = f"{emoji} *NVIDIA ALERT!*\n\n"
    message += f"💵 Price: ${current}\n"
    message += f"📊 Change: {change}%\n"
    message += f"🕐 {datetime.now(pytz.timezone('Asia/Jerusalem')).strftime('%H:%M:%S IST')}\n"
    
    if change < -2:
        message += "\n⚠️ *Significant Drop*\n• Negative news?\n• Market correction?"
    elif change > 3:
        message += "\n📈 *Strong Gain*\n• Positive news?\n• AI chip demand?"
    
    send_telegram_message(message)

if __name__ == "__main__":
    main()
