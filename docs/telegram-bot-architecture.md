# Telegram collector: architecture and integration plan

Status: design / preparation, no live bot deployed.

## Goal
A separate Telegram bot records **additional observed events** during each Mafia game, independently of the existing game-support bot. It calculates micro-scores from merged, verified events. Later the collector can be integrated with the main bot using stable IDs and event contracts.

## Related code inspected
- [emercons/im-bot](https://github.com/emercons/im-bot): Telethon/MTProto, Playwright Telegram Web, MCP adapter, separate skills/core; useful for optional chat history integration, but unnecessary for ordinary Bot API button workflows.
- [emercons/im-bot-emercons-private](https://github.com/emercons/im-bot-emercons-private): private overlay and uncommitted secrets/session handling.
- [emercons/carRentalRiskBot](https://github.com/emercons/carRentalRiskBot): transport-independent domain core, event journal, deduplication and recovery concepts. Its WhatsApp-specific code is not reused.
- [nkomarov/Telegram-Bot-Anekdot-by-Keyword](https://github.com/nkomarov/Telegram-Bot-Anekdot-by-Keyword): repository identified; implementation not yet verified.

## Proposed MVP stack
- Python 3.12+, aiogram 3 (proposed, not yet a confirmed dependency of the existing game bot).
- SQLite for single-instance MVP, with migration-ready storage interfaces for PostgreSQL.
- Telegram Bot API long polling in local development; webhook optional later.
- No LLM required for structured button events; optional transcription/parser must remain untrusted and require confirmation.
- Docker / systemd deploy possible; no bot token in repository.

## Layers
1. `telegram_adapter`: commands, inline keyboards, callback routing, access control.
2. `application`: game selection, event validation, source reconciliation, corrections, scoring requests.
3. `domain`: immutable event schema, scoring rules and versioning, deterministic score ledger.
4. `storage`: append-only raw submissions, canonical events, player seats, mapping, scores, audit history.
5. `integration`: future import/export adapter for main bot and its authoritative game state.

## Identity boundaries
- Internal `game_id` is a UUID, not a chat ID or date.
- `seat_number` 1..10 is used in public scoring records; no real names in repository or fixtures.
- `telegram_user_id` only in access-controlled runtime storage for authorized recorders, never in public examples.
- External game bot integration: `source_system` + `external_game_id` mapping; never assume both bots use identical IDs.
- A bot cannot read another bot's private state by default; integration requires an explicit API, shared database contract, export, or authorized events.

## Event pipeline
```text
Telegram button -> authorization -> game/phase validation
  -> append raw submission (source=observer)
  -> normalize + idempotency check
  -> reconcile with app events
  -> accepted / disputed / pending event
  -> versioned deterministic scoring
  -> per-player breakdown and game leaderboard
```

## Data consistency
- Use `update_id` / callback ID and an application idempotency key to prevent double submissions.
- Never count the same logical event twice when observer and game app both report it.
- Corrections append superseding events; do not overwrite raw evidence.
- Distinguish `observed`, `confirmed`, `disputed`, `retracted`.
- Scoring only from confirmed canonical events; incomplete games show a provisional badge.
- Preserve original event time, submission time and source.

## Permissions
- Administrator: creates/links games, assigns recorders, resolves disputes.
- Recorder: logs events for assigned games, can correct own submissions.
- Viewer: sees scoreboards if enabled.
- Reject messages and callbacks from unauthorized users; recheck permissions on every callback.
- Group mode: use explicit commands and callbacks; avoid requiring broad group-message visibility.

## Integration with main game bot (later)
1. Discover its language, framework, API, data model and lifecycle before selecting transport.
2. Define `GameStarted`, `PhaseChanged`, `PlayerEliminated`, `NightKillResolved`, `GameEnded` contracts with schema version and stable external IDs.
3. Import authoritative events with `source=game_app`; do not silently override observer disagreements.
4. Export score summary as JSON; allow main bot to render it.
5. Keep both bots separately deployable until the integration contract is tested.

## Out of scope for MVP
- Automated scraping of private Telegram chats.
- Capturing real names, handles or other personal identifiers in public GitHub.
- Autonomous inference of nominations, votes or roles from arbitrary conversations.
- Integration with the existing main game bot before its repository/API is identified.
