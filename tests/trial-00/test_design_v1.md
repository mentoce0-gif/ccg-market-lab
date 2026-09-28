# TRIAL-00 受入テスト設計 v1：Teacher Command Center v2

| 項目 | 内容 |
|---|---|
| 設計の版 | v1 |
| 設計した文脈の ID | `ctx-r6-trial00-20260927` |
| 設計日 | 2026-09-27 |
| ロール | R6 独立テスト設計者（R5 とは別の文脈） |
| 対象 | 試行 #0 `pre_spec`「Teacher Command Center v2」（英語、教員向け、Etsy のデジタル・スプレッドシート商品） |
| 後付けの記録 | **後付け：商品は本テストより前に作られた（v2 §8.4）** |
| 読んだもの | `v2_skeleton.md`（§3 原則5/6、§4.2、§6、§7.1〜7.5、§8.4、§9.3、§11、§16、付録A）、`TRIAL-00_teacher-command-center.md`（proposals/ と直下の2版） |
| 読んでいないもの | `build_command_center.py`、`verify_cc.py`、`listing/` 配下の全て、`driver/`。本設計を書き終えるまで、xlsx も開いていない |
| 実行するもの | `tests/trial-00/test_trial00_v1.py`（pytest）。重大度は §7.5（S0〜S3） |

## 0. 前提と方針

- 本設計は仕様と TRIAL-00 の記述だけから作った。xlsx を開いた後に期待値は変えない。変える必要が出たら、末尾の「実装時の注記」に書き、次の版（v2）で直す。
- **未実行は合格ではない。** 手動のテストは pytest で `skip(reason="MANUAL: ...")` とし、本書では「未実行」と記録する。
- 掲載一式（`listing/`）が無い場合、掲載のテストは **失敗** とする（skip しない）。掲載が無いのは T4 の欠陥だから。
- 検算は R6 が独自に書いた Python で行う。制作者の検証スクリプトの論理は使わない（読んでもいない）。
- 再計算は、`Blank` の**写し**を一時フォルダで openpyxl で編集し、headless の LibreOffice で xlsx に変換（＝再計算）して、openpyxl（`data_only=True`）で値を読む。`products/` には書き込まない。
- 受入条件の文（§7.1 の型）は、TRIAL-00 に無い。本設計では次の仮の文で読む：「英語圏の教員［対象者］が、学期中［状況］に授業計画・課題・成績・順位の管理［用事］を、名簿と課題と点数の入力［入力］から、生徒ごとの成績と相対順位と個票が出る状態［完了条件］まで実施できる。対象外は、ブックが記載する上限（人数・課題数）を超える入力、成績の公式な判定［境界］。」 [未検証：R3 の企画票が無いので R6 の仮置き]
- Etsy の制限値（タグ13個・各20字・タイトル140字）は [未検証]。一次情報で確かめていない。

## 1. 計算の規則（検算で使う）

Start Here やシート上の説明に規則が書いてあれば、それに従う。書いていなければ、次の既定値で検算する（既定値と違う規則が文書にあれば「実装時の注記」に記録する）。

| 記号 | 規則（既定値） |
|---|---|
| 空欄 | まだ採点していない。分子にも分母にも入れない |
| `M`（未提出） | 0点として扱い、分母（配点）に入れる。提出率では未提出に数える |
| `EX`（免除） | 分子にも分母にも入れない。提出率の分母からも外す |
| 分類の％ | 分類内の（得点の和）÷（配点の和）。採点済みが0件なら空欄（エラーにしない） |
| 総合の成績 | Σ(重み × 分類の％) ÷ Σ(採点済みのある分類の重み) |
| 文字の評定 | Setup の閾値表に従う |
| 提出率 | 提出済み ÷（採点対象の課題数 − EX の数）。`M` は未提出 |
| 順位 | 総合の成績の降順。同点は同じ順位（1,1,3 型）。成績が空の生徒は順位を付けない |
| パーセンタイル | 文書に書かれた式に従う（既定の式は置かない。書かれていなければ検算の対象外として注記） |

## 2. テストケース

列：ID／根拠（仕様の条項・要求）／入力／期待結果／失敗時の重大度／自動か手動か。

### 2.1 要求への適合（§7.2、付録A）

