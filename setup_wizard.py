"""
🧙 Setup Wizard — Pehli baar yahi chalao
Yeh automatically config.py banayega
"""

import os
import sys

CYAN  = "\033[96m"
GREEN = "\033[92m"
YELLOW= "\033[93m"
RED   = "\033[91m"
BOLD  = "\033[1m"
RESET = "\033[0m"

def pr(color, text):
    print(color + text + RESET)

def ask(prompt, default=""):
    if default:
        val = input(f"  {prompt} [{default}]: ").strip()
        return val if val else default
    else:
        while True:
            val = input(f"  {prompt}: ").strip()
            if val:
                return val
            pr(RED, "  ⚠ Khali nahi chhod sakte!")

def main():
    os.system("clear")
    pr(BOLD + CYAN, """
╔═══════════════════════════════════════════════╗
║     🤖  FUTURES BOT SETUP WIZARD              ║
║     Ek baar setup karo, bot chalata rahega    ║
╚═══════════════════════════════════════════════╝
""")

    pr(YELLOW, "📋 Pehle kuch zaroori cheezein:")
    print("""
  1. BYBIT TESTNET pe free account banao (koi real paisa nahi lagta):
     👉  https://testnet.bybit.com/

  2. Login karo phir:
     Top right corner → Profile icon → API Management → Create New Key

     Name: MyBot (kuch bhi likho)
     Permissions: ✅ Trade  ✅ Futures  (Withdraw bilkul mat dena!)

     API Key aur Secret Key copy karo

  3. Telegram bot (optional, baad mein bhi kar sakte ho):
     Telegram mein @BotFather → /newbot → token copy karo
    """)

    input(f"  {YELLOW}API Key ready hai? Enter dabao...{RESET}")
    print()

    # ─── Exchange ───────────────────────────────
    pr(BOLD, "\n📡 STEP 1: Exchange choose karo")
    print("""
    1. bybit     ← Shuruaat ke liye best (Recommended)
    2. binance   ← Sabse popular
    3. okx       ← Acchi fees
    4. kucoinfutures
    """)
    ex_choice = ask("Number likhao (1/2/3/4)", "1")
    exchanges = {"1": "bybit", "2": "binance", "3": "okx", "4": "kucoinfutures"}
    exchange_id = exchanges.get(ex_choice, "bybit")
    pr(GREEN, f"  ✅ {exchange_id.upper()} select hua")

    # ─── API Keys ───────────────────────────────
    pr(BOLD, "\n🔑 STEP 2: API Keys daalo")
    pr(YELLOW, "  (Testnet keys daalo — real keys mat daalo abhi!)")
    api_key    = ask("API Key paste karo")
    api_secret = ask("Secret Key paste karo")
    passphrase = ""
    if exchange_id in ("okx", "kucoinfutures"):
        passphrase = ask("Passphrase (OKX/KuCoin ke liye)")

    # ─── Trading pair ───────────────────────────
    pr(BOLD, "\n💰 STEP 3: Kaunsa coin trade karna hai?")
    print("""
    1. BTC  — Bitcoin (sabse stable)
    2. ETH  — Ethereum (popular)
    3. SOL  — Solana (fast mover)
    4. XRP  — Ripple
    5. DOGE — Dogecoin
    """)
    coin_choice = ask("Number likhao (1/2/3/4/5)", "1")
    coins = {
        "1": "BTC/USDT:USDT",
        "2": "ETH/USDT:USDT",
        "3": "SOL/USDT:USDT",
        "4": "XRP/USDT:USDT",
        "5": "DOGE/USDT:USDT",
    }
    symbol = coins.get(coin_choice, "BTC/USDT:USDT")
    pr(GREEN, f"  ✅ {symbol} select hua")

    # ─── Strategy ───────────────────────────────
    pr(BOLD, "\n📊 STEP 4: Strategy choose karo")
    print("""
    1. grid  — Price range mein auto buy/sell (sideways market best)
    2. dca   — Girte price mein kharidna, upar pe sell (trending market best)
    """)
    strat_choice = ask("Number likhao (1/2)", "1")
    strategy = "grid" if strat_choice == "1" else "dca"
    pr(GREEN, f"  ✅ {strategy.upper()} strategy select hua")

    # ─── Investment ─────────────────────────────
    pr(BOLD, "\n💵 STEP 5: Kitna invest karna hai? (USDT mein)")
    pr(YELLOW, "  Testnet mein fake money hai, koi risk nahi!")
    investment = ask("Amount likhao", "100")

    # ─── Leverage ───────────────────────────────
    pr(BOLD, "\n⚡ STEP 6: Leverage (1x = safe, 5x = moderate)")
    pr(YELLOW, "  Shuruaat mein 3x ya 5x rakho")
    leverage = ask("Leverage likhao (1-20)", "3")

    # ─── Telegram ───────────────────────────────
    pr(BOLD, "\n📱 STEP 7: Telegram notifications (optional)")
    want_tg = ask("Telegram setup karna hai? (yes/no)", "no")
    tg_token = "TELEGRAM_TOKEN_YAHAN_DAALO"
    tg_chat  = "TELEGRAM_CHAT_ID_YAHAN_DAALO"
    if want_tg.lower() in ("yes", "y", "ha", "han"):
        pr(YELLOW, "  @BotFather → /newbot → token copy karo")
        tg_token = ask("Telegram Bot Token paste karo")
        pr(YELLOW, "  Apne bot ko ek message bhejo, phir")
        pr(YELLOW, "  https://api.telegram.org/bot<TOKEN>/getUpdates mein chat id dekho")
        tg_chat  = ask("Chat ID paste karo")

    # ─── Write config ───────────────────────────
    config_content = f'''"""
Bot Configuration — Setup Wizard se banaya gaya
"""

EXCHANGE_ID    = "{exchange_id}"
API_KEY        = "{api_key}"
API_SECRET     = "{api_secret}"
API_PASSPHRASE = "{passphrase}"

PAPER_TRADING  = True   # Pehle True rakho, test karo, phir False

SYMBOL         = "{symbol}"
LEVERAGE       = {leverage}
MARGIN_MODE    = "isolated"

STRATEGY       = "{strategy}"

GRID_INVESTMENT_USDT  = {investment}
GRID_LEVELS           = 6
GRID_SPREAD_PERCENT   = 0.8
GRID_DIRECTION        = "both"

DCA_BASE_ORDER_USDT   = {int(int(investment) * 0.2)}
DCA_SAFETY_ORDER_USDT = {int(int(investment) * 0.15)}
DCA_MAX_SAFETY_ORDERS = 5
DCA_PRICE_DEVIATION   = 1.5
DCA_TAKE_PROFIT_PCT   = 2.0

STOP_LOSS_PCT  = 5.0
TAKE_PROFIT_PCT= 4.0
MAX_DAILY_LOSS = {int(int(investment) * 0.3)}
CHECK_INTERVAL = 30

TELEGRAM_TOKEN   = "{tg_token}"
TELEGRAM_CHAT_ID = "{tg_chat}"
'''

    script_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(script_dir, "config.py")
    with open(config_path, "w") as f:
        f.write(config_content)

    pr(GREEN, "\n✅ config.py ban gaya!")

    # ─── Test connection ────────────────────────
    pr(BOLD, "\n🔌 Exchange connection test kar raha hun...")
    try:
        import ccxt
        params = {"apiKey": api_key, "secret": api_secret,
                  "enableRateLimit": True, "options": {"defaultType": "future"}}
        if passphrase:
            params["password"] = passphrase
        ex = getattr(ccxt, exchange_id)(params)
        ex.set_sandbox_mode(True)
        ex.load_markets()
        pr(GREEN, f"  ✅ {exchange_id.upper()} se connection successful!")

        bal = ex.fetch_balance({"type": "future"})
        usdt = bal.get("USDT", {})
        free = float(usdt.get("free", 0))
        pr(GREEN, f"  ✅ Balance: ${free:,.2f} USDT (testnet)")

    except Exception as e:
        pr(RED, f"  ❌ Connection failed: {e}")
        pr(YELLOW, "  Check karo: API key sahi hai? Testnet pe banaya?")
        sys.exit(1)

    # ─── Done ───────────────────────────────────
    pr(BOLD + GREEN, """
╔═══════════════════════════════════════════════╗
║  🎉  SETUP COMPLETE!                          ║
╚═══════════════════════════════════════════════╝
""")
    print(f"  Exchange  : {exchange_id.upper()}")
    print(f"  Symbol    : {symbol}")
    print(f"  Strategy  : {strategy.upper()}")
    print(f"  Leverage  : {leverage}x")
    print(f"  Investment: ${investment} USDT")
    print(f"  Mode      : PAPER TEST (fake money)")
    pr(YELLOW, "\n  Ab bot chalane ke liye:")
    pr(BOLD + CYAN, "  python3 bot.py")
    print()


if __name__ == "__main__":
    main()
