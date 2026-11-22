# Observer Mini App UI — implementation status

The clickable prototype is in [web/observer/index.html](../web/observer/index.html). It can be opened as a static HTML file in a browser to inspect geometry and interactions.

## Seat geometry
Two vertical columns, five square buttons each. Left column bottom-to-top: 1, 2, 3, 4, 5. Right column top-to-bottom: 6, 7, 8, 9, 10. The seat panel uses approximately 28% of the content width; **Telegram does not guarantee an exact fraction of the physical screen**.

## Event UX
Observer selects an event type, actor and required targets; free-text note is available for unanticipated events. Phase selector and local preview are included. All identifiers are seat numbers, not real player names.

## Critical launch gate
This is a **client-side prototype**, not a connected Telegram Mini App. It does **not** send observations to the server, authenticate users, or persist records across reloads. Do not use it to record a real game yet.

To enable real Telegram Mini App operation:
1. Deploy the frontend on HTTPS.
2. Add authenticated API endpoints for game state, event submissions and score retrieval.
3. Verify Telegram WebApp `initData` signature **server-side** using the bot token; never trust `initDataUnsafe` for authorization.
4. Validate roles, allowed events, phases, recorder permissions and idempotency on the backend.
5. Persist raw submissions, distinguish pending/confirmed/disputed, and support correction/retraction.
6. Configure a BotFather menu button or a bot reply keyboard with a Web App URL.
7. Run end-to-end tests inside Telegram on mobile before a real match.

Existing Bot API inline-keyboard bot remains a fallback. Its scoring implementation is partial and has not been live-tested.
