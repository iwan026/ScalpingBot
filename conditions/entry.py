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
        """Evaluasi indikator dengan minimal 3 konfirmasi"""
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

        # Validasi semua indikator
        self._validate_snr(indicators['snr'], current_price, signal)
        self._validate_rsi(indicators['rsi'], signal)
        self._validate_ema(indicators['ema'], signal)
        self._validate_fvg(indicators['fvg'], current_price, signal)
        self._validate_price_action(indicators['price_action'], signal)

        # Hitung confidence berdasarkan 3 konfirmasi
        signal.confidence = min(len(signal.reasons) / 3, 1.0)

        # Eksekusi hanya jika 3+ konfirmasi
        if len(signal.reasons) >= 3:
            self._determine_direction(signal)
            self._set_risk_parameters(signal)
        else:
            signal.direction = None

        return signal

    def _determine_direction(self, signal):
        """Tentukan arah trading berdasarkan mayoritas sinyal"""
        if signal.direction is None:
            buy_signals = sum(1 for reason in signal.reasons 
                            if any(kw in reason.lower() 
                                  for kw in ['buy', 'bullish', 'long', 'up']))
            sell_signals = sum(1 for reason in signal.reasons 
                             if any(kw in reason.lower() 
                                   for kw in ['sell', 'bearish', 'short', 'down']))
            signal.direction = "buy" if buy_signals > sell_signals else "sell"

    def _validate_snr(self, snr, price, signal):
        """Validasi Support/Resistance"""
        for level in snr.values['levels']:
            if abs(level['price'] - price) < 0.0010:
                if level['type'] == 'support' and not level['breakout']:
                    signal.reasons.append(f"Support {level['price']:.5f} (buy)")
                elif level['type'] == 'resistance' and not level['breakout']:
                    signal.reasons.append(f"Resistance {level['price']:.5f} (sell)")

    def _validate_rsi(self, rsi, signal):
        """Validasi RSI"""
        if rsi.values['oversold']:
            signal.reasons.append("RSI Oversold (buy)")
        elif rsi.values['overbought']:
            signal.reasons.append("RSI Overbought (sell)")
        
        if rsi.values['divergence'] == 'bullish':
            signal.reasons.append("RSI Bullish Divergence (buy)")
        elif rsi.values['divergence'] == 'bearish':
            signal.reasons.append("RSI Bearish Divergence (sell)")

    def _validate_ema(self, ema, signal):
        """Validasi EMA"""
        if not ema.is_valid:
            return

        if ema.values['crossover'] == "golden":
            signal.reasons.append("EMA Golden Cross (buy)")
        elif ema.values['crossover'] == "death":
            signal.reasons.append("EMA Death Cross (sell)")
        
        if ema.values['trend'] == "up":
            signal.reasons.append("EMA Trend Up (buy)")
        else:
            signal.reasons.append("EMA Trend Down (sell)")

    def _validate_fvg(self, fvg, price, signal):
        """Validasi Fair Value Gap"""
        if not fvg.is_valid:
            return

        for gap in fvg.values['gaps']:
            if gap['direction'] == 'bullish' and price > gap['high']:
                signal.reasons.append(f"Bullish FVG {gap['high']:.5f} (buy)")
            elif gap['direction'] == 'bearish' and price < gap['low']:
                signal.reasons.append(f"Bearish FVG {gap['low']:.5f} (sell)")

    def _validate_price_action(self, price_action, signal):
        """Validasi Price Action"""
        if not price_action.is_valid:
            return

        if price_action.values['pinbar'] == 'bullish':
            signal.reasons.append("Bullish Pinbar (buy)")
        elif price_action.values['pinbar'] == 'bearish':
            signal.reasons.append("Bearish Pinbar (sell)")

        if price_action.values['engulfing'] == 'bullish':
            signal.reasons.append("Bullish Engulfing (buy)")
        elif price_action.values['engulfing'] == 'bearish':
            signal.reasons.append("Bearish Engulfing (sell)")

    def _set_risk_parameters(self, signal):
        """Hitung SL/TP"""
        multiplier = self.point * 10
        if signal.direction == 'buy':
            signal.stop_loss = signal.entry_price - settings.STOP_LOSS_PIPS * multiplier
            signal.take_profit = signal.entry_price + settings.TAKE_PROFIT_PIPS * multiplier
        else:
            signal.stop_loss = signal.entry_price + settings.STOP_LOSS_PIPS * multiplier
            signal.take_profit = signal.entry_price - settings.TAKE_PROFIT_PIPS * multiplier