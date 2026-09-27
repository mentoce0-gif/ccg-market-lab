"""Independent recomputation of Teacher Command Center results (R6, ctx-r6-trial00-20260927).

Written from the calculation rules stated in the product's own "Start Here" /
Setup text and from test_design_v1.md section 1. It does not reuse the maker's
formulas or verification script. Cell locations were taken from header labels.

Rules (Start Here B25-B28, Gradebook A2, Setup A29):
- Category % = points earned / points possible on graded work.
  numeric score -> earned += score, possible += points
  "M"           -> earned += 0,     possible += points
  "EX"          -> skipped
  blank         -> if past due and Setup "count past-due blanks as 0" == Yes:
                     possible += points; otherwise skipped
  Extra credit: points possible = 0 (adds to earned only).
- Overall = sum(w_c * pct_c) / sum(w_c) over categories whose pct is numeric.
- Letter grade: highest "Min %" row <= overall.
- Submission rate = due items turned in / due items not EX.
- Missing = count of "M" + count of past-due blanks.
- Performance index = weighted blend of overall and submission rate
  (compared only when both are numeric; the one-sided case is not documented).
- Rank: 1 = highest performance index, ties share a rank (competition ranking).
- Status: "At risk" below either line; "Watch" within 0.10 of either line;
  otherwise "On track".
- Percentile: formula is not documented -> only properties are checked
  (in [0, 1]; ordering consistent with the performance index).
"""
from __future__ import annotations

import datetime as dt
from dataclasses import dataclass, field

EPS = 1e-9
TOL = 1e-6


# ---------------------------------------------------------------- utilities
def to_date(v):
    if v is None or v == "":
        return None
    if isinstance(v, dt.datetime):
        return v.date()
    if isinstance(v, dt.date):
        return v
    if isinstance(v, (int, float)) and not isinstance(v, bool):
        return (dt.datetime(1899, 12, 30) + dt.timedelta(days=float(v))).date()
    return None


def is_num(v) -> bool:
    return isinstance(v, (int, float)) and not isinstance(v, bool)


def norm(v):
    """Normalise a recalculated cell value: '' -> None."""
    if isinstance(v, str) and v == "":
        return None
    return v


def kind(v) -> str:
    if is_num(v):
        return "score"
    if v is None or (isinstance(v, str) and v.strip() == ""):
        return "blank"
    s = str(v).strip().upper()
    if s == "M":
        return "M"
    if s == "EX":
        return "EX"
    return "other"


# ---------------------------------------------------------------- model
@dataclass
class Assignment:
    number: int
    name: str
    category: str | None
    points: float
    due: dt.date | None


@dataclass
class Model:
    as_of: dt.date | None
    count_blanks: bool
    weights: dict  # category -> weight
    scale: list  # [(min, letter)] ascending
    perf_w_overall: float
    perf_w_sub: float
    risk_overall: float
    risk_sub: float
    students: list  # names in roster order (index i -> gradebook row 10+i)
    assignments: dict  # number -> Assignment
    grid: dict = field(default_factory=dict)  # (student_idx, assignment_no) -> raw value


def _find_label(ws, text, max_row=60, max_col=30):
    for row in ws.iter_rows(min_row=1, max_row=max_row, max_col=max_col):
        for c in row:
            if isinstance(c.value, str) and c.value.strip().lower().startswith(text.lower()):
                return c.row, c.column
    raise LookupError(f"label {text!r} not found on {ws.title}")


