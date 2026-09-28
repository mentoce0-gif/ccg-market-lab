"""取り込み（受注番号で重複を除く）・納品の確認・variant・原典の変化・損益の集計（§8.2、§12.1）。"""
import csv
import hashlib
import hmac
import json
import os
from datetime import date, datetime, timedelta
from pathlib import Path

from . import config as C
from .control import engage_stop, open_ticket, quarantine_listing, require_allowed, require_not_stopped
from .db import audit, now_iso, tx


# ------------------------------------------------------------------ 仮名化
def pseudonymize(buyer_id, salt: str | None = None) -> str:
    salt = salt or os.environ.get("CCG_PSEUDO_SALT")
    if not salt:
        raise RuntimeError("CCG_PSEUDO_SALT が未設定。購入者 ID を生のまま保存しない")
    return "cus_" + hmac.new(salt.encode(), str(buyer_id).encode(), hashlib.sha256).hexdigest()[:16]


def _cents(money: dict | None) -> int:
    """Etsy の Money 型 {amount, divisor, currency_code} をセントに [未検証]。"""
    if not money:
        return 0
    return round(money["amount"] * 100 / money.get("divisor", 100))


def estimate_fee_cents(gross_cents: int, tax_cents: int) -> int:
    """§12.1 の料率で見積もる。実際の請求（fee_basis='actual'）で置き換える。"""
    fee = gross_cents * C.ETSY_TRANSACTION_RATE
    fee += (gross_cents + tax_cents) * C.ETSY_PAYMENT_RATE + C.ETSY_PAYMENT_FIXED_CENTS
    fee += C.ETSY_LISTING_FEE_CENTS
    if C.FX_APPLIES:
        fee += gross_cents * C.ETSY_FX_RATE
    return round(fee)


# ------------------------------------------------------------------ variant（§8.1、§14 #9）
def variant_for(conn, experiment_id, price_cents, channel="etsy", audience=None, copy_hash=None, currency="USD", now=None) -> str:
    """価格・販路・対象者・主な説明のどれかが違えば、別の variant ID。"""
    r = conn.execute(
        "SELECT variant_id FROM variant WHERE experiment_id=? AND price_cents=? AND currency=? AND channel=? "
        "AND audience IS ? AND main_copy_hash IS ?",
        (experiment_id, price_cents, currency, channel, audience, copy_hash),
    ).fetchone()
    if r:
        return r["variant_id"]
    n = conn.execute("SELECT COUNT(*) FROM variant WHERE experiment_id=?", (experiment_id,)).fetchone()[0] + 1
    vid = f"{experiment_id}-v{n}"
    conn.execute(
        "INSERT INTO variant (variant_id, experiment_id, price_cents, currency, channel, audience, main_copy_hash, created_at) "
        "VALUES (?,?,?,?,?,?,?,?)",
        (vid, experiment_id, price_cents, currency, channel, audience, copy_hash, now_iso(now)),
    )
    return vid


def attach_variant(conn, listing_id, variant_id, at: str) -> None:
    """掲載に適用する variant を切り替える。古い期間を閉じ、以後の閲覧・注文は新しい variant に数える。"""
    with tx(conn):
        conn.execute("UPDATE listing_variant SET to_at=? WHERE listing_id=? AND to_at IS NULL", (at, listing_id))
        conn.execute("INSERT INTO listing_variant (listing_id, variant_id, from_at) VALUES (?,?,?)", (listing_id, variant_id, at))
        conn.execute("UPDATE listing SET variant_id=? WHERE listing_id=?", (variant_id, listing_id))


def _variant_at(conn, listing_id, at: str):
    r = conn.execute(
        "SELECT variant_id FROM listing_variant WHERE listing_id=? AND from_at<=? AND (to_at IS NULL OR to_at>?) "
        "ORDER BY from_at DESC LIMIT 1",
        (listing_id, at, at),
    ).fetchone()
    return r["variant_id"] if r else None


