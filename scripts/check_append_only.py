"""tests/ と results/ は追記だけ（v2 §4.2）。基準のコミットとの差分に、変更・削除・改名があれば失敗する。

使い方：python scripts/check_append_only.py origin/main
テストを変える時は、既存のファイルを書き換えず、版を上げた新しいファイルを足す（例：test_design_v2.md）。
"""
import subprocess
import sys

base = sys.argv[1] if len(sys.argv) > 1 else "origin/main"
out = subprocess.run(["git", "diff", "--name-status", f"{base}...HEAD", "--", "tests", "results"],
                     capture_output=True, text=True, check=True).stdout
bad = [l for l in out.splitlines() if l and not l.startswith("A")]
if bad:
    print("tests/ と results/ は追記だけです。次の変更は許されません：")
    print("\n".join(bad))
    sys.exit(1)
print(f"ok: tests/ と results/ は追記だけ（{len(out.splitlines())} 件の追加）")
