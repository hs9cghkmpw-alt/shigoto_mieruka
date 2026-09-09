# Roadmap

## P0 — Restore verified baseline
- [ ] Connector API `pull` / `collect` contract mismatchを修正
- [ ] Regression testで`since` forwardingを確認
- [ ] GitHub Actions greenを確認

## P1 — Persistence integrity
- [ ] Evidence source re-hash verification
- [ ] duplicate identity/content strategyを明文化・実装
- [ ] security no-downgradeをstorage boundaryでも強制
- [ ] upsertによるaudit/history上書きを排除または制約
- [ ] typed read reconstruction
- [ ] schema migration framework

## P2 — Lifecycle integrity
- [ ] atomic multi-entity ingestion lifecycle
- [ ] Knowledge transition graphの完全実装
- [ ] Knowledge status historyの監査性強化
- [ ] Fact / Analysis / Knowledge / Capabilityのdomain validation統一

## P3 — Association quality
- [ ] multi-event → WorkTrace grouping
- [ ] reason → evidence lineage強化
- [ ] labeled real-work datasetによるweight calibration
- [ ] coverage / selective accuracy / calibration / correction burden測定

## P4 — Real connectors
- [ ] provider-specific connector contract
- [ ] authentication boundary
- [ ] secret management
- [ ] sandbox/integration test
- [ ] retry / rate-limit / cursor / duplicate handling

## P5 — UI
Minimum end-to-end surface:
- [ ] chronological Timeline
- [ ] UNASSIGNED / ambiguous tray
- [ ] candidate score + evidence references
- [ ] human confirmation
- [ ] correction
- [ ] Fact / Analysis / Knowledge separation
- [ ] Capability hypothesis review
- [ ] audit history

## P6 — Real-world validation
- [ ] actual work data collection protocol
- [ ] privacy/security review
- [ ] labeling protocol
- [ ] baseline comparison
- [ ] usability / recording burden evaluation
- [ ] only then publish empirical performance numbers
