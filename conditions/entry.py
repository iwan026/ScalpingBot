import MetaTrader5 as mt5
from dataclasses import dataclass
from typing import Dict
from config import settings

@dataclass
class TradeSignal:
    symbol: str
    direction: str  # 'buy' or 'sell'
    entry_price: float
    stop_loss: float
    take_profit: float
    confidence: float
    reasons: list
    timestamp: float

class EntryConditions:
    def __init__(self, symbol: str):
        self.symbol = symbol
        self.point = mt5.symbol_info(symbol).point
        self.config = settings.INDICATOR_CONFIG

    def check_conditions(self, indicators: Dict) -> TradeSignal:
        """Evaluasi semua indikator untuk generate sinyal trading"""
        current_price = mt5.symbol_info_tick(self.symbol).ask
        signal = TradeSignal(
            symbol=self.symbol,
            direction=None,
            entry_price=current_price,
            stop_loss=0,
            take_profit=0,
            confidence=0,
            reasons=[],
            timestamp=mt5.symbol_info(self.symbol).time
        )

        # Validasi masing-masing indikator
        self._validate_snr(indicators['snr'], current_price, signal)
        self._validate_rsi(indicators['rsi'], signal)
        self._validate_ema(indicators['ema'], signal)
        self._validate_fvg(indicators['fvg'], current_price, signal)
        self._validate_price_action(indicators['price_action'], signal)

        # Hitung confidence score (0-1)
        signal.confidence = min(len(signal.reasons) / 5, 1.0)

        # Set SL/TP jika memenuhi syarat
        if signal.direction:
            self._set_risk_parameters(signal)

        return signal

    def _validate_snr(self, snr, price, signal):
        """Validasi Support/Resistance"""
        for level in snr.values['levels']:
            if (abs(level['price'] - price) < 0.0010:
                if level['type'] == 'support' and not level['breakout']:
                    signal.reasons.append(f"Near Support ({level['price']:.5f})")
                elif level['type'] == 'resistance' and not level['breakout']:
                    signal.reasons.append(f"Near Resistance ({level['price']:.5f})")

    def _validate_rsi(self, rsi, signal):
        """Validasi RSI Conditions"""
        if rsi.values['oversold']:
            signal.reasons.append("RSI Oversold")
        elif rsi.values['overbought']:
            signal.reasons.append("RSI Overbought")
        
        if rsi.values['divergence'] == 'bullish':
            signal.reasons.append("Bullish Divergence")

    def _set_risk_parameters(self, signal):
        """Hitung SL dan TP berdasarkan risk management"""
        if signal.direction == 'buy':
            signal.stop_loss = signal.entry_price - settings.STOP_LOSS_PIPS * self.point * 10
            signal.take_profit = signal.entry_price + settings.TAKE_PROFIT_PIPS * self.point * 10
        else:
            signal.stop_loss = signal.entry_price + settings.STOP_LOSS_PIPS * self.point * 10
            signal.take_profit = signal.entry_price - settings.TAKE_PROFIT_PIPS * self.point * 10