| ID | 根拠 | 入力 | 期待結果 | 重大度 | 方式 |
|---|---|---|---|---|---|
| T00-FIT-01 | §7.3「2版を同梱」 | `products/trial-00_teacher-command-center/` | `Teacher_Command_Center_Sample.xlsx` と `..._Blank.xlsx` が両方あり、openpyxl で開ける | S1 | 自動 |
| T00-FIT-02 | 付録A「9タブ」 | 両ブック | 表示中のシートがちょうど9枚。名前が Start Here、Dashboard、Setup、Roster、Pacing、Assignments、Gradebook、Standings、Student Report に1対1で対応（大小文字・空白・括弧の補足は無視） | S2 | 自動 |
| T00-FIT-03 | 付録A「連動」 | Sample の全数式 | 次のシート間参照がある：Assignments→Pacing、Gradebook→Roster、Gradebook→Assignments、Standings→Gradebook、Student Report→（Gradebook か Standings）、Dashboard→（他シートのどれか） | S2 | 自動 |
| T00-FIT-04 | 付録A「数式 2,344個」（事実の照合） | Sample | 数式のセル数が 2,344 と一致する。違えば記録の誤り | S3 | 自動 |
| T00-FIT-05 | §7.2「用事の完了」正常3ケース | Blank の写しに、(a) 生徒5人・課題6件、(b) 生徒20人・課題12件、(c) 全分類に点数あり、を入力して再計算 | エラー0、検算と一致、Standings と Student Report に値が出る | S1 | 自動（2.3 の検算と共通） |

### 2.2 スプレッドシートの追加テスト（§7.3）

| ID | 根拠 | 入力 | 期待結果 | 重大度 | 方式 |
|---|---|---|---|---|---|
| T00-SS-01 | §7.3 エラー0 | Sample を LibreOffice で再計算 | 全シートの全セルに `#VALUE!` `#REF!` `#DIV/0!` `#NAME?` `#N/A` `#NUM!` `#NULL!` `Err:xxx` 等が0件 | S1 | 自動 |
| T00-SS-02 | §7.3 空の版が崩れない | Blank を LibreOffice で再計算（入力なし） | エラー0件 | S1 | 自動 |
| T00-SS-03 | §7.3 空の版の表示 | Blank を開いた見た目 | 入力前に 0% やエラー風の表示、崩れた罫線が目立たない | S3 | **手動・未実行** |
| T00-SS-04 | §7.3 別実装で検算 | Sample を再計算した値 | 1章の規則で Python が求めた、分類の％・総合・評定・提出率・順位が、ブックの値と全件一致（数値の許容差 1e-6） | S1 | 自動 |
| T00-SS-05 | §7.3 Excel 2007 の関数だけ | 両ブックの全数式 | 使う関数が全て下の許可リストにある。`_xlfn.` の接頭辞が0件 | S2 | 自動 |
| T00-SS-06 | §7.3 条件付き書式は同じシート内 | 両ブックの条件付き書式 | 式に `!`（他シート参照）や外部参照が無い。名前付き範囲経由の他シート参照も不可 | S2 | 自動 |
| T00-SS-07 | §7.3 Google スプレッドシート | 両ブックを Google スプレッドシートで開く | 開ける。主要な計算結果（総合・順位）が Excel/LibreOffice 版と一致 | S1 | **手動・未実行**（§17 #2、Shun） |
| T00-SS-08 | §7.3 納品は openpyxl の元ファイル | 両ブックの `docProps/app.xml` | `Application` に LibreOffice / OpenOffice が含まれない | S2 | 自動 |
| T00-SS-09 | §7.2 再現性 | Sample を2回、別々に再計算 | 全セルの値が完全一致 | S2 | 自動 |

