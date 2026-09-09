# Architectural Decisions

## ADR-001 — Uncertain association must abstain
**Decision:** margin不足では`UNASSIGNED`にする。

**Reason:** 強制分類による誤帰属は、後続のFact/Analysis/Knowledgeを汚染するため。

## ADR-002 — Prediction and observation are separate
**Decision:** Association結果をObserved/Reported factへ逆流させない。

**Reason:** 推定を事実として固定すると、誤りの訂正可能性と証拠追跡性を失うため。

## ADR-003 — Human gate for validated Knowledge
**Decision:** Knowledgeはcandidateから開始し、人間承認なしにvalidatedへ昇格させない。

**Reason:** 分析結果を組織的な知識として固定する際の誤推論・誤一般化を防ぐため。

## ADR-004 — Capability is contextual
**Decision:** Capabilityは条件付き仮説として保存する。

**Reason:** 同じ仕事でも環境、支援、期限、作業種別によって結果が変わり、単一の能力値に還元できないため。

## ADR-005 — Raw source content is not persisted by default
**Decision:** Evidenceにはmetadata/hashを保持し、raw source contentは既定ではSQLiteに保存しない。

**Reason:** データ最小化と情報漏えいリスク低減のため。

## ADR-006 — Association score is not probability
**Decision:** 現在のscoreはraw scoreとして扱い、calibration前は確率表示しない。

**Reason:** 重み付きヒューリスティックから確率を名乗るには実ラベルによる校正が必要なため。

## ADR-007 — Corrections preserve prediction history
**Decision:** 人間訂正時に元predictionを破壊しない。

**Reason:** モデル/ルールの失敗分析と監査可能性を維持するため。

## ADR-008 — No real-world claims from fixtures
**Decision:** fixture、synthetic data、CI passのみから実運用精度を主張しない。

**Reason:** 実仕事データでの分布・ラベル品質・訂正負担を再現できないため。

## ADR-009 — Connector owns provider-specific retrieval
**Decision:** 認証・API固有処理はconnector境界内に置き、generic ingestion layerに埋め込まない。

**Reason:** provider差異を隔離し、テスト可能性とセキュリティ境界を維持するため。

## ADR-010 — Documentation is part of the product boundary
**Decision:** レビュー、設計判断、未解決課題、作業履歴をGitHubに残す。

**Reason:** 別担当者・別AIへの移行時に、コードだけでは設計意図と既知の限界を復元できないため。
