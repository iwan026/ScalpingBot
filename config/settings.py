SYMBOLS = ["EURUSD", "GBPUSD", "USDJPY", "XAUUSD"]
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
    "token": "YOUR_BOT_TOKEN",
    "chat_id": "YOUR_CHAT_ID",
    "timeout": 10
}

MT5 = {
    "login": 123456,
    "server": "HFMarkets-Demo",
    "password": "your_password",
    "timeout": 5000
}