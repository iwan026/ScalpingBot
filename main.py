import time
import MetaTrader5 as mt5
from indicators.snr import detect_high_volume_snr
from indicators.rsi import detect_rsi_divergence
from indicators.ema import get_moving_averages
from indicators.price_action import detect_pinbar
from indicators.supply_demand import detect_supply_demand_zones
from indicators.fvg import detect_fvg_with_volume
from conditions.entry_conditions import check_entry_conditions
from utils.mt5_utils import setup_mt5, send_order
from utils.config import SYMBOLS, TIMEFRAME, LOT_SIZE
from utils.telegram_notifier import send_telegram_notification, format_signal_message

def main():
    if not setup_mt5():
        print("Gagal menginisialisasi MT5")
        return
    
    print(f"Memulai bot trading scalping untuk {len(SYMBOLS)} symbols")
    
    while True:
        for symbol in SYMBOLS:
            try:
                # Dapatkan data indikator
                indicators = {
                    'snr': detect_high_volume_snr(symbol, TIMEFRAME),
                    'rsi': detect_rsi_divergence(symbol, TIMEFRAME),
                    'ema': get_moving_averages(symbol, TIMEFRAME),
                    'pinbar': detect_pinbar(symbol, TIMEFRAME),
                    'supply_demand': detect_supply_demand_zones(symbol, TIMEFRAME),
                    'fvg': detect_fvg_with_volume(symbol, TIMEFRAME)
                }
                
                # Evaluasi kondisi entry
                signal = check_entry_conditions(symbol, indicators)
                tick = mt5.symbol_info_tick(symbol)
                current_price = tick.ask if signal['buy'] else tick.bid
                
                if signal['buy'] or signal['sell']:
                    # Kirim notifikasi Telegram
                    message = format_signal_message(symbol, signal, current_price)
                    send_telegram_notification(message)
                    
                    # Eksekusi order
                    print(f"\n{symbol} {'BUY' if signal['buy'] else 'SELL'} Signal - Confidence: {signal['confidence']:.0%}")
                    print("Alasan:", ", ".join(signal['reasons']))
                    
                    result = send_order(
                        symbol=symbol,
                        order_type=mt5.ORDER_BUY if signal['buy'] else mt5.ORDER_SELL,
                        lot=LOT_SIZE,
                        stop_loss=signal['sl'],
                        take_profit=signal['tp']
                    )
                    print("Order Result:", result)
                
            except Exception as e:
                print(f"\nError processing {symbol}: {str(e)}")
        
        # Tunggu hingga candle berikutnya
        time_left = 60 - (time.time() % 60)
        print(f"\nMenunggu {time_left:.1f} detik untuk candle berikutnya...", end='\r')
        time.sleep(time_left)

if __name__ == "__main__":
    main()