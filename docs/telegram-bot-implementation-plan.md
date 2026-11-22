# Telegram micro-scoring bot: implementation handoff

Status: ready for implementation; no code deployed or credentials configured.

## Milestone 0 — baseline
- Read `scoring-rules.md`, `data-collection.md`, `open-questions.md`, and anonymized fixture.
- Freeze scoring rule version `v0.1` with explicit unresolved semantics.
- Define acceptance criteria and no-personal-data-in-repository policy.

## Milestone 1 — pure scoring engine
- Define typed `Game`, `Seat`, `RawSubmission`, `CanonicalEvent`, `ScoreEntry`, `RuleVersion`.
- Implement deterministic `score(game, events, rule_version)` independent of Telegram.
- Add unit tests for nominations vs votes, night checks, wills (+3/-3/-1), successful shots, no-shoot penalties, survival, role exclusivity.
- Test anonymized example total = 60 with explicit assumptions and missing-event markers.
- Add tests for invalid roles, duplicate events, retractions, incomplete chronology and unknown roles.

## Milestone 2 — local bot MVP
- Set up Python, aiogram 3, SQLite, migrations, environment-based token loading.
- Implement `/start`, `/games`, `/event`, `/score`, `/undo`.
- Inline seat-selection keyboards, preview + confirmation, event source `observer`.
- Admin allowlist and per-game recorder assignments.
- Idempotency and persistent pending interaction state.
- Synthetic end-to-end tests; never test with a real game without explicit consent.

## Milestone 3 — observer/application reconciliation
- Add `source=game_app` importer for JSON events.
- Deduplicate identical logical events while retaining both source records.
- Mark conflicting events disputed; exclude disputed events from confirmed scores.
- Add audit and correction workflows; compare score changes before/after correction.

## Milestone 4 — integration readiness
- Identify and inspect main game bot repository and runtime/API.
- Write versioned import/export JSON schemas and mapping table for external game IDs.
- Test lifecycle and replay; only then consider embedding the collector in main bot.

## Suggested code layout
```text
src/mafia_scoring/
  domain/{models.py,rules.py,engine.py}
  application/{record_event.py,reconcile.py,scoreboard.py}
  adapters/telegram/{bot.py,handlers.py,keyboards.py}
  adapters/game_app/{contracts.py,importer.py}
  storage/{sqlite.py,migrations/}
tests/{test_rules.py,test_reconciliation.py,test_telegram_flows.py}
docs/{telegram-bot-architecture.md,telegram-bot-ux.md,telegram-bot-implementation-plan.md}
```

## Security & operations
- `TELEGRAM_BOT_TOKEN` from environment or secret store only; provide `.env.example` with placeholders.
- Redact tokens, Telegram IDs and message content from logs.
- SQLite backups, schema migrations, restart/replay tests and graceful shutdown.
- Use long polling with a single worker; avoid concurrent pollers on one token.
- Store no personal names or Telegram handles in public fixtures.

## Acceptance criteria
1. Two independent observers logging the same nomination yield one canonical scored event.
2. A red will with 2 black and 1 red yields author +3 and each named target −1.
3. A black will yields no points.
4. Unknown roles or disputed source events do not produce unverified score entries.
5. A confirmed correction causes a reproducible recalculation without losing original evidence.
6. Bot recovers from restart without duplicate events or duplicate acknowledgments.
7. Public repository contains only anonymous example data and no credentials.
8. Standalone bot can export a game score summary without depending on main game bot.
