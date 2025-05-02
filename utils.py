import logging
import sys
import requests
from datetime import datetime
from config import settings
import MetaTrader5 as mt5


def setup_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
    )

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    file_handler = logging.FileHandler("trading_bot.log")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger


def calculate_sl_tp_in_price(
    symbol: str, direction: str, entry_price: float, usd_amount: float, lot_size: float
) -> tuple[float, float]:
    """
    Hitung harga SL/TP berdasarkan target USD.
    Return: (sl_price, tp_price)
    """
    symbol_info = mt5.symbol_info(symbol)
    point = symbol_info.point

    pip_value = 0.0001

    if "JPY" in symbol:
        pip_value = 0.01
        pip_size = pip_value * point * 100
    else:
        pip_size = pip_value

    if "JPY" in symbol:
        pip_value_usd = (pip_size / entry_price) * 100000 * lot_size
    else:
        pip_value_usd = pip_size * 100000 * lot_size

    pips = usd_amount / pip_value_usd

    # Hitung harga SL/TP
    if direction == "buy":
        sl_price = entry_price - (pips * pip_size)
        tp_price = entry_price + (pips * pip_size)
    else:
        sl_price = entry_price + (pips * pip_size)
        tp_price = entry_price - (pips * pip_size)

    # Round sesuai digit harga symbol
    digits = symbol_info.digits
    return (round(sl_price, digits), round(tp_price, digits))


class TelegramNotifier:
    def __init__(self):
        self.token = settings.TELEGRAM_TOKEN
        self.chat_id = settings.TELEGRAM_CHAT_ID

    def send_trade_notification(
        self, symbol: str, direction: str, price: float, sl: float, tp: float
    ) -> bool:
        if direction == "buy":
            sl_diff = price - sl
            tp_diff = tp - price
        else:
            sl_diff = sl - price
            tp_diff = price - tp

        symbol_info = mt5.symbol_info(symbol)
        point = symbol_info.point

        if "JPY" in symbol:
            pip_size = 0.01
            sl_usd = (sl_diff / pip_size) * (10 / price) * 100000 * settings.LOT_SIZE
            tp_usd = (tp_diff / pip_size) * (10 / price) * 100000 * settings.LOT_SIZE
        else:
            pip_size = 0.0001
            sl_usd = (sl_diff / pip_size) * 100000 * settings.LOT_SIZE
            tp_usd = (tp_diff / pip_size) * 100000 * settings.LOT_SIZE

        message = (
            f"<b>🚀 Trade Opened</b>\n\n"
            f"<b>Pair:</b> {symbol}\n"
            f"<b>Type:</b> {'BUY' if direction == 'buy' else 'SELL'}\n"
            f"<b>Price:</b> {price:.5f}\n"
            f"<b>Stop Loss:</b> {sl:.5f} (${sl_usd:.2f})\n"
            f"<b>Take Profit:</b> {tp:.5f} (${tp_usd:.2f})\n"
            f"<b>Time:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )
        return self._send_message(message)

    def _send_message(self, message: str) -> bool:
        url = f"https://api.telegram.org/bot{self.token}/sendMessage"
        payload = {"chat_id": self.chat_id, "text": message, "parse_mode": "HTML"}
        try:
            response = requests.post(url, json=payload)
            return response.status_code == 200
        except Exception as e:
            logging.error(f"Telegram error: {str(e)}")
            return False
