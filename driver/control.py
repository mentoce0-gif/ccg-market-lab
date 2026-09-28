"""停止スイッチ・委任・状態遷移・例外票・単一実行のロック・テスト結果の書き込み制限。"""
import json
import sqlite3
from datetime import datetime, timedelta

from .db import audit, now_iso, tx


class Stopped(Exception):
    pass


class NotAuthorized(Exception):
    pass


class TransitionRefused(Exception):
    pass


# ------------------------------------------------------------------ 停止スイッチ
def engage_stop(conn, scope: str, reason: str, now=None) -> None:
    conn.execute(
        "INSERT INTO stop_switch (scope, engaged, reason, engaged_at) VALUES (?,1,?,?) "
        "ON CONFLICT(scope) DO UPDATE SET engaged=1, reason=excluded.reason, engaged_at=excluded.engaged_at, "
        "cleared_evidence=NULL, cleared_at=NULL",
        (scope, reason, now_iso(now)),
    )
    audit(conn, "driver", "engage_stop", "ok", f"{scope}: {reason}", now)


def clear_stop(conn, scope: str, evidence: str, now=None) -> None:
    """復旧には、停止の原因が解消したことを示す検査記録が要る（§4.2）。"""
    if not evidence or not evidence.strip():
        audit(conn, "driver", "clear_stop", "denied", f"{scope}: no evidence", now)
        raise TransitionRefused("停止の解除には検査記録（証拠）が必要")
    conn.execute(
        "UPDATE stop_switch SET engaged=0, cleared_evidence=?, cleared_at=? WHERE scope=?",
        (evidence, now_iso(now), scope),
    )
    audit(conn, "driver", "clear_stop", "ok", f"{scope}: {evidence}", now)


def stopped_scopes(conn, *scopes: str) -> list[str]:
    q = ",".join("?" * (len(scopes) + 1))
    rows = conn.execute(f"SELECT scope FROM stop_switch WHERE engaged=1 AND scope IN ({q})", ("global", *scopes))
    return [r["scope"] for r in rows]


def require_not_stopped(conn, *scopes: str) -> None:
    hit = stopped_scopes(conn, *scopes)
    if hit:
        raise Stopped(f"停止中: {', '.join(hit)}")


def quarantine_listing(conn, listing_id: str, reason: str, client=None, now=None) -> None:
    engage_stop(conn, f"listing:{listing_id}", reason, now)
    row = conn.execute("SELECT experiment_id, state FROM listing WHERE listing_id=?", (listing_id,)).fetchone()
    if row is None:
        return
    conn.execute("UPDATE listing SET state='quarantined' WHERE listing_id=?", (listing_id,))
    _set_state(conn, row["experiment_id"], "QUARANTINED", f"stop:{reason}", now)
    if client is not None and row["state"] == "active":
        try:
            client.deactivate_listing(listing_id)
        except Exception as e:  # noqa: BLE001  API で止められない時は、人に止めてもらう
            open_ticket(conn, kind="manual_stop", dedupe_key=f"manual_stop:{listing_id}",
                        ask="Etsy の管理画面で、この掲載を停止（Deactivate）してください", minutes=3,
                        target=f"Etsy 掲載 {listing_id}", reason=f"{reason}（API で停止できない: {e}）",
                        options=[{"label": "停止する", "recommended": True}, {"label": "停止しない（理由を記入）", "recommended": False}],
                        deadline=now_iso(now), on_no_answer="台帳では停止扱いのまま。新しい販売と支出は止める", now=now)


# ------------------------------------------------------------------ 委任（§9.3）
def grant(conn, auth_id, version, action, account, scope: dict, basis, granted_at, expires_at=None, cost_cap_jpy=None):
    conn.execute(
        "INSERT INTO authorization (auth_id, version, action, account, scope, cost_cap_jpy, granted_at, expires_at, basis) "
        "VALUES (?,?,?,?,?,?,?,?,?)",
        (auth_id, version, action, account, json.dumps(scope), cost_cap_jpy, granted_at, expires_at, basis),
    )


def require_allowed(conn, action: str, params: dict, now: datetime, actor: str = "driver") -> sqlite3.Row:
    """委任の範囲の外なら NotAuthorized。拒否も監査に残す。"""
    rows = conn.execute(
        "SELECT * FROM authorization WHERE action=? AND revoked=0 ORDER BY version DESC", (action,)
    ).fetchall()
    ts = now_iso(now)
    for r in rows:
        if r["granted_at"] > ts or (r["expires_at"] and r["expires_at"] <= ts):
            continue
        sc = json.loads(r["scope"])
        price = params.get("price_cents")
        if price is not None and not (sc.get("price_min_cents", 0) <= price <= sc.get("price_max_cents", 0)):
            continue
        if sc.get("formats") and params.get("format") not in sc["formats"]:
            continue
        if not set(sc.get("requires_gates", [])) <= set(params.get("gates_passed", [])):
            continue
        audit(conn, actor, action, "allowed", f"auth={r['auth_id']} v{r['version']}", now)
        return r
    audit(conn, actor, action, "denied", json.dumps(params, ensure_ascii=False), now)
    raise NotAuthorized(f"{action} は委任の範囲外（{params}）")


# ------------------------------------------------------------------ 状態遷移（§6）
CHAIN = ["OBSERVED", "VERIFIED", "BRIEFED", "BUILT", "QA_PASSED", "READY", "LIVE", "MEASURED"]
FINAL = {"KEEP", "REVISE", "STOP", "INCONCLUSIVE"}
SIDE = {"QUARANTINED", "BLOCKED"}


