# 仕事みえる化 / Work Memory / Work Trace

## 目的

実際の仕事で発生する証跡を安全にWorkTrace化し、仕事・環境・支援条件と結果を実データから振り返れる基盤を作る。

単純な工数管理、常時監視、単一スコアによる人事評価を目的としない。

## 現在地

**Phase 1: 実験基盤 — CI検証済み。**  
**Phase 1.5: 証拠・永続化・ライフサイクル強化 — 実装中。**

現在は以下まで実装している。

- WorkItem / WorkTrace / EvidenceRefのドメインモデル
- OBSERVED / REPORTEDのprovenance分離
- source ID・観測時刻・取得時刻・content hash・extractor versionによるEvidence lineage
- PUBLIC / INTERNAL / CONFIDENTIAL / RESTRICTEDの機密区分
- 派生データの機密区分継承
- Evidence → WorkTraceの取り込み境界
- 決定論的Association Engine
- confidenceだけでなく候補間marginを使った曖昧性制御
- 暫定紐付けと本人確認・訂正の分離
- 訂正時に元のpredictionを破壊しない履歴保持
- 実験CSVの厳格なスキーマ検証
- GO / GRAY / STOPの証拠ベース再計算
- 記録時間・確認時間・訂正率等の集計
- ローカルSQLite永続化基盤
- FACT → ANALYSIS → KNOWLEDGEのKnowledge昇格に人間承認ゲート
- 決定論的fixtureによる回帰テスト
- GitHub ActionsによるCI

## 現在のデータ経路

```text
外部ソース
  ↓
EvidenceRef
  ↓
WorkTrace（OBSERVED）
  ↓
候補生成
  ↓
決定論的推定
  ↓
暫定紐付け / UNASSIGNED
  ↓
本人確認・訂正
  ↓
Fact
  ↓
Analysis
  ↓
Knowledge（人間承認後のみvalidated）
```

重要なのは、**推定を観測事実へ逆流させないこと**である。

## 安全原則

- FACT / ANALYSIS / KNOWLEDGEを混同しない
- observed / reportedを上書き統合しない
- AIの推測を観測事実として保存しない
- 誤紐付けより未分類を優先する
- confidenceが高くても候補間marginが小さければ未分類にする
- 暫定紐付けを確定事実として扱わない
- 訂正時に元のpredictionを消さない
- Evidenceのsource identityとcontent hashを保持する
- 派生データの機密区分を緩和しない
- Knowledgeは人間承認なしにvalidatedへ昇格させない
- 記録負担を秒単位で測定する
- 外部AIはデフォルトOFF
- 人事評価を単一スコアで自動決定しない
- 実データを捏造しない
- 実験結果を見てGO/STOP基準を変更しない

## 実装上の境界

Association Engineは観測済みシグナルから候補を生成する。メール・チャット・ファイル等からシグナルを収集する具体的コネクタはまだ実装していない。

Evidence → WorkTraceの共通取り込み境界とSQLite永続化は実装済みだが、特定サービスの自動収集は別フェーズとする。

Capability Profileの統計モデル、実運用UI、実データによる有効性検証は未完了。ここを架空データで埋めない。

## 実証実験

実際の仕事データは `examples/real_data_experiment_template.csv` に記録し、`src/experiment/validate_real_data.py` で検証・集計する。

決定論的fixtureは回帰テスト専用であり、実仕事の性能実証値として扱わない。

## 開発原則

「作った」ではなく「証跡を再現でき、壊れた推定を検出でき、訂正可能である」ことを完成条件とする。

安全性・provenance・再現性を壊す高速化は採用しない。
