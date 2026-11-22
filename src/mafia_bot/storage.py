"""SQLite append-only submissions for an anonymized ten-seat game."""
import json
import sqlite3
import uuid
from pathlib import Path

SCHEMA = """
CREATE TABLE IF NOT EXISTS games (
  id TEXT PRIMARY KEY,
  status TEXT NOT NULL DEFAULT 'open',
  day INTEGER NOT NULL DEFAULT 1
);
CREATE TABLE IF NOT EXISTS seats (
  game_id TEXT NOT NULL REFERENCES games(id),
  seat INTEGER NOT NULL CHECK(seat BETWEEN 1 AND 10),
  role TEXT NOT NULL CHECK(role IN ('red','sheriff','mafia','don','unknown')),
  PRIMARY KEY(game_id, seat)
);
CREATE TABLE IF NOT EXISTS events (
  id TEXT PRIMARY KEY,
  game_id TEXT NOT NULL REFERENCES games(id),
  kind TEXT NOT NULL,
  actor INTEGER NOT NULL,
  targets TEXT NOT NULL,
  day INTEGER NOT NULL,
  submitted_by INTEGER NOT NULL,
  source_key TEXT NOT NULL UNIQUE,
  retracted INTEGER NOT NULL DEFAULT 0,
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
"""

class Store:
    def __init__(self, path):
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        self.db = sqlite3.connect(path, isolation_level=None)
        self.db.execute("PRAGMA foreign_keys=ON")
        self.db.executescript(SCHEMA)

    def create_game(self):
        game_id = str(uuid.uuid4())
        with self.db:
            self.db.execute("INSERT INTO games(id) VALUES (?)", (game_id,))
            self.db.executemany(
                "INSERT INTO seats(game_id,seat,role) VALUES (?,?,?)",
                [(game_id, n, "unknown") for n in range(1, 11)])
        return game_id

    def games(self):
        return self.db.execute("SELECT id,day,status FROM games ORDER BY rowid DESC LIMIT 20").fetchall()

    def exists(self, game_id):
        return bool(self.db.execute("SELECT 1 FROM games WHERE id=?", (game_id,)).fetchone())

    def set_role(self, game_id, seat, role):
        if not self.exists(game_id) or seat not in range(1, 11):
            raise ValueError("Invalid game or seat")
        if role not in ("red", "sheriff", "mafia", "don", "unknown"):
            raise ValueError("Invalid role")
        self.db.execute("UPDATE seats SET role=? WHERE game_id=? AND seat=?", (role, game_id, seat))

    def roles(self, game_id):
        return dict(self.db.execute("SELECT seat,role FROM seats WHERE game_id=?", (game_id,)).fetchall())

    def add(self, game_id, kind, actor, targets, day, sender, source_key):
        if not self.exists(game_id) or kind not in ("nomination","vote","will"):
            raise ValueError("Invalid game/event")
        if actor not in range(1,11) or any(t not in range(1,11) for t in targets):
            raise ValueError("Invalid seats")
        if len(targets) != (3 if kind == "will" else 1) or len(set(targets)) != len(targets):
            raise ValueError("Invalid target count")
        if kind == "will" and actor in targets:
            raise ValueError("Author cannot name self")
        event_id = str(uuid.uuid4())
        self.db.execute(
            "INSERT OR IGNORE INTO events(id,game_id,kind,actor,targets,day,submitted_by,source_key) VALUES (?,?,?,?,?,?,?,?)",
            (event_id,game_id,kind,actor,json.dumps(targets),day,sender,source_key))
        row = self.db.execute("SELECT id FROM events WHERE source_key=?", (source_key,)).fetchone()
        return row[0]

    def events(self, game_id):
        rows = self.db.execute(
            "SELECT id,kind,actor,targets,day,submitted_by FROM events WHERE game_id=? AND retracted=0 ORDER BY rowid",
            (game_id,)).fetchall()
        return [dict(id=r[0],kind=r[1],actor=r[2],targets=json.loads(r[3]),day=r[4],submitted_by=r[5]) for r in rows]

    def undo_last(self, game_id, sender):
        row = self.db.execute(
            "SELECT id FROM events WHERE game_id=? AND submitted_by=? AND retracted=0 ORDER BY rowid DESC LIMIT 1",
            (game_id,sender)).fetchone()
        if row:
            self.db.execute("UPDATE events SET retracted=1 WHERE id=?", row)
            return row[0]
        return None