def read_model(wb) -> Model:
    """Read inputs from a *recalculated* (data_only) workbook."""
    su = wb["Setup"]
    r, c = _find_label(su, "As of")
    as_of = to_date(su.cell(r, c + 1).value)
    r, c = _find_label(su, "Count past-due blanks")
    count_blanks = str(su.cell(r, c + 1).value or "").strip().lower() == "yes"
    r, c = _find_label(su, "Category")
    weights = {}
    rr = r + 1
    while True:
        name = su.cell(rr, c).value
        if not isinstance(name, str) or name.strip() == "" or name.strip().lower() == "total":
            break
        w = su.cell(rr, c + 1).value
        weights[name.strip()] = float(w) if is_num(w) else 0.0
        rr += 1
    r, c = _find_label(su, "Min %")
    scale = []
    rr = r + 1
    while is_num(su.cell(rr, c).value):
        scale.append((float(su.cell(rr, c).value), str(su.cell(rr, c + 1).value)))
        rr += 1
    scale.sort()
    r, c = _find_label(su, "Weight of overall grade")
    pwo = float(su.cell(r, c + 1).value)
    r, c = _find_label(su, "Weight of submission rate")
    pws = float(su.cell(r, c + 1).value)
    r, c = _find_label(su, "Overall grade below")
    ro = float(su.cell(r, c + 1).value)
    r, c = _find_label(su, "Submission rate below")
    rs = float(su.cell(r, c + 1).value)

    ro_ws = wb["Roster"]
    students = []
    for i in range(40):
        v = ro_ws.cell(6 + i, 2).value
        students.append(v.strip() if isinstance(v, str) and v.strip() else None)

    asg_ws = wb["Assignments"]
    pac = wb["Pacing"]
    unit_end = {}
    for rr in range(6, 26):
        u = pac.cell(rr, 2).value
        if isinstance(u, str) and u.strip():
            unit_end[u.strip()] = to_date(pac.cell(rr, 6).value)  # "Ends" column
    assignments = {}
    for k in range(1, 61):
        rr = 5 + k
        name = asg_ws.cell(rr, 2).value
        if not (isinstance(name, str) and name.strip()):
            continue
        unit = asg_ws.cell(rr, 3).value
        typed = to_date(asg_ws.cell(rr, 6).value)
        due = typed if typed else unit_end.get(unit.strip() if isinstance(unit, str) else unit)
        pts = asg_ws.cell(rr, 5).value
        cat = asg_ws.cell(rr, 4).value
        assignments[k] = Assignment(k, name.strip(), cat.strip() if isinstance(cat, str) else None,
                                    float(pts) if is_num(pts) else 0.0, due)

    gb = wb["Gradebook"]
    grid = {}
    col_of = {}
    for col in range(13, 13 + 60):  # M .. BT, row 4 holds assignment numbers
        n = gb.cell(4, col).value
        if is_num(n):
            col_of[int(n)] = col
    for i in range(40):
        for k, col in col_of.items():
            grid[(i, k)] = norm(gb.cell(10 + i, col).value)
    return Model(as_of, count_blanks, weights, scale, pwo, pws, ro, rs, students, assignments, grid)


# ---------------------------------------------------------------- calculations
def is_due(model: Model, a: Assignment) -> bool:
    return a.due is not None and model.as_of is not None and a.due <= model.as_of


def letter(model: Model, overall):
    if overall is None:
        return None
    g = None
    for mn, lt in model.scale:
        if overall + EPS >= mn:
            g = lt
    return g


def near_grade_boundary(model: Model, overall) -> bool:
    return overall is not None and any(abs(overall - mn) < 1e-7 for mn, _ in model.scale)


def student_metrics(model: Model, i: int) -> dict:
    earned = {c: 0.0 for c in model.weights}
    possible = {c: 0.0 for c in model.weights}
    counted = {c: 0 for c in model.weights}
    turned_in = due_not_ex = missing = 0
    statuses = {}
    for k, a in sorted(model.assignments.items()):
        v = model.grid.get((i, k))
        kd = kind(v)
        due = is_due(model, a)
        c = a.category
        if kd == "score":
            statuses[k] = "Submitted"
        elif kd == "EX":
            statuses[k] = "Excused"
        elif kd == "M" or (kd == "blank" and due):
            statuses[k] = "Missing"
        else:
            statuses[k] = "Not due yet" if kd == "blank" else "other"
        if c in earned:
            if kd == "score":
                earned[c] += float(v)
                possible[c] += a.points
                counted[c] += 1
            elif kd == "M":
                possible[c] += a.points
                counted[c] += 1
            elif kd == "blank" and due and model.count_blanks:
                possible[c] += a.points
                counted[c] += 1
        if kd == "M" or (kd == "blank" and due):
            missing += 1
        if due and kd != "EX":
            due_not_ex += 1
            if kd == "score":
                turned_in += 1
    pct = {}
    for c in model.weights:
        pct[c] = earned[c] / possible[c] if possible[c] > 0 else None
    wsum = sum(model.weights[c] for c in model.weights if pct[c] is not None)
    overall = (sum(model.weights[c] * pct[c] for c in model.weights if pct[c] is not None) / wsum
               if wsum > 0 else None)
    sub = turned_in / due_not_ex if due_not_ex > 0 else None
    return {"pct": pct, "overall": overall, "grade": letter(model, overall), "sub": sub,
            "missing": missing, "statuses": statuses}


