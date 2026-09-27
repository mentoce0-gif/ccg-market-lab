# AI自走事業の実証・販路・法務・需要の再検証

**公開情報からは、指定された「90日・純収益月1万円・課金10件以上・顧客集中30%以下・L3」を同時に満たす再現性は確認できず、売上の自己申告と自律運用の実証を分け、販路ごとの制約を踏まえて実測する必要がある。**

調査・取得日：2026-09-27。対象資料：`02_deep_research_prompt_filled.txt`。添付文書は調査範囲の指定として扱い、その数値・引用・証拠グレードを事実とはみなしていない。候補の選定・順位付けは行わない。

## 読み方と調査の限界

- 「一致」は一次資料に同じ主張があるという意味であり、銀行明細や全注文を独立監査した意味ではない。本人の売上申告はCのまま。
- 「不一致」は定義・値・日付・事例の性質が資料と食い違うもの。「確認不能」は原典未取得、期間不明、定義不足など。確認不能は虚偽や売上ゼロを意味しない。
- `[未検証]` は一次による裏付けを確保できなかった主張、`[二次]` は第三者による紹介。未判明値は `?（未確認）` とした。
- 公式の規約・料金は全て上記取得日時点。公開日・改定日がない現行ページは「日付不記載」とする。2026年6月より前の文書しか確認できない場合は「最新版未確認」。日付のない現行スナップショットを、特定日の歴史的実績には転用しない。
- 直近12か月の執行確認対象は2025-09-27〜2026-09-27。「個別執行未確認」は、その期間に停止・削除がなかったという意味ではない。
- 添付の追加指示に従い、自走実験を先に確認し、人が運営するAI製品は大型主張5件を参考確認した。A/Bを20件揃えるために、Cや二次記事を昇格させてはいない。

## 主要な反証と、それを補う支持

反証：大きなMRRは人間が運営するAI製品の数字であり、自走事業の成績ではない。自走実験は少額・ゼロ売上の自己申告が中心で、実験期間、費用、人手、独立顧客の数が揃わない。失敗側にも、商品販売への誘導や合成事例が混ざる。したがって「失敗率」もこの一覧からは算出できない。

改善に必要な情報：注文ID、顧客ID、返金、決済確定額、API等の費用、人手分数、障害時間を同じ期間で照合する。AI自身の活動報告やチェーンの送金数を売上台帳の代用にしない。

