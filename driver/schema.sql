-- CCG 台帳（v2 §11 のデータ契約）。SQLite。
-- 金額：円は整数（円）、ドルは整数（セント）。時刻は ISO 8601（JST, +09:00）。
-- 個人情報は置かない。顧客は HMAC で仮名化した ID だけを持つ。

PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS meta (
  key   TEXT PRIMARY KEY,
  value TEXT NOT NULL
);

-- 需要の取得元（§5.1）
CREATE TABLE IF NOT EXISTS source (
  source_id        TEXT PRIMARY KEY,
  url_or_api       TEXT NOT NULL,
  permission_basis TEXT NOT NULL,       -- 取得を許可された根拠
  checked_on       TEXT NOT NULL,
  next_check_on    TEXT NOT NULL,
  limits           TEXT,
  status           TEXT NOT NULL DEFAULT 'pending'  -- pending / registered / rejected
);

-- 需要記録（§5.2, §5.3）。raw_excerpt はデータとしてのみ扱う（実行しない）
CREATE TABLE IF NOT EXISTS demand (
  demand_id      TEXT PRIMARY KEY,
  source_id      TEXT NOT NULL REFERENCES source(source_id),
  written_at     TEXT NOT NULL,         -- 書かれた日。取得日で代えない
  url            TEXT NOT NULL,
  raw_excerpt    TEXT NOT NULL,
  job            TEXT,
  situation      TEXT,
  evidence_class TEXT NOT NULL CHECK (evidence_class IN ('E0','E1','E2','E3','E4')),
  dup_group      TEXT,
  exclude_reason TEXT,
  source_gone    INTEGER NOT NULL DEFAULT 0
);

