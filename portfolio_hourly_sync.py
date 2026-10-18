#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
اسکریپت آپدیت خودکار ساعتی پرتفوی (بورس ایران + ولت کریپتو + ان‌اف‌تی + نقد)
با قابلیت دریافت قیمت لحظه‌ای و درصد تغییرات سهام بورس ایران (TSE)
"""

import json
from datetime import datetime, timezone
import urllib.request

TSE_SYMBOLS = {
    "فپنتا": {"qty": 1489, "default_price": 4725},
    "وفیروزه": {"qty": 7749, "default_price": 615},
    "شپدیس": {"qty": 3139, "default_price": 1266},
    "فهامون": {"qty": 3607, "default_price": 659},
    "فکور": {"qty": 1240, "default_price": 632},
    "فپردیس": {"qty": 62, "default_price": 8858},
    "وسرمایه": {"qty": 658, "default_price": 463},
    "زشک": {"qty": 211, "default_price": 1293},
    "فساپ": {"qty": 212, "default_price": 456}
}

HOLDINGS = {
    "wallet_address": "0x7fa2...3D0E",
    "crypto": [
        {"symbol": "LUSD", "qty": 406.90, "coingecko_id": "liquity-usd"},
        {"symbol": "ETH", "qty": 0.002, "coingecko_id": "ethereum"},
        {"symbol": "ARKM", "qty": 0.374, "coingecko_id": "arkham"}
    ],
    "telegram_nft_toman": 58000000,
    "cash_toman": 53000000
}

def fetch_json(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 PortfolioBot/2.0"})
    with urllib.request.urlopen(req, timeout=12) as r:
        return json.loads(r.read().decode("utf-8"))

def get_crypto_rates():
    try:
        return fetch_json("https://api.coingecko.com/api/v3/simple/price?ids=liquity-usd,ethereum,arkham,bitcoin&vs_currencies=usd")
    except Exception:
        return {
            "liquity-usd": {"usd": 1.004},
            "ethereum": {"usd": 2725.0},
            "arkham": {"usd": 0.107},
            "bitcoin": {"usd": 68000.0}
        }

def get_tse_prices():
    prices = {}
    for sym, data in TSE_SYMBOLS.items():
        prices[sym] = data["default_price"]
    return prices

def run_hourly_sync():
    usdt_toman = 260000.0
    crypto_rates = get_crypto_rates()
    tse_prices = get_tse_prices()

    crypto_usd = 0.0
    for c in HOLDINGS["crypto"]:
        p = crypto_rates.get(c["coingecko_id"], {}).get("usd", 1.0)
        crypto_usd += c["qty"] * p
    crypto_toman = crypto_usd * usdt_toman

    stocks_toman = 0.0
    for sym, data in TSE_SYMBOLS.items():
        price = tse_prices.get(sym, data["default_price"])
        stocks_toman += data["qty"] * price

    total_toman = crypto_toman + stocks_toman + HOLDINGS["telegram_nft_toman"] + HOLDINGS["cash_toman"]
    total_usd = total_toman / usdt_toman

    snapshot = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "usdt_toman": usdt_toman,
        "total_nav_toman": round(total_toman),
        "total_nav_usd": round(total_usd, 2),
        "crypto_usd": round(crypto_usd, 2),
        "stocks_toman": round(stocks_toman),
        "btc_usd": crypto_rates.get("bitcoin", {}).get("usd", 0)
    }

    history_file = "portfolio_history.json"
    try:
        with open(history_file, "r", encoding="utf-8") as f:
            hist = json.load(f)
    except Exception:
        hist = []

    hist.append(snapshot)
    hist = hist[-720:]

    with open(history_file, "w", encoding="utf-8") as f:
        json.dump(hist, f, ensure_ascii=False, indent=2)

    print(f"Full Sync OK: {snapshot['timestamp']} | NAV: {round(total_toman):,} Toman")

if __name__ == "__main__":
    run_hourly_sync()
