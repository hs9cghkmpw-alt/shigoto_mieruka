# 仕事みえる化 / Work Memory / Work Trace

## 目的

実際の仕事で発生するWork Traceを記録・分析し、**本人がどのような仕事・環境・支援条件で能力を発揮できるかを実データから可視化する**ための基盤。

単純な工数管理、常時監視、単一スコアによる人事評価を目的としない。

## 現在地

**Phase 1: 実験可能な基盤 — 実装済み・CI検証済み**。

現在は、WorkTraceからWorkItemへの安全な暫定紐付けと、その実験結果を検証・集計するための基盤がある。実際の仕事データは捏造せず、実運用で取得したデータだけを実証に使用する。

### 実装済み

- WorkItem / WorkTraceの最小ドメインモデル
- OBSERVED / REPORTEDのprovenance分離
- PUBLIC / INTERNAL / CONFIDENTIAL / RESTRICTEDの機密区分
- 派生データの機密区分継承
- 決定論的Association Engine
- 信号からの候補生成・スコアリング
- 一意の高信頼候補だけを暫定紐付け
- 曖昧・低信頼ケースの未分類化
- 実験CSVの厳格なスキーマ検証
- GO / GRAY / STOPの証拠ベース再計算
- 訂正理由・記録時間・確認時間の集計
- 実データCSV検証CLI
- 決定論的fixtureによる回帰テスト
- GitHub ActionsによるCI

## 重要な設計原則

```text
観測事実
  ↓
WorkTrace
  ↓
候補生成
  ↓
決定論的推定
  ↓
暫定紐付け
  ↓
本人確認・訂正
  ↓
分析
```

- FACT / ANALYSIS / KNOWLEDGEを混同しない
- observed / reportedを上書き統合しない
- AIの推測を観測事実として保存しない
- 誤紐付けより未分類を優先する
- 暫定紐付けを確定事実として扱わない
- 実験結果のGO/GRAY/STOPを入力値として盲信しない
- 訂正履歴を保持する
- 派生データの機密区分を緩和しない
- 記録負担を秒単位で測定する
- 外部AIはデフォルトOFF
- 人事評価を単一スコアで自動決定しない
- 実データを捏造しない
- 実験結果を見てGO/STOP基準を変更しない

## 実装上の境界

現在のAssociation Engineは**観測済みシグナルから候補を生成して暫定紐付けする決定論的基盤**であり、メール・チャット・ファイル等からシグナル自体を取得するコネクタはまだ含まない。

また、FACT → ANALYSIS → KNOWLEDGE → Capability Profileの長期分析系は設計対象であり、Phase 1の実証対象ではない。

## 実証実験

実際の仕事データを以下のCSVテンプレートへ記録し、検証CLIで集計する。

- `examples/real_data_experiment_template.csv`
- `src/experiment/validate_real_data.py`

必要な実データが存在しない場合、システムは空のままにする。架空データで実証結果を作らない。

## 開発原則

仕様より実証を優先する。ただし、安全性・provenance・再現性を壊す変更は採用しない。
