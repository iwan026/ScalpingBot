import requests
from config import settings
from datetime import datetime

class TelegramNotifier:
    def __init__(self):
        self.token = settings.TELEGRAM["token"]
        self.chat_id = settings.TELEGRAM["chat_id"]
        self.timeout = settings.TELEGRAM["timeout"]

    def send_signal(self, signal):
        message = self._format_message(signal)
        return self._send_message(message)

    def _format_message(self, signal):
        return (
            f"🚀 *Sinyal Trading* 🚀\n\n"
            f"• Pair: `{signal.symbol}`\n"
            f"• Arah: {'🟢 BUY' if signal.direction == 'buy' else '🔴 SELL'}\n"
            f"• Entry: `{signal.entry_price:.5f}`\n"
            f"• SL: `{signal.stop_loss:.5f}`\n"
            f"• TP: `{signal.take_profit:.5f}`\n"
            f"• Confidence: `{signal.confidence:.0%}`\n"
            f"• Waktu: `{datetime.fromtimestamp(signal.timestamp)}`\n\n"
            f"*Alasan:*\n"
            + "\n".join([f"✓ {reason}" for reason in signal.reasons])
        )

    def _send_message(self, text):
        url = f"https://api.telegram.org/bot{self.token}/sendMessage"
        payload = {
            "chat_id": self.chat_id,
            "text": text,
            "parse_mode": "Markdown",
            "disable_web_page_preview": True
        }

        try:
            response = requests.post(
                url,
                json=payload,
                timeout=self.timeout
            )
            return response.status_code == 200
        except Exception as e:
            print(f"Gagal kirim notifikasi: {e}")
            return False