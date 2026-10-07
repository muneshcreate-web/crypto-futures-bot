"""
Grid Futures Strategy
Price range mein automatically Long+Short orders lagata hai
"""

from exchange import ExchangeClient
from notify import send
from config import (
    SYMBOL, LEVERAGE, GRID_INVESTMENT_USDT,
    GRID_LEVELS, GRID_SPREAD_PERCENT, GRID_DIRECTION,
    STOP_LOSS_PCT, TAKE_PROFIT_PCT,
)


class GridStrategy:
    def __init__(self, client: ExchangeClient):
        self.client = client
        self.entry_price = None
        self.buy_orders: dict[float, str] = {}   # price → order_id
        self.sell_orders: dict[float, str] = {}
        self.trade_count = 0
        self.profit = 0.0

    def setup(self):
        price = self.client.get_price()
        self.entry_price = price
        spread = GRID_SPREAD_PERCENT / 100
        usdt_per = GRID_INVESTMENT_USDT / GRID_LEVELS

        send(
            f"🤖 <b>Grid Futures Bot Shuru!</b>\n"
            f"Symbol: {SYMBOL} | {LEVERAGE}x leverage\n"
            f"Price: ${price:,.2f}\n"
            f"Levels: {GRID_LEVELS} | Spread: {GRID_SPREAD_PERCENT}%\n"
            f"Direction: {GRID_DIRECTION.upper()}\n"
            f"Investment: ${GRID_INVESTMENT_USDT}"
        )

        for i in range(1, GRID_LEVELS + 1):
            # Long (BUY) orders — price ke neeche
            if GRID_DIRECTION in ("long", "both"):
                bp = self.client.price_to_precision(price * (1 - i * spread))
                qty = self.client.usdt_to_contracts(usdt_per, bp)
                if qty > 0:
                    try:
                        o = self.client.place_limit_order("buy", qty, bp)
                        self.buy_orders[bp] = o["id"]
                        send(f"✅ LONG Level {i}: {qty} @ ${bp:,.2f}")
                    except Exception as e:
                        send(f"⚠️ LONG L{i} error: {e}")

            # Short (SELL) orders — price ke upar
            if GRID_DIRECTION in ("short", "both"):
                sp = self.client.price_to_precision(price * (1 + i * spread))
                qty = self.client.usdt_to_contracts(usdt_per, sp)
                if qty > 0:
                    try:
                        o = self.client.place_limit_order("sell", qty, sp)
                        self.sell_orders[sp] = o["id"]
                        send(f"✅ SHORT Level {i}: {qty} @ ${sp:,.2f}")
                    except Exception as e:
                        send(f"⚠️ SHORT L{i} error: {e}")

    def tick(self) -> bool:
        """Returns False agar stop/profit trigger ho"""
        price = self.client.get_price()

        # Risk checks
        if self.entry_price:
            drop = (self.entry_price - price) / self.entry_price * 100
            rise = (price - self.entry_price) / self.entry_price * 100

            if drop >= STOP_LOSS_PCT:
                send(f"🛑 <b>STOP LOSS!</b> -{drop:.1f}% | ${price:,.2f}")
                self._close_all()
                return False

            if rise >= TAKE_PROFIT_PCT:
                send(f"🏆 <b>TAKE PROFIT!</b> +{rise:.1f}% | ${price:,.2f}")
                self._close_all()
                return False

        # Check filled orders
        open_ids = {o["id"] for o in self.client.get_open_orders()}

        for bp, oid in list(self.buy_orders.items()):
            if oid not in open_ids:
                del self.buy_orders[bp]
                profit_est = (GRID_INVESTMENT_USDT / GRID_LEVELS) * (GRID_SPREAD_PERCENT / 100)
                self.profit += profit_est
                self.trade_count += 1
                send(
                    f"🟢 <b>LONG Filled #{self.trade_count}</b>\n"
                    f"@ ${bp:,.2f} | Profit est: +${profit_est:.2f}\n"
                    f"Total: +${self.profit:.2f}"
                )
                # Re-place same buy order
                spread = GRID_SPREAD_PERCENT / 100
                usdt_per = GRID_INVESTMENT_USDT / GRID_LEVELS
                qty = self.client.usdt_to_contracts(usdt_per, bp)
                try:
                    o = self.client.place_limit_order("buy", qty, bp)
                    self.buy_orders[bp] = o["id"]
                except Exception as e:
                    send(f"⚠️ Re-order error: {e}")

        for sp, oid in list(self.sell_orders.items()):
            if oid not in open_ids:
                del self.sell_orders[sp]
                profit_est = (GRID_INVESTMENT_USDT / GRID_LEVELS) * (GRID_SPREAD_PERCENT / 100)
                self.profit += profit_est
                self.trade_count += 1
                send(
                    f"🔴 <b>SHORT Filled #{self.trade_count}</b>\n"
                    f"@ ${sp:,.2f} | Profit est: +${profit_est:.2f}\n"
                    f"Total: +${self.profit:.2f}"
                )
                usdt_per = GRID_INVESTMENT_USDT / GRID_LEVELS
                qty = self.client.usdt_to_contracts(usdt_per, sp)
                try:
                    o = self.client.place_limit_order("sell", qty, sp)
                    self.sell_orders[sp] = o["id"]
                except Exception as e:
                    send(f"⚠️ Re-order error: {e}")

        return True

    def _close_all(self):
        self.client.cancel_all_orders()
        self.client.close_all_positions()
        send("🔴 Sabhi orders cancel + positions close ho gayi.")
