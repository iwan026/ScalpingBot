import MetaTrader5 as mt5
import pandas as pd

def detect_fvg_with_volume(symbol, timeframe, lookback=30):
    rates = mt5.copy_rates_from_pos(symbol, timeframe, 0, lookback)
    df = pd.DataFrame(rates)
    
    fvg_list = []
    
    # Normalisasi volume
    df['volume_norm'] = (df['real_volume'] - df['real_volume'].mean()) / df['real_volume'].std()
    
    for i in range(1, len(df)-1):
        prev_low = df['low'].iloc[i-1]
        prev_high = df['high'].iloc[i-1]
        current_low = df['low'].iloc[i]
        current_high = df['high'].iloc[i]
        
        # Bullish FVG (gap di bawah)
        if current_low > prev_high and df['volume_norm'].iloc[i] > 1.0:
            fvg_list.append({
                'type': 'bullish',
                'high': prev_high,
                'low': current_low,
                'time': pd.to_datetime(df['time'].iloc[i], unit='s'),
                'volume': df['real_volume'].iloc[i]
            })
        
        # Bearish FVG (gap di atas)
        elif current_high < prev_low and df['volume_norm'].iloc[i] > 1.0:
            fvg_list.append({
                'type': 'bearish',
                'high': current_high,
                'low': prev_low,
                'time': pd.to_datetime(df['time'].iloc[i], unit='s'),
                'volume': df['real_volume'].iloc[i]
            })
    
    return fvg_list