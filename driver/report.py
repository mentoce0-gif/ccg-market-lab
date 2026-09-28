"""週報（§13.1）と H票の A4（§9.1、§13.2）。数字は台帳からだけ作り、出す前に台帳と突き合わせる（§14 #11）。"""
import html
import json
from datetime import date, datetime, time, timedelta

from . import config as C
from .ledger import evaluate, general_views, human_minutes, metrics

NUMERIC = ("revenue_jpy", "fees_jpy", "costs_jpy", "net_jpy", "charges", "buyers", "delivered_ok", "delivery_missing", "excluded")


def build_claims(conn, period_end: date, as_of: datetime) -> dict:
    start7 = period_end - timedelta(days=6)
    far = date(2000, 1, 1)
    last7 = metrics(conn, start7, period_end)
    cum = metrics(conn, far, period_end)
    trials = []
    for e in conn.execute("SELECT * FROM experiment ORDER BY experiment_id").fetchall():
        m = metrics(conn, far, period_end, e["experiment_id"])
        views = None
        for l in conn.execute("SELECT listing_id FROM listing WHERE experiment_id=?", (e["experiment_id"],)).fetchall():
            v = general_views(conn, l["listing_id"], period_end - timedelta(days=13), period_end)
            views = v if views is None else views + (v or 0)
        verdict, why = ("未実行", "LIVE になっていない") if e["state"] not in ("LIVE", "MEASURED") else evaluate(
            views, m["charges"], m["buyers"], m["marginal_jpy"], m["delivery_missing"] == 0)
        trials.append({"experiment_id": e["experiment_id"], "state": e["state"], "pre_spec": bool(e["pre_spec"]),
                       "views_14d": views, "charges": m["charges"], "revenue_jpy": m["revenue_jpy"],
                       "verdict": verdict, "why": why})
    tickets = [dict(t) for t in conn.execute(
        "SELECT ticket_id, ask, minutes, deadline FROM ticket WHERE status='open' ORDER BY ticket_id").fetchall()]
    end_of_period = datetime.combine(period_end + timedelta(days=1), time(0), C.JST)
    provisional = []
    if as_of < end_of_period:
        provisional.append("期間の終わりより前に作成（あとで確定版に置き換える）")
    if cum["fees_estimated"]:
        provisional.append("手数料は料率からの推定（実際の請求で置き換える）")
    return {
        "rule_version": C.RULE_VERSION,
        "period_end": period_end.isoformat(),
        "as_of": as_of.astimezone(C.JST).isoformat(timespec="minutes"),
        "last7": {**{k: last7[k] for k in NUMERIC}, "human": human_minutes(conn, start7, period_end)},
        "cumulative": {**{k: cum[k] for k in NUMERIC}, "top_customer_share": cum["top_customer_share"],
                       "human": human_minutes(conn, far, period_end)},
        "trials": trials,
        "open_tickets": tickets,
        "provisional": provisional,
    }


def verify(conn, claims: dict) -> list[str]:
    """報告の数字を台帳から計算し直して比べる。1つでも違えば、その報告は未確認。"""
    fresh = build_claims(conn, date.fromisoformat(claims["period_end"]),
                         datetime.fromisoformat(claims["as_of"]))
    diffs = []

    def walk(a, b, path):
        if isinstance(a, dict) and isinstance(b, dict):
            for k in set(a) | set(b):
                walk(a.get(k), b.get(k), f"{path}.{k}")
        elif isinstance(a, list) and isinstance(b, list):
            if len(a) != len(b):
                diffs.append(f"{path}: 件数 {len(a)} ≠ 台帳 {len(b)}")
            for i, (x, y) in enumerate(zip(a, b)):
                walk(x, y, f"{path}[{i}]")
        elif a != b:
            diffs.append(f"{path}: 報告 {a!r} ≠ 台帳 {b!r}")

    walk(claims, fresh, "")
    return diffs


def _yen(n):
    return f"¥{n:,}"


