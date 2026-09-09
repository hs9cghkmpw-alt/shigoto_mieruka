# 仕事みえる化 / Work Memory / Work Trace

## 目的

実際の仕事で発生する証跡を安全にWorkTrace化し、仕事・環境・支援条件と結果を実データから振り返れる基盤を作る。

単純な工数管理、常時監視、単一スコアによる人事評価を目的としない。

## 現在地

**技術基盤: 是正済み。**  
**実運用製品としての完成: 未達。** 実データ・利用者UI・サービス固有コネクタが必要なため、ここを架空データで「100%」とは宣言しない。

実装済み:

- WorkItem / WorkTrace / EvidenceRef / CapabilityHypothesis
- OBSERVED / REPORTED の provenance 分離
- source ID・観測時刻・取得時刻・content hash・extractor version によるlineage
- raw source contentをSQLiteへ保存しないEvidence保持
- EvidenceのACTIVE / RETAINED / EXPIRED / REVOKED lifecycle
- Evidence → WorkTrace の共通取り込み境界
- SourceConnector Protocol（サービス固有コネクタを安全に追加できる契約）
- 決定論的Association Engine
- raw association scoreとcalibrated confidenceの意味分離（現時点はuncalibrated）
- 候補間marginによる曖昧性制御
- 候補ごとのevidence reference保持
- 暫定紐付けと本人確認・訂正の分離
- 訂正時に元predictionを破壊しない監査情報
- strict invariantを含む単一のcanonical validation API
- SQLiteによるWorkItem / Evidence / WorkTrace / Correction / Audit Event永続化
- FACT → ANALYSIS → KNOWLEDGEの人間承認ゲート
- Knowledgeのcandidate / validated / expired / superseded / rejected lifecycle
- Analysisの作成者・作成時刻・method version・input method
- evidence countだけでなくevidence diversityの保持
- 能力を単一点数化せず、条件付きCapability Hypothesisとして保持
- 決定論的fixtureによる回帰テスト
- 実データCSVの厳格な検証
- GO / GRAY / STOPの証拠ベース再計算
- GitHub ActionsによるCI

## データ経路

```text
SourceConnector
  ↓
SourceEvent
  ↓
Evidence（digest + metadata）
  ↓
WorkTrace（OBSERVED / UNASSIGNED）
  ↓
候補生成
  ↓
raw association score
  ↓
margin gate
  ↓
PROVISIONAL / UNASSIGNED
  ↓
本人確認・訂正
  ↓
Fact
  ↓
Analysis（audit metadata付き）
  ↓
Knowledge candidate
  ↓
人間承認
  ↓
validated / expired / superseded / rejected
  ↓
条件付きCapability Hypothesis
```

## 絶対ルール

1. 推定を観測事実へ逆流させない。
2. observed / reportedを上書き統合しない。
3. raw source contentを既定のSQLite保存対象にしない。
4. association scoreを確率として表示しない。校正データがない限り `uncalibrated` とする。
5. 高スコアでもmarginが不足する候補は未分類にする。
6. provisionalをconfirmed factとして扱わない。
7. 訂正で元predictionを消さない。
8. 派生データの機密区分を緩和しない。
9. Knowledgeは人間承認なしにvalidatedへ昇格させない。
10. Capabilityは「能力がある」という断定ではなく、条件・観測結果・証拠を持つ仮説として扱う。
11. 実データを捏造しない。
12. fixtureの性能を実運用性能として報告しない。
13. CI成功を実世界有効性の証明と混同しない。

## 残る実証上の限界

技術的な安全境界を実装しても、次の3点はコードだけでは証明できない。

- メール・チャット・ファイル・カレンダー等の実サービスからの実データ収集
- 実仕事データに対するassociation精度・校正・訂正率・記録負担の測定
- 実運用UIでの本人確認・訂正・レビュー体験

したがって「100点」は**実装可能な技術的欠陥を残さない**という意味で扱い、実データを使わないまま実運用性能を100点と偽装しない。

## 実証実験

実際の仕事データは `examples/real_data_experiment_template.csv` に記録し、`src/experiment/validate_real_data.py` で検証する。

決定論的fixtureは回帰テスト専用。実仕事の性能実証値には使用しない。
