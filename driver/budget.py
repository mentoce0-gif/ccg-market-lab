"""予算の予約と上限（§2.4）。予約を原子的に取ってから処理を始める。"""
import uuid
from datetime import date

from . import config as C
from .control import engage_stop, open_ticket, require_not_stopped
from .db import audit, now_iso, tx


class BudgetExceeded(Exception):
    pass


def _fees_from_txn(conn, start: date, end: date) -> int:
    """売上に連動する手数料（Etsy）も枠に含める。実在の取引だけ（synthetic は除く）。"""
    r = conn.execute(
        "SELECT COALESCE(SUM(CAST(ROUND(fee_cents * jpy_per_usd / 100.0) AS INTEGER)),0) FROM txn "
        "WHERE paid=1 AND flag<>'synthetic' AND substr(paid_at,1,10) BETWEEN ? AND ?",
        (start.isoformat(), end.isoformat()),
    ).fetchone()
    return r[0]


def used(conn, start: date, end: date, category: str | None = None, experiment_id: str | None = None) -> int:
    """確定・暫定の費用＋保留中の予約（＋手数料区分なら取引の手数料）。"""
    where, args = ["on_date BETWEEN ? AND ?", "status='held'"], [start.isoformat(), end.isoformat()]
    cwhere, cargs = ["incurred_on BETWEEN ? AND ?", "status IN ('provisional','final')"], [start.isoformat(), end.isoformat()]
    if category:
        where.append("category=?"); args.append(category)
        cwhere.append("category=?"); cargs.append(category)
    if experiment_id:
        where.append("experiment_id=?"); args.append(experiment_id)
        cwhere.append("experiment_id=?"); cargs.append(experiment_id)
    held = conn.execute(f"SELECT COALESCE(SUM(amount_jpy),0) FROM reservation WHERE {' AND '.join(where)}", args).fetchone()[0]
    spent = conn.execute(f"SELECT COALESCE(SUM(amount_jpy),0) FROM cost WHERE {' AND '.join(cwhere)}", cargs).fetchone()[0]
    fees = _fees_from_txn(conn, start, end) if category in (None, "fees") and experiment_id is None else 0
    return held + spent + fees


def _month_bounds(d: date) -> tuple[date, date]:
    start = d.replace(day=1)
    nxt = date(d.year + (d.month == 12), d.month % 12 + 1, 1)
    return start, date.fromordinal(nxt.toordinal() - 1)


def headroom(conn, on_date: date, category: str, experiment_id: str | None = None) -> int:
    """その日に、その区分で使える残額。窓・暦月・90日・試行ごとの厳しい方。"""
    ws, we = C.window_bounds(C.window_of(on_date))
    ms, me = _month_bounds(on_date)
    limits = [
        C.CATEGORY_CAP_PER_WINDOW[category] - used(conn, ws, we, category),
        C.WINDOW_TOTAL_CAP - used(conn, ws, we),
        C.MONTH_TOTAL_CAP - used(conn, ms, me),
        C.POC_TOTAL_CAP - used(conn, date(2000, 1, 1), C.DAY90),
    ]
    if category == "trial" and experiment_id:
        limits.append(C.PER_TRIAL_CAP - used(conn, date(2000, 1, 1), C.DAY90, "trial", experiment_id))
    return min(limits)


