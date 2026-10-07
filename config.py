"""
Universal Futures Bot — Configuration
Supported exchanges: binance, bybit, okx, kucoinfutures, bitget, gate
Cloud (Railway) pe environment variables se values aati hain — keys yahan mat likhna!
"""

import os

# ══════════════════════════════════════════════
#  EXCHANGE SETTINGS — Environment variables se aata hai (Railway mein set karo)
# ══════════════════════════════════════════════
EXCHANGE_ID    = os.getenv("EXCHANGE_ID",    "bybit")
API_KEY        = os.getenv("API_KEY",        "")
API_SECRET     = os.getenv("API_SECRET",     "")
API_PASSPHRASE = os.getenv("API_PASSPHRASE", "")

PAPER_TRADING  = os.getenv("PAPER_TRADING", "true").lower() == "true"

# ══════════════════════════════════════════════
#  TRADING SETTINGS
# ══════════════════════════════════════════════
SYMBOL      = os.getenv("SYMBOL",      "BTC/USDT:USDT")
LEVERAGE    = int(os.getenv("LEVERAGE", "5"))
MARGIN_MODE = os.getenv("MARGIN_MODE", "isolated")

# ══════════════════════════════════════════════
#  STRATEGY
# ══════════════════════════════════════════════
STRATEGY = os.getenv("STRATEGY", "grid")

# --- Grid Settings ---
GRID_INVESTMENT_USDT  = float(os.getenv("GRID_INVESTMENT_USDT",  "100"))
GRID_LEVELS           = int(os.getenv("GRID_LEVELS",             "6"))
GRID_SPREAD_PERCENT   = float(os.getenv("GRID_SPREAD_PERCENT",   "0.8"))
GRID_DIRECTION        = os.getenv("GRID_DIRECTION",              "both")

# --- DCA Settings ---
DCA_BASE_ORDER_USDT   = float(os.getenv("DCA_BASE_ORDER_USDT",   "20"))
DCA_SAFETY_ORDER_USDT = float(os.getenv("DCA_SAFETY_ORDER_USDT", "15"))
DCA_MAX_SAFETY_ORDERS = int(os.getenv("DCA_MAX_SAFETY_ORDERS",   "5"))
DCA_PRICE_DEVIATION   = float(os.getenv("DCA_PRICE_DEVIATION",   "1.5"))
DCA_TAKE_PROFIT_PCT   = float(os.getenv("DCA_TAKE_PROFIT_PCT",   "2.0"))

# ══════════════════════════════════════════════
#  RISK MANAGEMENT
# ══════════════════════════════════════════════
STOP_LOSS_PCT   = float(os.getenv("STOP_LOSS_PCT",   "5.0"))
TAKE_PROFIT_PCT = float(os.getenv("TAKE_PROFIT_PCT", "4.0"))
MAX_DAILY_LOSS  = float(os.getenv("MAX_DAILY_LOSS",  "30.0"))
CHECK_INTERVAL  = int(os.getenv("CHECK_INTERVAL",    "30"))

# ══════════════════════════════════════════════
#  TELEGRAM NOTIFICATIONS
# ══════════════════════════════════════════════
TELEGRAM_TOKEN   = os.getenv("TELEGRAM_TOKEN",   "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")

# ══════════════════════════════════════════════
#  POPULAR SYMBOLS REFERENCE
# ══════════════════════════════════════════════
# Binance Futures : "BTC/USDT:USDT", "ETH/USDT:USDT"
# Bybit Futures   : "BTC/USDT:USDT", "SOL/USDT:USDT"
# OKX Futures     : "BTC/USDT:USDT", "DOGE/USDT:USDT"
# KuCoin Futures  : "BTC/USDT:USDT", "XRP/USDT:USDT"
