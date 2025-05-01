from .base import BaseIndicator, IndicatorResult
import talib
import numpy as np

class EMAIndicator(BaseIndicator):
    def load_config(self):
        from config import settings
        return settings.INDICATOR_CONFIG["EMA"]
    
    def calculate(self):
        df = self.get_data(max(self.config["fast"], self.config["slow"]))
        close_prices = df['close'].values
        
        # Hitung EMA
        ema_fast = talib.EMA(close_prices, timeperiod=self.config["fast"])
        ema_slow = talib.EMA(close_prices, timeperiod=self.config["slow"])
        
        # Deteksi crossover
        crossover = self._detect_crossover(ema_fast, ema_slow)
        
        return IndicatorResult(
            symbol=self.symbol,
            timeframe=self.timeframe,
            values={
                "fast": ema_fast[-1],
                "slow": ema_slow[-1],
                "trend": "up" if ema_fast[-1] > ema_slow[-1] else "down",
                "crossover": crossover
            },
            timestamp=df['time'].iloc[-1],
            is_valid=not (np.isnan(ema_fast[-1]) or np.isnan(ema_slow[-1]))
        )
    
    def _detect_crossover(self, fast, slow):
        """Deteksi golden cross/death cross"""
        if len(fast) < 2 or len(slow) < 2:
            return None
            
        curr_fast, prev_fast = fast[-1], fast[-2]
        curr_slow, prev_slow = slow[-1], slow[-2]
        
        if curr_fast > curr_slow and prev_fast <= prev_slow:
            return "golden"
        elif curr_fast < curr_slow and prev_fast >= prev_slow:
            return "death"
        return None