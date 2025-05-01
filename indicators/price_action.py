import MetaTrader5 as mt5
import pandas as pd

def detect_pinbar(symbol, timeframe, lookback=20):
    rates = mt5.copy_rates_from_pos(symbol, timeframe, 0, lookback)
    df = pd.DataFrame(rates)
    
    pinbars = []
    
    for i in range(len(df)):
        candle = df.iloc[i]
        body_size = abs(candle['close'] - candle['open'])
        upper_wick = candle['high'] - max(candle['open'], candle['close'])
        lower_wick = min(candle['open'], candle['close']) - candle['low']
        
        # Bullish Pin Bar (Lower Shadow > 2*Body and Upper Shadow small)
        if lower_wick > 2 * body_size and upper_wick < body_size:
            pinbars.append({
                'type': 'bullish',
                'time': pd.to_datetime(candle['time'], unit='s'),
                'price': candle['low'],
                'body_size': body_size
            })
        
        # Bearish Pin Bar (Upper Shadow > 2*Body and Lower Shadow small)
        elif upper_wick > 2 * body_size and lower_wick < body_size:
            pinbars.append({
                'type': 'bearish',
                'time': pd.to_datetime(candle['time'], unit='s'),
                'price': candle['high'],
                'body_size': body_size
            })
    
    return pinbars