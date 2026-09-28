# 最小構成のドライバ（v2 §10.2）

標準ライブラリだけ（Python 3.11、SQLite）。LLM は使わない。

## §10.2 の対応

| §10.2 の項目 | 実装 |
|---|---|
| 台帳（試行・商品の版・注文・費用・人手・権限） | `schema.sql`（§11 のデータ契約＋予約・停止・例外票・監査） |
| 損益の計算 | `ledger.metrics`（§12.1。返金は毎回台帳から再計算） |
| 受注番号による重複の排除 | `ledger.ingest_receipts`（receipt_id が主キー） |
| 予算の予約と上限 | `budget.reserve / settle / release`（区分・30日窓・暦月・90日・試行ごとの厳しい方。`BEGIN IMMEDIATE` で原子的に） |
| 停止スイッチ | `control.engage_stop / clear_stop / quarantine_listing`（解除には証拠が要る） |
| 週報の生成 | `report.build_claims → verify → render_weekly`（台帳と一致しなければ「未確認」） |
| H票のひな形 | `report.render_ticket_a4`（A4 一枚の HTML。md で承認を求めない） |
| §14 の受入テスト | `tests/test_acceptance_s14.py`（15項目＋補助2件。#15 は D-009 の承認済みの版だけを公開） |

## 使い方

```
python -m pytest driver/tests -q                       # §14 の受入テスト
python -m driver tick --fixture driver/fixtures/dry_run.json   # DRY_RUN（既定）
python -m driver report --period-end 2026-10-11
python -m driver ticket-a4 H-0001                      # reports/tickets/H-0001.html
```

- 既定は DRY_RUN。取り込んだ取引には `synthetic` の印が付き、報告の数字に入らない。台帳は `ledger/dry_run.sqlite`（コミットしない）。
- `CCG_MODE=LIVE` の時だけ Etsy API を読み、`ledger/ccg.sqlite` に書く。必要な環境変数：`ETSY_SHOP_ID`・`ETSY_API_KEY`・`ETSY_READ_TOKEN`・`CCG_PSEUDO_SALT`（購入者 ID の仮名化）。リポジトリには置かない。
- 人手の正本は `ledger/human_work.csv`。実行のたびに読み直す。

## まだ無いもの・未検証

- Etsy API の項目名とエンドポイント（`etsy.py`）は公開仕様からの想定 [未検証]。Seller App のキーで実際に呼んで確かめる（v2 §17 #5）。
- 出品・停止の書き込み（`HttpEtsy.activate_listing / deactivate_listing`）は未実装。D-009 により、公開は Shun が承認した掲載一式（ハッシュで照合）だけ。停止の書き込みを実装するまで、停止は例外票で人に頼む。
- 手数料は §12.1 の料率からの推定。実際の請求（Etsy の支払い台帳）で置き換える処理は、キーが届いてから。
- 日次の定時実行（GitHub Actions の cron）は、キーを秘密に入れた後に足す。今は CI でテストだけ回す。
- CI の「tests/・results/ は追記だけ」の検査は `scripts/check_append_only.py`。R5 のジョブに書き込み権限を与えない設定（ブランチ保護など）は Shun の操作が要る。
