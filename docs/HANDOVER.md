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
最新CIではconnector APIの`pull` / `collect`不一致が残っている。まずこの契約を統一し、テストとCIで確認する。

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
