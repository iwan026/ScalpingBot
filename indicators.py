import talib
import MetaTrader5 as mt5
import numpy as np
import time


def get_ema(symbol: str, timeframe: str) -> dict:
    rates = mt5.copy_rates_from_pos(
        symbol, getattr(mt5, f"TIMEFRAME_{timeframe}"), 0, 100
    )
    closes = [rate[4] for rate in rates]

    ema_21 = talib.EMA(np.array(closes), timeperiod=21)[-1]
    ema_50 = talib.EMA(np.array(closes), timeperiod=50)[-1]

    current_price = mt5.symbol_info_tick(symbol).ask
    return {
        "ema_21": ema_21,
        "ema_50": ema_50,
        "current_price": current_price,
    }


def get_engulfing(symbol: str, timeframe: str) -> str:
    rates = mt5.copy_rates_from_pos(
        symbol, getattr(mt5, f"TIMEFRAME_{timeframe}"), 0, 3
    )

    if len(rates) < 3:
        return None

    prev = rates[-2]
    last = rates[-1]

    timeframe_seconds = {
        "M1": 60,
        "M5": 300,
        "M15": 900,
        "H1": 3600,
        "H4": 14400,
        "D1": 86400,
    }.get(timeframe, 60)

    current_time = time.time()
    last_candle_close_time = last[0] + timeframe_seconds

    if current_time < last_candle_close_time:
        return None

    # Bullish Engulfing
    if (
        prev[4] < prev[1]
        and last[4] > last[1]
        and last[1] <= prev[4]
        and last[4] >= prev[1]
    ):
        return "bullish"

    # Bearish Engulfing
    elif (
        prev[4] > prev[1]
        and last[4] < last[1]
        and last[1] >= prev[4]
        and last[4] <= prev[1]
    ):
        return "bearish"

    return None


def check_entry_conditions(symbol: str, timeframe: str) -> str:
    ema_data = get_ema(symbol, timeframe)
    ema_21 = ema_data["ema_21"]
    ema_50 = ema_data["ema_50"]
    current_price = ema_data["current_price"]

    engulfing = get_engulfing(symbol, timeframe)

    # Buy conditions
    if engulfing == "bullish":
        if (ema_21 > ema_50) and (
            (current_price > ema_21) or (ema_50 < current_price < ema_21)
        ):
            return "buy"

    # Sell conditions
    elif engulfing == "bearish":
        if (ema_21 < ema_50) and (
            (current_price < ema_21) or (ema_21 < current_price < ema_50)
        ):
            return "sell"

    return None
