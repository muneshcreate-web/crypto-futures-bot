"""
Universal Futures Trading Bot — Main Entry
Supports: Binance, Bybit, OKX, KuCoin, Bitget
Strategies: Grid, DCA
"""

import time
import sys
from datetime import datetime
from exchange import ExchangeClient
from notify import send
from config import (
    EXCHANGE_ID, SYMBOL, LEVERAGE, PAPER_TRADING,
    STRATEGY, CHECK_INTERVAL, MAX_DAILY_LOSS,
)


def confirm_live():
    print("\n" + "═" * 50)
    print(f"  ⚠️  LIVE TRADING MODE — REAL MONEY")
    print(f"  Exchange : {EXCHANGE_ID.upper()}")
    print(f"  Symbol   : {SYMBOL}")
    print(f"  Leverage : {LEVERAGE}x")
    print(f"  Strategy : {STRATEGY.upper()}")
    print("═" * 50)
    ans = input("\n  'yes' type karo confirm karne ke liye: ")
    if ans.strip().lower() != "yes":
        print("Cancelled.")
        sys.exit(0)


def main():
    mode = "📝 PAPER TEST" if PAPER_TRADING else "💰 LIVE"
    print(f"\n{'═'*50}")
    print(f"  Universal Futures Bot  |  {mode}")
    print(f"  Exchange: {EXCHANGE_ID.upper()}  |  {SYMBOL}  |  {LEVERAGE}x")
    print(f"  Strategy: {STRATEGY.upper()}")
    print(f"{'═'*50}\n")

    if not PAPER_TRADING:
        confirm_live()

    # Connect exchange
    print("[INFO] Exchange se connect ho raha hun...")
    client = ExchangeClient()
    bal = client.get_balance()
    print(f"[INFO] Balance: ${bal['free']:.2f} USDT free / ${bal['total']:.2f} total")

    # Load strategy
    if STRATEGY == "grid":
        from strategies.grid import GridStrategy
        strategy = GridStrategy(client)
    elif STRATEGY == "dca":
        from strategies.dca import DCAStrategy
        strategy = DCAStrategy(client)
    else:
        print(f"[ERROR] Unknown strategy: {STRATEGY}")
        sys.exit(1)

    send(
        f"🚀 <b>Bot Live!</b>\n"
        f"Exchange: {EXCHANGE_ID.upper()} | {mode}\n"
        f"Pair: {SYMBOL} | {LEVERAGE}x\n"
        f"Strategy: {STRATEGY.upper()}\n"
        f"Balance: ${bal['free']:.2f} USDT"
    )

    # Initial setup
    if STRATEGY == "grid":
        strategy.setup()

    # Main loop
    daily_loss_tracker = 0.0
    last_report = time.time()
    start_balance = bal["total"]

    while True:
        try:
            ok = strategy.tick()
            if not ok:
                send("🔴 Bot band ho gaya.")
                break

            # Daily loss check
            current_bal = client.get_balance()["total"]
            daily_pnl = current_bal - start_balance
            if daily_pnl <= -MAX_DAILY_LOSS:
                send(
                    f"🛑 <b>Daily Loss Limit Hit!</b>\n"
                    f"Loss: ${abs(daily_pnl):.2f} / Limit: ${MAX_DAILY_LOSS}\n"
                    "Bot band ho raha hai."
                )
                client.cancel_all_orders()
                client.close_all_positions()
                break

            # Hourly status
            if time.time() - last_report > 3600:
                price = client.get_price()
                positions = client.get_positions()
                pos_info = f"{len(positions)} open" if positions else "none"
                send(
                    f"📊 <b>Hourly Status</b>\n"
                    f"Price: ${price:,.2f}\n"
                    f"Balance: ${current_bal:.2f} USDT\n"
                    f"PnL today: ${daily_pnl:+.2f}\n"
                    f"Positions: {pos_info}"
                )
                last_report = time.time()

            time.sleep(CHECK_INTERVAL)

        except KeyboardInterrupt:
            send("⏹️ Bot manually band kiya gaya.")
            client.cancel_all_orders()
            client.close_all_positions()
            break
        except Exception as e:
            send(f"⚠️ Error: {e}")
            time.sleep(30)


if __name__ == "__main__":
    main()
