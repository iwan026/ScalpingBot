import pytest
import MetaTrader5 as mt5
from indicators import (
    SNRIndicator,
    RSIIndicator,
    EMAIndicator,
    FVGIndicator,
    PriceActionIndicator
)

@pytest.fixture
def setup_mt5():
    mt5.initialize()
    yield
    mt5.shutdown()

def test_snr_indicator(setup_mt5):
    indicator = SNRIndicator("EURUSD", "M1")
    result = indicator.calculate()
    
    assert hasattr(result, 'values')
    assert 'levels' in result.values
    assert isinstance(result.is_valid, bool)

def test_rsi_indicator(setup_mt5):
    indicator = RSIIndicator("EURUSD", "M1")
    result = indicator.calculate()
    
    assert 0 <= result.values['value'] <= 100
    assert result.values['divergence'] in [None, 'bullish', 'bearish']

def test_ema_crossover(setup_mt5):
    indicator = EMAIndicator("EURUSD", "M1")
    result = indicator.calculate()
    
    assert result.values['crossover'] in [None, 'golden', 'death']
    assert isinstance(result.values['fast'], float)

def test_fvg_detection(setup_mt5):
    indicator = FVGIndicator("EURUSD", "M1")
    result = indicator.calculate()
    
    if result.values['fgv_list']:
        assert result.values['current_fvg'] in [None, result.values['fgv_list'][-1]]

def test_price_action(setup_mt5):
    indicator = PriceActionIndicator("EURUSD", "M1")
    result = indicator.calculate()
    
    assert any(result.values.values()) == result.is_valid