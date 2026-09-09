# 仕事みえる化 — 作業・レビュー・引き継ぎログ

## 目的
このファイルは、実装だけでは追えない「なぜこの設計になったか」「何をレビューし、何が残っているか」をGitHub上に残すための引き継ぎ台帳です。

対象: `hs9cghkmpw-alt/shigoto_mieruka`

## 2026-09-09 現在地
- 最新の厳格レビュー: **72/100**
- 最新確認済みCI: **63 passed / 1 failed**
- 失敗箇所: `tests/test_connectors.py::test_connector_registry_is_explicit_and_does_not_fake_provider_access`
- 原因: `ConnectorRegistry.pull()` が `collect()` を呼ぶ一方、テスト用コネクタは `pull()` を実装しており、connector API の命名が不一致。
- 次の修正: `SourceConnector` と `ConnectorRegistry` の公開APIを `pull()` に統一し、`since` の受け渡しもテストする。

## これまでの主要レビュー
### Review 1 — 初期評価
- 評価: 約55–58/100
- 主な指摘:
  - association / evidence lineage が弱い
  - CSV中心の実験で、実データ接続がない
  - Evidence→WorkTrace の実運用パイプライン不足
  - confidence の意味論が弱い
  - Knowledge lifecycle / Capability modeling / persistence / UI が不足

### Review 2 — 強化後の厳格レビュー
- 評価: **72/100**
- 改善済み:
  - Evidence hash / lifecycle
  - canonical validation
  - Association margin gate
  - raw score と calibrated confidence の分離
  - candidate evidence IDs
  - correction audit
  - SQLite persistence / read APIs
  - FACT→ANALYSIS→KNOWLEDGE の承認ゲート
  - Knowledge status history
  - CapabilityHypothesis
  - Timeline
  - CI / regression tests
- 残課題:
  1. Evidence source再ハッシュ検証・重複戦略
  2. SQLite typed reconstruction
  3. upsert / audit append-only性
  4. persistence層でのsecurity no-downgrade
  5. 認証済み実プロバイダconnector
  6. 複数イベント→Trace grouping
  7. association weight の実データ校正
  8. candidate reason→evidenceの完全な追跡
  9. Knowledge lifecycleの遷移履歴・制約
  10. Capability persistence / domain validationの強化
  11. atomicなmulti-entity transaction
  12. schema migration framework
  13. UI
  14. 実仕事データでの評価

## 設計上の合意事項
- 観測/報告データと分析・仮説・Knowledgeを混同しない。
- 不明な関連付けは誤分類より `UNASSIGNED` を優先する。
- PredictionをObserved Factへ逆流させない。
- provisionalをconfirmedとして扱わない。
- correctionで元predictionを破壊しない。
- 機密区分を派生処理で下げない。
- Knowledgeのvalidated化は人間承認を必須とする。
- Capabilityは能力断定ではなく、条件付き仮説として扱う。
- 実データがない状態で実運用精度を捏造しない。
- fixture / CIの成功を実世界有効性の証明としない。

## 引き継ぎルール
1. 実装変更はGitHub commitに残す。
2. レビュー結果はこのログまたはレビュー文書に残す。
3. CI失敗は原因・commit・runを追跡可能な形で残す。
4. 「実装済み」と「外部実証が必要」を明確に分ける。
5. 新しい担当者は、まず `README.md` → `docs/WORK_LOG.md` → テスト → CI履歴の順に確認する。
6. 判断を変更した場合は、理由と影響範囲をこのログへ追記する。

## 次の優先順位
1. Connector API不一致を修正し、CI greenを確認。
2. persistence security no-downgrade をテスト付きで強化。
3. append-only audit / update履歴を強化。
4. schema migrationを導入。
5. typed read APIとatomic lifecycleを強化。
6. 最小UIで Timeline / UNASSIGNED / confirmation / correction を実データ相当で通す。
7. 認証情報をGitHubへ保存せず、実プロバイダconnectorの統合テスト境界を設計。
8. ラベル付き実仕事データで評価し、coverage / selective accuracy / calibration / correction burdenを測る。

## 注意
このログは「会話全文の逐語録」ではありません。GitHubで他の担当者が設計判断・レビュー結果・未完了事項を追跡できることを目的とした、要点ベースの作業記録です。会話に存在しない事実・性能値・実運用結果は追加しません。