# ------------------------------------------------------------------ 取り込み（§14 #1, #2, #7, #8）
def ingest_receipts(conn, receipts: list[dict], *, jpy_per_usd: float, salt: str | None = None,
                    mark_synthetic: bool = False, now: datetime | None = None) -> dict:
    """同じ receipt を何度取り込んでも1件。返金・支払いの状態は最新で上書きし、売上は毎回台帳から計算し直す。"""
    stats = {"new": 0, "updated": 0, "unchanged": 0, "delivery_missing": 0}
    for r in receipts:
        rid = str(r["receipt_id"])
        raw_hash = hashlib.sha256(json.dumps(r, sort_keys=True).encode()).hexdigest()
        cust = pseudonymize(r["buyer_user_id"], salt)
        tx_items = r.get("transactions") or [{}]
        listing_id = str(tx_items[0].get("listing_id")) if tx_items[0].get("listing_id") is not None else None
        gross = _cents(r.get("subtotal"))
        tax = _cents(r.get("total_tax_cost"))
        refund = sum(_cents(x.get("amount")) for x in r.get("refunds") or [])
        paid = 1 if r.get("is_paid") else 0
        paid_at = datetime.fromtimestamp(r["create_timestamp"], C.JST).isoformat(timespec="seconds") if paid else None
        with tx(conn):
            flag = "synthetic" if mark_synthetic else _customer_flag(conn, cust)
            prev = conn.execute("SELECT raw_hash, refund_cents, fee_basis FROM txn WHERE receipt_id=?", (rid,)).fetchone()
            if prev and prev["raw_hash"] == raw_hash:
                stats["unchanged"] += 1
                continue
            lst = conn.execute("SELECT * FROM listing WHERE listing_id=?", (listing_id,)).fetchone() if listing_id else None
            exp_id = lst["experiment_id"] if lst else None
            var_id = _variant_at(conn, listing_id, paid_at) if (lst and paid_at) else None
            delivery_ok = None if lst is None else int(bool(lst["has_digital_file"]))
            if prev is None:
                conn.execute(
                    "INSERT INTO txn (receipt_id, customer_id, listing_id, variant_id, experiment_id, currency, gross_cents, "
                    "tax_cents, fee_cents, refund_cents, jpy_per_usd, paid, paid_at, flag, delivery_ok, ingested_at, raw_hash) "
                    "VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                    (rid, cust, listing_id, var_id, exp_id, (r.get("subtotal") or {}).get("currency_code", "USD"), gross,
                     tax, estimate_fee_cents(gross, tax) if paid else 0, refund, jpy_per_usd, paid, paid_at, flag,
                     delivery_ok, now_iso(now), raw_hash),
                )
                conn.execute(
                    "INSERT INTO event (at, experiment_id, kind, customer_id, receipt_id, flag, evidence) VALUES (?,?,?,?,?,?,?)",
                    (paid_at or now_iso(now), exp_id, "purchase" if paid else "order_unpaid", cust, rid, flag, f"etsy_receipt:{rid}"),
                )
                stats["new"] += 1
            else:
                conn.execute(
                    "UPDATE txn SET refund_cents=?, paid=?, paid_at=COALESCE(paid_at, ?), raw_hash=?, "
                    "fee_cents=CASE WHEN fee_basis='estimate' THEN ? ELSE fee_cents END WHERE receipt_id=?",
                    (refund, paid, paid_at, raw_hash, estimate_fee_cents(gross, tax) if paid else 0, rid),
                )
                if refund > prev["refund_cents"]:
                    conn.execute(
                        "INSERT INTO event (at, experiment_id, kind, customer_id, receipt_id, flag, evidence) VALUES (?,?,?,?,?,?,?)",
                        (now_iso(now), exp_id, "refund", cust, rid, flag, f"etsy_receipt:{rid}"),
                    )
                stats["updated"] += 1
            if paid and delivery_ok == 0 and flag != "synthetic":
                stats["delivery_missing"] += 1
                open_ticket(
                    conn, kind="delivery_missing", dedupe_key=f"delivery:{rid}",
                    ask="注文は確定したが納品ファイルが添付されていません。復旧か返金を選んでください",
                    minutes=10, target=f"Etsy 注文 {rid}（掲載 {listing_id}）",
                    reason="Etsy の掲載にダウンロード用ファイルがない（API で確認）",
                    options=[{"label": "Claude がファイルを添付し直し、購入者への連絡文を下書き（送信は Shun）", "recommended": True},
                             {"label": "全額返金（元の決済経路）", "recommended": False}],
                    deadline=(now or datetime.now(C.JST)).date().isoformat(),
                    on_no_answer="この掲載の販売は止めたまま。関係のない処理は続ける", now=now,
                )
                engage_stop(conn, f"listing:{listing_id}", f"納品ファイルの欠落（注文 {rid}）", now)
    return stats


