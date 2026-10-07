"""
DCA (Dollar Cost Averaging) Futures Strategy
Price girne pe zyada buy karo, phir profit pe sab close karo
"""

from exchange import ExchangeClient
from notify import send
from config import (
    SYMBOL, LEVERAGE,
    DCA_BASE_ORDER_USDT, DCA_SAFETY_ORDER_USDT,
    DCA_MAX_SAFETY_ORDERS, DCA_PRICE_DEVIATION,
    DCA_TAKE_PROFIT_PCT, STOP_LOSS_PCT,
)


class DCAStrategy:
    def __init__(self, client: ExchangeClient):
        self.client = client
        self.base_price = None
        self.avg_entry = None
        self.total_qty = 0.0
        self.safety_count = 0
        self.profit = 0.0
        self.cycle = 0
        self.active = False

    def _open_base_order(self):
        price = self.client.get_price()
        self.base_price = price
        qty = self.client.usdt_to_contracts(DCA_BASE_ORDER_USDT, price)
        try:
            self.client.place_market_order("buy", qty)
            self.total_qty = qty
            self.avg_entry = price
            self.safety_count = 0
            self.active = True
            send(
                f"🟢 <b>DCA Cycle #{self.cycle + 1} Shuru</b>\n"
                f"Base order: {qty} @ ${price:,.2f}\n"
                f"TP target: ${price * (1 + DCA_TAKE_PROFIT_PCT/100):,.2f}"
            )
        except Exception as e:
            send(f"❌ Base order error: {e}")

    def _open_safety_order(self):
        price = self.client.get_price()
        qty = self.client.usdt_to_contracts(DCA_SAFETY_ORDER_USDT, price)
        try:
            self.client.place_market_order("buy", qty)
            total_cost = self.avg_entry * self.total_qty + price * qty
            self.total_qty += qty
            self.avg_entry = total_cost / self.total_qty
            self.safety_count += 1
            send(
                f"🔵 <b>Safety Order #{self.safety_count}</b>\n"
                f"Bought {qty} @ ${price:,.2f}\n"
                f"Avg entry: ${self.avg_entry:,.2f}\n"
                f"TP target: ${self.avg_entry * (1 + DCA_TAKE_PROFIT_PCT/100):,.2f}"
            )
        except Exception as e:
            send(f"❌ Safety order error: {e}")

    def _close_position(self, reason: str):
        price = self.client.get_price()
        pnl = (price - self.avg_entry) / self.avg_entry * 100
        usdt_pnl = (price - self.avg_entry) * self.total_qty
        try:
            self.client.place_market_order("sell", self.total_qty, {"reduceOnly": True})
            self.profit += usdt_pnl
            self.cycle += 1
            send(
                f"{'🏆' if pnl > 0 else '🛑'} <b>{reason}</b>\n"
                f"PnL: {pnl:+.2f}% | ${usdt_pnl:+.2f}\n"
                f"Total profit: ${self.profit:+.2f}\n"
                f"Cycles done: {self.cycle}"
            )
        except Exception as e:
            send(f"❌ Close error: {e}")
        finally:
            self.active = False
            self.total_qty = 0.0
            self.avg_entry = None
            self.base_price = None

    def tick(self) -> bool:
        if not self.active:
            self._open_base_order()
            return True

        price = self.client.get_price()

        # Take profit
        tp_price = self.avg_entry * (1 + DCA_TAKE_PROFIT_PCT / 100)
        if price >= tp_price:
            self._close_position("TAKE PROFIT!")
            return True  # Start new cycle

        # Stop loss
        sl_price = self.avg_entry * (1 - STOP_LOSS_PCT / 100)
        if price <= sl_price:
            self._close_position("STOP LOSS")
            return False  # Stop bot after hard loss

        # Safety orders
        if self.safety_count < DCA_MAX_SAFETY_ORDERS:
            deviation_price = self.avg_entry * (
                1 - DCA_PRICE_DEVIATION / 100 * (self.safety_count + 1)
            )
            if price <= deviation_price:
                self._open_safety_order()

        return True
