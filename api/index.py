"""Vercel ASGI entrypoint. Explicitly fail closed until a database is provisioned."""
import os
from fastapi import FastAPI, HTTPException, Header
from pydantic import BaseModel, Field
from .telegram_auth import verify_init_data

app = FastAPI(title="Mafia scoring API", docs_url=None, redoc_url=None)

class Submission(BaseModel):
    game_id: str
    kind: str
    actor: int = Field(ge=1, le=10)
    targets: list[int] = Field(default_factory=list)
    phase: str
    note: str = Field(default="", max_length=2000)
    idempotency_key: str = Field(min_length=8, max_length=128)

@app.get("/api/health")
def health():
    return {"status":"ready_for_configuration","database_configured":bool(os.environ.get("SUPABASE_URL"))}

@app.post("/api/events", status_code=503)
def submit_event(event: Submission, x_telegram_init_data: str = Header(default="")):
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    if not token:
        raise HTTPException(503, "Bot credentials not configured")
    user = verify_init_data(x_telegram_init_data, token)
    if not user:
        raise HTTPException(401, "Invalid Telegram initData")
    # No writes are permitted until role authorization and durable storage are implemented.
    raise HTTPException(503, "Event storage not configured")
