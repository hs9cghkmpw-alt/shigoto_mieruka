# Handover Guide

## Goal
この文書を読んだ担当者が、過去の会話を読まなくても安全に開発を再開できることを目的とする。

## Start here
1. `README.md`
2. `docs/PROJECT_CONTEXT.md`
3. `docs/ARCHITECTURE.md`
4. `docs/DOMAIN_MODEL.md`
5. `docs/DECISIONS.md`
6. `docs/REVIEW_HISTORY.md`
7. `docs/WORK_LOG.md`
8. `tests/`
9. `.github/workflows/`

## Working protocol
1. 最新mainを確認。
2. 最新CI runを確認。
3. 変更対象と既知の制約を確認。
4. まず再現テストを書く/実行する。
5. 実装する。
6. ローカルテストとcompileを通す。
7. GitHubへcommit。
8. GitHub Actions結果を確認。
9. 作業・レビュー結果を`docs/WORK_LOG.md`等へ追記。
10. READMEの「現在地」と矛盾しないか確認。

## Reporting rules
- `implemented` と `verified` を区別する。
- CI greenとreal-world validityを区別する。
- fixture performanceをproduction performanceとして報告しない。
- 未認証connectorを「実サービス接続済み」と呼ばない。
- scoreをcalibrated probabilityと呼ばない。
- 不明な関連付けを勝手に確定しない。

## Current first task
READMEと直近の実装履歴では、connector API不一致を含む初期レビュー指摘への修正commit群（`collect`契約整合、CI failure修正、Connector Registry回帰テスト等）が追加済みと記録されている。一方、`docs/WORK_LOG.md` の「現在地」と「次の修正」は古いスナップショットを含むため、作業再開時は次の順で再確認する。

1. `git log -n 20 --oneline` で最新commitを確認。
2. 最新CI runと失敗ジョブを確認。
3. `tests/` と `.github/workflows/` を実行可能な状態で確認。
4. `README.md`・`docs/WORK_LOG.md`・このHANDOVERの「現在地」が一致しているか確認。
5. 不一致があれば、実装済み／CI検証済み／外部実証待ちを分離してから次作業を決める。

現時点でコードから外部実証ができない境界は、実サービス認証済みconnector、実仕事データ評価、UI実利用性である。これらは「connector API不一致の修正済み」とは別ゲートとして扱う。

## Security rules
- 秘密情報、API token、個人情報をrepositoryへcommitしない。
- raw source contentを既定で永続化しない。
- security classificationを派生処理で下げない。
- 外部connectorは認証情報をコードへハードコードしない。

## Definition of done for a change
A change is not considered complete merely because code was written. Prefer:
- domain invariants covered by tests
- regression test added for a discovered bug
- compile/test success
- GitHub Actions verification
- work/review log updated when architecture or behavior changes
- documentation consistent with actual implementation

## If uncertain
UNASSIGNED / unknown is safer than an invented association. Document uncertainty explicitly and request human confirmation where the domain requires it.
