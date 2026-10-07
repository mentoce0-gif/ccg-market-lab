# CCG 90日 PoC

チームCCG（Claude・ChatGPT/Codex・Grok、所有者 Shun）で、AI がほぼ自走して収益を上げる事業を1つ立ち上げ、90日で「月1万円の再現性」を確かめる。このリポジトリは、3つの AI と Shun が同じ資料を読み、議論し、決定を残すための共有の場所。

## 今の状態（2026-10-07 夜）

- GitHub 本体: [`mentoce0-gif/ccg-market-lab`](https://github.com/mentoce0-gif/ccg-market-lab)（**public**、2026-09-27 夜に変更。未ログインでも repo と Issues が読める）。
- 正本の仕様：[`docs/spec/v2_skeleton.md`](docs/spec/v2_skeleton.md)。食い違いは v2 を優先する。
- 販路：Etsy（英語・デジタルダウンロード）。店名 QuietColumnsStudio。**Payoneer は未対応で、Etsy は開店していない**（2026-10-07 Shun 報告）。09-28 の申請は、別のアカウントを作ったことが原因とみられ通らなかった（原因は [未検証]）。最初のアカウントで登録をやり直す予定のまま。日本の売り手は Payoneer 経由で登録するため、開店と #0 の公開はこれ待ち。
- 試行の順番（D-008）：試行1＝#0、試行2の本命＝CAND-01 の作り替え版、CAND-02 は48時間ゲートを通れば3本目。CAND-03 は保留。
- 出品（D-009）：Shun が1件ずつ確認して承認したものだけを公開する。委任はしない。
- 試行 #0：Teacher Command Center v2（`pre_spec`）。run2 で自動テストの S0〜S2 は0件。Shun の Google スプレッドシートでの確認も問題なし → **T3 合格（暫定）**（[run2](results/trial-00/2026-09-28_run2.md)、[手動の確認](results/trial-00/2026-09-29_manual1.md)）。次は T4（掲載一式を A4 で Shun が承認）。
- Grok はリポジトリに直結し、毎日 07:30 JST に Issue #1 へ SESSION-END を書く（D-007）。
- ChatGPT は毎日 07:45 JST の結果を Issue のコメントに書き戻す（D-010）。書き込めるかは初回で確かめる。
- Day 1 = 2026-10-05、Day 90 = 2027-01-02。
- 議題：[AGENDA-001 販路は Etsy だけでよいか／マーケットインと開発効率](discussion/AGENDA-001_販路と速度.md)（Grok は回答済み：[Issue #7](https://github.com/mentoce0-gif/ccg-market-lab/issues/7)。ChatGPT は未回答。2本目の販路は U-007）。
- 是正の対応：[2026-09-28 の是正対応](discussion/2026-09-28_是正対応.md)。

## 初めて読む人（AI を含む）の順番

1. このファイル
2. 自分の役割の指示：Claude は `CLAUDE.md`、ChatGPT/Codex は `AGENTS.md`、Grok は `GROK.md`
3. 正本の仕様 `docs/spec/v2_skeleton.md`
4. `docs/history/2026-09-27_log.md`
5. `decisions/log.md`
6. `proposals/`

## Issues

- #1 ops session-log
- #2 signals
- #3 candidates
- #4 red-team
- #5 ceo decisions
