from .base import BaseIndicator, IndicatorResult
import numpy as np

class SNRIndicator(BaseIndicator):
    def load_config(self):
        from config import settings
        return settings.INDICATOR_CONFIG["SNR"]
    
    def calculate(self):
        df = self.get_data(self.config["lookback"])
        df['volume_norm'] = (df['real_volume'] - df['real_volume'].mean()) / df['real_volume'].std()
        
        levels = []
        for i in range(1, len(df)-1):
            if df['volume_norm'][i] > self.config["volume_threshold"]:
                if df['close'][i] < df['open'][i]:  # Support
                    levels.append({
                        'type': 'support',
                        'price': df['low'][i],
                        'time': df['time'][i],
                        'volume': df['real_volume'][i]
                    })
                else:  # Resistance
                    levels.append({
                        'type': 'resistance',
                        'price': df['high'][i],
                        'time': df['time'][i],
                        'volume': df['real_volume'][i]
                    })
        
        return IndicatorResult(
            symbol=self.symbol,
            timeframe=self.timeframe,
            values={
                "levels": levels,
                "breakout": False,
                "fakeout": False
            },
            timestamp=df['time'].iloc[-1],
            is_valid=len(levels) > 0
        )