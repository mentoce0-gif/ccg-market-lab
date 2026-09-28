"""Headless LibreOffice recalculation helper (R6, ctx-r6-trial00-20260927).

Converts an xlsx into a new xlsx in a temp directory. A private LibreOffice
profile is used with "always recalculate on load" for OOXML, so every formula
is evaluated by LibreOffice regardless of cached values. Never writes to
products/.
"""
from __future__ import annotations

import os
import shutil
import subprocess
import tempfile
import uuid
from pathlib import Path

REGISTRY = """<?xml version="1.0" encoding="UTF-8"?>
<oor:items xmlns:oor="http://openoffice.org/2001/registry" xmlns:xs="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
<item oor:path="/org.openoffice.Office.Calc/Formula/Load"><prop oor:name="OOXMLRecalcMode" oor:op="fuse"><value>0</value></prop></item>
<item oor:path="/org.openoffice.Office.Calc/Formula/Load"><prop oor:name="ODFRecalcMode" oor:op="fuse"><value>0</value></prop></item>
</oor:items>
"""

ERROR_TOKENS = ("#VALUE!", "#REF!", "#DIV/0!", "#NAME?", "#N/A", "#NUM!", "#NULL!", "#GETTING_DATA")


def is_error_value(v) -> bool:
    if not isinstance(v, str):
        return False
    s = v.strip()
    return s in ERROR_TOKENS or s.startswith("Err:") or s.startswith("#ERR") or s == "#N/A"


def soffice_bin() -> str | None:
    return shutil.which("soffice") or shutil.which("libreoffice")


def recalc(src: Path, outdir: Path, timeout: int = 180) -> Path:
    """Recalculate `src` with LibreOffice; return path of the recalculated xlsx in `outdir`."""
    src = Path(src)
    outdir = Path(outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    binary = soffice_bin()
    if binary is None:
        raise RuntimeError("LibreOffice (soffice) not found")
    profile = Path(tempfile.mkdtemp(prefix="lo-profile-"))
    user = profile / "user"
    user.mkdir(parents=True)
    (user / "registrymodifications.xcu").write_text(REGISTRY, encoding="utf-8")
    # Work on a uniquely named copy so parallel/multiple runs never collide.
    work_in = outdir / f"in_{uuid.uuid4().hex}"
    work_in.mkdir()
    staged = work_in / src.name
    shutil.copy2(src, staged)
    work_out = outdir / f"out_{uuid.uuid4().hex}"
    work_out.mkdir()
    cmd = [
        binary,
        f"-env:UserInstallation={profile.as_uri()}",
        "--headless",
        "--norestore",
        "--nolockcheck",
        "--convert-to",
        "xlsx:Calc MS Excel 2007 XML",
        "--outdir",
        str(work_out),
        str(staged),
    ]
    env = dict(os.environ)
    env.setdefault("HOME", str(profile))
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, env=env)
    finally:
        shutil.rmtree(profile, ignore_errors=True)
    out = work_out / src.name
    if proc.returncode != 0 or not out.exists():
        raise RuntimeError(
            f"LibreOffice conversion failed rc={proc.returncode}\nstdout={proc.stdout}\nstderr={proc.stderr}"
        )
    return out