-- 試行（experiment）と variant。価格・販路などが変わったら variant を分ける（§8.1）
CREATE TABLE IF NOT EXISTS experiment (
  experiment_id  TEXT PRIMARY KEY,
  parent_id      TEXT,
  hypothesis     TEXT NOT NULL,
  audience       TEXT,
  format         TEXT,
  channel        TEXT NOT NULL DEFAULT 'etsy',
  budget_jpy     INTEGER NOT NULL DEFAULT 3000 CHECK (budget_jpy <= 3000),
  start_on       TEXT,
  end_on         TEXT,
  stop_rule      TEXT,
  state          TEXT NOT NULL DEFAULT 'OBSERVED',
  pre_spec       INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS experiment_demand (
  experiment_id TEXT NOT NULL REFERENCES experiment(experiment_id),
  demand_id     TEXT NOT NULL REFERENCES demand(demand_id),
  PRIMARY KEY (experiment_id, demand_id)
);

CREATE TABLE IF NOT EXISTS variant (
  variant_id    TEXT PRIMARY KEY,
  experiment_id TEXT NOT NULL REFERENCES experiment(experiment_id),
  price_cents   INTEGER NOT NULL,
  currency      TEXT NOT NULL DEFAULT 'USD',
  channel       TEXT NOT NULL,
  audience      TEXT,
  main_copy_hash TEXT,
  created_at    TEXT NOT NULL,
  UNIQUE (experiment_id, price_cents, currency, channel, audience, main_copy_hash)
);

-- 状態遷移の記録（§6）。証拠 ID がない遷移は入れない
CREATE TABLE IF NOT EXISTS state_transition (
  id            INTEGER PRIMARY KEY AUTOINCREMENT,
  experiment_id TEXT NOT NULL REFERENCES experiment(experiment_id),
  from_state    TEXT NOT NULL,
  to_state      TEXT NOT NULL,
  evidence      TEXT NOT NULL,
  at            TEXT NOT NULL
);

-- 商品の版（artifact）
CREATE TABLE IF NOT EXISTS artifact (
  artifact_id    TEXT NOT NULL,
  version        TEXT NOT NULL,
  experiment_id  TEXT REFERENCES experiment(experiment_id),
  sha256         TEXT NOT NULL,
  gen_cost_jpy   INTEGER NOT NULL DEFAULT 0,
  input_sources  TEXT,                -- JSON: 依存する demand_id / 原典 URL
  refresh_due    TEXT,
  delivered_to   TEXT,
  needs_recheck  INTEGER NOT NULL DEFAULT 0,
  PRIMARY KEY (artifact_id, version)
);

-- テスト結果（§4.2：追記のみ。R5 は書けない）
CREATE TABLE IF NOT EXISTS test_record (
  test_id        TEXT NOT NULL,
  artifact_id    TEXT NOT NULL,
  artifact_version TEXT NOT NULL,
  requirement_id TEXT,
  expected       TEXT NOT NULL,
  actual         TEXT NOT NULL,
  passed         INTEGER NOT NULL,
  evidence       TEXT NOT NULL,
  severity       TEXT CHECK (severity IN ('S0','S1','S2','S3')),
  design_version TEXT NOT NULL,
  run_at         TEXT NOT NULL,
  design_context_id TEXT NOT NULL,
  recorded_by_role  TEXT NOT NULL
);
CREATE TRIGGER IF NOT EXISTS test_record_no_update BEFORE UPDATE ON test_record
BEGIN SELECT RAISE(ABORT, 'test_record is append-only'); END;
CREATE TRIGGER IF NOT EXISTS test_record_no_delete BEFORE DELETE ON test_record
BEGIN SELECT RAISE(ABORT, 'test_record is append-only'); END;

-- 委任（§9.3）
CREATE TABLE IF NOT EXISTS authorization (
  auth_id        TEXT PRIMARY KEY,
  version        INTEGER NOT NULL,
  action         TEXT NOT NULL,       -- publish_listing / update_listing / change_price / spend / refund / ...
  account        TEXT NOT NULL,
  scope          TEXT NOT NULL,       -- JSON: {price_min_cents, price_max_cents, formats, requires_gates}
  cost_cap_jpy   INTEGER,
  granted_at     TEXT NOT NULL,
  expires_at     TEXT,
  basis          TEXT NOT NULL,       -- A4 承認シートの ID など
  revoked        INTEGER NOT NULL DEFAULT 0
);

-- 掲載と累計閲覧数のスナップショット（§8.2）
CREATE TABLE IF NOT EXISTS listing (
  listing_id    TEXT PRIMARY KEY,
  experiment_id TEXT NOT NULL REFERENCES experiment(experiment_id),
  variant_id    TEXT NOT NULL REFERENCES variant(variant_id),
  published_on  TEXT,
  state         TEXT NOT NULL DEFAULT 'draft',  -- draft / active / quarantined / inactive
  has_digital_file INTEGER NOT NULL DEFAULT 0,
  file_sha256   TEXT
);

CREATE TABLE IF NOT EXISTS view_snapshot (
  listing_id  TEXT NOT NULL REFERENCES listing(listing_id),
  on_date     TEXT NOT NULL,
  cumulative_views INTEGER NOT NULL,
  PRIMARY KEY (listing_id, on_date)
);

-- 公開の意図（再起動で二重公開しないため。§14 #12）
CREATE TABLE IF NOT EXISTS publish_intent (
  idem_key    TEXT PRIMARY KEY,
  listing_id  TEXT NOT NULL,
  status      TEXT NOT NULL,          -- pending / done / refused
  created_at  TEXT NOT NULL,
  done_at     TEXT
);

-- 取引（Etsy の receipt 単位）。receipt_id で重複を除く（§14 #1）
CREATE TABLE IF NOT EXISTS txn (
  receipt_id     TEXT PRIMARY KEY,
  customer_id    TEXT NOT NULL,       -- 仮名化 ID
  listing_id     TEXT,
  variant_id     TEXT,
  experiment_id  TEXT,
  currency       TEXT NOT NULL,
  gross_cents    INTEGER NOT NULL,    -- 税を除く商品の売上
  tax_cents      INTEGER NOT NULL DEFAULT 0,
  fee_cents      INTEGER NOT NULL DEFAULT 0,
  fee_basis      TEXT NOT NULL DEFAULT 'estimate', -- estimate / actual
  refund_cents   INTEGER NOT NULL DEFAULT 0,
  jpy_per_usd    REAL NOT NULL,       -- 円換算の基準
  paid           INTEGER NOT NULL,
  paid_at        TEXT,                -- 決済の確定日時
  payout_at      TEXT,                -- 入金日
  flag           TEXT NOT NULL DEFAULT 'none' CHECK (flag IN ('none','bot','test','related','synthetic','self')),
  delivery_ok    INTEGER,             -- NULL=未確認, 1=納品可, 0=納品物欠落
  ingested_at    TEXT NOT NULL,
  raw_hash       TEXT NOT NULL
);

-- variant の適用期間（同じ掲載で価格を変えたら、期間を区切って新しい variant にする。§14 #9）
CREATE TABLE IF NOT EXISTS listing_variant (
  listing_id TEXT NOT NULL REFERENCES listing(listing_id),
  variant_id TEXT NOT NULL REFERENCES variant(variant_id),
  from_at    TEXT NOT NULL,
  to_at      TEXT,
  PRIMARY KEY (listing_id, from_at)
);

-- 除外する顧客（自己・知人・テスト）。仮名化 ID と根拠だけを持つ（§14 #8）
CREATE TABLE IF NOT EXISTS customer_flag (
  customer_id TEXT PRIMARY KEY,
  flag        TEXT NOT NULL CHECK (flag IN ('test','related','self','bot')),
  basis       TEXT NOT NULL
);

-- 出来事（§11 event）
CREATE TABLE IF NOT EXISTS event (
  event_id      INTEGER PRIMARY KEY AUTOINCREMENT,
  at            TEXT NOT NULL,
  experiment_id TEXT,
  kind          TEXT NOT NULL,
  customer_id   TEXT,
  receipt_id    TEXT,
  flag          TEXT NOT NULL DEFAULT 'none',
  evidence      TEXT
);

-- 費用（§11 cost）。区分は §2.4 の4つ
CREATE TABLE IF NOT EXISTS cost (
  cost_id       TEXT PRIMARY KEY,
  incurred_on   TEXT NOT NULL,
  paid_on       TEXT,
  currency      TEXT NOT NULL,
  amount_jpy    INTEGER NOT NULL,
  category      TEXT NOT NULL CHECK (category IN ('base','trial','delivery','fees')),
  experiment_id TEXT,
  vendor        TEXT NOT NULL,
  status        TEXT NOT NULL CHECK (status IN ('reserved','provisional','final')),
  note          TEXT
);

-- 予算の予約（§2.4：原子的に予約してから処理）
CREATE TABLE IF NOT EXISTS reservation (
  reservation_id TEXT PRIMARY KEY,
  created_at     TEXT NOT NULL,
  on_date        TEXT NOT NULL,
  category       TEXT NOT NULL,
  experiment_id  TEXT,
  amount_jpy     INTEGER NOT NULL,
  status         TEXT NOT NULL CHECK (status IN ('held','settled','released')),
  actual_cost_id TEXT
);

-- 人手（§11 human_work）
CREATE TABLE IF NOT EXISTS human_work (
  id             INTEGER PRIMARY KEY AUTOINCREMENT,
  at             TEXT NOT NULL,
  minutes        INTEGER,
  role           TEXT NOT NULL,
  experiment_id  TEXT,
  kind           TEXT NOT NULL CHECK (kind IN ('normal','abnormal','exception')),
  exception_reason TEXT,
  task           TEXT,
  is_ai_relay    INTEGER NOT NULL DEFAULT 0
);

-- 判定（§11 decision）
CREATE TABLE IF NOT EXISTS decision (
  id            INTEGER PRIMARY KEY AUTOINCREMENT,
  decided_on    TEXT NOT NULL,
  rule_version  TEXT NOT NULL,
  experiment_id TEXT,
  evidence_ids  TEXT NOT NULL,
  conclusion    TEXT NOT NULL,
  counter_evidence TEXT NOT NULL,
  missing       TEXT,
  next_change   TEXT
);

-- 例外票（H票）。期限切れでも承認にしない（§14 #13）
CREATE TABLE IF NOT EXISTS ticket (
  ticket_id     TEXT PRIMARY KEY,
  created_at    TEXT NOT NULL,
  kind          TEXT NOT NULL,
  dedupe_key    TEXT NOT NULL UNIQUE,
  ask           TEXT NOT NULL,
  minutes       INTEGER NOT NULL,
  target        TEXT NOT NULL,
  reason        TEXT NOT NULL,
  options       TEXT NOT NULL,        -- JSON: [{label, recommended}]
  deadline      TEXT NOT NULL,
  on_no_answer  TEXT NOT NULL,
  status        TEXT NOT NULL DEFAULT 'open' CHECK (status IN ('open','answered','closed')),
  answer        TEXT,
  answered_at   TEXT
);

-- 停止スイッチ（全体と掲載ごと）
CREATE TABLE IF NOT EXISTS stop_switch (
  scope        TEXT PRIMARY KEY,      -- 'global' または 'listing:<id>' / 'experiment:<id>'
  engaged      INTEGER NOT NULL,
  reason       TEXT NOT NULL,
  engaged_at   TEXT NOT NULL,
  cleared_evidence TEXT,
  cleared_at   TEXT
);

-- 監査の記録（拒否した操作も残す）
CREATE TABLE IF NOT EXISTS audit (
  id      INTEGER PRIMARY KEY AUTOINCREMENT,
  at      TEXT NOT NULL,
  actor   TEXT NOT NULL,
  action  TEXT NOT NULL,
  outcome TEXT NOT NULL,
  detail  TEXT
);
CREATE TRIGGER IF NOT EXISTS audit_no_update BEFORE UPDATE ON audit
BEGIN SELECT RAISE(ABORT, 'audit is append-only'); END;
CREATE TRIGGER IF NOT EXISTS audit_no_delete BEFORE DELETE ON audit
BEGIN SELECT RAISE(ABORT, 'audit is append-only'); END;

-- 単一実行のロック
CREATE TABLE IF NOT EXISTS run_lock (
  name       TEXT PRIMARY KEY,
  holder     TEXT NOT NULL,
  expires_at TEXT NOT NULL
);
