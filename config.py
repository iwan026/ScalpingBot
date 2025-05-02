from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    MT5_LOGIN: int
    MT5_PASSWORD: str
    MT5_SERVER: str

    SYMBOLS: list = [
        "EURUSD",
        "GBPUSD",
        "USDJPY",
        "EURGBP",
        "EURJPY",
        "GBPJPY",
        "BTCUSD",
    ]
    TIMEFRAME: str = "M1"
    LOT_SIZE: float = 0.01
    MAX_OPEN_POSITIONS: int = 2

    TELEGRAM_TOKEN: str
    TELEGRAM_CHAT_ID: str

    class Config:
        env_file = ".env"


settings = Settings()
