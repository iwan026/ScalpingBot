import time
import MetaTrader5 as mt5
from datetime import datetime
from typing import Dict, Optional

# Import modul kustom
from config import settings
from indicators import (
    SNRIndicator,
    RSIIndicator, 
    EMAIndicator,
    FVGIndicator,
    PriceActionIndicator
)
from conditions.entry import EntryConditions
from utils.mt5 import MT5Connector
from utils.notifier import TelegramNotifier

class ScalpingBot:
    def __init__(self):
        self.mt5 = MT5Connector()
        self.notifier = TelegramNotifier()
        self.active_trades = {}
        self.today = datetime.now().date()
        
        # Inisialisasi indikator
        self.indicators = {
            'snr': SNRIndicator,
            'rsi': RSIIndicator,
            'ema': EMAIndicator,
            'fvg': FVGIndicator,
            'price_action': PriceActionIndicator
        }
        
    def check_market_conditions(self, symbol: str) -> Optional[Dict]:
        """Mengumpulkan dan mengevaluasi semua data indikator"""
        if not mt5.symbol_info(symbol).visible:
            return None
            
        indicator_data = {}
        for name, indicator_class in self.indicators.items():
            try:
                indicator = indicator_class(symbol, settings.TIMEFRAME)
                indicator_data[name] = indicator.calculate()
            except Exception as e:
                print(f"Error calculating {name} for {symbol}: {str(e)}")
                indicator_data[name] = None
                
        return indicator_data
    
    def manage_risk(self) -> bool:
        """Manajemen risiko harian"""
        if datetime.now().date() != self.today:
            self.today = datetime.now().date()
            self.active_trades.clear()
            return True
            
        if len(self.active_trades) >= settings.MAX_TRADES:
            print("Max trades reached for today")
            return False
            
        return True
    
    def run(self):
        print(f"Memulai ScalpingBot (Min. 3 Konfirmasi Indikator)")
        print(f"Pair: {', '.join(settings.SYMBOLS)} | TF: {settings.TIMEFRAME}")
        print(f"Risk: SL={settings.STOP_LOSS_PIPS}pips | TP={settings.TAKE_PROFIT_PIPS}pips\n")
        
        while True:
            try:
                if not self.manage_risk():
                    time.sleep(60)
                    continue
                
                for symbol in settings.SYMBOLS:
                    try:
                        indicators = self.check_market_conditions(symbol)
                        if not indicators:
                            continue
                            
                        signal = EntryConditions(symbol).check_conditions(indicators)
                        
                        if signal.direction and len(signal.reasons) >= 3:
                            print(f"\n{'='*40}")
                            print(f"🚨 SIGNAL {signal.direction.upper()} {symbol}")
                            print(f"📊 Price: {signal.entry_price:.5f}")
                            print(f"🔍 Alasan ({len(signal.reasons)}/3):")
                            for reason in signal.reasons:
                                print(f" - {reason}")
                            print(f"💎 Confidence: {signal.confidence:.0%}")
                            
                            # Eksekusi order
                            result = self.mt5.send_order(
                                symbol=symbol,
                                order_type=signal.direction,
                                lot=settings.LOT_SIZE,
                                sl=signal.stop_loss,
                                tp=signal.take_profit
                            )
                            
                            if result:
                                self.active_trades[symbol] = {
                                    'ticket': result.order,
                                    'time': datetime.now()
                                }
                                self.notifier.send_signal(signal)
                        
                    except Exception as e:
                        print(f"\n⚠️ Error processing {symbol}: {str(e)}")
                        continue
                
                time_left = 60 - (time.time() % 60)
                print(f"\r⏳ Next candle in {time_left:.1f}s", end="", flush=True)
                time.sleep(max(0.1, time_left))
                
            except KeyboardInterrupt:
                print("\n🛑 Bot dihentikan manual")
                break
            except Exception as e:
                print(f"\n‼️ Critical error: {str(e)}")
                time.sleep(60)

if __name__ == "__main__":
    bot = ScalpingBot()
    bot.run()