def _customer_flag(conn, customer_id) -> str:
    r = conn.execute("SELECT flag FROM customer_flag WHERE customer_id=?", (customer_id,)).fetchone()
    return r["flag"] if r else "none"


def flag_customer(conn, customer_id, flag, basis) -> None:
    """知人・自己・テストの購入者を印付けする。取引は台帳に残し、成功の指標から除く（§14 #8）。"""
    with tx(conn):
        conn.execute(
            "INSERT INTO customer_flag (customer_id, flag, basis) VALUES (?,?,?) "
            "ON CONFLICT(customer_id) DO UPDATE SET flag=excluded.flag, basis=excluded.basis",
            (customer_id, flag, basis),
        )
        conn.execute("UPDATE txn SET flag=? WHERE customer_id=? AND flag<>'synthetic'", (flag, customer_id))


def refresh_listing(conn, client, listing_id, on_date: date) -> None:
    """累計閲覧数（日次）と、ダウンロード用ファイルの有無を API で記録する。"""
    info = client.get_listing(listing_id)
    files = client.get_listing_files(listing_id)
    with tx(conn):
        if "views" in info:
            conn.execute(
                "INSERT INTO view_snapshot (listing_id, on_date, cumulative_views) VALUES (?,?,?) "
                "ON CONFLICT(listing_id, on_date) DO UPDATE SET cumulative_views=excluded.cumulative_views",
                (listing_id, on_date.isoformat(), int(info["views"])),
            )
        conn.execute("UPDATE listing SET has_digital_file=? WHERE listing_id=?", (1 if files else 0, listing_id))


# ------------------------------------------------------------------ 公開（§14 #12）
def publish(conn, client, listing_id: str, *, gates_passed: list[str], fmt: str, now: datetime) -> str:
    """停止スイッチと委任を確かめ、意図を先に記録してから公開する。再起動しても二重に公開しない。"""
    lst = conn.execute("SELECT l.*, v.price_cents FROM listing l JOIN variant v ON v.variant_id=l.variant_id "
                       "WHERE listing_id=?", (listing_id,)).fetchone()
    key = f"publish:{listing_id}:{lst['variant_id']}"
    require_not_stopped(conn, f"listing:{listing_id}", f"experiment:{lst['experiment_id']}")
    require_allowed(conn, "publish_listing", {"price_cents": lst["price_cents"], "format": fmt, "gates_passed": gates_passed}, now)
    intent = conn.execute("SELECT status FROM publish_intent WHERE idem_key=?", (key,)).fetchone()
    if intent and intent["status"] == "done":
        return "already"
    if intent and intent["status"] == "pending":
        # 途中で止まった。まず Etsy 側の状態を確かめ、公開済みなら呼び直さない
        if client.get_listing(listing_id).get("state") == "active":
            _mark_published(conn, key, listing_id, now)
            audit(conn, "driver", "publish", "recovered", key, now)
            return "recovered"
    else:
        with tx(conn):
            conn.execute("INSERT INTO publish_intent (idem_key, listing_id, status, created_at) VALUES (?,?,'pending',?)",
                         (key, listing_id, now_iso(now)))
    client.activate_listing(listing_id)
    _mark_published(conn, key, listing_id, now)
    audit(conn, "driver", "publish", "ok", key, now)
    return "published"


