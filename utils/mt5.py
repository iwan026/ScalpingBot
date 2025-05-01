import MetaTrader5 as mt5
from config import settings
import time

class MT5Connector:
    def __init__(self):
        self.connected = False
        self.connect()

    def connect(self):
        if not mt5.initialize(
            login=settings.MT5["login"],
            server=settings.MT5["server"],
            password=settings.MT5["password"],
            timeout=settings.MT5["timeout"]
        ):
            print(f"Gagal konek ke MT5: {mt5.last_error()}")
            self.connected = False
            return False
        
        self.connected = True
        print("Berhasil terkoneksi dengan MT5")
        return True

    def send_order(self, symbol: str, order_type: str, lot: float, sl: float, tp: float):
        if not self.connected:
            if not self.connect():
                return None

        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": symbol,
            "volume": lot,
            "type": mt5.ORDER_BUY if order_type == 'buy' else mt5.ORDER_SELL,
            "price": mt5.symbol_info_tick(symbol).ask if order_type == 'buy' else mt5.symbol_info_tick(symbol).bid,
            "sl": sl,
            "tp": tp,
            "deviation": 10,
            "magic": 123456,
            "comment": "Python Scalping Bot",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC
        }

        result = mt5.order_send(request)
        if result.retcode != mt5.TRADE_RETCODE_DONE:
            print(f"Order gagal: {result.comment}")
            return None
        
        return result