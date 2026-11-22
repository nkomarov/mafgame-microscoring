# Deployment plan: Vercel + dedicated Supabase project

Status: **deployment preparation**, not production-ready. No production project, database, secrets or bot token have been provisioned by this document.

## Verified account inventory (2026-11-22)
- Vercel team: `Nikolay Komarov's projects` (Hobby). Existing projects: `friends-calendar-web`, `mygrandpa-ai`.
- Supabase existing projects: `Friends Calendar Supa` (eu-west-1), `mygrandpa-ai` (eu-central-1).
- Do **not** reuse those databases for this project. A new Supabase project may incur charges or require free-tier capacity.

## Architecture
Telegram Mini App -> Vercel HTTPS static frontend -> authenticated API -> dedicated Supabase PostgreSQL.
Telegram bot webhook -> same API (later). Existing aiogram long-polling CLI is **not** a Vercel Function and should not be started in Vercel.
Alternative: VPS Docker container running aiogram long polling + FastAPI, with PostgreSQL or SQLite for a single process.

## Already prepared
- `web/observer/index.html`: visual prototype, no server persistence.
- `vercel.json`: routes for static prototype and Python API.
- `api/index.py`: health endpoint and **fail-closed** event submission stub.
- `api/telegram_auth.py`: server-side Telegram initData HMAC verification.
- `tests/test_telegram_auth.py`: valid/tampered/expired/duplicate signature tests.

## Mandatory before real use
1. Finish the authoritative event schema, persistence, observer ACL and idempotency.
2. Add a dedicated Supabase project in an EU region, schema migrations, backups, least-privilege service credentials and RLS (deny public access by default).
3. Connect backend to Supabase; use a transaction pooler or HTTP Data API for Vercel functions.
4. Ensure the Mini App sends requests with `Telegram.WebApp.initData`; **never** trust client-provided user ID or initDataUnsafe.
5. Enforce authorized observer-to-game assignment; don't equate any valid Telegram signature with authorization.
6. Configure the Vercel project Git link to `nkomarov/mafgame-microscoring`, project root at repo root, and explicit production branch.
7. Add `TELEGRAM_BOT_TOKEN` (server-side only), `SUPABASE_URL`, a server-only credential, and admin allowlist via Vercel environment variables. Never prefix secrets with `NEXT_PUBLIC_`.
8. Create bot with BotFather, configure HTTPS Mini App menu button and webhook (once webhook handler is implemented).
9. Run unit, API, Telegram mobile E2E, restart/replay, authorization, double-click and load tests before activating real recording.
10. Confirm GitHub branch protection and deployment checks before enabling auto-deploy.

## Rollout
- Stage A: local UI and scoring tests (no live data).
- Stage B: private Vercel preview for visual testing only.
- Stage C: dedicated Supabase, migrations, authenticated end-to-end recording.
- Stage D: BotFather token and Mini App menu, private pilot.
- Stage E: integration with main game bot after its API is inspected.

## Fail-closed behavior
`POST /api/events` intentionally returns HTTP 503 even with valid Telegram initData until storage and authorization are implemented. This is safer than silently accepting data and losing game observations.

## VPS fallback
Deploy a single long-running aiogram worker under Docker/systemd; HTTPS via reverse proxy (Caddy), persistent DB volume, scheduled backups, restart policy and health checks. Avoid running polling and webhook for the same bot simultaneously.