def render_weekly(claims: dict, diffs: list[str]) -> str:
    t = claims["open_tickets"]
    work = "なし" if not t else f"{t[0]['ask']}（{t[0]['minutes']}分、期限 {t[0]['deadline']}、{t[0]['ticket_id']}）"
    live = [x for x in claims["trials"] if x["verdict"] != "未実行"]
    if diffs:
        result = "判定保留。理由は、報告の数字が台帳と一致しない（未確認）"
    elif not live:
        result = "判定保留。理由は、LIVE の試行がまだない（到達・購入は未計測）"
    else:
        result = "／".join(f"{x['experiment_id']}：{x['verdict']}（{x['why']}）" for x in live)
        result = f"{result}。理由は、一般閲覧 {sum((x['views_14d'] or 0) for x in live)}・課金 {sum(x['charges'] for x in live)} 件"
    L, K = claims["last7"], claims["cumulative"]
    status = "未確認（台帳と不一致）" if diffs else ("暫定" if claims["provisional"] else "確定")
    lines = [
        f"> 今週のあなたの作業：{work}",
        f"> 結果：{result}。",
        "",
        f"# 週報 {claims['period_end']}（{status}）",
        "",
        f"作成 {claims['as_of']}／規則の版 {claims['rule_version']}",
    ]
    if claims["provisional"]:
        lines += ["", "暫定の理由：" + "；".join(claims["provisional"])]
    if diffs:
        lines += ["", "## 台帳との不一致（この報告の数字は使わない）", *[f"- {d}" for d in diffs]]

    def hm(h):
        return f"通常 {h['normal']}分／異常 {h['abnormal']}分（うち AI 間の中継 {h['relay']}分）／初期の例外 {h['exception']}分／分数の未記入 {h['unrecorded']}件"

    lines += [
        "", "## 1. 売上・費用・利益・人手",
        "", "| | 直近7日 | 累計 |", "|---|---:|---:|",
        f"| 適格な売上 | {_yen(L['revenue_jpy'])} | {_yen(K['revenue_jpy'])} |",
        f"| 手数料 | {_yen(L['fees_jpy'])} | {_yen(K['fees_jpy'])} |",
        f"| 事業費 | {_yen(L['costs_jpy'])} | {_yen(K['costs_jpy'])} |",
        f"| 事業純収益 | {_yen(L['net_jpy'])} | {_yen(K['net_jpy'])} |",
        f"| 課金（購入者） | {L['charges']}（{L['buyers']}人） | {K['charges']}（{K['buyers']}人） |",
        f"| 集計から除いた取引 | {L['excluded']} | {K['excluded']} |",
        f"| 納品ファイルの欠落 | {L['delivery_missing']} | {K['delivery_missing']} |",
        "", f"人手（直近7日）：{hm(L['human'])}", f"人手（累計）：{hm(K['human'])}",
        "", "## 2. 試行ごとの結果", "", "| 試行 | 状態 | 印 | 一般閲覧(14日) | 課金 | 売上 | 判定 |", "|---|---|---|---:|---:|---:|---|",
    ]
    for x in claims["trials"]:
        v = "未計測" if x["views_14d"] is None else x["views_14d"]
        lines.append(f"| {x['experiment_id']} | {x['state']} | {'pre_spec' if x['pre_spec'] else ''} | {v} | {x['charges']} | "
                     f"{_yen(x['revenue_jpy'])} | {x['verdict']}：{x['why']} |")
    lines += [
        "", "## 3. 反証と欠測", "", "（週次の運営が記入。空なら未記入と書く）",
        "", "## 4. 次週の一変更", "", "（週次の運営が記入）",
        "", "## 5. 必要な人の操作", "",
        *([f"- {x['ticket_id']}：{x['ask']}（{x['minutes']}分、期限 {x['deadline']}）" for x in t] or ["- なし"]),
        "", f"<!-- claims: {json.dumps(claims, ensure_ascii=False, sort_keys=True)} -->", "",
    ]
    return "\n".join(lines)


def render_ticket_a4(ticket, week_minutes: int) -> str:
    """H票を A4 一枚の HTML にする（印刷・PDF 化して Shun に渡す）。md では承認を求めない（原則15）。"""
    e = html.escape
    opts = json.loads(ticket["options"])
    rows = [
        ("依頼ID", ticket["ticket_id"]),
        ("これだけやってください", ticket["ask"]),
        ("所要時間", f"{ticket['minutes']}分"),
        ("対象", ticket["target"]),
        ("必要な理由", ticket["reason"]),
        ("選択肢", "<br>".join(("◎ 推奨：" if o.get("recommended") else "○ ") + e(o["label"]) for o in opts)),
        ("期限", ticket["deadline"]),
        ("未回答の時", ticket["on_no_answer"]),
        ("今週の人手の累計", f"{week_minutes}分"),
    ]
    body = "\n".join(f"<tr><th>{e(k)}</th><td>{v if k == '選択肢' else e(str(v))}</td></tr>" for k, v in rows)
    return f"""<!doctype html><html lang="ja"><head><meta charset="utf-8"><title>{e(ticket['ticket_id'])}</title>
<style>@page{{size:A4;margin:18mm}}body{{font-family:"Noto Sans JP",sans-serif;font-size:11pt;color:#111;background:#fff}}
h1{{font-size:16pt;margin:0 0 8mm}}table{{border-collapse:collapse;width:100%}}th,td{{border:1px solid #999;padding:3mm;vertical-align:top;text-align:left}}
th{{width:42mm;background:#f2f2f2}}.sign{{margin-top:10mm}}</style></head><body>
<h1>承認・操作の依頼（{e(ticket['kind'])}）</h1><table>{body}</table>
<p class="sign">回答：□ 推奨案　□ 代替案　□ その他（　　　　　　　　　）　日付：　　　　　署名：Shun</p></body></html>"""