**Excel 2007 の許可リストの判断：** Excel 2007 で導入済みの関数は許可（SUMIFS、COUNTIFS、AVERAGEIFS、IFERROR を含む）。Excel 2010 以降の関数は不可：`IFNA`（2013）、`XLOOKUP`、`FILTER`、`LET`、`IFS`、`MAXIFS`、`MINIFS`、`TEXTJOIN`、`CONCAT`、`SWITCH`、`UNIQUE`、`SORT`、`SORTBY`、`SEQUENCE`、`XMATCH`、`AGGREGATE`（2010）、`RANK.EQ`/`RANK.AVG`/`PERCENTILE.INC`/`STDEV.S` など2010の新名。理由：§7.3 は「Excel 2007 の頃からある関数だけ」と明記しており、2010/2013 の関数は xlsx 内で `_xlfn.` 付きで保存され、古い環境で `#NAME?` になりうる。`IFNA` は Google スプレッドシートでは動くが、§7.3 の文言に従い不可とする。許可リストは実装ファイルに明示する（SUM、SUMIF、SUMIFS、SUMPRODUCT、COUNT、COUNTA、COUNTBLANK、COUNTIF、COUNTIFS、AVERAGE、AVERAGEIF、AVERAGEIFS、MIN、MAX、LARGE、SMALL、RANK、PERCENTRANK、PERCENTILE、MEDIAN、ROUND、ROUNDUP、ROUNDDOWN、INT、ABS、MOD、IF、IFERROR、AND、OR、NOT、TRUE、FALSE、ISBLANK、ISNUMBER、ISTEXT、ISERROR、ISNA、INDEX、MATCH、VLOOKUP、HLOOKUP、LOOKUP、CHOOSE、OFFSET、INDIRECT、ROW、ROWS、COLUMN、COLUMNS、TEXT、LEFT、RIGHT、MID、LEN、TRIM、UPPER、LOWER、PROPER、CONCATENATE、REPT、SUBSTITUTE、FIND、SEARCH、VALUE、EXACT、DATE、TODAY、NOW、YEAR、MONTH、DAY、WEEKDAY、WEEKNUM、NETWORKDAYS、WORKDAY、EDATE、EOMONTH、DATEDIF、N、T、NA、MAXA、MINA、STDEV、SUBTOTAL、HYPERLINK、ISODD、ISEVEN、CEILING、FLOOR）。ただし OFFSET と INDIRECT は許可するが揮発性なので注記に数だけ記録する。

### 2.3 端のケース（§7.3、§7.2「用事の完了」境界2ケース）

全て Blank の**写し**に入力して LibreOffice で再計算する。各ケースの期待：エラー0件、かつ 1章の規則による検算と一致。

| ID | 入力 | 追加の期待 | 重大度 | 方式 |
|---|---|---|---|---|
| T00-EDGE-01 | 生徒3人、課題3件、点数の一部を空欄 | 空欄は分母に入らない | S1 | 自動 |
| T00-EDGE-02 | 生徒3人、うち1人の課題に `M` | `M` は0点・分母に入る・提出率が下がる | S1 | 自動 |
| T00-EDGE-03 | 生徒3人、うち1人の課題に `EX` | `EX` は分子・分母・提出率の分母から外れる | S1 | 自動 |
| T00-EDGE-04 | 生徒4人が全員同じ点 | 全員が同じ順位（1位）。パーセンタイルでエラーが出ない | S1 | 自動 |
| T00-EDGE-05 | 生徒1人だけ | 順位1、パーセンタイルでエラーが出ない（0 除算しない） | S1 | 自動 |
| T00-EDGE-06 | 生徒はいるが点数が全て空欄 | 総合は空欄か表示なし。エラー0 | S1 | 自動 |

### 2.4 対象外の扱い（§7.2）

| ID | 根拠 | 入力 | 期待結果 | 重大度 | 方式 |
|---|---|---|---|---|---|
| T00-OOS-01 | §7.2 対象外 | Start Here の本文 | 人数と課題数の上限が数字で書かれている | S2 | 自動 |
| T00-OOS-02 | §7.2 用事の完了（境界） | 上限ちょうどの人数を Blank の写しに入力 | エラー0。上限の最後の生徒が Standings に出る | S1 | 自動 |
| T00-OOS-03 | §7.2 対象外 | 点数のセル | 範囲外の入力（配点を超える数・負の数・無関係な文字）に対し、データの入力規則か条件付き書式の警告がある | S2 | 自動（規則の有無だけ） |
| T00-OOS-04 | §7.2 対象外 | 上限+1人目の入力 | 黙って誤った順位を出さず、範囲外と分かる | S2 | **手動・未実行** |

### 2.5 使えること（§7.2）

| ID | 根拠 | 入力 | 期待結果 | 重大度 | 方式 |
|---|---|---|---|---|---|
| T00-USE-01 | §7.4 #4、§7.2 | 両ブック | 先頭のシートが Start Here で、開いた時の作業シートも Start Here | S3 | 自動 |
| T00-USE-02 | §7.2 リンク切れ | 両ブックのハイパーリンク | ブック内リンクの参照先シートが全て存在 | S2 | 自動 |
| T00-USE-03 | §7.2 文字欠け | 両ブックの文字列 | 英語の商品に日本語（CJK 文字）や `TODO` `FIXME` `lorem` `[未検証]` `XXX` の残りが無い | S3 | 自動 |
| T00-USE-04 | §7.2 開ける・読める | Excel と Google スプレッドシートで開く | 開ける、列幅で文字が切れていない | S2 | **手動・未実行** |