def _mark_published(conn, key, listing_id, now):
    with tx(conn):
        conn.execute("UPDATE publish_intent SET status='done', done_at=? WHERE idem_key=?", (now_iso(now), key))
        conn.execute("UPDATE listing SET state='active', published_on=COALESCE(published_on, ?) WHERE listing_id=?",
                     (now.date().isoformat(), listing_id))


# ------------------------------------------------------------------ 原典の変化（§14 #10）
def mark_source_changed(conn, ref: str, *, critical: bool, client=None, now=None) -> list[str]:
    """ref（demand_id か原典 URL）に依存する商品に再確認の印。重要なら販売を止める。"""
    hit = []
    for a in conn.execute("SELECT artifact_id, version, experiment_id, input_sources FROM artifact").fetchall():
        if ref in json.loads(a["input_sources"] or "[]"):
            hit.append(a)
    with tx(conn):
        conn.execute("UPDATE demand SET source_gone=1 WHERE demand_id=? OR url=?", (ref, ref))
        for a in hit:
            conn.execute("UPDATE artifact SET needs_recheck=1 WHERE artifact_id=? AND version=?", (a["artifact_id"], a["version"]))
        if critical:
            for a in hit:
                for l in conn.execute("SELECT listing_id FROM listing WHERE experiment_id=? AND state='active'",
                                      (a["experiment_id"],)).fetchall():
                    quarantine_listing(conn, l["listing_id"], f"根拠の原典が変化: {ref}", client, now)
    return [f"{a['artifact_id']}@{a['version']}" for a in hit]


# ------------------------------------------------------------------ 人手（ledger/human_work.csv が正本）
def load_human_work(conn, csv_path: Path) -> int:
    rows = list(csv.DictReader(csv_path.open(encoding="utf-8")))
    with tx(conn):
        conn.execute("DELETE FROM human_work")
        for r in rows:
            conn.execute(
                "INSERT INTO human_work (at, minutes, role, experiment_id, kind, exception_reason, task, is_ai_relay) "
                "VALUES (?,?,?,?,?,?,?,?)",
                (r["date"], int(r["minutes"]) if r["minutes"].strip() else None, r["role"], r["trial_id"] or None,
                 r["kind"], r["exception_reason"] or None, r["note"], 1 if r["is_ai_relay"].strip() == "yes" else 0),
            )
    return len(rows)


# ------------------------------------------------------------------ 集計（§8.2、§12.1）
def _range_args(start: date, end_incl: date):
    return start.isoformat(), (end_incl + timedelta(days=1)).isoformat()


def metrics(conn, start: date, end_incl: date, experiment_id: str | None = None) -> dict:
    """期間の損益。売上は毎回、台帳の取引から計算し直す（返金で再計算される）。"""
    s, e = _range_args(start, end_incl)
    cond, args = "paid=1 AND paid_at>=? AND paid_at<?", [s, e]
    if experiment_id:
        cond += " AND experiment_id=?"; args.append(experiment_id)
    rows = conn.execute(f"SELECT * FROM txn WHERE {cond}", args).fetchall()
    real = [r for r in rows if r["flag"] != "synthetic"]
    qual = [r for r in real if r["flag"] == "none" and r["refund_cents"] < r["gross_cents"]]
    yen = lambda c, r: round(c * r["jpy_per_usd"] / 100)  # noqa: E731
    revenue = sum(yen(r["gross_cents"] - r["refund_cents"], r) for r in qual)
    # 除外した取引（知人・テスト・全額返金）の手数料も、実際にかかった費用として引く（保守側）
    fees = sum(yen(r["fee_cents"], r) for r in real)
    by_cust: dict[str, int] = {}
    for r in qual:
        by_cust[r["customer_id"]] = by_cust.get(r["customer_id"], 0) + yen(r["gross_cents"] - r["refund_cents"], r)
    ccond, cargs = "incurred_on>=? AND incurred_on<? AND status IN ('provisional','final')", [s, e]
    if experiment_id:
        ccond += " AND experiment_id=?"; cargs.append(experiment_id)
    costs = conn.execute(f"SELECT COALESCE(SUM(amount_jpy),0) FROM cost WHERE {ccond}", cargs).fetchone()[0]
    delivery_var = conn.execute(
        f"SELECT COALESCE(SUM(amount_jpy),0) FROM cost WHERE {ccond} AND category='delivery'", cargs).fetchone()[0]
    return {
        "revenue_jpy": revenue,
        "fees_jpy": fees,
        "costs_jpy": costs,
        "net_jpy": revenue - fees - costs,
        "marginal_jpy": revenue - fees - delivery_var,
        "charges": len(qual),
        "buyers": len(by_cust),
        "top_customer_share": round(max(by_cust.values()) / revenue, 4) if revenue > 0 else None,
        "delivered_ok": sum(1 for r in qual if r["delivery_ok"] == 1),
        "delivery_missing": sum(1 for r in qual if r["delivery_ok"] == 0),
        "excluded": len(real) - len(qual),
        "fees_estimated": any(r["fee_basis"] == "estimate" for r in real),
    }


