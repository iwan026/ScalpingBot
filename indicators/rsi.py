import MetaTrader5 as mt5
import pandas as pd
import talib

def detect_rsi_divergence(symbol, timeframe, rsi_period=14, lookback=50):
    rates = mt5.copy_rates_from_pos(symbol, timeframe, 0, lookback)
    df = pd.DataFrame(rates)
    
    # Hitung RSI
    df['rsi'] = talib.RSI(df['close'], timeperiod=rsi_period)
    
    # Temukan puncak dan lembah
    df['peak'] = df['high'][(df['high'].shift(1) < df['high']) & (df['high'].shift(-1) < df['high']]
    df['trough'] = df['low'][(df['low'].shift(1) > df['low']) & (df['low'].shift(-1) > df['low'])]
    
    divergences = []
    
    # Deteksi bearish divergence (harga higher high, RSI lower high)
    peaks = df[df['peak'].notna()]
    for i in range(1, len(peaks)):
        if peaks['high'].iloc[i] > peaks['high'].iloc[i-1] and peaks['rsi'].iloc[i] < peaks['rsi'].iloc[i-1]:
            divergences.append({
                'type': 'bearish',
                'price_high': peaks['high'].iloc[i],
                'time': peaks.index[i],
                'rsi_value': peaks['rsi'].iloc[i]
            })
    
    # Deteksi bullish divergence (harga lower low, RSI higher low)
    troughs = df[df['trough'].notna()]
    for i in range(1, len(troughs)):
        if troughs['low'].iloc[i] < troughs['low'].iloc[i-1] and troughs['rsi'].iloc[i] > troughs['rsi'].iloc[i-1]:
            divergences.append({
                'type': 'bullish',
                'price_low': troughs['low'].iloc[i],
                'time': troughs.index[i],
                'rsi_value': troughs['rsi'].iloc[i]
            })
    
    return divergences