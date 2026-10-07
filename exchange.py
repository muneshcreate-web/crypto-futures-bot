"""
Exchange connector — ccxt ke through koi bhi exchange support karta hai
"""

import ccxt
import time
from config import (
    EXCHANGE_ID, API_KEY, API_SECRET, API_PASSPHRASE,
    PAPER_TRADING, SYMBOL, LEVERAGE, MARGIN_MODE,
)


def build_exchange() -> ccxt.Exchange:
    params = {
        "apiKey": API_KEY,
        "secret": API_SECRET,
        "enableRateLimit": True,
        "options": {"defaultType": "future"},
    }
    if API_PASSPHRASE:
        params["password"] = API_PASSPHRASE

    ex: ccxt.Exchange = getattr(ccxt, EXCHANGE_ID)(params)

    # Testnet / sandbox urls
    if PAPER_TRADING:
        if EXCHANGE_ID == "binance":
            ex.set_sandbox_mode(True)
        elif EXCHANGE_ID == "bybit":
            ex.set_sandbox_mode(True)
        elif EXCHANGE_ID == "okx":
            ex.set_sandbox_mode(True)
        # KuCoin/Bitget use paper keys directly from exchange UI
    return ex


class ExchangeClient:
    def __init__(self):
        self.ex = build_exchange()
        self.ex.load_markets()
        self._setup_leverage()

    def _setup_leverage(self):
        try:
            self.ex.set_leverage(LEVERAGE, SYMBOL)
        except Exception:
            pass  # Some exchanges set leverage per-order
        try:
            self.ex.set_margin_mode(MARGIN_MODE, SYMBOL)
        except Exception:
            pass

    # ─── Market data ───────────────────────────

    def get_price(self) -> float:
        ticker = self.ex.fetch_ticker(SYMBOL)
        return float(ticker["last"])

    def get_orderbook(self, depth: int = 5) -> dict:
        return self.ex.fetch_order_book(SYMBOL, depth)

    def get_ohlcv(self, timeframe: str = "5m", limit: int = 50) -> list:
        return self.ex.fetch_ohlcv(SYMBOL, timeframe, limit=limit)

    # ─── Account ───────────────────────────────

    def get_balance(self) -> dict:
        bal = self.ex.fetch_balance({"type": "future"})
        usdt = bal.get("USDT", {})
        return {
            "free": float(usdt.get("free", 0)),
            "used": float(usdt.get("used", 0)),
            "total": float(usdt.get("total", 0)),
        }

    def get_positions(self) -> list:
        positions = self.ex.fetch_positions([SYMBOL])
        return [p for p in positions if float(p.get("contracts", 0) or 0) != 0]

    # ─── Orders ────────────────────────────────

    def place_limit_order(self, side: str, amount: float, price: float,
                          params: dict = None) -> dict:
        return self.ex.create_order(
            SYMBOL, "limit", side, amount, price, params or {}
        )

    def place_market_order(self, side: str, amount: float,
                           params: dict = None) -> dict:
        return self.ex.create_order(
            SYMBOL, "market", side, amount, None, params or {}
        )

    def cancel_order(self, order_id: str) -> dict:
        return self.ex.cancel_order(order_id, SYMBOL)

    def cancel_all_orders(self):
        try:
            self.ex.cancel_all_orders(SYMBOL)
        except Exception:
            for o in self.get_open_orders():
                try:
                    self.cancel_order(o["id"])
                except Exception:
                    pass

    def get_open_orders(self) -> list:
        return self.ex.fetch_open_orders(SYMBOL)

    def close_all_positions(self):
        for pos in self.get_positions():
            side = "sell" if pos["side"] == "long" else "buy"
            amt = abs(float(pos["contracts"]))
            if amt > 0:
                self.place_market_order(side, amt, {"reduceOnly": True})

    # ─── Precision helpers ─────────────────────

    def amount_to_precision(self, amount: float) -> float:
        return float(self.ex.amount_to_precision(SYMBOL, amount))

    def price_to_precision(self, price: float) -> float:
        return float(self.ex.price_to_precision(SYMBOL, price))

    def usdt_to_contracts(self, usdt: float, price: float) -> float:
        market = self.ex.market(SYMBOL)
        contract_size = float(market.get("contractSize", 1))
        contracts = (usdt * LEVERAGE) / (price * contract_size)
        return self.amount_to_precision(contracts)