def _set_state(conn, experiment_id, to_state, evidence, now=None):
    row = conn.execute("SELECT state FROM experiment WHERE experiment_id=?", (experiment_id,)).fetchone()
    if row is None:
        return
    conn.execute(
        "INSERT INTO state_transition (experiment_id, from_state, to_state, evidence, at) VALUES (?,?,?,?,?)",
        (experiment_id, row["state"], to_state, evidence, now_iso(now)),
    )
    conn.execute("UPDATE experiment SET state=? WHERE experiment_id=?", (to_state, experiment_id))


def transition(conn, experiment_id: str, to_state: str, evidence: str, now=None) -> None:
    """AI が「完了」と書いただけでは進めない。状態ごとの証拠を求める（§10.4）。"""
    cur = conn.execute("SELECT state FROM experiment WHERE experiment_id=?", (experiment_id,)).fetchone()
    if cur is None:
        raise TransitionRefused(f"unknown experiment {experiment_id}")
    frm = cur["state"]
    if not evidence or not evidence.strip():
        raise TransitionRefused("証拠のない遷移は受け付けない")
    ok = (
        to_state in SIDE
        or (frm in CHAIN and to_state in CHAIN and CHAIN.index(to_state) == CHAIN.index(frm) + 1)
        or (frm == "MEASURED" and to_state in FINAL)
        or (frm in SIDE and to_state in CHAIN)  # 復旧：証拠付きで元の系列へ戻す
    )
    if not ok:
        raise TransitionRefused(f"{frm} → {to_state} は許されない")
    if to_state == "QA_PASSED":
        bad = conn.execute(
            "SELECT COUNT(*) FROM test_record t JOIN artifact a ON a.artifact_id=t.artifact_id AND a.version=t.artifact_version "
            "WHERE a.experiment_id=? AND t.passed=0 AND t.severity IN ('S0','S1','S2')",
            (experiment_id,),
        ).fetchone()[0]
        n = conn.execute(
            "SELECT COUNT(*) FROM test_record t JOIN artifact a ON a.artifact_id=t.artifact_id AND a.version=t.artifact_version "
            "WHERE a.experiment_id=?",
            (experiment_id,),
        ).fetchone()[0]
        if n == 0 or bad:
            raise TransitionRefused(f"QA_PASSED には固定テストの合格が要る（記録 {n} 件、S0〜S2 の不合格 {bad} 件）")
    if to_state == "LIVE":
        live = conn.execute(
            "SELECT COUNT(*) FROM listing WHERE experiment_id=? AND state='active'", (experiment_id,)
        ).fetchone()[0]
        if not live:
            raise TransitionRefused("LIVE には公開済みの掲載が要る")
    _set_state(conn, experiment_id, to_state, evidence, now)


# ------------------------------------------------------------------ テスト結果（§4.2、§14 #6）
def record_test_result(conn, role: str, **rec) -> None:
    """R5（制作者）はテスト結果を書けない。拒否を監査に残す。更新・削除はトリガーで禁止。"""
    if role == "R5":
        audit(conn, role, "record_test_result", "denied", rec.get("test_id", ""))
        raise PermissionError("制作のジョブはテスト結果を書き込めない")
    cols = ["test_id", "artifact_id", "artifact_version", "requirement_id", "expected", "actual", "passed",
            "evidence", "severity", "design_version", "run_at", "design_context_id"]
    conn.execute(
        f"INSERT INTO test_record ({','.join(cols)}, recorded_by_role) VALUES ({','.join('?' * (len(cols) + 1))})",
        (*[rec.get(c) for c in cols], role),
    )


# ------------------------------------------------------------------ 例外票（H票、§9.1）
def open_ticket(conn, *, kind, dedupe_key, ask, minutes, target, reason, options, deadline, on_no_answer, now=None) -> str:
    """同じ原因の票は1件にまとめる（二重通知しない）。"""
    row = conn.execute("SELECT ticket_id FROM ticket WHERE dedupe_key=?", (dedupe_key,)).fetchone()
    if row:
        return row["ticket_id"]
    n = conn.execute("SELECT COUNT(*) FROM ticket").fetchone()[0] + 1
    tid = f"H-{n:04d}"
    conn.execute(
        "INSERT INTO ticket (ticket_id, created_at, kind, dedupe_key, ask, minutes, target, reason, options, deadline, on_no_answer) "
        "VALUES (?,?,?,?,?,?,?,?,?,?,?)",
        (tid, now_iso(now), kind, dedupe_key, ask, minutes, target, reason, json.dumps(options, ensure_ascii=False),
         deadline, on_no_answer),
    )
    return tid


def ticket_outcome(conn, ticket_id: str) -> str:
    """期限が過ぎても同意とは扱わない（§10.3、§14 #13）。回答がなければ常に 'pending'。"""
    r = conn.execute("SELECT status, answer FROM ticket WHERE ticket_id=?", (ticket_id,)).fetchone()
    if r is None or r["status"] == "open" or not r["answer"]:
        return "pending"
    return r["answer"]


# ------------------------------------------------------------------ 単一実行のロック
def acquire_lock(conn, name: str, holder: str, now: datetime, ttl_minutes: int = 60) -> bool:
    with tx(conn):
        r = conn.execute("SELECT holder, expires_at FROM run_lock WHERE name=?", (name,)).fetchone()
        if r and r["holder"] != holder and r["expires_at"] > now_iso(now):
            return False
        conn.execute(
            "INSERT INTO run_lock (name, holder, expires_at) VALUES (?,?,?) "
            "ON CONFLICT(name) DO UPDATE SET holder=excluded.holder, expires_at=excluded.expires_at",
            (name, holder, now_iso(now + timedelta(minutes=ttl_minutes))),
        )
    return True


def release_lock(conn, name: str, holder: str) -> None:
    conn.execute("DELETE FROM run_lock WHERE name=? AND holder=?", (name, holder))
