from typing import Dict, List
import MetaTrader5 as mt5
from utils.config import STOP_LOSS_PIPS, TAKE_PROFIT_PIPS

def check_entry_conditions(symbol: str, indicators: Dict) -> Dict:
    sr_levels = indicators['snr']
    divergences = indicators['rsi']
    ma_data = indicators['ema']
    pinbars = indicators['pinbar']
    supply_demand = indicators['supply_demand']
    fvg_list = indicators['fvg']
    
    signal = {
        'buy': False,
        'sell': False,
        'confidence': 0,
        'reasons': [],
        'sl': 0,
        'tp': 0
    }
    
    current_price = mt5.symbol_info_tick(symbol).ask
    point = mt5.symbol_info(symbol).point
    
    # Konfirmasi indikator
    near_support = any(abs(level['price'] - current_price) < 0.0010 for level in sr_levels if level['type'] == 'support')
    near_resistance = any(abs(level['price'] - current_price) < 0.0010 for level in sr_levels if level['type'] == 'resistance')
    bullish_div = any(d['type'] == 'bullish' for d in divergences)
    bearish_div = any(d['type'] == 'bearish' for d in divergences)
    ma_cross_up = ma_data['ma_cross_up']
    ma_cross_down = ma_data['ma_cross_down']
    bullish_pin = any(p['type'] == 'bullish' for p in pinbars)
    bearish_pin = any(p['type'] == 'bearish' for p in pinbars)
    
    # Supply/Demand dan FVG
    near_demand = any(zone['low'] <= current_price <= zone['high'] for zone in supply_demand if zone['type'] == 'demand')
    near_supply = any(zone['low'] <= current_price <= zone['high'] for zone in supply_demand if zone['type'] == 'supply')
    bullish_fvg = any(fvg['low'] <= current_price <= fvg['high'] for fvg in fvg_list if fvg['type'] == 'bullish')
    bearish_fvg = any(fvg['low'] <= current_price <= fvg['high'] for fvg in fvg_list if fvg['type'] == 'bearish')
    
    # Evaluasi BUY (minimal 3 konfirmasi dari 6)
    buy_conditions = 0
    buy_reasons = []
    
    if near_support or near_demand:
        buy_conditions += 1
        buy_reasons.append("Near Support/Demand Zone")
    if bullish_div:
        buy_conditions += 1
        buy_reasons.append("Bullish RSI Divergence")
    if ma_cross_up:
        buy_conditions += 1
        buy_reasons.append("MA Crossover Up")
    if bullish_pin:
        buy_conditions += 1
        buy_reasons.append("Bullish Pin Bar")
    if bullish_fvg:
        buy_conditions += 1
        buy_reasons.append("Bullish FVG")
    
    if buy_conditions >= 3:
        sl = current_price - STOP_LOSS_PIPS * point * 10
        tp = current_price + TAKE_PROFIT_PIPS * point * 10
        signal.update({
            'buy': True,
            'confidence': buy_conditions / 6,
            'reasons': buy_reasons,
            'sl': sl,
            'tp': tp
        })
    
    # Evaluasi SELL (minimal 3 konfirmasi dari 6)
    sell_conditions = 0
    sell_reasons = []
    
    if near_resistance or near_supply:
        sell_conditions += 1
        sell_reasons.append("Near Resistance/Supply Zone")
    if bearish_div:
        sell_conditions += 1
        sell_reasons.append("Bearish RSI Divergence")
    if ma_cross_down:
        sell_conditions += 1
        sell_reasons.append("MA Crossover Down")
    if bearish_pin:
        sell_conditions += 1
        sell_reasons.append("Bearish Pin Bar")
    if bearish_fvg:
        sell_conditions += 1
        sell_reasons.append("Bearish FVG")
    
    if sell_conditions >= 3:
        sl = current_price + STOP_LOSS_PIPS * point * 10
        tp = current_price - TAKE_PROFIT_PIPS * point * 10
        signal.update({
            'sell': True,
            'confidence': sell_conditions / 6,
            'reasons': sell_reasons,
            'sl': sl,
            'tp': tp
        })
    
    return signal