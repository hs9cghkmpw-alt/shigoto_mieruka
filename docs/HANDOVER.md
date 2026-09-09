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
直近の実装コミットで、Connector Registryは`SourceConnector`契約の`collect`へ整合され、関連するCI失敗3件も修正済みと記録されている。次の作業では、最新main上で以下を再確認し、実装記録とCI実行結果の一致を確証化する。

1. `pull` / `collect` の旧契約が残っていないことを検索で確認。
2. 最新CIでcompile・tests・regression testsが実行されていることを確認。
3. `docs/WORK_LOG.md` とREADMEの現在地を実装実態に合わせて更新。
4. 実サービス認証、実仕事データ、UI実利用性はコード/CIとは別の外部実証境界として扱う。

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
