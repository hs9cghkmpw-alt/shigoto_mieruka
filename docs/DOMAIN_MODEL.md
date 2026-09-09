# Domain Model

## WorkItem
仕事・案件・依頼など、WorkTraceを関連付ける対象。

## WorkTrace
実際に発生した仕事イベントを時系列で保持する中心モデル。predictionとassignment stateを持ち得るが、predictionはobserved factではない。

## EvidenceRef / Evidence
外部ソース由来の証拠とその参照。source ID、時刻、content hash、extractor metadata、lifecycle、security classificationを管理する。

## Assignment
- `PROVISIONAL`: association engineによる暫定関連付け。
- `UNASSIGNED`: 根拠不足・margin不足などで未分類。
- `CONFIRMED`: 人間確認済み。
- `CORRECTED`: 人間訂正を記録し、元predictionを破壊しない。

## Fact
確認済みの事実。source trace IDsを持つ。推定結果だけから自動生成してobserved factへ昇格させない。

## Analysis
Factを入力として作る分析・仮説。作成者、作成時刻、method version、input methodなどの監査メタデータを持つ。

## Knowledge
Analysisから生成される知識候補。通常は`candidate`から始まり、人間承認を経て`validated`になる。expired / superseded / rejectedを含むlifecycleを持つ。

## CapabilityHypothesis
特定の仕事種別・環境・支援条件などの文脈に依存する仮説。人間の恒常的な能力を単一スコアで断定するモデルではない。

## Evidence status
- ACTIVE
- RETAINED
- EXPIRED
- REVOKED

## Provenance
`OBSERVED` と `REPORTED` は区別する。Derived informationは観測情報を上書きしない。

## Security
派生物のclassificationは入力証拠より緩和しない。現在の順序は PUBLIC < INTERNAL < CONFIDENTIAL < RESTRICTED。

## Timeline
Persisted WorkTrace rowsから決定論的に時系列を構築するpresentation向けモデル。推測で欠損イベントを生成しない。
