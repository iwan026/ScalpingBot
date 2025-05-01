import MetaTrader5 as mt5
from utils.config import SYMBOLS

def setup_mt5():
    if not mt5.initialize():
        print("Gagal menginisialisasi MT5, error code:", mt5.last_error())
        return False
    
    # Preload market data untuk semua symbol
    for symbol in SYMBOLS:
        mt5.symbol_select(symbol, True)
    
    return True

def send_order(symbol, order_type, lot, stop_loss=None, take_profit=None):
    price = mt5.symbol_info_tick(symbol).ask if order_type == mt5.ORDER_BUY else mt5.symbol_info_tick(symbol).bid
    
    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": symbol,
        "volume": lot,
        "type": order_type,
        "price": price,
        "sl": stop_loss,
        "tp": take_profit,
        "deviation": 10,
        "magic": 123456,
        "comment": "Python Scalping Bot",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_IOC,
    }
    
    return mt5.order_send(request)