### 2.6 権利・機密（§7.2、§7.5 S0、CLAUDE.md 10）

| ID | 根拠 | 入力 | 期待結果 | 重大度 | 方式 |
|---|---|---|---|---|---|
| T00-RC-01 | 機密 | 両ブック | hidden / veryHidden のシートが0枚 | S2（中に秘密があれば S0） | 自動 |
| T00-RC-02 | 機密・安全 | xlsx の中身（zip） | `vbaProject.bin`、`externalLinks/`、外部の接続（`connections.xml`）が無い。ハイパーリンクの外部 URL は0件（あれば一覧を人が見る） | S1 | 自動 |
| T00-RC-03 | 個人情報 | `docProps/core.xml`・`app.xml` | creator / lastModifiedBy / Company / Manager に `@`（メール）や実在の人の名前が無い。検出には所有者の名前の断片（リポジトリに既に書かれている表記のみ）を使う | S0 | 自動 |
| T00-RC-04 | 個人情報 | 両ブックの全文字列 | メールアドレス、電話番号、住所らしい文字列が0件 | S0 | 自動 |
| T00-RC-05 | 個人情報 | Sample の生徒名 | 明らかに架空の名前で、実在の人に結び付かない | S0 | **手動・未実行** |

### 2.7 「売れる見込み」（§7.4）

§7.4 は #5 だけが確定。#1〜#4 は [較正待ち] なので、結果は記録するが T3 の合否には **暫定** として扱う（較正後に v2 で確定させる）。

| ID | §7.4 | 入力 | 期待結果 | 重大度 | 方式 |
|---|---|---|---|---|---|
| T00-SELL-01 | #1 自作が面倒か [較正待ち] | Sample の数式 | 他シートを参照する数式を持つシートが3枚以上 | S2（暫定） | 自動 |
| T00-SELL-01M | #1 後半 [較正待ち] | 人の見積もり | 買い手が1時間で再現できない | — | **手動・未実行** |
| T00-SELL-02 | #2 価格帯の根拠 [較正待ち] | 同じ用事の上位出品の価格とレビュー数の記録 | 記録があり、設定価格がその帯に入る | S2（暫定） | **手動・未実行**（Etsy を自動取得しない：CLAUDE.md 8） |
| T00-SELL-03 | #3 見た目 [較正待ち] | 掲載一式 | プレビュー5枚以上（T00-LST-02 で自動）。実データに近いサンプル（手動） | S2（暫定） | 自動＋**手動・未実行** |
| T00-SELL-04 | #4 最初の体験 [較正待ち] | Start Here | Start Here がある（T00-FIT-02 で自動）。5分で自分のデータに置き換えられる（手動） | S2（暫定） | 自動＋**手動・未実行** |
| T00-SELL-05 | #5 不合格の例（確定） | Sample と listing.json | 数式を持つシートが2枚以上（1枚で完結しない）、かつ価格が $1〜7 の帯に入らない（> $7） | S1 | 自動 |

### 2.8 掲載一式（§7.2「販売の説明」、§7.4 #3/#4、§9.3、§16）

契約：`products/trial-00_teacher-command-center/listing/listing.json`。キー `title`(str)、`price_usd`(数)、`tags`(str の配列)、`description_file`、`faq_file`、`previews`(相対パスの png の配列)、`files_delivered`(納品する xlsx の相対パスの配列)、`ai_disclosure`(str)。ほかに `description.md`、`faq.md`、`previews/*.png`。相対パスは `listing/` からの相対とし、見つからなければ商品フォルダからの相対も試す。

