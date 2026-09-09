# Project Context

## 1. What this project is
「仕事みえる化」は、実際の仕事で発生した証跡を安全に記録し、WorkTraceとして時系列化し、案件・仕事・依頼との関連付け、本人による確認・訂正、Fact / Analysis / Knowledge / Capability Hypothesis への段階的な変換を可能にする基盤。

目的は単純な工数管理や常時監視、人事評価用の単一スコアではない。

## 2. Core philosophy
- Observed / Reported と Derived / Analysis を分離する。
- 推定結果を観測事実へ逆流させない。
- 関連付けに確信がなければ UNASSIGNED を選ぶ。
- provisional と confirmed を分離する。
- 訂正しても元のpredictionと証拠参照を破壊しない。
- Knowledgeのvalidated化には人間承認を要求する。
- Capabilityは能力の断定ではなく、条件付き仮説。
- 機密区分を派生処理で緩和しない。
- 実データがない場合、実運用性能を捏造しない。

## 3. Main data flow
```text
SourceConnector
  -> SourceEvent
  -> Evidence
  -> WorkTrace
  -> Association
  -> margin gate
  -> PROVISIONAL / UNASSIGNED
  -> human confirmation / correction
  -> Fact
  -> Analysis
  -> Knowledge(candidate)
  -> human approval
  -> Knowledge lifecycle
  -> CapabilityHypothesis
```

## 4. Repository map
- `src/domain/` — ドメインモデル、validation、security、assignment、timeline、knowledge lifecycle、capability
- `src/association/` — candidate生成、score、margin gate
- `src/ingestion/` — SourceEvent、connector protocol、Evidence/Trace変換、pipeline
- `src/storage/` — SQLite persistence、DomainStore
- `src/experiment/` — 実データ評価用metrics
- `src/presentation/` — UI要件・設計メモ
- `tests/` — regression / contract tests
- `docs/` — 引き継ぎ、設計判断、レビュー、作業記録
- `.github/workflows/` — CI

## 5. Trust boundaries
### Observed
実際に取得・報告された情報。Predictionを混ぜない。

### Derived
Association score、candidate、Analysisなどの計算・推論結果。観測事実と同格に扱わない。

### Human-confirmed
本人または権限を持つ人間が確認・訂正した状態。Knowledge validated化もここに属する。

### External validation required
認証済み実サービスconnector、実仕事データによる精度・校正・訂正負担、UI usabilityはコードとfixtureだけでは証明できない。

## 6. Current status
技術基盤は強化済みだが、実運用製品として完成とは宣言しない。

最新確認済みCI: 63 passed / 1 failed。失敗はconnector API (`pull` / `collect`) の不一致。

最新厳格レビュー: 72/100。

## 7. First actions for a new maintainer
1. READMEを読む。
2. `docs/WORK_LOG.md` を読む。
3. `docs/DECISIONS.md` と `docs/REVIEW_HISTORY.md` を読む。
4. `docs/ARCHITECTURE.md` と `docs/DOMAIN_MODEL.md` を読む。
5. 最新CIを確認する。
6. 失敗テストを再現してから実装を変更する。
7. 変更→テスト→CI→作業ログ更新の順で記録する。

## 8. Never assume
- association scoreは確率ではない。
- fixtureのaccuracyは実運用accuracyではない。
- CI greenは実世界有効性の証明ではない。
- connector protocolが存在することは、実サービス認証・取得が完了したことを意味しない。
- CapabilityHypothesisは人の能力評価ではない。
