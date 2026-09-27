# CCG 90日 PoC

チームCCG（Claude・ChatGPT/Codex・Grok、所有者 Shun）で、AI がほぼ自走して収益を上げる事業を1つ立ち上げ、90日で「月1万円の再現性」を確かめる。このリポジトリは、3つの AI と Shun が同じ資料を読み、議論し、決定を残すための共有の場所。

## 今の状態（2026-09-27）

- 正本の仕様：[`docs/spec/v2_skeleton.md`](docs/spec/v2_skeleton.md)（骨子 v2.0.2）。v1（Codex）に Claude の計画と照合結果をマージしたもの。食い違いは v2 を優先する。
- 販路：Etsy（英語・デジタルダウンロード）。店の環境設定と店名（QuietColumnsStudio）まで完了。Payoneer の住所確認待ち。
- 試行 #0：Teacher Command Center v2（仕様前に作った試行。`pre_spec`）。
- 候補：CAND-01（予定表→カレンダー）、CAND-02（色を変えられるサッカー招待状）、CAND-03 案 ClaimLoop（ChatGPT 提出）。試行の順番は未決（[`decisions/log.md`](decisions/log.md)）。
- 凍結：Kindle セール告知（仕様の除外領域「量産アフィリエイト」）。
- Day 1 = 2026-10-05、Day 90 = 2027-01-02。

## 初めて読む人（AI を含む）の順番

1. このファイル
2. 自分の役割の指示：Claude は [`CLAUDE.md`](CLAUDE.md)、ChatGPT/Codex は [`AGENTS.md`](AGENTS.md)、Grok は [`GROK.md`](GROK.md)
3. 正本の仕様 [`docs/spec/v2_skeleton.md`](docs/spec/v2_skeleton.md)
4. これまでの経緯 [`docs/history/2026-09-27_log.md`](docs/history/2026-09-27_log.md)
5. 決定の記録 [`decisions/log.md`](decisions/log.md)
6. 候補と試行 [`proposals/`](proposals/)

## 新しいチャット・タスクの始め方（Shun 用）

1つの話題に1つのチャットを使い、終わったら閉じる。長いチャットを続けない。最初にこれを貼る：

```
ccg-poc リポジトリの CLAUDE.md を読んでから始めて。今日やること：［例：U-001 の決定を反映して、#0 の掲載一式を作る］
```

## 話し方の決まり（全員共通）

| 何をするか | どこで | 決まり |
|---|---|---|
| 議論する | GitHub Issues（1議題1 Issue） | コメントの1行目に署名 `[Claude]` `[ChatGPT]` `[Grok]` `[Shun]`。反証を先に書く。確かめていない数字や固有名詞には `[未検証]` |
| 仕様・候補・コードを変える | Pull Request | 本文に「変えたこと・理由・反証」。仕様の変更は版を上げる。テスト（`tests/`）を作る人と商品を作る人は別 |
| 決める | `decisions/log.md` に1行 | 決めるのは Shun。承認が要るものは A4 一枚の承認シートで出し、そのリンクを残す |
| 人の作業を記録する | `ledger/human_work.csv` | Shun が AI 同士の間で文章を運んだ時間も、分単位で必ず書く（仕様の原則16） |

- AI 同士が同意しても、それは証拠ではない。証拠は、機械のテスト・外部の原典・決済の確定・必要な人の判断。
- リポジトリには、個人情報（住所・本名・口座・本人確認書類）を置かない。
- 外部サイトの自動取得は、規約で許されたものだけ（Etsy のページは不可。公式 API の範囲で）。

## フォルダ

```
docs/spec/        仕様（v1 = Codex 原案、v2 = 正本）
docs/history/     これまでの議論と、元の調査資料
proposals/        候補（CAND-xx）と試行（TRIAL-xx）の企画票
reviews/          各 AI のレビュー（1ファイル1レビュー）
decisions/        決定の記録
products/         商品と、その制作・検算スクリプト
ledger/           台帳（人手・費用・注文）。ドライバができたら SQLite に移す
.github/          Issue と PR のひな形
```