| ID | 根拠 | 入力 | 期待結果 | 重大度 | 方式 |
|---|---|---|---|---|---|
| T00-LST-01 | T4 必須の成果物 | listing.json | ファイルがあり、JSON として読め、8つのキーが全て正しい型 | S2（無ければ公開不可） | 自動 |
| T00-LST-02 | §7.4 #3、§7.2 | `previews` | 5枚以上。全て存在し、PNG の署名と IHDR が正しく、幅と高さが0でない | S2 | 自動 |
| T00-LST-03 | §9.3 委任の価格帯 | `price_usd` | 12 ≦ price ≦ 19 | S2（委任の外なので公開不可） | 自動 |
| T00-LST-04 | §7.2、§16 AI の表示 | description と `ai_disclosure` | `ai_disclosure` が空でない。説明文に AI を使って作ったことの明示（`AI` の語と created/made/generated/assisted/used/built のどれか）があり、`ai_disclosure` の文が説明文に含まれる | S1 | 自動 |
| T00-LST-05 | §7.2 範囲・形式・更新・返品 | description | 形式（xlsx / Excel / Google Sheets）、同梱物（Sample と Blank の両方）、限界（limit / up to / not included 等）、更新の条件（update）、返品の条件（refund / return / exchange）が書かれている | S2 | 自動 |
| T00-LST-06 | §7.2 実物と一致 | description と納品ブック | 説明文が「◯◯ tab / sheet」と名指すものが全て実在のシート名に対応。「N tabs / sheets」と書けば N が実際の表示シート数と一致 | S1 | 自動 |
| T00-LST-07 | §7.2 事実・数値 | description の数値の主張 | 「up to N students / assignments / categories」等の上限が、Start Here の記載と一致し、Blank の写しに N 人入れて最後の生徒が計算される（生徒の場合） | S1 | 自動 |
| T00-LST-08 | §7.3 納品物、§11 artifact のハッシュ | `files_delivered` | 全て存在し、Sample と Blank を両方含み、商品フォルダの xlsx とバイト単位で同じ。sha256 を計算して結果に記録（listing.json に sha256 の記録があれば一致を確認）。`docProps/app.xml` の Application が LibreOffice でない | S1 | 自動 |
| T00-LST-09 | Etsy の制限 [未検証] | `tags`、`title` | タグ13個以下、各20字以下、タイトル140字以下 | S2 | 自動 |
| T00-LST-10 | §9.3 FAQ 同梱 | description_file、faq_file | 両方存在し、空でない | S2 | 自動 |
| T00-LST-11 | §7.2 文字欠け | description、faq、title | CJK 文字、`TODO` `FIXME` `lorem` `[未検証]` `TBD` の残りが無い | S3 | 自動 |
| T00-LST-12 | §7.2 プレビューが実物と一致 | プレビュー画像 | 画像に写るシート・数値が実物と一致し、誇張が無い | S2 | **手動・未実行** |
| T00-LST-13 | §7.2 | description が Google Sheets 対応を名乗る場合 | T00-SS-07 が合格していること | S1 | **手動・未実行**（T00-SS-07 に依存） |

## 3. 未実行の一覧（合格に数えない）

T00-SS-03、T00-SS-07、T00-OOS-04、T00-USE-04、T00-RC-05、T00-SELL-01M、T00-SELL-02、T00-SELL-03（手動の部分）、T00-SELL-04（手動の部分）、T00-LST-12、T00-LST-13。

## 4. 合否のまとめ方

- T3（品質）の合格：S0〜S2 の失敗が0件、かつ手動の S0/S1 項目（T00-SS-07、T00-RC-05、T00-LST-13）が実行済み。点数の平均で打ち消さない（§7.5）。
- [較正待ち] の項目は、暫定の結果として記録する。
- 結果は `results/` に追記する（本設計の範囲外。R7 が行う）。

## 実装時の注記

（xlsx を開いた後に、設計との差を見つけた場合だけ追記する。上の本文は書き換えない。）

2026-09-27、`ctx-r6-trial00-20260927` で追記。本文の期待値は変えていない。v2 で本文に取り込む。

