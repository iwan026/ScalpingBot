from .base import BaseIndicator, IndicatorResult
import numpy as np

class PriceActionIndicator(BaseIndicator):
    def calculate(self):
        df = self.get_data(20)
        patterns = {
            "pinbar": self._detect_pinbar(df),
            "engulfing": self._detect_engulfing(df)
        }
        
        return IndicatorResult(
            symbol=self.symbol,
            timeframe=self.timeframe,
            values=patterns,
            timestamp=df['time'].iloc[-1],
            is_valid=any(patterns.values())
        )
    
    def _detect_pinbar(self, df):
        last_candle = df.iloc[-1]
        body_size = abs(last_candle['close'] - last_candle['open'])
        upper_wick = last_candle['high'] - max(last_candle['open'], last_candle['close'])
        lower_wick = min(last_candle['open'], last_candle['close']) - last_candle['low']
        
        # Bullish Pin Bar
        if lower_wick > 2 * body_size and upper_wick < body_size:
            return {"type": "bullish", "confidence": min(lower_wick/body_size, 3)}
        
        # Bearish Pin Bar
        elif upper_wick > 2 * body_size and lower_wick < body_size:
            return {"type": "bearish", "confidence": min(upper_wick/body_size, 3)}
        
        return None
    
    def _detect_engulfing(self, df):
        if len(df) < 3:
            return None
            
        last_candle = df.iloc[-1]
        prev_candle = df.iloc[-2]
        
        # Bullish Engulfing
        if (last_candle['close'] > last_candle['open'] and 
            prev_candle['close'] < prev_candle['open'] and
            last_candle['open'] < prev_candle['close'] and 
            last_candle['close'] > prev_candle['open']):
            return {"type": "bullish", "size": last_candle['close'] - last_candle['open']}
        
        # Bearish Engulfing
        elif (last_candle['close'] < last_candle['open'] and 
              prev_candle['close'] > prev_candle['open'] and
              last_candle['open'] > prev_candle['close'] and 
              last_candle['close'] < prev_candle['open']):
            return {"type": "bearish", "size": last_candle['open'] - last_candle['close']}
        
        return None