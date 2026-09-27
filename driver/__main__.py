"""使い方：
  python -m driver init
  python -m driver tick --fixture driver/fixtures/dry_run.json      # DRY_RUN（既定）
  python -m driver report --period-end 2026-10-11
  python -m driver ticket-a4 H-0001

CCG_MODE=LIVE の時だけ Etsy API を読む（キーは環境変数）。§14 の受入テストに合格するまでは DRY_RUN のまま。
"""
import argparse
import json
import os
from datetime import date, datetime, timedelta
from pathlib import Path

from . import config as C
from .db import connect, init
from .etsy import FakeEtsy, HttpEtsy
from .ledger import load_human_work
from .report import render_ticket_a4
from .tick import tick, write_weekly

ROOT = Path(__file__).resolve().parent.parent


def main(argv=None):
    ap = argparse.ArgumentParser(prog="driver")
    ap.add_argument("--db", default=os.environ.get("CCG_DB"))
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("init")
    t = sub.add_parser("tick")
    t.add_argument("--fixture")
    t.add_argument("--jpy-per-usd", type=float, default=float(os.environ.get("CCG_JPY_PER_USD", "149")))
    r = sub.add_parser("report")
    r.add_argument("--period-end", required=True)
    a = sub.add_parser("ticket-a4")
    a.add_argument("ticket_id")
    args = ap.parse_args(argv)

    live = os.environ.get("CCG_MODE") == "LIVE"
    db_path = args.db or str(ROOT / "ledger" / ("ccg.sqlite" if live else "dry_run.sqlite"))
    conn = connect(db_path)
    init(conn)
    load_human_work(conn, ROOT / "ledger" / "human_work.csv")
    now = datetime.now(C.JST)

    if args.cmd == "init":
        print(f"ok: {db_path}")
    elif args.cmd == "tick":
        if live:
            client, salt = HttpEtsy(), os.environ["CCG_PSEUDO_SALT"]
        else:
            fx = json.loads(Path(args.fixture).read_text()) if args.fixture else {"receipts": [], "listings": {}}
            client, salt = FakeEtsy(fx["receipts"], fx["listings"]), "dry-run-only-salt"
        out = tick(conn, client, now, jpy_per_usd=args.jpy_per_usd, salt=salt, dry_run=not live,
                   reports_dir=ROOT / "reports" / ("weekly" if live else "dry_run"))
        print(json.dumps(out, ensure_ascii=False, indent=2))
    elif args.cmd == "report":
        p = write_weekly(conn, date.fromisoformat(args.period_end), now,
                         ROOT / "reports" / ("weekly" if live else "dry_run"))
        print(p)
    elif args.cmd == "ticket-a4":
        tk = conn.execute("SELECT * FROM ticket WHERE ticket_id=?", (args.ticket_id,)).fetchone()
        mins = conn.execute("SELECT COALESCE(SUM(minutes),0) FROM human_work WHERE kind<>'exception' AND at>=?",
                            ((now.date() - timedelta(days=now.weekday())).isoformat(),)).fetchone()[0]
        out = ROOT / "reports" / "tickets" / f"{args.ticket_id}.html"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(render_ticket_a4(tk, mins), encoding="utf-8")
        print(out)


if __name__ == "__main__":
    main()