1. **環境。** 実装を始めた時点では LibreOffice の Calc の部品が入っておらず、xlsx を読めなかった。途中で指揮役が `libreoffice-calc` を入れ、再計算のテストを実行できた。環境が欠けても合格に見えないように、`T00-ENV-01`（再計算ができるか）を加えた。失敗すれば、再計算のテストは全て「BLOCKED・未実行」として skip になる。
2. **ハーネスの自己検査を加えた。** `T00-HARN-01`（手で計算した小さな例で、R6 の検算が正しいか）と `T00-CASE-build`（Blank の写しの正しいセルに入力が入るか）。商品のテストではない。
3. **空欄の規則が 1章の既定値と違った。** Start Here（B25〜B26）とシート上の説明に「期限を過ぎた空欄は、Setup が Yes の時は0点」とある。1章の規則どおり、文書の規則で検算する。T00-EDGE-01 は2つに分けた。Setup を No にして「空欄は分母に入らない」（本文の期待）を確かめるものと、Yes にして文書の規則を確かめるもの。T00-EDGE-06 は、全て空欄だと Yes の規則で0点になり本文の期待と食い違うため、「As of を全ての締切より前にする」入力にした。
4. **順位の基準。** 本文は「総合の成績の降順」としていたが、Standings（A4）は Performance index の降順と書いている。文書に従った。同点の判定は 1e-9 の許容差を使う（本文の「同点は同じ順位」を、浮動小数の丸めの差で崩さないため）。
5. **書かれていない規則。** パーセンタイルの式は文書に無い。本文どおり値は検算せず、0〜1 の範囲にあることと、Performance index と順序が合うことだけを確かめる。Performance index は、総合と提出率の一方が欠けた時の扱いが書かれていないので、両方がある生徒だけを比べる。「Watch = 線から10ポイント以内」は「線＋0.10 未満」と読んだ。
6. **検算の範囲を広げた。** Gradebook の Missing の件数、Dashboard の Class average・Work turned in・Students at risk、Student Report（選んだ生徒の総合・提出率・未提出、課題ごとの状態）、Pacing の Ends が単元の最後の週に入るか、を加えた。どれも Start Here に書かれた機能。締切の日付を打っていない課題の締切には、ブックの Pacing の「Ends」の値を入力として使う（Ends 自体は上の週の範囲で別に確かめる）。端のケースの入力では、締切を全て打ち込んだ。
7. **許可リストの漏れ（R6 の見落とし）。** v1 のリストから STDEVP・STDEVA・STDEVPA・VAR・VARP が抜けていた。どれも Excel 2007 より前からある関数なので、許可リストに加えた。
8. **T00-USE-05 を追加（S3）。** Start Here（B19）は、課題の状態を「Submitted, Missing, Excused or Not due yet」と約束している。Student Report で表示が約束どおりかを確かめる。検算（T00-SS-04）では「Turned in」も Submitted と同じ意味として受け入れ、言葉の違いはこのテストだけで扱う。
9. **T00-SELL-05 を2つに分けた。** 05a は構造（数式のあるシートが2枚以上）、05b は価格（> $7。listing.json が必要）。
10. **openpyxl の制約。** openpyxl で編集した写しからはグラフが消える。計算のテストには影響しないが、グラフの描画は自動では検査していない（T00-USE-04 の手動で見る）。
11. **掲載一式の出現。** 実装中に `listing/` ができた。R6 は中身を読んでいない。テストは契約の上で動く。掲載が無い時の動きは、フィクスチャのエラーではなく**テスト本体で失敗する**形に直した（本文の「掲載が無ければ失敗」を守るため）。
12. **sha256 の記録先。** 契約に sha256 のキーが無い。T00-LST-08 は、計算した値を junit の property と標準出力に記録する。listing.json に `sha256` か `hashes` の辞書があれば、それとも照合する。記録の置き場所（§11 の artifact）は R7／R0 が決めること。

### 初回の実行結果（2026-09-27）

`4 failed, 56 passed, 11 skipped`。skip は全て MANUAL で、未実行。

| テスト | 結果 | 重大度 | 内容 |
|---|---|---|---|
| T00-FIT-04 | 失敗 | S3 | 数式のセルは 2,345 個で、記録（付録A・TRIAL-00）の 2,344 と合わない。記録か数え方のどちらかを直す |
| T00-EDGE-03（EX） | 失敗 | S1 | 数学的には全員同点（0.8）なのに、EX のある生徒だけが浮動小数の差で3位になる。さらに Standings の O9:R9 と Dashboard の H11:I11 に `#N/A` が出る。直し方の例：比べる前に ROUND で丸める |
| T00-OOS-03 | 失敗 | S2 | Gradebook の点数の欄に、範囲外の入力（配点を超える数、負の数、文字）を止める入力規則も、知らせる条件付き書式も無い。直し方の例：点数のセルに条件付き書式を足し、配点（行7）を超えるか0未満の時に色を付ける |
| T00-USE-05 | 失敗 | S3 | Start Here は「Submitted」と書いているが、Student Report は「Turned in」と表示する。どちらかの言葉に揃える |
