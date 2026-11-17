"""Small memory: human feedback and approved articles, retrieved into the next draft prompt.
No training happens; the model just sees recent lessons and examples."""
import difflib
import sqlite3
from contextlib import closing

from .settings import ROOT


def run(sql, args=()):
    with closing(sqlite3.connect(ROOT / "data/learning.sqlite")) as db:
        db.executescript(
            "CREATE TABLE IF NOT EXISTS feedback(id INTEGER PRIMARY KEY, job_id TEXT, kind TEXT, "
            "text TEXT UNIQUE);"
            "CREATE TABLE IF NOT EXISTS exemplars(job_id TEXT PRIMARY KEY, format TEXT, title TEXT, "
            "body TEXT, at TEXT DEFAULT CURRENT_TIMESTAMP);"
            "CREATE TABLE IF NOT EXISTS ai_drafts(job_id TEXT PRIMARY KEY, body TEXT);")
        rows = db.execute(sql, args).fetchall()
        db.commit()
        return rows


def remember(job_id, kind, text):
    if text and text.strip():
        run("INSERT OR IGNORE INTO feedback(job_id, kind, text) VALUES (?,?,?)", (job_id, kind, text.strip()))


def lessons(limit=12):
    return [f"{k}: {t}" for k, t in run("SELECT kind, text FROM feedback ORDER BY id DESC LIMIT ?", (limit,))]


def save_ai_draft(job_id, body):
    run("INSERT OR REPLACE INTO ai_drafts VALUES (?,?)", (job_id, body))


def record_edits(job_id, approved):
    """Store what the human changed between the model's last draft and the approved text."""
    row = run("SELECT body FROM ai_drafts WHERE job_id=?", (job_id,))
    if not row:
        return
    old, new = row[0][0].split(), approved.split()
    ops = [o for o in difflib.SequenceMatcher(None, old, new).get_opcodes()
           if o[0] in ("replace", "delete") and o[2] - o[1] >= 2]  # ignore one-word tweaks
    for _, i1, i2, j1, j2 in ops[:8]:
        remember(job_id, "human edit", f'replaced "{" ".join(old[i1:i2])[:160]}" with "{" ".join(new[j1:j2])[:160]}"'
                 if j2 > j1 else f'deleted "{" ".join(old[i1:i2])[:160]}"')


def add_exemplar(job_id, fmt, body):
    title = body.splitlines()[0].lstrip("# ").strip()
    run("INSERT OR REPLACE INTO exemplars(job_id, format, title, body) VALUES (?,?,?,?)",
        (job_id, fmt, title, body))


def exemplars(fmt, limit=2):
    return [{"title": t, "article": b} for t, b in
            run("SELECT title, body FROM exemplars WHERE format=? ORDER BY at DESC LIMIT ?", (fmt, limit))]
