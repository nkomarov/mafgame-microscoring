# Telegram collector: minimal-input UX

## Primary flow
1. Authorized recorder sends `/games` or `/start` and selects an active game.
2. Bot displays game status, phase and 10 numbered seats.
3. Tap `+ Event` -> choose event category -> actor seat -> target seat(s) -> preview -> Confirm.
4. Bot acknowledges with event ID, rule matched and provisional point delta.
5. `/score` shows current leaderboard and breakdown, with a clear incomplete-data indication.
6. `/undo` creates a retraction of the last authorized submission; no destructive delete.

## MVP event buttons
- Nomination: actor seat -> target seat.
- Vote: actor seat -> target seat.
- Will (red eliminated): author seat -> three distinct targets; validate author role only after role confirmation.
- First speech / split organization / broken split / split saved: actor and relevant phase, require observer confirmation because definitions remain open.
- Sheriff/don checks, night kills, elimination and survival: ideally imported from main game bot later; temporary manual admin entry for standalone testing.

## Interaction rules
- Use compact inline keyboards with seat numbers 1–10; no free-text player names.
- Every callback includes a short opaque session/action ID, not the full event payload.
- A callback from a stale game or phase is rejected with a refresh option.
- Confirmation preview shows `Game ID`, `Day/Night`, `Event`, `Actor`, `Target`, `Delta`.
- Unknown roles -> store observation, defer score until roles confirmed.
- When observers disagree, show `disputed`; admin must reconcile.
- Allow multiple observers to independently log the same event without double scoring.

## Suggested commands
`/start`, `/games`, `/game`, `/event`, `/score`, `/my_events`, `/undo`, `/help`; admin-only `/newgame`, `/assign`, `/resolve`, `/closegame`.

## First pilot
One administrator, one recorder, synthetic game with 10 numbered seats, and the anonymized fixture from `data/game-2026-11-13.md`. Verify every recorded action against the rule tables and independently recomputed totals.
