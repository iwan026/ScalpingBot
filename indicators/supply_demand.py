import MetaTrader5 as mt5
import pandas as pd
import numpy as np

def detect_supply_demand_zones(symbol, timeframe, lookback=50):
    rates = mt5.copy_rates_from_pos(symbol, timeframe, 0, lookback)
    df = pd.DataFrame(rates)
    
    # Identifikasi base candle (candle besar dengan volume tinggi)
    df['body'] = abs(df['close'] - df['open'])
    df['volume_zscore'] = (df['real_volume'] - df['real_volume'].mean()) / df['real_volume'].std()
    
    # Deteksi Supply Zone (Distribution)
    supply_zones = []
    for i in range(2, len(df)-2):
        if df['volume_zscore'][i] > 1.5 and df['body'][i] > df['body'].mean():
            if df['close'][i] < df['open'][i]:  # Bearish candle
                zone = {
                    'type': 'supply',
                    'high': df['high'][i],
                    'low': df['low'][i],
                    'time': pd.to_datetime(df['time'][i], unit='s'),
                    'volume': df['real_volume'][i]
                }
                supply_zones.append(zone)
    
    # Deteksi Demand Zone (Accumulation)
    demand_zones = []
    for i in range(2, len(df)-2):
        if df['volume_zscore'][i] > 1.5 and df['body'][i] > df['body'].mean():
            if df['close'][i] > df['open'][i]:  # Bullish candle
                zone = {
                    'type': 'demand',
                    'high': df['high'][i],
                    'low': df['low'][i],
                    'time': pd.to_datetime(df['time'][i], unit='s'),
                    'volume': df['real_volume'][i]
                }
                demand_zones.append(zone)
    
    return supply_zones + demand_zones