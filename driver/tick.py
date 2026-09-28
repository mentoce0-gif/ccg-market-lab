"""日次の処理（§10.1、§10.4）。LLM は使わない。"""
import time as _time
from datetime import datetime, timedelta
from pathlib import Path

from .budget import check_fee_headroom
from .control import acquire_lock, open_ticket, quarantine_listing, release_lock
from .etsy import RetryLimitExceeded, call_with_retry
from .ledger import ingest_receipts, refresh_listing
from .report import build_claims, render_weekly, verify


def tick(conn, client, now: datetime, *, jpy_per_usd: float, salt: str | None, dry_run: bool,
         reports_dir: Path | None = None, sleep=_time.sleep, holder: str = "daily") -> dict:
    if not acquire_lock(conn, "tick", holder, now):
        return {"status": "locked"}
    out: dict = {"status": "ok", "dry_run": dry_run}
    try:
        try:
            receipts = call_with_retry(client.get_receipts, sleep=sleep)
            out["ingest"] = ingest_receipts(conn, receipts, jpy_per_usd=jpy_per_usd, salt=salt,
                                            mark_synthetic=dry_run, now=now)
        except RetryLimitExceeded as e:
            out["ingest"] = "failed"
            _api_ticket(conn, "receipts", str(e), now)

        for l in conn.execute("SELECT listing_id, state FROM listing WHERE state IN ('active','quarantined')").fetchall():
            try:
                call_with_retry(lambda lid=l["listing_id"]: refresh_listing(conn, client, lid, now.date()), sleep=sleep)
            except RetryLimitExceeded as e:
                _api_ticket(conn, f"listing:{l['listing_id']}", str(e), now)
                continue
            has = conn.execute("SELECT has_digital_file FROM listing WHERE listing_id=?", (l["listing_id"],)).fetchone()[0]
            if l["state"] == "active" and not has:
                quarantine_listing(conn, l["listing_id"], "公開中の掲載に納品ファイルがない", client, now)

        out["fee_stop"] = check_fee_headroom(conn, now.date())

        # 日曜 18:00 以降に週報（§10.3）
        if reports_dir is not None and now.weekday() == 6 and now.hour >= 18:
            out["report"] = str(write_weekly(conn, now.date(), now, reports_dir))
    finally:
        release_lock(conn, "tick", holder)
    return out


def write_weekly(conn, period_end, now, reports_dir: Path) -> Path:
    claims = build_claims(conn, period_end, now)
    diffs = verify(conn, claims)
    reports_dir.mkdir(parents=True, exist_ok=True)
    path = reports_dir / f"{period_end.isoformat()}.md"
    path.write_text(render_weekly(claims, diffs), encoding="utf-8")
    return path


def _api_ticket(conn, what, err, now):
    open_ticket(conn, kind="api_failure", dedupe_key=f"api:{what}:{now.date().isoformat()}",
                ask="Etsy API の取り込みが続けて失敗しました。キーの有効期限を確認してください", minutes=5,
                target=f"Etsy API（{what}）", reason=err,
                options=[{"label": "キーを再発行して環境の秘密に入れ直す", "recommended": True},
                         {"label": "明日の再実行を待つ", "recommended": False}],
                deadline=(now + timedelta(days=1)).date().isoformat(),
                on_no_answer="取り込みは翌日に再試行。数字は未計測のまま報告する", now=now)