def class_metrics(model: Model) -> dict:
    out = {}
    for i, name in enumerate(model.students):
        if name is None:
            continue
        m = student_metrics(model, i)
        o, s = m["overall"], m["sub"]
        if o is not None and s is not None:
            m["perf"] = (model.perf_w_overall * o + model.perf_w_sub * s) / (model.perf_w_overall + model.perf_w_sub)
        else:
            m["perf"] = None
        if (o is not None and o < model.risk_overall) or (s is not None and s < model.risk_sub):
            m["status"] = "At risk"
        elif (o is not None and o < model.risk_overall + 0.1) or (s is not None and s < model.risk_sub + 0.1):
            m["status"] = "Watch"
        else:
            m["status"] = "On track"
        # boundary flag: skip status comparison if within float noise of a line
        lines = [model.risk_overall, model.risk_overall + 0.1, model.risk_sub, model.risk_sub + 0.1]
        m["status_boundary"] = any(x is not None and abs(x - L) < 1e-7 for x in (o, s) for L in lines)
        out[i] = m
    perfs = [(i, m["perf"]) for i, m in out.items() if m["perf"] is not None]
    for i, p in perfs:
        out[i]["rank"] = 1 + sum(1 for _, q in perfs if q > p + EPS)
    for i, m in out.items():
        m.setdefault("rank", None)
    return out


# ---------------------------------------------------------------- comparison
def _eq(a, b) -> bool:
    a, b = norm(a), norm(b)
    if a is None or b is None:
        return a is None and b is None
    if is_num(a) and is_num(b):
        return abs(float(a) - float(b)) <= TOL
    return str(a).strip() == str(b).strip()


