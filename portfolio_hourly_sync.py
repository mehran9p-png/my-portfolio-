#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
اسکریپت آپدیت خودکار ساعتی پرتفوی اختصاصی (بورس ایران + ولت کریپتو + ان‌اف‌تی + نقد)
پیکربندی شده برای گیت‌هاب اکشنز (GitHub Actions)
"""

import json
from datetime import datetime, timezone
import urllib.request

# پیکربندی دارایی‌های استخراج شده
HOLDINGS = {
    "wallet_address": "0x7fa2...3D0E",
    "crypto": [
        {"symbol": "LUSD", "qty": 406.90, "coingecko_id": "liquity-usd", "is_stable": True},
        {"symbol": "ETH", "qty": 0.002, "coingecko_id": "ethereum", "is_stable": False},
        {"symbol": "ARKM", "qty": 0.374, "coingecko_id": "arkham", "is_stable": False}
    ],
    "telegram_nft_toman": 50000000,
    "cash_toman": 56000000,
    "tse_stocks": [
        {"symbol": "فپنتا", "qty": 1489, "price_toman": 4725},
        {"symbol": "وفیروزه", "qty": 7749, "price_toman": 615},
        {"symbol": "شپدیس", "qty": 3139, "price_toman": 1266},
        {"symbol": "فهامون", "qty": 3607, "price_toman": 659},
        {"symbol": "فکور", "qty": 1240, "price_toman": 632},
        {"symbol": "فردیس", "qty": 62, "price_toman": 8858},
        {"symbol": "وسرمایه", "qty": 658, "price_toman": 463},
        {"symbol": "زشک", "qty": 211, "price_toman": 1293},
        {"symbol": "فساپ", "qty": 212, "price_toman": 456}
    ]
}

def fetch_json(url):
    req = urllib.request.Request(url, headers={"User-Agent": "PortfolioBot/1.0"})
    with urllib.request.urlopen(req, timeout=12) as r:
        return json.loads(r.read().decode("utf-8"))

def get_live_rates():
    # دریافت قیمت کوین‌ها از CoinGecko
    try:
        cg = fetch_json("https://api.coingecko.com/api/v3/simple/price?ids=liquity-usd,ethereum,arkham,bitcoin&vs_currencies=usd")
    except Exception:
        cg = {"liquity-usd": {"usd": 1.004}, "ethereum": {"usd": 2725.0}, "arkham": {"usd": 0.107}, "bitcoin": {"usd": 68000.0}}
    return cg

def run_hourly_sync():
    usdt_toman = 260000.0  # نرخ مبنای اعلامی
    rates = get_live_rates()

    # ۱. محاسبه کریپتو
    crypto_usd = 0.0
    for c in HOLDINGS["crypto"]:
        p = rates.get(c["coingecko_id"], {}).get("usd", 1.0)
        crypto_usd += c["qty"] * p
    crypto_toman = crypto_usd * usdt_toman

    # ۲. محاسبه بورس
    stocks_toman = sum(s["qty"] * s["price_toman"] for s in HOLDINGS["tse_stocks"])
    stocks_usd = stocks_toman / usdt_toman

    # ۳. جمع کل
    total_toman = crypto_toman + stocks_toman + HOLDINGS["telegram_nft_toman"] + HOLDINGS["cash_toman"]
    total_usd = total_toman / usdt_toman

    snapshot = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "usdt_toman": usdt_toman,
        "total_nav_toman": round(total_toman),
        "total_nav_usd": round(total_usd, 2),
        "crypto_usd": round(crypto_usd, 2),
        "stocks_toman": round(stocks_toman),
        "btc_usd": rates.get("bitcoin", {}).get("usd", 0)
    }

    # افزودن به فایل تاریخچه ساعتی
    history_file = "portfolio_history.json"
    try:
        with open(history_file, "r", encoding="utf-8") as f:
            hist = json.load(f)
    except Exception:
        hist = []

    hist.append(snapshot)
    hist = hist[-720:]  # نگهداری ۷۲۰ ساعت (یک ماه گذشته)

    with open(history_file, "w", encoding="utf-8") as f:
        json.dump(hist, f, ensure_ascii=False, indent=2)

    print(f"Hourly Sync OK: {snapshot['timestamp']} | NAV: {round(total_toman):,} Toman (${round(total_usd, 2)})")

if __name__ == "__main__":
    run_hourly_sync()