支持：Apifyには開発者への実際の分配を示す公式集計があり、決済・実行APIも存在する。限定された作業は、ルール・検証器・支出上限を組み合わせれば自動化できる。ただし、分配総額は個人の期待収益でも、90日無監督の証明でもない。[Apify公式パートナー情報](https://apify.com/partners/actor-developers)

## B1　事例と証拠シードの裏取り

### 1. AIが運営するとされた実験群

重複はA13=B03、A14=D09、A20=B07を一件として扱う。

| ID | 判定 | 一次で確認できた内容・修正 | 証拠と自走の扱い |
|---|---|---|---|
| B02 | 一致。ただし証拠区分を修正 | 本人転載に240通超の営業メール、返信1、売上$0、3月の停止という記述。原稿末尾に$19の運営ツールキット販売がある | C相当の自己申告に加えてD要素。集計から除外し、障害の参考に限定。[本人転載](https://dev.to/the200dollarceo/my-ai-venture-sent-240-emails-and-made-0-so-i-killed-it-heres-the-autopsy-3h09) |
| A13=B03 | 一致は申告内容に限定 | 79日、2販売、$54。$27の商品が販売対象。本文中の時間経過と添付の掲載日を同一観測日として扱えない | 独立取引確認なし。稼ぎ方販売への誘導を含む資料としてD側に隔離。人手ゼロも未監査。[投稿](https://www.indiehackers.com/post/i-am-an-autonomous-ai-agent-79-days-2-sales-54-here-is-the-honest-data-5e48398e85) |
| B04／S2 | 一致。ただし因果は限定 | 2026-07-31の本人報告。価格$149〜349、売上$0。認証・決済経路の故障や裁量制限を記載 | C。「市場全体に需要がない」とは証明しない。到達・決済障害と需要を分離して再計測する必要。[原報告](https://automatonagency.com/insights/autonomous-agent-revenue-experiment-teardown) |
| B05 | 一致は売上$0という本人申告 | Solana API／Agentverseの利用・接触が売上に結びつかなかった報告 | C。149 interactionsの計測定義・独立利用者数は[未検証]。接触≠購入。[投稿](https://www.indiehackers.com/post/shipped-a-solana-defi-api-agentverse-agent-as-a-solo-builder-0-revenue-real-traffic-wrong-payment-rails-13c20484fd) |
| B06 | 確認不能 | 資金$350→$250.50という原投稿の証拠画像・条件を確保できず | [未検証]。B扱いを維持できない。[指定X投稿](https://x.com/AlexReibman/status/2082878672906891578) |
| A20=B07 | 数値は一致、C分類は不一致 | 2026-09-16投稿に6か月107記事、4販売、4,920円。承認は人。本文自体が同じ運用手順・プロンプトの販売導線 | Dとして収益証拠の集計から除外。L3の裏付けにならない。[本人記事](https://note.com/kazuyuki_ai_lab/n/n4fcdcdd9a65b) |
| B08 | 不一致 | 「17登録、2転換、0有料」は一社の実測記録ではなく、5事例を合成した説明だと本文が明記 | 個別失敗件数から除外。障害類型の説明としてのみ扱う。[原記事](https://blog.tobira.ai/built-ai-agent-product-onboarding-post-mortem/) |
| A19=B09 | 売上申告は一致、自走の解釈は不一致 | 2026-06-23記事に3月受託1,937,635円＋書籍21,403円＝1,959,038円。AI月2万円のほかサーバー等もある。対外行為は人が承認 | C。受託売上とAIが獲得した売上は別。毎回承認する範囲はL1。9事業ゼロの申告も残す。[本人記事](https://zenn.dev/joinclass/articles/1-ai-20260622220005-15275) |
| A14=D09 | 一致は本人の少額決済報告 | 9月投稿・コメントに3 USDT、微小x402、8.1 XNO。209セッション・4完了という説明もある | C。本文と後日コメントの期間を混ぜない。全額・費用・独立顧客数は不明。オンチェーン明細の独立再照合未実施。[投稿](https://www.indiehackers.com/post/i-let-an-ai-agent-run-my-llm-security-products-whole-sales-loop-for-30-days-here-s-what-actually-broke-e16f092b52) |
| B16 | 対象期間外 | 2月の1円獲得実験。承認を伴う | 3月以降の事例件数から除外。過去の参考のみ。[本人記事](https://zenn.dev/agent_workshop/articles/ai-1yen-challenge) |
| B18 | 確認不能 | 放置した6エージェント中1体が自活したという紹介から、検証可能な本人原典に到達できず | [二次][未検証]。資金・存続・収益を集計しない。[紹介](https://enterprisedna.co/resources/ai-pulse/ai-pulse-2026-08-11-the-abandoned-agent-that-s-still-alive-and-self-employed-fiv/) |
| B10 | 確認不能 | 「短時間でクラウド費7万円」の指定原典を取得できず | [未検証]。具体額は外す。コスト暴走という設計上の失敗類型はB2に残す。[指定記事](https://zenn.dev/i_ichi/articles/openclaw-agent-vol2) |

**この群から成功確率や平均利益を出さない。** 公開する動機、期間、原価、顧客、運営主体が揃わず、D資料もある。改善策は、今後のPoCを事前に固定した成功条件で測ることであり、事例を追加して見かけの母数を増やすことではない。

### 2. 人が運営するAI製品：大型主張5件

通貨・期間・投資益・累計額が混在するため、厳密な売上順位は作れない。添付の大型金額主張からA31・A05・A02・A03・A01を監査対象にした。この5件を同一尺度の「上位ランキング」とはしない。

| ID | 判定 | 修正・確認結果 | 自走の証拠に使えない理由 |
|---|---|---|---|
| A31 | 確認不能 | Cursor $2B ARR、Harvey $195M等は今回の探索で該当時点の一次を確保できず。[二次][未検証] | 大企業のARRであり、個人の無監督運営でも純利益でもない |
| A05 | 一致は本人申告 | 2026-09-23のParakeetAI記事に月$1M、150万ユーザー。100人超のUGC制作者を利用 | 少人数コアチームと総人的投入は別。[本人インタビュー](https://www.indiehackers.com/post/tech/from-weekend-project-to-1m-mrr-in-two-years-YRaa1QlGTjaqh0XgzWkc) |
| A02 | 「事業売上$10M」の解釈は不一致 | 本人は事業収入と投資益の合計を説明。事業部分は月$200k〜250k、投資益は未実現を含む | 除外領域の投資益を収益実証に混ぜない。C。[本人記事](https://levels.io/passed-10m-revenue-investment-gains) |
| A03 | 確認不能 | Rezi・PROSP・Comp AIの集合記事から、該当期間の公開決済台帳を独立確認できず | 二次集合記事をAにしない。各社の売上・MRR・累計を合算しない。[二次記事](https://saasxtra.com/the-state-of-ai-startups/) |
| A01 | 添付の組合せは確認不能 | 別時点の本人記事に月売上$105k・利益$80kという申告。これは約76.2%。添付の87%・2,573契約と同じ観測窓ではない | 別時点の数字で87%を直接反証もしない。いずれもL3証拠ではない。[本人記事](https://levels.io/photoai-40870-line-index-php-105k-mo-revenue) |

A30のStripe集計も、会社設立者や人が運営する事業についての参考資料であり、自走率ではない。今回確認した公式記事の数字と、添付の「3倍」「4倍」という主張の対応は確認不能。[Stripe公式分析](https://stripe.com/blog/top-solo-founder-traits)

### 3. 日付・重複・A/B区分の追加監査

| 対象 | 判定と扱い |
|---|---|
| A10 Runbear | 一次ページの掲載年月日を確定できず、対象期間の件数から除外。[記事](https://www.indiehackers.com/post/tech/dialing-in-an-ai-products-icp-and-growing-it-to-400k-arr-l3XkEjvP43kuUwjxzUnd) |
| A24 Apify高収益開発者 | 公式ヘルプは2025-10-22。対象期間外。「上位月$10k超」は公式自己申告で、典型値ではない。料金条件は旧記述を採用しない。[公式ヘルプ](https://help.apify.com/en/articles/8684010-make-money-publishing-your-actors-on-apify-store) |
| A23=D06 | 公式現行ページの月$1.6Mは取得日付きスナップショットとして残す。公開日不明なので期間内の新規発表件数から除外。$563kは後述の2025年記事 |
| B12 | 原典・日付を確定できず除外。[指定HN](https://news.ycombinator.com/item?id=49793953) |
| B14 | HNの話題だけではAmazonによるMeta側への措置の一次日付・範囲を確定できず除外。[指定HN](https://news.ycombinator.com/item?id=49789982) |
| A21・A22・B17 | 同じ二次検証記事への参照。三つの独立事例ではない。原取引・公開台帳未確認として一件に統合。[二次記事](https://note.com/aikensyou/n/nb9271b080f16) |
| D01 | X画像の主張のみでtx hashと商品納品を独立照合できず確認不能。[指定投稿](https://x.com/useQPay/status/2104054695673356569) |
| D07 | Apify上の販売ページと公式x402機能は確認。ただし価格提示・対応機能は販売実績ではなく、Bの取引証拠にはならない。[商品ページ](https://apify.com/johnvc/store-actor-intelligence-api) |
| D08 | Baseの30日310万tx・$1.2Mは該当一次集計に到達できず確認不能。[二次記事](https://cryptobriefing.com/agent-payments-growth-x402/) |
| D11 | AWSの2026-06-15発表は一次確認。Visa・Mastercardも同週に出荷したという束ねた主張は[未検証]。発表≠GMV。[AWS](https://aws.amazon.com/about-aws/whats-new/2026/06/aws-waf-ai-traffic-monetization/) |
| D12 | $73M÷176M≒$0.415で、添付の平均$0.31と算術不一致。分母・期間・TRMの真性0.6〜7.5%は一次未確認。[二次集計](https://agenticfinancegraph.com/x402-protocol-how-ai-agents-pay-with-usdc-statistics) |

### 4. S1〜S12の監査

| Seed | 判定 | 確認結果・訂正 |
|---|---|---|
| S1 NanoCorp | 一部一致／歴史的日付は確認不能 | 7月20日週の公式週報は30,272社・収益あり206社。割算0.6805%は正しいが、稼働者コホートや「ever」の定義は不明で成功確率ではない。トップの30日$1,530を9月15日時点と固定する根拠は得られず。[週報](https://www.nanocorp.so/changelogs)・[現行トップ](https://www.nanocorp.so/) |
| S2 Automaton | 一致は自己報告 | 売上ゼロと障害は確認。需要欠如だけに原因を絞れない。B04参照 |
| S3 x402 | 確認不能／古い観測を現在値にしない | 日次$28k・約半分人工という二次分析、個人サイト外部支払ゼロの原取引を今回一次で再現できず。新しい研究でも独立した需要の識別が課題。下表参照 |
| S4 RLI | 不一致 | 7月1日の研究者記事ではFable 5が15.8%。評価の甘さはモデル別2.9倍・2.3倍で一律3倍ではない。9月27日の現行榜はGPT-6 Astra 20.83%。長期事業成功率ではない。[研究者記事](https://safe.ai/blog/significant-increase-in-digital-labor-automation)・[現行榜](https://labs.scale.com/leaderboard/rli) |
| S5 Magentic Marketplace | おおむね一致／対象モデルに限定 | 提案順序・速度への偏り、規模拡大時の低下、攻撃への弱さを原研究が報告。2025年の実験を2026年全モデルの成績としない。[Microsoft Research](https://www.microsoft.com/en-us/research/blog/magentic-marketplace-an-open-source-simulation-environment-for-studying-agentic-markets/) |
| S6 Polsia | 確認不能 | 月$500k、30日解約84.6%とも該当一次の定義・データを確保できず。[二次][未検証]。プラットフォーム収入と入居事業の利益を分離する必要。[紹介記事](https://www.sofarbot.com/stories/polsia-ben-broca-500000-monthly-revenue) |
| S7 規約・執行 | 複数の不一致 | KDPは現在「形式ごとに週10タイトル」。ChatGPTはデジタル商品の外部決済誘導も禁止対象。YouTubeの2025年名称変更は確認できるが2026年大量削除は未確認。Cloudflareの特定日デフォルト遮断も未確認。詳細B3 |
| S8 Project Vend 2 | 一致。ただし自律性を過大評価しない | 2025-12-18。改善はあるが購入承認・実物作業・修復に人が関与。L3の90日実証ではない。[Anthropic](https://www.anthropic.com/research/project-vend-2) |
| S9 Vending-Bench 2 | 一致はシミュレーション成績 | 現行上位の期末残高は$10k超。実時間1年の商売・実現純利益とは別。[公式ベンチ](https://andonlabs.com/evals/vending-bench-2) |
| S10 Apify | 不一致 | 現行公式は月$1.6M・4,500 community developers。単純比$355.56を平均所得・期待収益にしない。標準式は売上×80%−プラットフォーム使用費。旧レンタル移行は確認。詳細下記 |
| S11 MCP | 一部一致／利用資格は未確定 | MCP Marketplace規約は85%還元・Stripe Connect Express。日本の出品者受入れ、売上総額、他ディレクトリ全体に課金掲載がないという断定は未確認。[規約](https://mcp-marketplace.io/terms) |
| S12 JPYC | 発行額は公式掲載確認、実用性は未確認 | 2026-04-15の公式発表の検索取得部分に累計21億円超。全文取得には制限があり、M2M投資の詳細は[未検証]。発行残高・累計発行・商取引額を混同しない。[公式発表](https://corporate.jpyc.co.jp/news/posts/series-b-second-close) |

YouTubeの名称変更は新たなAI全面禁止ではない。[TeamYouTubeの説明](https://support.google.com/youtube/thread/356734251?hl=en&msgid=441502354)。Googleの公式履歴には3月・6月・8月のほか9月24日開始の更新も掲載されている。日付の確認から「すべてのAI生成物が対象」とは推論できない。[Google Search Status](https://status.search.google.com/summary)

### 5. Apify：金額と計算式の修正

| 数字 | 何の数字か | 採用方法 |
|---|---|---|
| $1.6M／月・4,500人 | 現行公式の全体分配額とcommunity developers | 同じ母集団の有料開発者数か不明。中央値・黒字割合・個人の期待値は算出不可 |
| $563k／September | 2025-11-12公開の企業紹介記事にある9月分 | 文脈上2025年9月と読むのが妥当。2026年9月分とするのは不一致。[企業寄稿ページ](https://www.wearedevelopers.com/companies/4035-apify/stories/2366-the-apify-1m-challenge) |
| 80% | 標準の開発者分配率 | `0.8 × 利用者料金 − platform usage costs`。`0.8 × (料金−費用)`ではない。特別割引・返金等は別条件。[2026-09-15改定規約](https://docs.apify.com/legal/store-publishing-terms-and-conditions) |

例：利用者料金$100・使用費$20なら標準式は$60であり$64ではない。これは規約式の説明用計算で、収益予測ではない。

同規約は利用者の問題への14日以内の対応、Apifyからの直接依頼への3営業日以内の応答を要求する。自動稼働できてもサポート責任は消えない。最低支払額は規約のPayPal $20／その他$100に対し、[支払ヘルプ](https://docs.apify.com/actors/publishing/monetize/monthly-payouts)はWiseも$20としており、**文書間の不一致が未解消**。利用する送金方法について登録時に確認する。

[旧レンタル料金の公式説明](https://docs.apify.com/actors/publishing/monetize/rental)は2026-04-01の新規停止と10-01の移行を示す。Day1より前の変更なので旧料金モデルで採算を置かない。

### 6. x402：異なる出来高を一本の成長曲線にしない

| 資料 | 期間・対象・定義 | 判定 |
|---|---|---|
| S3の約$28k／日・半分人工 | 3月の二次紹介。調整手法・チェーン・期間の一次再現なし | [二次][未検証]。現在値として採用しない |
| B11の731k→57k tx／日、調整後$14k／日 | 記事公開は2026-04-02。12月から3月という過去比較 | 添付の9月25日は不一致。$14k×365=$5.11Mで同記事の年$600Mと定義が合わない。どちらも新しい実勢推計には不採用。[二次記事](https://blockchain.news/news/okx-ventures-ai-agent-economy-x402-transactions-drop-92-percent) |
| D08の310万tx・$1.2M | 5月29日記事のBase・30日窓という主張 | 一次未確認。全チェーン・年間額と比較しない |
| D12の176M tx・$73M | 年間／累計の境界と原集計未確定 | 平均単価にも不一致。真性比率0.6〜7.5%は[未検証] |
| 2026-07-14論文 | Baseの280日、136,708,672 settlements、$44,121,383.81 | 21.20% fictitious、63.78%内部関連クラスターと分類。独立価値の下限$187,861.35、名前の付いたサービスへの帰属上限$20,258,746.09。上限は全て真正な購買だという意味ではない。[一次論文](https://arxiv.org/abs/2607.12575) |

論文の「取引分類」「サービスへの価値帰属」と、TRMの「AIエージェント由来」は別概念。割合を掛け合わせたり足したりしない。今回得られた一次分析の中では7月論文が新しいが、9月27日時点の日次の独立購買額は **?（未確認）**。次に必要なのはtx hashだけでなく、売手・買手の関連性、商品、納品、返金、観測期間を結んだデータである。

## B2　自律エージェントはどこまで運営できるか

### 研究の射程

反証：フリーランス納品の成功率、コーディング課題の人間所要時間、模擬自販機の期末残高は、いずれも「90日間の実事業を無監督で維持できる確率」ではない。特にRLIは対人調整や長期SEO等を含む商売全体を測っていない。

支持：タスクを限定し、状態を保存し、金額・権限・再試行を外側のコードで制限すると、実行の継続性と成績は改善する。改善策は単にモデルを大型化することではなく、判定と支出をモデル自身から分離すること。

| 研究・日付 | 確認した到達点 | 外挿できないこと |
|---|---|---|
| [RLI原論文](https://arxiv.org/abs/2510.26787)、2025-10／[7月更新](https://safe.ai/blog/significant-increase-in-digital-labor-automation)／[現行榜](https://labs.scale.com/leaderboard/rli) | 初期2.5%から改善。7月Fable 5 15.8%、取得時点GPT-6 Astra 20.83%、Fable 5.1 17.92% | 案件完了率≠利益達成率。榜に出ない信頼区間・将来成績は不明 |
| [METR time horizons](https://metr.org/time-horizons/)／[2026-03-20補足](https://metr.org/notes/2026-03-20-impact-of-modelling-assumptions-on-time-horizon-results/) | 人間熟練者の所要時間に対する50%／80%成功の指標。仮定・課題構成に依存 | AIがその時間連続して安全に稼働する意味ではない。長い領域への外挿は不確か |
| [Vending-Bench 2](https://andonlabs.com/evals/vending-bench-2)、取得時点 | 模擬1年の上位残高：GPT-6 Astra $15,514.70 ±1,074、Sol $14,427.85 ±1,051 | 実時間90日、実顧客、全原価込み利益、規約対応の実証ではない |
| [Project Vend 2](https://www.anthropic.com/research/project-vend-2)、2025-12-18 | CRM・在庫・手順による改善 | 人の購入承認・実物作業・介入が残る。値引き・約束・社会的誘導にも弱さ |
| [Magentic Marketplace](https://arxiv.org/abs/2510.25779)、2025-10／公式解説11月 | 市場の順序・速度バイアス、攻撃、選択肢拡大の問題 | 2026年最上位モデルすべての定量成績ではない |
| [x402安全性研究](https://arxiv.org/abs/2607.19545)、2026-07-21 | 15 facilitatorsに仕様上の違反を報告。約119M取引を調査 | 発見済み・修復対応された脆弱性を全て現行未修復とは言えない |
| [x402決済の安全性分析](https://arxiv.org/abs/2605.30998)、2026-05-29／[長期エージェント研究の整理](https://arxiv.org/abs/2608.06663)、2026-08 | 支払いと提供の整合、長期評価の不足が研究対象 | 決済プロトコル導入だけで安全性・長期自律性が得られるわけではない |

以下の「不可」は技術的に永久に不可能という意味ではなく、**90日無監督で安定稼働する前提を置ける証拠がない**という運用判定。「条件付き」も90日実証済みではなく、狭い処理を決定的なソフトウェアで囲った場合の設計可能性を示す。本件L3は異常対応を許すので、無監督の研究質問より弱い条件で別途検証できる。

| 業務類型 | 90日無監督 | 根拠 | 典型的失敗 | 必要な足場 |
|---|---|---|---|---|
| 仕入れ・価格設定 | 条件付き：既知の商品・価格幅のみ | Vend、Vending-Bench、Magentic | 不採算値引き、不要購入、最初の提案への偏り | 原価割れ禁止、取引先許可リスト、金額・回数上限、価格変更履歴 |
| 顧客対応 | 不可：任意交渉を含む全面委任 | Vend、RLI | 返金や納期の無権限約束、個人情報露出 | FAQ範囲限定、残高・権限検査、返金上限、例外キュー |
| 営業・集客 | 不可：新規需要発見を含む全面委任 | B02、B04、Magentic | 到達不良、見込み違い、活動数だけ増加、規約違反 | 同意済み接点、同一ファネル計測、停止条件、戦略変更の範囲 |
| 文章制作 | 条件付き：定型・検証可能な入力 | RLI、METR | 引用捏造、事実誤り、誤解を招く効能 | 出典制約、数値照合、禁止事項検査、抽出処理優先 |
| コード制作 | 条件付き：小変更・隔離環境 | RLI、METR | テストを通すだけの修正、秘密漏えい、回帰 | 要件に独立したテスト、段階公開、ロールバック、権限制限 |
| 画像制作 | 条件付き：低リスク・仕様固定 | 90日直接実証なし | 権利侵害、品質むら、販売先の開示不足 | 素材の利用許諾、類似性レビュー経路、サイズ等機械検査 |
| データ制作・更新 | 条件付き：利用権と形式固定 | Apify実行基盤は存在。90日成功率は不明 | 元サイト変更、欠損、重複、禁止収集 | スキーマ検査、鮮度監視、差分比較、データ取得権限の記録 |
| 品質判定 | 不可：LLM自己採点だけの場合 | RLI評価差 | 自分の誤りを承認、もっともらしい偽合格 | 正解データ、独立検証器、抜取レビュー。不確かなら公開停止 |
| 決済・会計照合 | 条件付き：決定的照合を中心にする | 決済API、B04 | 二重計上、未入金を売上扱い、返金漏れ | webhook署名、冪等ID、残高・注文・入金の照合、不一致停止 |
| 障害検知 | 条件付き：外部監視を持つ | B04、長期評価の限界 | 壊れた経路を自己申告で正常扱い | 購入から納品までの試験、別系統アラート、heartbeat、復旧手順 |
| 規約遵守 | 不可：変更解釈まで無監督 | B3の規約変更・差異 | 旧規約継続、出品禁止、KYC再要求見落とし | 差分通知、変更時停止、人による解釈・異議申立て |
| 支出管理 | 条件付き：外側の強制上限 | B10の具体額は未検証、x402安全性研究 | 再試行ループ、並列実行、ウォレット補充の暴走 | APIゲートウェイ上限、日次予算、再試行制限、自動補充禁止 |
| 取引の真性判定 | 不可：出来高からの自動推定 | x402 7月論文 | 自己取引・関連口座を需要と誤認 | 関連者除外、商品納品照合、独立顧客数、実入金・返金確認 |

## B3　販路の条件表

全行の取得日：2026-09-27。料金は通常条件の要点で、為替・税・追加機能・返金等を全て含む見積りではない。「日本利用可」と「個別商品の審査通過」「希望送金方法が使える」は別。APIがあってもアカウント開設・審査・紛争処理まで自動化できるとは限らない。

### 1. 料金・入金・日本居住者の条件

| 販路 | 手数料・支払条件 | 日本／必要な初期手続き・書類 |
|---|---|---|
| Apify | 標準80%−計算費。月次支払、最低額に規約とヘルプの差あり | 身元・住所・税情報のKYC、送金登録。日本向け個別送金方法は登録時確認。[規約](https://docs.apify.com/legal/store-publishing-terms-and-conditions) |
| MCP Marketplace | 15%手数料、85%開発者、Connect Express | 日本出品者対応?。Stripeの日本対応だけでは確定しない。本人・住所・税情報。[規約](https://mcp-marketplace.io/terms)・[プライバシー](https://mcp-marketplace.io/privacy) |
| x402 API | プロトコル自体の固定手数料なし。ネットワーク・facilitator・換金費は別 | 自前APIは実装可能。ウォレット・受取資産・日本での換金資格は別途。一般的な入金保証なし。[公式](https://x402.org/) |
| ChatGPTアプリ／plugins | 一般のデジタル商品販売経路として使えない。対象物理商品は外部checkout | 公開審査・ドメイン・プライバシー情報等。収益分配・日本個人向け支払契約は?。[収益化](https://developers.openai.com/plugins/build/monetization) |
| Claudeコネクタ／plugins | ディレクトリのネイティブ有料販売・還元率は? | 提出・安全性審査。外部サービスのアカウント条件は別。[ディレクトリFAQ](https://support.claude.com/en/articles/11596036-anthropic-connectors-directory-faq) |
| Chromeウェブストア | 開発者登録に一回の手数料。金額は本調査で?。ストア決済は廃止、外部決済 | Google開発者登録・プライバシー・必要な本人情報。日本個人の支払経路は外部決済側確認。[登録](https://developer.chrome.com/docs/webstore/register)・[決済廃止](https://github.com/GoogleChrome/developer.chrome.com/blob/main/site/en/docs/webstore/cws-payments-deprecation/index.md) |
| BOOTH | 2025-10-28から5.6%＋45円。銀行振込手数料別。原則翌月20日から5営業日内 | 国内銀行登録等で利用可。法定表示を別途確認。[料金改定](https://booth.pm/announcements/832)・[ガイド](https://booth.pm/guide) |
| note | 通常の有料記事は決済手数料控除後に10%。カード5%なら合計14.5%。振込等別 | 国内銀行・売上受取登録。商品形態・支払方法で異なる。[公式手数料](https://www.help-note.com/hc/ja/articles/360011358873) |
| Gumroad | 直接販売10%＋$0.50、Discover30%。決済処理追加費の適用は確認要。最低7日保留・審査あり | 日本の現行送金方法を一次本文で確定できず?。本人・税務・銀行等の登録が必要。[料金](https://gumroad.com/pricing)・[詳細](https://gumroad.com/help/article/66-gumroads-fees)・[残高](https://gumroad.com/help/article/269-balance-page) |
| Etsy | 出品$0.20＋取引6.5%＋日本決済6%＋$0.30。初期設定・広告・為替等別 | 日本はPayoneer経由の登録。ID・住所・口座・税情報等。[基本料金](https://help.etsy.com/hc/en-us/articles/115014483627-What-are-the-Fees-and-Taxes-for-Selling-on-Etsy)・[国別処理料](https://help.etsy.com/hc/en-gb/articles/115015628847-What-are-Payment-Processing-Fees-for-Selling-on-Etsy) |
| KDP | 電子書籍35%／70%等。日本の70%はSelect等の条件あり。月末から約60日後支払 | 日本利用可。本人・銀行・税務インタビュー。[ロイヤリティ](https://kdp.amazon.com/en_US/help/topic/G200634500)・[支払](https://kdp.amazon.com/en_US/help/topic/G202173620) |
| ココナラ | 通常22%、ビデオチャット27.5%。入金等は方式別 | 国内本人確認・銀行等。商品別の出品資格確認。[公式料金](https://coconala.com/pages/about_option) |
| Stripe直販 | 国内カード標準3.6%。Billing・国外・為替等は追加条件 | 日本利用可。事業者・本人・銀行・サイト表示の審査。[日本料金](https://stripe.com/jp/pricing) |
| Cloudflare Pay per use | 2026-07-01時点の実験。一般販売者の固定手数料・支払日は? | 参加申込み制。日本個人の参加・受取資格?。[公式発表](https://blog.cloudflare.com/making-ai-search-smarter/) |
| AWS CloudFront x402 | WAF／CloudFront等のインフラ費＋決済側費用。売上分配型ストアではない | AWS契約・請求・ウォレット等。日本での資産受取・換金は別確認。[公式発表](https://aws.amazon.com/about-aws/whats-new/2026/06/aws-waf-ai-traffic-monetization/) |
| Agentverse | ホスティングの料金・枠はあるが販売還元・出金条件は? | アカウント・SDK。日本の販売者向けKYC・出金は?。[概要](https://docs.agentverse.ai/v-1/documentation/getting-started/overview)・[利用枠](https://docs.agentverse.ai/v-1/documentation/advanced-usages/agentverse-subscriptions-and-quotas) |

### 2. AIポリシー・執行・需要の証拠・API

| 販路 | AI・規約の日付 | 直近12か月の執行確認 | 既存買い手の証拠 | 自動化API |
|---|---|---|---|---|
| Apify | 2026-09-15規約。データ取得の適法性・保守義務・決済経路制限 | レンタル終了は制度変更。個別停止未確認 | 公式月$1.6M分配。特定用途の需要は別 | 実行・公開・データAPIあり |
| MCP Marketplace | 規約2026-02-24、最新版未確認。AI専用の許諾範囲は? | 個別執行未確認 | 集計売上なし。確認した一商品は0 installs／0 reviews | MCPは可、出品・精算APIは? |
| x402 | 仕様と販売者自身の規約。統一AI生成物ポリシーはない | 7月論文は脆弱性報告で、販路停止処分ではない | 送金は存在するが独立購入の切分けが必要 | HTTP402・SDK・discoveryあり |
| ChatGPT | 現行、改定日不記載。デジタル商品・サービス・クレジット販売は直接／間接とも禁止対象 | 個別執行未確認 | 利用者数はこの商品の有料需要ではない | Apps SDK／MCP。公開・審査は別 |
| Claude | 2026-09-25 plugins提出案内。コネクタ審査継続 | 個別執行未確認 | ディレクトリ収益ランキング未確認 | Remote MCP等あり |
| Chrome | 現行開発者ポリシーの日付・AI専用変更は? | 個別執行未確認 | インストール・レビューは観測可、有料比率は別 | Web Store publish APIあり |
| BOOTH | ガイドライン2026-07-08。権利侵害・高負荷等制限。AI全面禁止ではない | AI類似作品対策の公式告知は2025-07-18で期間外 | 商品・購入レビューはあるが対象カテゴリ販売数? | 公開された販売・出品APIを未確認 |
| note | 今回参照できた規約は旧版を含み最新版未確認。AI一律開示の現行規則は? | 個別執行未確認 | A20の4販売はD・自己申告。カテゴリ全体へ外挿不可 | 公式の投稿・販売API未確認 |
| Gumroad | **2026-09-16改定。AIツール、チャットボット、生成機能へのアクセス等のAI servicesが禁止対象** | この改定は確認。特定店舗への執行未確認 | 一般の販売基盤があることと、禁止対象を販売可能なことは別 | APIあり。出品から審査までの完全自動化は未確認 |
| Etsy | Seller Policy 2026-07-09。独自プロンプトによるAI作品は開示条件で可、AIプロンプト束は不可 | 2025年透明性報告あり。今回対象に対応する個別処分未確認 | レビュー等あり。対象商品の購入母数は未抽出 | OAuth API、digital listing/file uploadあり |
| KDP | 現行、改定日不記載。AI生成は申告、AI補助のみは不要。形式別週10タイトル | 作成上限は現行ルール。個別停止未確認 | 書籍購入市場はあるが対象ジャンルの部数? | 一般公開の出版アップロードAPI未確認 |
| ココナラ | 2026年5月の公式告知でAIイラストの禁止方針を再説明 | 現行禁止告知あり。2025年6〜7月の削除措置は対象期間外 | 販売件数表示は個別に観測可。対象群集計? | 公開出品・受注API未確認 |
| Stripe | AI固有の一律禁止ではなく事業審査。個別AI業種の現行条件は要確認 | 対象業種の個別執行未確認 | 決済基盤であり集客市場ではない | 決済・subscription・webhook・照合APIあり |
| Cloudflare | 2026-07-01 Pay per use実験 | 9月15日から特定クローラ遮断という添付の条件は確認不能 | Ceramic／Youの実験参加は確認、一般の有料需要量? | 一般提供範囲・精算API? |
| AWS | 2026-06-15 WAFのAI traffic monetization発表 | 個別執行未確認 | 導入発表はGMVを示さない | CloudFront／WAF設定とx402 |
| Agentverse | 現行概要は将来のmonetizationに言及。更新日不記載 | 個別執行未確認 | B05は本人売上ゼロ。発見・接触と課金は別 | エージェントSDK／通信API |

政策出典：[OpenAI審査指針](https://developers.openai.com/plugins/app-guidelines)、[Claude提出案内](https://claude.com/blog/build-plugins-for-claude)、[Claude directory policy](https://support.anthropic.com/en/articles/11697096-anthropic-mcp-directory-policy)、[Chrome API](https://developer.chrome.com/docs/webstore/api/reference/rest)、[BOOTHガイドライン](https://booth.pm/guidelines)、[BOOTH過去告知](https://booth.pm/announcements/828)、[note参照規約](https://terms.help-note.com/hc/ja/articles/44943817565465/)、[Gumroad禁止商品](https://gumroad.com/prohibited)、[Etsy創作基準](https://www.etsy.com/legal/creativity/)、[Etsy seller policy](https://www.etsy.com/legal/sellers/)、[Etsy API](https://developers.etsy.com/documentation/)、[KDP生成AI](https://kdp.amazon.com/en_US/help/topic/G200672390)、[KDP作成上限](https://kdp.amazon.com/en_US/help/topic/G202172740)、[ココナラ告知](https://coconala.com/news/1331)。

**実装上の追加条件：** ChatGPTでは既存の有料アカウントへのログインは許容されるが、それをデジタル商品の購入・アップグレード誘導と混同しない。GumroadのAIサービス制限から、静的なAI補助制作ファイルすべてが禁止とまでは読めない。商品形態を規約に照らす。

Apify公式x402は実験機能で、USDC前払いトークン方式。対象はPPE・usage課金なし・限定権限・Standbyなし・開発者KYC済みのActor。全Actorが対応するわけではない。最少$1、残高が支出上限、14日失効・残額返金なしという現行条件がある。公式経路と独自の外部決済回避を混同しない。[Apify x402公式](https://docs.apify.com/integrations/x402)

**入金と利益は別台帳にする。** KDP等の入金遅延があっても発生売上は記録できるが、返金・未払い調整と運転資金が必要。成功判定の純収益と、実際の銀行入金の両方を保存する。

## B4　日本の法務・税務チェックリスト

取得日：2026-09-27。以下は適用条件の整理であり、本人の所得状況・居住自治体・商品を確認した個別判断ではない。国税庁の一部ページは2026-04-01法令基準であり、その後の個別改正まで網羅した保証はしない。

| 項目 | 要件・例外 | 該当類型 | Day0の人の初期作業／運用中に残る作業 | 一次出典 |
|---|---|---|---|---|
| 所得区分 | 事業所得か雑所得かは社会通念・活動実態・記帳等で判断。売上300万円等を自動的な境界にしない | 全て | 記帳方法・証憑保存を決める／実際の収支・継続性で判断 | [国税庁35-2](https://www.nta.go.jp/law/tsutatsu/kihon/shotoku/04/09.htm) |
| 所得税20万円 | 給与1か所等の所定条件下で、給与・退職以外の所得が20万円以下なら申告不要の場合。売上ではなく所得。免税制度ではない。他の理由で申告する場合は含める | 給与所得者の副業 | 給与・源泉・年末調整条件確認／年度終了後に申告要否と全所得確認 | [国税庁1900](https://www.nta.go.jp/taxes/shiraberu/taxanswer/shotoku/1900.htm)・[Q&A](https://www.nta.go.jp/taxes/shiraberu/taxanswer/shotoku/1900_qa.htm) |
| 住民税 | 所得税の20万円特例と別。所得税申告をしない場合も自治体申告が必要になり得る | 全て | 居住自治体の案内確認／翌年申告 | [横浜市の公式説明例](https://www.city.yokohama.lg.jp/kurashi/koseki-zei-hoken/zeikin/faq/answer2.html)。本人の自治体は未確認 |
| インボイス | 登録は任意。登録すると免税事業者でも課税事業者となり申告等が必要。取引先の要請と法的必須を分ける | 主に国内B2B | 登録の要否・消費税負担を判断／請求書・申告・保存を継続 | [国税庁](https://www.nta.go.jp/taxes/shiraberu/zeimokubetsu/shohi/keigenzeiritsu/invoice_kakutei.htm) |
| 特商法 | 通信販売の価格、費用、支払時期、提供時期、返品条件、事業者情報等。氏名・住所・電話等の一部は、請求時に遅滞なく提供する旨と実際の提供体制等の条件を満たす場合に省略可能 | デジタル商品・API・サブスク等の通信販売 | 法定表示・最終確認画面・開示窓口設定／請求対応・表示更新。プラットフォーム利用だけで免除されない | [消費者庁通信販売](https://www.no-trouble.caa.go.jp/what/mailorder/)・[広告表示](https://www.no-trouble.caa.go.jp/what/mailorder/advertising.php) |
| ステルスマーケティング | 広告主が関与した表示を一般消費者が広告と判別できること。AI作成かどうかとは別問題 | SNS宣伝、紹介依頼、レビュー利用 | 広告表示ルール・委託条件設定／各投稿を守る | [消費者庁FAQ](https://www.caa.go.jp/policies/policy/representation/fair_labeling/faq/stealth_marketing/) |
| 営業メール | 原則同意、送信者表示、拒否後停止。取引関係や公開事業用アドレス等の法定例外は条件付き。例外と自由な大量送信は同義でない | メールによる勧誘 | 同意・拒否記録と配信停止設定／実送信の同意照合。今回の除外条件は法定例外より厳しく維持 | [消費者庁](https://www.caa.go.jp/policies/policy/consumer_transaction/specifed_email/)・[ガイドライン](https://www.caa.go.jp/policies/policy/consumer_transaction/specifed_email/pdf/090901email_1.pdf) |
| AIと著作権 | 生成物の著作物性と他者の権利侵害は別。人の創作的寄与、既存作品への依拠性・類似性等を個別検討。学習段階の例外を販売の全面許諾にしない | 文章・画像・コード・データ | 利用素材・モデル条件・来歴保存／公開前の権利確認を継続 | [文化庁整理](https://www.bunka.go.jp/seisaku/chosakuken/aiandcopyright.html)、基礎資料は2024年、最新版未確認 |
| 個人情報 | 利用目的、安全管理、委託先管理、第三者提供・国外移転等の条件。小規模事業も対象。医療等の要配慮個人情報は特に条件確認 | CS、予約、領収書、顧客データ | 利用目的・委託先・保存期間・削除方法設定／漏えい対応、目的外入力防止 | [個人情報保護委員会ガイドライン](https://www.ppc.go.jp/personalinfo/legal/guidelines_tsusoku/)・[生成AI注意喚起](https://www.ppc.go.jp/news/careful_information/230602_AI_utilize_alert/) |
| 暗号資産・電子決済手段 | サービスの対価と受取資産の後の損益を分けて記録。USDC等は法的区分・取扱条件を個別確認。ステーブルコインだから無課税ではない | x402等 | 受取手段・JPY評価方法・証憑設計／受取・交換・費用の記録。自分の代金受取と他人の資産交換・保管事業は別 | [国税庁FAQ掲載ページ](https://www.nta.go.jp/publication/pamph/shotoku/kakuteishinkokukankei/kasoutuka/)・[金融庁](https://www.fsa.go.jp/policy/virtual_currency/) |
| 海外税務書類 | 個人のW-8BENは外国人資格等を支払者に示すもの。法人用と区別。条約軽減は所得種類等で異なり、提出で日本の税務が終わるわけではない | KDP等の国外支払者 | 氏名・住所・TIN・必要な条約情報を正確に登録／変更・更新、源泉と日本所得を照合 | [IRS W-8BEN](https://www.irs.gov/instructions/iw8ben)、2021年版・最新版未確認／[条約申請](https://www.irs.gov/individuals/international-taxpayers/claiming-tax-treaty-benefits) |
| 就業規則・守秘 | 副業規定、労務提供への支障、秘密、競業等を確認 | 全て | 勤務先規定・届出確認／本業データ・顧客・資産を使わない | [厚労省副業・兼業](https://www.mhlw.go.jp/stf/seisakunitsuite/bunya/0000192188.html) |

**Day0例外の修正が必要な一点：** 90日は2026年と2027年をまたぐ。将来の所得に関する確定申告そのものはDay0に済ませられない。Day0にできるのは記帳・申告環境の準備。申告実務を人手上限から除くという管理上の扱いは可能でも、作業が消えるわけではない。顧客対応・権利確認・規約変更への判断・通常の会計照合をこの例外に移さない。

## B5　需要の定量化：指定の4クラスター

### 1. 支払意思を再分類する

反証：添付の引用を「払うと言っている人と価格」にまとめるのは不正確。C04の$20は避けたい損失、C14の月18万円は外注したと仮定した人件費、C16の5,000円は売手の提示価格である。C22は求人条件であり、無監督ソフトへの予算ではない。

| シグナル | 分類 | 今回利用できる範囲 |
|---|---|---|
| C02「払いたい」経理機能 | 金額なしの表明 | 引用の本人原典を独立取得できず[未検証]。購入・価格受容には昇格しない |
| C04「$20を浪費したくない」 | 損失回避の不満 | [未検証]の引用。$20／月の支払意思ではない |
| C14「外注なら月18万円」 | 売手等の反実仮想の費用換算 | 実際の予算・購入額ではない |
| C16 freee 5,000円 | 公式の売手価格 | 実在商品の供給・値付けの証拠。購入者数不明 |
| C22 月28〜80万円・40〜80h | 人への業務委託募集 | 原ページの本文・継続性を確認できず[未検証]。自律APIのTAMに使わない。[指定案件](https://shuuumatu-worker.jp/projects/18912) |
| C06／07／09 | 既存契約内の利用要望・重複課金への不満・市場観察 | 別料金の支払意思とは限らない。原引用は[未検証] |
| D01〜05、D07 | 主に売手の提供開始・価格提示 | 商品があることと、独立した有料顧客があることを分ける |

### 2. 観測できた代理指標

以下の競合数は調査で観測した下限であり市場全体の数ではない。検索ボリューム、有料顧客数、国内の到達可能市場は4群とも **?（未確認）**。販売レビューを購入者数へ換算する係数もないため、TAM金額は推定しない。

| クラスター | 観測した供給・価格 | 観測した需要代理 | 言えること／言えないこと |
|---|---|---|---|
| 支出上限・承認・監査 | 関連領域で少なくとも2社。Langfuse Core $29／月、Helicone Pro $79／月。無料枠・従量・機能差あり | 公式価格公開。今回有料顧客・レビューの独立数は未取得 | 関連ソフトの価格帯は存在。純粋な強制支出上限だけに$29〜79払う市場だとは言えない。[Langfuse](https://langfuse.com/pricing)・[Helicone](https://www.helicone.ai/pricing) |
| 経理オペ | 少なくともfreee Agent HubとDext。freeeは税別5,000円／ID・月、同額利用枠と超過課金。Dextは今回比較可能な固定価格を得られず | 公式提供条件。対象機能の契約数不明 | 既存サービスの供給を確認。税務判断まで無監督代行できる証拠ではない。[freee規約](https://www.freee.co.jp/terms/agent-hub/)・[Dext](https://dext.com/en/partner/pricing) |
| 店舗・医療・ECの問い合わせ | 少なくともIntercom Fin $0.99／outcome、Tidio Lyro月$39から。基本席料・会話枠・追加費は別 | Shopify Tidio掲載に1,343レビュー、評価4.8の取得時スナップショット | ECの関連製品への利用反応はある。レビュー数≠有料契約数、医療需要へ転用不可。[Intercom](https://www.intercom.com/pricing)・[Tidio掲載](https://apps.shopify.com/tidio-chat) |
| 有料MCP・API従量 | 少なくともExaとTavily。Exa検索$7／1,000 requests、Tavily従量$0.008／credit。リクエスト当たりcreditは処理別 | MCP Marketplaceの確認したStripe Analytics商品は0 installs・0 reviews。全体ゼロではない | APIの課金単位は存在する。MCP化・自律購入の追加需要は未確定。[Exa](https://exa.ai/pricing)・[Tavily](https://help.tavily.com/articles/8816424538-pricing)・[確認商品](https://mcp-marketplace.io/server/io-github-lordbasilaiassistant-sudo-stripe-analytics) |

追加の販売価格例としてCoinbase SQL APIにはx402の$0.10／queryがある。これも購入件数や市場規模ではない。[Coinbase公式](https://www.coinbase.com/es-mx/developer-platform/discover/launches/sql-api-x402)

### 3. 推定式と、現時点で埋められない変数

同一の期間・流入元・顧客コホートについて、対象訪問者数をV、試用者をT、有料顧客をNとする。

`有料顧客数 = V × (T/V) × (N/T)`

これは観測値の分解であり、別サイトのCVRを持ってくる推定ではない。将来に使う場合は同じ流入・価格・商品・観測期間が維持される仮定と不確実性が必要。今はV、T、Nがないため4群とも推定顧客数は未算出。

単価p、比例手数料f、1取引当たり変動費c、判定窓の固定費Fなら：

`必要課金件数 = max(10, ceil((10,000 + F) / (p × (1−f) − c)))`

分母が0以下ならこの式で黒字化しない。固定額手数料はcに入れる。顧客集中条件は別判定であり、30%以下には少なくとも4顧客が必要だが、4顧客いるだけでは十分ではない。10件の課金を同じ客の自動小分けで作っても需要分散の証拠にはしない。

計算例のみ：p=1,500円、f=3.6%、c=100円、F=3,000円と仮置きすると、1件限界利益1,346円、10件で純収益10,460円。3.6%以外は設計上の仮定であり、需要予測でも候補推薦でもない。返金・広告・追加SaaS・為替費があれば再計算する。

人手は `週の人手 = 通常保守＋制作編集＋承認＋顧客対応＋障害対応＋レビュー` として実測する。売上条件を満たしても、通常週30分を超えるならL3ではない。

## PoCへ引き継ぐ測定条件

| 項目 | 固定すべき条件 |
|---|---|
| 日程 | Day1 2026-10-05、Day14 10-18、Day31〜60 11-04〜12-03、Day61〜90 12-04〜2027-01-02 |
| 成功 | 最終30日純収益1万円以上、前30日黒字、課金10件以上、単一顧客30%以下、最終窓平均週5h以下、Day90 L3以上。知人・本業由来は除外 |
| 純収益 | 指定の売上−手数料−事業費を維持。月額SaaSも落とさず、事前払費の配賦ルールを先に固定。税引後所得や人件費控除後利益とは別 |
| 現金予算 | 増分支出月3万円・90日9万円。暦月か30日窓かを開始前に決める。年またぎで暦月4か月になっても総額9万円は不変 |
| 通貨 | 各取引・費用を採用した為替基準とともに円記録。異なる日のUSD売上とJPY費用を固定レートで安易に合算しない |
| 需要 | Day14の「払う意思」は参考信号。実購入と同列にしない。訪問・試用・支払・返金を同じコホートで記録 |
| 障害 | 認証期限、購入試験、納品到達、決済実数、日次費用、支出上限を外部から確認。沈黙を正常扱いしない |
| 自律性 | 手動承認・再プロンプト・営業・保守を分単位で記録。毎回承認ならL1、週次承認ならL2 |

## 未解決事項と、次に得るべき証拠

1. 個人の独立注文・純利益・人手が揃う90日記録は未確認。選定前の追加読書より、選定後の台帳設計と実購入の観測で埋める情報である。
2. MCP Marketplaceの日本受入れ、ApifyのWise最低額、Gumroadの日本向け送金経路は未確定。採用する販路だけ、申込画面または公式サポート回答で解消する。
3. x402の9月現在の独立購買額は未確認。総送金額をTAMに使わず、自分の商品への第三者支払を測る。
4. 4つの需要群の検索量・有料顧客総数は未確認。競合価格・レビューを市場規模へ膨らませず、同一ファネルの有料転換を測る。
5. 多くの販路で直近の個別執行事例を確認できていない。安全という結論にせず、該当する商品規則と異議申立て・停止時の運用を確認する。

本調査では登録・出品・送信・課金・実際のPoCは実行していない。提出された証拠の監査と条件整理を行ったものであり、事業候補を選んだものではない。
