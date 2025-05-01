from .base import BaseIndicator, IndicatorResult
import numpy as np

class FVGIndicator(BaseIndicator):
    def load_config(self):
        from config import settings
        return settings.INDICATOR_CONFIG["FVG"]
    
    def calculate(self):
        df = self.get_data(self.config["lookback"])
        df['volume_norm'] = (df['real_volume'] - df['real_volume'].mean()) / df['real_volume'].std()
        
        fvg_list = []
        for i in range(1, len(df)):
            # Bullish FVG (gap di bawah)
            if df['low'].iloc[i] > df['high'].iloc[i-1] and df['volume_norm'].iloc[i] > self.config["volume_threshold"]:
                fvg_list.append({
                    'type': 'bullish',
                    'high': df['high'].iloc[i-1],
                    'low': df['low'].iloc[i],
                    'time': df['time'].iloc[i]
                })
            
            # Bearish FVG (gap di atas)
            elif df['high'].iloc[i] < df['low'].iloc[i-1] and df['volume_norm'].iloc[i] > self.config["volume_threshold"]:
                fvg_list.append({
                    'type': 'bearish',
                    'high': df['high'].iloc[i],
                    'low': df['low'].iloc[i-1],
                    'time': df['time'].iloc[i]
                })
        
        return IndicatorResult(
            symbol=self.symbol,
            timeframe=self.timeframe,
            values={
                "fgv_list": fvg_list,
                "current_fvg": self._get_current_fvg(df, fvg_list)
            },
            timestamp=df['time'].iloc[-1],
            is_valid=len(fvg_list) > 0
        )
    
    def _get_current_fvg(self, df, fvg_list):
        """Cek apakah harga saat ini berada di area FVG"""
        if not fvg_list:
            return None
            
        last_candle = df.iloc[-1]
        for fvg in fvg_list[-3:]:  # Cek 3 FVG terakhir
            if fvg['low'] <= last_candle['close'] <= fvg['high']:
                return fvg
        return None