def compare_workbook(wb) -> list[str]:
    """Return a list of human-readable mismatches between the workbook and R6's recomputation."""
    model = read_model(wb)
    res = class_metrics(model)
    mism: list[str] = []
    gb = wb["Gradebook"]
    hdr = {str(gb.cell(9, c).value).strip(): c for c in range(1, 13) if gb.cell(9, c).value is not None}
    need = ["Student", "Overall", "Grade", "Turned in", "Missing"]
    for h in need:
        if h not in hdr:
            return [f"HARNESS: Gradebook header {h!r} not found in row 9: {hdr}"]
    cat_col = {c: hdr.get(c) for c in model.weights}
    st = wb["Standings"]
    shdr = {str(st.cell(7, c).value).strip(): c for c in range(1, 12) if st.cell(7, c).value is not None}
    for h in ["Student", "Perf. index", "Rank", "Percentile", "Status"]:
        if h not in shdr:
            return [f"HARNESS: Standings header {h!r} not found in row 7: {shdr}"]

    for i, name in enumerate(model.students):
        r = 10 + i
        if name is None:
            continue
        m = res[i]
        if not _eq(gb.cell(r, hdr["Student"]).value, name):
            mism.append(f"Gradebook row {r}: name {gb.cell(r, hdr['Student']).value!r} != roster {name!r}")
        for c, col in cat_col.items():
            if col is None:
                mism.append(f"Gradebook: category column {c!r} missing")
                continue
            if not _eq(gb.cell(r, col).value, m["pct"][c]):
                mism.append(f"{name} {c}%: book={norm(gb.cell(r, col).value)!r} r6={m['pct'][c]!r}")
        if not _eq(gb.cell(r, hdr["Overall"]).value, m["overall"]):
            mism.append(f"{name} overall: book={norm(gb.cell(r, hdr['Overall']).value)!r} r6={m['overall']!r}")
        if not near_grade_boundary(model, m["overall"]) and not _eq(gb.cell(r, hdr["Grade"]).value, m["grade"]):
            mism.append(f"{name} grade: book={norm(gb.cell(r, hdr['Grade']).value)!r} r6={m['grade']!r}")
        if not _eq(gb.cell(r, hdr["Turned in"]).value, m["sub"]):
            mism.append(f"{name} submission rate: book={norm(gb.cell(r, hdr['Turned in']).value)!r} r6={m['sub']!r}")
        if not _eq(gb.cell(r, hdr["Missing"]).value, m["missing"]):
            mism.append(f"{name} missing: book={norm(gb.cell(r, hdr['Missing']).value)!r} r6={m['missing']!r}")

        sr = 8 + i
        if not _eq(st.cell(sr, shdr["Student"]).value, name):
            mism.append(f"Standings row {sr}: name {st.cell(sr, shdr['Student']).value!r} != {name!r}")
        bp = norm(st.cell(sr, shdr["Perf. index"]).value)
        if m["perf"] is not None and not _eq(bp, m["perf"]):
            mism.append(f"{name} perf index: book={bp!r} r6={m['perf']!r}")
        if m["perf"] is not None and not _eq(st.cell(sr, shdr["Rank"]).value, m["rank"]):
            mism.append(f"{name} rank: book={norm(st.cell(sr, shdr['Rank']).value)!r} r6={m['rank']!r}")
        if not m["status_boundary"] and not _eq(st.cell(sr, shdr["Status"]).value, m["status"]):
            mism.append(f"{name} status: book={norm(st.cell(sr, shdr['Status']).value)!r} r6={m['status']!r}")

    # percentile properties
    pts = []
    for i, m in res.items():
        p = norm(st.cell(8 + i, shdr["Percentile"]).value)
        f = norm(st.cell(8 + i, shdr["Perf. index"]).value)
        if f is not None:
            if not is_num(p) or not (-TOL <= float(p) <= 1 + TOL):
                mism.append(f"{model.students[i]} percentile out of [0,1] or not numeric: {p!r}")
            elif is_num(f):
                pts.append((float(f), float(p), model.students[i]))
    for f1, p1, n1 in pts:
        for f2, p2, n2 in pts:
            if f1 > f2 + EPS and p1 < p2 - TOL:
                mism.append(f"percentile order: {n1} index {f1:.4f} > {n2} {f2:.4f} but pct {p1} < {p2}")
            if abs(f1 - f2) <= EPS and abs(p1 - p2) > TOL:
                mism.append(f"percentile tie: {n1} and {n2} same index, pct {p1} != {p2}")

    # Dashboard headline numbers (Start Here B16)
    db = wb["Dashboard"]
    overalls = [m["overall"] for m in res.values() if m["overall"] is not None]
    subs = [m["sub"] for m in res.values() if m["sub"] is not None]
    try:
        r, c = _find_label(db, "Class average")
        exp = sum(overalls) / len(overalls) if overalls else None
        if not _eq(db.cell(r + 1, c).value, exp):
            mism.append(f"Dashboard class average: book={norm(db.cell(r + 1, c).value)!r} r6={exp!r}")
        r, c = _find_label(db, "Work turned in")
        exp = sum(subs) / len(subs) if subs else None
        if not _eq(db.cell(r + 1, c).value, exp):
            mism.append(f"Dashboard submission rate: book={norm(db.cell(r + 1, c).value)!r} r6={exp!r}")
        r, c = _find_label(db, "Students at risk")
        exp = sum(1 for m in res.values() if m["status"] == "At risk")
        if not any(m["status_boundary"] for m in res.values()) and not _eq(db.cell(r + 1, c).value, exp):
            mism.append(f"Dashboard at-risk count: book={norm(db.cell(r + 1, c).value)!r} r6={exp!r}")
    except LookupError as e:
        mism.append(f"HARNESS: {e}")

    # Student Report for the selected student
    rp = wb["Student Report"]
    sel = rp["B4"].value
    if isinstance(sel, str) and sel.strip() in model.students:
        i = model.students.index(sel.strip())
        m = res[i]
        for label, key in (("Overall grade", "overall"), ("Work turned in", "sub"), ("Missing items", "missing")):
            r, c = _find_label(rp, label)
            if not _eq(rp.cell(r, c + 1).value, m[key]):
                mism.append(f"Student Report {label}: book={norm(rp.cell(r, c + 1).value)!r} r6={m[key]!r}")
        accepted = {"Submitted": {"Submitted", "Turned in"}}  # wording checked separately (T00-USE-05)
        for k, a in sorted(model.assignments.items()):
            row = 14 + k
            got = norm(rp.cell(row, 8).value)
            exp = m["statuses"][k]
            if got not in accepted.get(exp, {exp}):
                mism.append(f"Student Report row {row} ({a.name}) status: book={got!r} r6={exp!r}")
    return mism


def pacing_end_checks(wb) -> list[str]:
    """Unit 'Ends' date must fall inside the last week of the unit (Start Here B11-B12)."""
    out = []
    su = wb["Setup"]
    r, c = _find_label(su, "Term starts")
    start = to_date(su.cell(r, c + 1).value)
    pac = wb["Pacing"]
    for rr in range(6, 26):
        u, sw, wk = pac.cell(rr, 2).value, pac.cell(rr, 3).value, pac.cell(rr, 4).value
        if not (isinstance(u, str) and u.strip() and is_num(sw) and is_num(wk) and wk >= 1 and start):
            continue
        lo = start + dt.timedelta(days=7 * (int(sw) + int(wk) - 2))
        hi = lo + dt.timedelta(days=6)
        end = to_date(pac.cell(rr, 6).value)
        if end is None or not (lo <= end <= hi):
            out.append(f"Pacing row {rr} ({u}): Ends={end} not in last unit week [{lo}, {hi}]")
    return out
