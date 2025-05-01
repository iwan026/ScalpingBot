from dataclasses import dataclass
import MetaTrader5 as mt5
import pandas as pd

@dataclass
class IndicatorResult:
    symbol: str
    timeframe: str
    values: dict
    timestamp: float
    is_valid: bool = False

class BaseIndicator:
    def __init__(self, symbol, timeframe):
        self.symbol = symbol
        self.timeframe = timeframe
        self.config = self.load_config()
        
    def load_config(self):
        """Override di subclass"""
        return {}
    
    def get_data(self, lookback):
        rates = mt5.copy_rates_from_pos(
            self.symbol, 
            getattr(mt5, f"TIMEFRAME_{self.timeframe}"), 
            0, 
            lookback
        )
        return pd.DataFrame(rates)
    
    def calculate(self):
        raise NotImplementedError