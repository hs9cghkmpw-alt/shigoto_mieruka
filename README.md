# 仕事みえる化 / Work Memory / Work Trace

## 目的
実際の仕事で発生する証跡を安全にWorkTrace化し、仕事・環境・支援条件と結果を実データから振り返れる基盤を作る。

単純な工数管理、常時監視、単一スコアによる人事評価を目的としない。

## 引き継ぎ・設計ドキュメント
新しい担当者は以下を上から順に読むこと。

1. [`docs/HANDOVER.md`](docs/HANDOVER.md) — 開発再開手順・報告ルール
2. [`docs/PROJECT_CONTEXT.md`](docs/PROJECT_CONTEXT.md) — プロジェクト全体の前提
3. [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) — アーキテクチャとデータフロー
4. [`docs/DOMAIN_MODEL.md`](docs/DOMAIN_MODEL.md) — ドメインモデル・状態・境界
5. [`docs/DECISIONS.md`](docs/DECISIONS.md) — 設計判断と理由
6. [`docs/REVIEW_HISTORY.md`](docs/REVIEW_HISTORY.md) — 厳格レビューと既知の問題
7. [`docs/WORK_LOG.md`](docs/WORK_LOG.md) — 作業・レビュー・引き継ぎログ
8. [`docs/ROADMAP.md`](docs/ROADMAP.md) — 実装優先順位

## 目的と現在地
**技術基盤: 強化済み。** ただし、**実運用製品の完成を100%とは宣言しない**。実サービス接続・実仕事データ・UI実証が必要だからである。

実装済み:
- WorkItem / WorkTrace / EvidenceRef / Fact / Analysis / Knowledge / CapabilityHypothesis
- OBSERVED / REPORTED のprovenance分離
- source ID・観測時刻・取得時刻・content hash・extractor versionによるlineage
- raw source contentをSQLiteへ保存しないEvidence保持とhash検証
- Evidence lifecycle
- SourceEvent → Evidence → WorkTrace取り込み境界
- SourceConnector Protocol
- 決定論的Association Engine + margin gate
- raw association scoreとcalibrated confidenceの意味分離
- candidate evidence reference保持
- provisional / confirmed / correctionの分離
- correction audit
- canonical validation + storage boundary validation
- SQLite永続化 + repository read API + schema version
- transaction boundary
- FACT → ANALYSIS → KNOWLEDGEの人間承認ゲート
- Knowledge lifecycleとstatus history
- Analysis audit metadata
- evidence count / diversity
- 条件付きCapability Hypothesis
- 実データ評価用 coverage / selective accuracy / calibration bins
- regression tests / GitHub Actions CI

## データ経路
```text
SourceConnector → SourceEvent → Evidence → WorkTrace
 → Association(raw score) → margin gate
 → PROVISIONAL / UNASSIGNED → 人間確認・訂正
 → Fact → Analysis → Knowledge(candidate)
 → 人間承認 → Knowledge lifecycle
 → 条件付きCapability Hypothesis
```

## 不変条件
1. 推定を観測事実へ逆流させない。
2. observed / reportedを上書き統合しない。
3. raw source contentを既定SQLite保存対象にしない。
4. association scoreを確率として表示しない。校正前はuncalibrated。
5. margin不足は未分類。
6. provisionalをconfirmed factとして扱わない。
7. 訂正で元predictionを破壊しない。
8. 派生データの機密区分を緩和しない。
9. Knowledgeは人間承認なしにvalidatedへ昇格させない。
10. Capabilityは断定ではなく条件付き仮説。
11. 実データを捏造しない。
12. fixture性能を実運用性能として報告しない。
13. CI成功を実世界有効性の証明と混同しない。

## 残る実証境界
コードだけでは以下を証明できない。
- 実サービス認証済みコネクタの運用安定性
- 実仕事データでの精度・校正・訂正率・記録負担
- UIによる本人確認・訂正・レビューの実利用性

この境界を「未実装の欠陥」と「外部実証が必要な事項」に分けて扱う。実データなしで100%の性能値は出さない。
