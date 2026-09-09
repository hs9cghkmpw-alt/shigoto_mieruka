# Review History

## Review A — Initial strict review
**評価:** 約55–58/100

主な問題:
- association/evidence lineage不足
- CSV中心の実験
- 実サービスconnectorなし
- Evidence→WorkTrace pipelineが限定的
- confidence semanticsが弱い
- Knowledge lifecycle / Capability / persistence / UIが不足

## Review B — Hardening review
**評価:** 72/100

改善として確認されたもの:
- Evidence hash / lifecycle
- canonical validation
- association margin gate
- raw score / calibrated confidenceの分離
- candidate evidence IDs
- correction audit
- SQLite persistence / read APIs
- FACT→ANALYSIS→KNOWLEDGE approval gate
- Knowledge status history
- CapabilityHypothesis
- Timeline
- CI regression tests

残課題:
1. source再ハッシュ検証と重複戦略
2. typed persistence reconstruction
3. upsertによるaudit/history上書きリスク
4. persistenceでのsecurity no-downgrade強制
5. authenticated real provider connector
6. multi-event grouping
7. empirical association calibration
8. reason→evidence lineageの強化
9. Knowledge transition graph / full history
10. domain validationの全モデル適用
11. atomic multi-entity lifecycle
12. schema migration framework
13. UI end-to-end validation
14. real-work labeled evaluation

## CI finding — 2026-09-09
Run: `34309130400`
Job: `102331923392`
Commit under test: `79a5f81b3e0c0f3298c96df5dadd0fac5a6f4917`

Result: **63 passed / 1 failed**

Failed test:
`tests/test_connectors.py::test_connector_registry_is_explicit_and_does_not_fake_provider_access`

Cause:
Registry's `pull()` delegated to `collect()`, while the connector contract/test object exposed `pull()`. This is an API naming mismatch, not evidence of provider connectivity.

Status:
Open at the time this document was created. Do not report CI green until a later run verifies it.
