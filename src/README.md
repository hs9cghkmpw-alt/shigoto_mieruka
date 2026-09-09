# src

Work Memory / Work Traceの最小実装領域。

## 方針

- 初期実装はPythonを候補とする
- ドメインモデルと実験ツールを先に作る
- 外部AIには依存しない
- 自動紐付けはルールベースから開始する
- 未分類を安全なフォールバックとして扱う

## 構成予定

```text
src/
├── domain/       # WorkItem / WorkTrace / FACT等
├── association/  # Work Item紐付け
└── validation/   # 入力・整合性検証
```
