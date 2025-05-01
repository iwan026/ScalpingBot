import MetaTrader5 as mt5
import pandas as pd
import talib

def get_moving_averages(symbol, timeframe, ma_fast=21, ma_slow=50):
    rates = mt5.copy_rates_from_pos(symbol, timeframe, 0, 100)
    df = pd.DataFrame(rates)
    
    df['ma_fast'] = talib.EMA(df['close'], timeperiod=ma_fast)
    df['ma_slow'] = talib.EMA(df['close'], timeperiod=ma_slow)
    
    current_candle = df.iloc[-1]
    prev_candle = df.iloc[-2]
    
    return {
        'ma_fast': current_candle['ma_fast'],
        'ma_slow': current_candle['ma_slow'],
        'ma_fast_prev': prev_candle['ma_fast'],
        'ma_slow_prev': prev_candle['ma_slow'],
        'ma_cross_up': current_candle['ma_fast'] > current_candle['ma_slow'] and prev_candle['ma_fast'] <= prev_candle['ma_slow'],
        'ma_cross_down': current_candle['ma_fast'] < current_candle['ma_slow'] and prev_candle['ma_fast'] >= prev_candle['ma_slow']
    }