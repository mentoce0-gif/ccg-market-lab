"""設計値（v2 §2・§12.1）。市場の実測値ではない。変える時は版を上げ、次の試行から適用する。"""
from datetime import date, timedelta, timezone

RULE_VERSION = "v2.0.2-driver.1"

JST = timezone(timedelta(hours=9))

DAY1 = date(2026, 10, 5)
DAY90 = DAY1 + timedelta(days=89)  # 2027-01-02
WINDOW_DAYS = 30

# §2.4 支出の枠（円）。30日窓ごとの区分の上限
CATEGORY_CAP_PER_WINDOW = {
    "base": 8_000,      # 共通基盤
    "trial": 12_000,    # 個別の試行
    "delivery": 4_000,  # 納品の変動費
    "fees": 6_000,      # 手数料・為替・予備（Etsy の手数料を含む）
}
WINDOW_TOTAL_CAP = 30_000
MONTH_TOTAL_CAP = 30_000
POC_TOTAL_CAP = 90_000
PER_TRIAL_CAP = 3_000
MAX_NEW_TRIALS_PER_WINDOW = 4

# 区分の使用率がこれを超えたら、販売と従量課金を止めて例外票を出す（設計値）
STOP_RATIO = 0.9

# §12.1 Etsy の手数料（2026-09-27 に確認。実際の請求で置き換える）
ETSY_TRANSACTION_RATE = 0.065
ETSY_PAYMENT_RATE = 0.060
ETSY_PAYMENT_FIXED_CENTS = 30
ETSY_LISTING_FEE_CENTS = 20   # 販売時の自動更新にも同額がかかる前提 [未検証]
ETSY_FX_RATE = 0.025          # 出品通貨と入金通貨が違う時
FX_APPLIES = True             # 米ドル出品・円入金を前提 [未検証：Payoneer の受け取り通貨次第]

# API 再試行（§14 #3）
MAX_ATTEMPTS = 4
BACKOFF_SECONDS = (2, 4, 8)


def day_index(d: date) -> int:
    """Day1 を 1 とする通し番号。Day1 より前は 0 以下。"""
    return (d - DAY1).days + 1


def window_of(d: date) -> int:
    """30日窓の番号（1〜3）。Day1 より前の準備の支出は、厳しい側に倒して窓1に入れる。"""
    return max(1, (max(day_index(d), 1) - 1) // WINDOW_DAYS + 1)


def window_bounds(n: int) -> tuple[date, date]:
    start = DAY1 + timedelta(days=(n - 1) * WINDOW_DAYS)
    end = start + timedelta(days=WINDOW_DAYS - 1)
    if n == 1:
        start = date(2000, 1, 1)  # 準備期間の支出を含める
    return start, end
