# Telegram Bot API — initialization checklist

**Status:** executable scaffold committed; not deployed, no live bot configured, and no Telegram integration test performed. The initial scoring implementation covers nominations, red votes and red wills only. All other rules remain in `scoring-rules.md` for later implementation.

## Create bot
1. Open official [@BotFather](https://t.me/BotFather) in Telegram.
2. Send `/newbot`, choose a display name and unique username ending in `bot`.
3. Copy the issued token into your local environment or secret manager, **not into GitHub or chat**.
4. Find your numeric Telegram user ID via a trusted method. Put it in `TELEGRAM_ADMIN_IDS`.
5. Choose a server or local machine that will run the process. For MVP, long polling needs no public HTTPS endpoint.

## Run locally (Linux/macOS)
```bash
git clone https://github.com/nkomarov/mafgame-microscoring.git
cd mafgame-microscoring
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export TELEGRAM_BOT_TOKEN='token-from-BotFather'
export TELEGRAM_ADMIN_IDS='your-numeric-telegram-user-id'
export PYTHONPATH=src
python -m unittest discover -s tests
python -m mafia_bot
```

## Windows PowerShell
```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
$env:TELEGRAM_BOT_TOKEN = 'token-from-BotFather'
$env:TELEGRAM_ADMIN_IDS = 'your-numeric-telegram-user-id'
$env:PYTHONPATH = 'src'
python -m unittest discover -s tests
python -m mafia_bot
```

## First interaction
1. `/start` shows commands.
2. `/newgame` creates an anonymous 10-seat game.
3. `/use <game-id>` selects the game.
4. `/role 7 don`, `/role 8 mafia`, `/role 4 sheriff`, etc. assign roles; unassigned roles remain unknown and affected events await scoring.
5. `/event` -> select nomination, vote or will -> actor -> target(s) -> confirm.
6. `/score` shows **partial provisional** scores; `/undo` retracts the latest submission by that operator.

## Known limitations before real-game pilot
- Admin-only access, no separate recorder enrollment yet.
- No phase/day progression; events currently stored as day 1.
- Only nomination, red vote and red will scoring implemented; no night, survival, split or sheriff check scoring.
- No cross-source reconciliation or main-game-bot integration yet.
- SQLite single-process local MVP; no deployment service or backup automation.
- Unscored actions remain pending; scoring is not an authoritative tournament result.
- Test suite is committed but has **not been executed in a verified runtime**.
- Do not paste the BotFather token into a public issue, repository, or this chat. If exposed, rotate it via BotFather.
