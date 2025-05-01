SYMBOLS = ["EURUSD", "EURJPY", "GBPJPY", "USDJPY", "GBPUSD"]
TIMEFRAME = "M1"
LOT_SIZE = 0.01
MAX_TRADES = 10

STOP_LOSS_PIPS = 5
TAKE_PROFIT_PIPS = 10
MAX_DAILY_LOSS = 2.0

INDICATOR_CONFIG = {
    "SNR": {
        "lookback": 100,
        "volume_threshold": 1.5,
        "min_volume": 500
    },
    "RSI": {
        "period": 14,
        "lookback": 50,
        "overbought": 70,
        "oversold": 30
    },
    "EMA": {
        "fast": 21,
        "slow": 50,
        "lookback": 100
    },
    "FVG": {
        "lookback": 30,
        "volume_threshold": 1.0
    },
    "PRICE_ACTION": {
        "pinbar_lookback": 20,
        "engulfing_lookback": 3
    }
}

TELEGRAM = {
    "token": "7667262262:AAGgQBRaC3kFoLSYFf6Q9P8ytsttrTfdzl0",
    "chat_id": "1198920849",
    "timeout": 10
}

MT5 = {
    "login": 48804718,
    "server": "HFMarketsGlobal-Demo",
    "password": "123@Demo",
    "timeout": 5000
}