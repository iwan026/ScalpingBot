import MetaTrader5 as mt5
import pandas as pd
import numpy as np

def detect_high_volume_snr(symbol, timeframe, lookback=100):
    rates = mt5.copy_rates_from_pos(symbol, timeframe, 0, lookback)
    df = pd.DataFrame(rates)
    df['time'] = pd.to_datetime(df['time'], unit='s')
    
    # Hitung normalisasi volume
    df['volume_norm'] = (df['real_volume'] - df['real_volume'].mean()) / df['real_volume'].std()
    
    # Inisialisasi list
    high_volume_levels = []
    threshold = 1.5
    
    for i in range(1, len(df)-1):
        # Deteksi level dengan volume tinggi
        if df['volume_norm'][i] > threshold:
            # Support
            if df['close'][i] < df['open'][i]:
                level_info = {
                    'type': 'support',
                    'price': df['low'][i],
                    'time': df['time'][i],
                    'volume': df['real_volume'][i],
                    'breakout': False,
                    'fakeout': False
                }
                high_volume_levels.append(level_info)
            
            # Resistance
            else:
                level_info = {
                    'type': 'resistance', 
                    'price': df['high'][i],
                    'time': df['time'][i],
                    'volume': df['real_volume'][i],
                    'breakout': False,
                    'fakeout': False
                }
                high_volume_levels.append(level_info)
    
    # Deteksi breakout dan fakeout
    for i, level in enumerate(high_volume_levels):
        idx = df[df['time'] == level['time']].index[0]
        
        # Untuk level support
        if level['type'] == 'support':
            # Cek breakout
            breakout_condition = any(df['low'][j] < level['price'] for j in range(idx+1, len(df)))
            
            # Cek fakeout
            if breakout_condition:
                level['breakout'] = True
                
                fakeout_condition = any(df['close'][j] > level['price'] for j in range(idx+1, len(df)))
                if fakeout_condition:
                    level['fakeout'] = True
        
        # Untuk level resistance 
        elif level['type'] == 'resistance':
            # Cek breakout
            breakout_condition = any(df['high'][j] > level['price'] for j in range(idx+1, len(df)))
            
            # Cek fakeout
            if breakout_condition:
                level['breakout'] = True

                fakeout_condition = any(df['close'][j] < level['price'] for j in range(idx+1, len(df)))
                if fakeout_condition:
                    level['fakeout'] = True
    
    return high_volume_levels