from .base import BaseIndicator, IndicatorResult
import talib
import numpy as np

class RSIIndicator(BaseIndicator):
    def load_config(self):
        from config import settings
        return settings.INDICATOR_CONFIG["RSI"]
    
    def calculate(self):
        df = self.get_data(self.config["lookback"])
        close_prices = df['close'].values
        
        # Hitung RSI menggunakan TA-Lib
        rsi_values = talib.RSI(close_prices, timeperiod=self.config["period"])
        
        # Deteksi divergence
        divergence = self._detect_divergence(df, rsi_values)
        
        return IndicatorResult(
            symbol=self.symbol,
            timeframe=self.timeframe,
            values={
                "value": rsi_values[-1],
                "divergence": divergence,
                "overbought": rsi_values[-1] > self.config["overbought"],
                "oversold": rsi_values[-1] < self.config["oversold"]
            },
            timestamp=df['time'].iloc[-1],
            is_valid=not np.isnan(rsi_values[-1])
        )
    
    def _detect_divergence(self, df, rsi_values):
        """Deteksi bullish/bearish divergence"""
        peaks = (df['high'].shift(1) < df['high']) & (df['high'].shift(-1) < df['high'])
        troughs = (df['low'].shift(1) > df['low']) & (df['low'].shift(-1) > df['low'])
        
        # Deteksi regular divergence
        last_peak = df[peaks]['high'].tail(2).values
        last_rsi_peak = rsi_values[peaks][-2:]
        
        if len(last_peak) >= 2 and last_peak[-1] > last_peak[-2] and last_rsi_peak[-1] < last_rsi_peak[-2]:
            return "bearish"
        
        last_trough = df[troughs]['low'].tail(2).values
        last_rsi_trough = rsi_values[troughs][-2:]
        
        if len(last_trough) >= 2 and last_trough[-1] < last_trough[-2] and last_rsi_trough[-1] > last_rsi_trough[-2]:
            return "bullish"
        
        return None