def reserve(conn, category: str, amount_jpy: int, on_date: date, experiment_id: str | None = None, actor="driver") -> str:
    """最悪の場合の費用を先に予約する。足りなければ拒否し、総額を超えない（§14 #4）。"""
    if category not in C.CATEGORY_CAP_PER_WINDOW:
        raise ValueError(category)
    if category == "trial" and not experiment_id:
        raise ValueError("個別の試行の費用には experiment_id が要る")
    with tx(conn):
        require_not_stopped(conn, "spend", *( [f"experiment:{experiment_id}"] if experiment_id else [] ))
        room = headroom(conn, on_date, category, experiment_id)
        if amount_jpy > room:
            audit(conn, actor, "reserve", "denied", f"{category} {amount_jpy} > room {room}")
            raise BudgetExceeded(f"{category}: 予約 {amount_jpy} 円 > 残額 {room} 円")
        rid = f"R-{uuid.uuid4().hex[:12]}"
        conn.execute(
            "INSERT INTO reservation (reservation_id, created_at, on_date, category, experiment_id, amount_jpy, status) "
            "VALUES (?,?,?,?,?,?,'held')",
            (rid, now_iso(), on_date.isoformat(), category, experiment_id, amount_jpy),
        )
        audit(conn, actor, "reserve", "ok", f"{rid} {category} {amount_jpy}")
    return rid


def settle(conn, reservation_id: str, actual_jpy: int, vendor: str, currency="JPY", note="") -> str:
    """実費を記録し、使わなかった予約を返す。実費が予約を超えたら例外票を出す。"""
    with tx(conn):
        r = conn.execute("SELECT * FROM reservation WHERE reservation_id=? AND status='held'", (reservation_id,)).fetchone()
        if r is None:
            raise ValueError(f"保留中の予約がない: {reservation_id}")
        cid = f"C-{reservation_id[2:]}"
        conn.execute(
            "INSERT INTO cost (cost_id, incurred_on, currency, amount_jpy, category, experiment_id, vendor, status, note) "
            "VALUES (?,?,?,?,?,?,?,'final',?)",
            (cid, r["on_date"], currency, actual_jpy, r["category"], r["experiment_id"], vendor, note),
        )
        conn.execute("UPDATE reservation SET status='settled', actual_cost_id=? WHERE reservation_id=?", (cid, reservation_id))
        if actual_jpy > r["amount_jpy"]:
            engage_stop(conn, "spend", f"実費が予約を超過: {reservation_id}")
            open_ticket(conn, kind="budget_overrun", dedupe_key=f"overrun:{reservation_id}",
                        ask="予約を超えた支出の扱いを決めてください", minutes=5, target=f"予約 {reservation_id}",
                        reason=f"予約 {r['amount_jpy']} 円に対し実費 {actual_jpy} 円", deadline=r["on_date"],
                        options=[{"label": "今回の超過を記録して支出の停止を解除", "recommended": False},
                                 {"label": "停止のまま、原因を直す", "recommended": True}],
                        on_no_answer="支出は止めたまま。関係のない処理は続ける")
    return cid


def release(conn, reservation_id: str) -> None:
    with tx(conn):
        conn.execute("UPDATE reservation SET status='released' WHERE reservation_id=? AND status='held'", (reservation_id,))


def check_fee_headroom(conn, on_date: date) -> bool:
    """手数料区分が上限に近づいたら、販売と従量課金を止めて例外票を出す（§2.4）。止めたら True。"""
    ws, we = C.window_bounds(C.window_of(on_date))
    cap = C.CATEGORY_CAP_PER_WINDOW["fees"]
    u = used(conn, ws, we, "fees")
    if u < cap * C.STOP_RATIO:
        return False
    engage_stop(conn, "global", f"手数料・予備の区分が {u}/{cap} 円")
    open_ticket(conn, kind="budget_near_cap", dedupe_key=f"feecap:{C.window_of(on_date)}",
                ask="手数料の区分が上限に近いので、販売を止めました。予算の変更案を選んでください", minutes=5,
                target=f"窓{C.window_of(on_date)} の手数料 {u}/{cap} 円", reason="売上連動の費用が枠の90%に達した",
                options=[{"label": "止めたまま、この窓を終える", "recommended": True},
                         {"label": "予備の区分を試行から移す（A4 で具体案）", "recommended": False}],
                deadline=we.isoformat(), on_no_answer="販売は止めたまま。照合と報告は続ける")
    return True
