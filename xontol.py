import time
import MetaTrader5 as mt5
from config import settings
from indicators import check_entry_conditions
from utils import setup_logger, TelegramNotifier, calculate_sl_tp_in_price

logger = setup_logger("XontolScalping")


class MT5Client:
    def __init__(self):
        self._connect()

    def _connect(self):
        if not mt5.initialize(
            login=settings.MT5_LOGIN,
            password=settings.MT5_PASSWORD,
            server=settings.MT5_SERVER,
        ):
            raise ConnectionError(f"MT5 init failed: {mt5.last_error()}")
        logger.info("Connected to MT5")

    def send_order(
        self,
        symbol: str,
        direction: str,
        lot: float,
        price: float,
        sl: float,
        tp: float,
    ):
        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": symbol,
            "volume": lot,
            "type": mt5.ORDER_TYPE_BUY if direction == "buy" else mt5.ORDER_TYPE_SELL,
            "price": price,
            "sl": sl,
            "tp": tp,
            "deviation": 10,
            "magic": 2024,
            "comment": "Xontol Scalping ($1 Risk)",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC,
        }
        result = mt5.order_send(request)
        if result.retcode != mt5.TRADE_RETCODE_DONE:
            logger.error(f"Order failed: {result.comment}")
        return result


class XontolScalping:
    def __init__(self):
        self.mt5 = MT5Client()
        self.notifier = TelegramNotifier()
        self.symbols = settings.SYMBOLS
        self.timeframe = settings.TIMEFRAME
        self.open_positions = {}
        self.last_checked_time = {}

    def _get_open_positions_count(self) -> int:
        positions = mt5.positions_get()
        return len(positions) if positions else 0

    def _update_open_positions(self):
        current_positions = mt5.positions_get()
        if current_positions:
            active_symbols = {pos.symbol: pos.ticket for pos in current_positions}
            self.open_positions = {
                k: v for k, v in self.open_positions.items() if k in active_symbols
            }

    def check_entry(self, symbol: str) -> bool:
        if self._get_open_positions_count() >= settings.MAX_OPEN_POSITIONS:
            return False

        if symbol in self.open_positions:
            return False

        direction = check_entry_conditions(symbol, self.timeframe)
        if not direction:
            return False

        tick = mt5.symbol_info_tick(symbol)
        price = tick.ask if direction == "buy" else tick.bid

        sl_price, tp_price = calculate_sl_tp_in_price(
            symbol=symbol,
            direction=direction,
            entry_price=price,
            usd_amount=1.0,
            lot_size=settings.LOT_SIZE,
        )

        result = self.mt5.send_order(
            symbol=symbol,
            direction=direction,
            lot=settings.LOT_SIZE,
            price=price,
            sl=sl_price,
            tp=tp_price,
        )

        if result and result.retcode == mt5.TRADE_RETCODE_DONE:
            self.open_positions[symbol] = result.order
            self.notifier.send_trade_notification(
                symbol=symbol,
                direction=direction,
                price=price,
                sl=sl_price,
                tp=tp_price,
            )
            return True
        return False

    def run(self):
        logger.info(f"Bot started - Max {settings.MAX_OPEN_POSITIONS} positions")
        try:
            while True:
                self._update_open_positions()

                if self._get_open_positions_count() >= settings.MAX_OPEN_POSITIONS:
                    time.sleep(1)
                    continue

                for symbol in self.symbols:
                    try:
                        self.check_entry(symbol)
                    except Exception as e:
                        logger.error(
                            f"Error checking {symbol}: {str(e)}", exc_info=True
                        )

                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("Bot stopped manually")
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}", exc_info=True)
        finally:
            mt5.shutdown()


if __name__ == "__main__":
    bot = XontolScalping()
    bot.run()
