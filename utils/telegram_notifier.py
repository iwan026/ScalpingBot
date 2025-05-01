import requests
from utils.config import TELEGRAM_TOKEN, TELEGRAM_CHAT_ID

def send_telegram_notification(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "HTML"
    }
    
    try:
        response = requests.post(url, json=payload)
        return response.status_code == 200
    except Exception as e:
        print(f"Gagal mengirim notifikasi Telegram: {e}")
        return False

def format_signal_message(symbol, signal, price):
    message = (
        f"<b>🚀 SINYAL TRADING DITEMUKAN</b>\n\n"
        f"<b>Pair:</b> {symbol}\n"
        f"<b>Arah:</b> {'BUY' if signal['buy'] else 'SELL'}\n"
        f"<b>Harga:</b> {price:.5f}\n"
        f"<b>Confidence:</b> {signal['confidence']:.0%}\n"
        f"<b>Alasan:</b>\n- " + "\n- ".join(signal['reasons']) + "\n\n"
        f"<b>SL:</b> {signal['sl']:.5f}\n"
        f"<b>TP:</b> {signal['tp']:.5f}"
    )
    return message