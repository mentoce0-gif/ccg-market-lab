# CCG 90日 PoC

チームCCG（Claude・ChatGPT/Codex・Grok、所有者 Shun）で、AI がほぼ自走して収益を上げる事業を1つ立ち上げ、90日で「月1万円の再現性」を確かめる。このリポジトリは、3つの AI と Shun が同じ資料を読み、議論し、決定を残すための共有の場所。

## 今の状態（2026-09-27 夜）

- GitHub 本体: `mentoce0-gif/ccg-market-lab`（private）。初期は空だったため、`ccg-poc-repo.zip` と運用 md を入れた。
- 正本の仕様：[`docs/spec/v2_skeleton.md`](docs/spec/v2_skeleton.md)。zip 内にある。食い違いは v2 を優先する。
- 販路：Etsy（英語・デジタルダウンロード）。店名 QuietColumnsStudio。Payoneer 住所確認待ち。
- 試行 #0：Teacher Command Center v2（`pre_spec`）。
- 候補：CAND-01 / CAND-02 / CAND-03。試行順番は未決 U-001。
- Grok はリポジトリ直結済み、毎日 07:30 JST に Issue へ SESSION-END を書く。`GROK.md` の「Grok は直読できない」前提は事実上破棄。正式な仕様改定は Shun 未決。
- Day 1 = 2026-10-05、Day 90 = 2027-01-02。

## 初めて読む人（AI を含む）の順番

1. このファイル
2. 自分の役割の指示：Claude は `CLAUDE.md`、ChatGPT/Codex は `AGENTS.md`、Grok は `GROK.md`
3. 正本の仕様（zip 内 `docs/spec/v2_skeleton.md`）
4. `docs/history/2026-09-27_log.md`
5. `decisions/log.md`
6. `proposals/`

## Issues

- #1 ops session-log
- #2 signals
- #3 candidates
- #4 red-team
- #5 ceo decisions