def human_minutes(conn, start: date, end_incl: date) -> dict:
    s, e = _range_args(start, end_incl)
    rows = conn.execute("SELECT kind, minutes, is_ai_relay FROM human_work WHERE at>=? AND at<?", (s, e)).fetchall()
    out = {"normal": 0, "abnormal": 0, "exception": 0, "relay": 0, "unrecorded": 0}
    for r in rows:
        if r["minutes"] is None:
            out["unrecorded"] += 1
            continue
        out[r["kind"]] += r["minutes"]
        if r["is_ai_relay"]:
            out["relay"] += r["minutes"]
    return out


def general_views(conn, listing_id: str, start: date, end_incl: date, variant_id: str | None = None) -> int | None:
    """一般閲覧＝累計閲覧数の日次差分（§8.2）。variant を指定したら、その適用期間の日だけ数える。"""
    snaps = conn.execute("SELECT on_date, cumulative_views FROM view_snapshot WHERE listing_id=? ORDER BY on_date",
                         (listing_id,)).fetchall()
    if not snaps:
        return None
    periods = None
    if variant_id:
        periods = conn.execute("SELECT from_at, to_at FROM listing_variant WHERE listing_id=? AND variant_id=?",
                               (listing_id, variant_id)).fetchall()
    total, prev = 0, None
    for sn in snaps:
        d = sn["on_date"]
        if prev is not None and start.isoformat() <= d <= end_incl.isoformat():
            inside = periods is None or any(p["from_at"][:10] < d and (p["to_at"] is None or d <= p["to_at"][:10]) for p in periods)
            if inside:
                total += max(0, sn["cumulative_views"] - prev)
        prev = sn["cumulative_views"]
    return total


# ------------------------------------------------------------------ 判定表（§8.3、一般閲覧ベース）
def evaluate(views_14d: int | None, purchases: int, buyers: int, marginal_jpy: int, delivery_ok: bool,
             severe_defect: bool = False) -> tuple[str, str]:
    note = "一般閲覧ベース"
    if severe_defect:
        return "STOP", "S0/S1 または支出の逸脱"
    if views_14d is None:
        return "INCONCLUSIVE", "到達は未計測"
    if buyers >= 3 and delivery_ok and marginal_jpy > 0:
        return "KEEP候補", note
    if purchases > 0 and marginal_jpy <= 0:
        return "STOP", "商品の限界利益が0以下（価格か提供方法を直す）"
    if purchases >= 1:
        return "観測を続ける", note
    if views_14d >= 100:
        return "STOP", f"到達{views_14d}・購入0。この条件の試行を終える（{note}）"
    if views_14d >= 30:
        return "REVISE", f"到達{views_14d}・購入0。弱い否定の信号（{note}）"
    return "INCONCLUSIVE", f"到達{views_14d}（30未満）。到達不足（{note}）"
