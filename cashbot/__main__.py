"""Run with: python -m cashbot --help"""
import argparse
import json
import re
import sqlite3
import sys
from datetime import datetime
from zoneinfo import ZoneInfo

import httpx
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.types import Command

from . import llm, research
from .settings import ROOT, ensure_dirs, job_id, product_facts, read_json
from .workflow import build_graph, digest, paths


def config(identifier):
    return {"configurable": {"thread_id": job_id(identifier)}, "recursion_limit": 40}


def reserve_job(identifier, source_id, initial=None):
    with sqlite3.connect(ROOT / "data/jobs.sqlite") as db:
        db.execute("CREATE TABLE IF NOT EXISTS jobs(id TEXT PRIMARY KEY, source_id TEXT UNIQUE)")
        if "initial_state" not in {row[1] for row in db.execute("PRAGMA table_info(jobs)")}:
            db.execute("ALTER TABLE jobs ADD COLUMN initial_state TEXT")
        try:
            db.execute("INSERT INTO jobs(id, source_id, initial_state) VALUES (?,?,?)",
                       (identifier, source_id, json.dumps(initial) if initial is not None else None))
        except sqlite3.IntegrityError:
            raise ValueError("This job ID or source/topic is already reserved. Use status or retry for that job; avoid duplicate articles.") from None


def reserved_initial(identifier):
    with sqlite3.connect(ROOT / "data/jobs.sqlite") as db:
        columns = {row[1] for row in db.execute("PRAGMA table_info(jobs)")}
        if "initial_state" not in columns:
            return None
        row = db.execute("SELECT initial_state FROM jobs WHERE id=?", (identifier,)).fetchone()
        return json.loads(row[0]) if row and row[0] else None


def used_sources():
    with sqlite3.connect(ROOT / "data/jobs.sqlite") as db:
        db.execute("CREATE TABLE IF NOT EXISTS jobs(id TEXT PRIMARY KEY, source_id TEXT UNIQUE)")
        return {r[0] for r in db.execute("SELECT source_id FROM jobs")}


def show(snapshot):
    state = snapshot.values
    if not state:
        raise ValueError("Job not found. Use the same job ID shown by the start command.")
    print("Job:", state["job_id"])
    print("Status:", state.get("status", "running"))
    print("Next:", ", ".join(snapshot.next) or "finished")
    if state.get("draft"):
        print("Draft:", paths(state)[0])
        print("Review:", paths(state)[1])
        print("SHA256:", digest(state["draft"]))
    for issue in state.get("issues", []):
        print("BLOCKER:", issue)


def guide_source(topic):
    note_path = (ROOT / topic["notes_file"]).resolve()
    note_path.relative_to(ROOT.resolve())
    if note_path.suffix != ".md":
        raise ValueError("Guide notes must be a Markdown file inside this project.")
    return {"id": topic["id"], "title": topic["topic"],
            "publisher": "Original editorial material", "url": "local:" + topic["notes_file"],
            "published_at": None, "kind": "fictional editorial notes, not news or legal authority",
            "text": note_path.read_text(encoding="utf-8")}


def begin(graph, identifier, topic, sources, demo=False, article_format="guide"):
    identifier = job_id(identifier)
    facts = product_facts(live=not demo)
    if not sources or not any(len(s["text"]) >= 150 for s in sources):
        raise ValueError("Not enough source text. Add an approved page or choose another source.")
    if not demo:
        llm.validate_config()
    initial = {"job_id": identifier, "topic": topic, "format": article_format,
               "sources": sources, "facts": facts, "demo": demo, "attempts": 0,
               "feedback": "", "issues": [], "notes": [], "status": "researching"}
    reserve_job(identifier, sources[0]["id"], initial)
    graph.invoke(initial, config(identifier))
    show(graph.get_state(config(identifier)))


def scheduled(graph, slot):
    schedule = read_json(ROOT / "schedule.json")
    date = datetime.now(ZoneInfo(schedule["timezone"]))
    identifier = f"{slot}-{date.strftime('%G-w%V')}"
    snapshot = graph.get_state(config(identifier))
    initial = reserved_initial(identifier) if not snapshot.values else None
    if snapshot.values or initial:
        print("This weekly slot already exists; skipping:", identifier)
        status = snapshot.values.get("status", "running") if snapshot.values else "reserved; no checkpoint"
        print("Status:", status)
        if any(task.error for task in snapshot.tasks):
            print("Last execution: failed")
        command = f"python -m cashbot status --job {identifier}"
        if initial or (snapshot.next and status != "awaiting_review"):
            print("Job is unfinished. After resolving the failure, retry:")
            command = f"python -m cashbot retry --job {identifier}"
        elif status == "blocked":
            print("Edit the draft, then recheck:")
            command = f"python -m cashbot check-edits --job {identifier}"
        elif status == "awaiting_review":
            print("Review the draft before approving, revising or rejecting it.")
        print("Next command:", command)
        return
    if slot == "guide":
        topics = read_json(ROOT / "guide_topics.json")
        candidate = next((t for t in topics if t["id"] not in used_sources()), None)
        if not candidate:
            raise ValueError("Guide backlog is empty. Add a new, distinct topic to guide_topics.json.")
        source = guide_source(candidate)
        begin(graph, identifier, candidate["topic"], [source], article_format="practical guide")
    else:
        packet = research.collect()
        for warning in packet["warnings"]:
            print("Source warning:", warning)
        keywords = schedule["news_keywords"]
        candidates = [s for s in packet["sources"] if s["id"] not in used_sources()
                      and s["published_at"] and len(s["text"]) >= 150]
        score = lambda s: sum(bool(re.search(r"" + re.escape(w) + r"", s["title"] + " " + s["text"], re.I))
                              for w in keywords)
        candidates.sort(key=score, reverse=True)
        if not candidates or score(candidates[0]) < 1:
            raise ValueError("No unused relevant dated story found. No article created. Choose a manual topic/source or add a guide instead.")
        source = candidates[0]
        begin(graph, identifier,
              "Explain this source for small Indian agencies/distributors: " + source["title"],
              [source], article_format="source-based explainer")


def main(argv=None):
    ensure_dirs()
    parser = argparse.ArgumentParser(description="Cashbook article bot: research, draft, review and export locally.")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("doctor")
    sub.add_parser("collect")
    sub.add_parser("sources")
    p = sub.add_parser("add-url")
    p.add_argument("--url", required=True)
    p.add_argument("--title", required=True)
    p = sub.add_parser("demo")
    p.add_argument("--job", default="demo-001")
    p = sub.add_parser("start")
    p.add_argument("--job", required=True)
    p.add_argument("--topic", required=True)
    p.add_argument("--source", required=True, help="ID printed by the sources command")
    p = sub.add_parser("publish", help="Build the static site page for an approved article.")
    p.add_argument("--job", required=True)
    p.add_argument("--slug")
    p.add_argument("--description")
    p = sub.add_parser("scheduled")
    p.add_argument("--slot", required=True, choices=["guide", "explainer"])
    for name in ("status", "retry", "check-edits", "approve", "revise", "reject"):
        p = sub.add_parser(name)
        p.add_argument("--job", required=True)
        if name == "approve":
            p.add_argument("--sha256", required=True)
            p.add_argument("--reviewed", action="store_true", required=True,
                           help="Confirm you checked sources, app claims, dates, numbers and permissions.")
        if name == "revise":
            p.add_argument("--feedback", required=True)
        if name == "reject":
            p.add_argument("--reason", default="", help="Optional; the bot remembers it for future drafts.")
    args = parser.parse_args(argv)
    if args.command == "doctor":
        import os
        print("Project:", ROOT)
        print("Python:", sys.version.split()[0])
        for task in ("review", "draft"):
            provider = llm.configured_provider(task)
            print(f"{task.capitalize()} provider:", provider)
            try:
                _, model, _ = llm.provider_config(provider)
                print("Key configured: True; model:", model)
            except ValueError as exc:
                print("Key configured: False;", exc)
        print("Owner verified app facts:", product_facts().get("owner_verified", False))
        print("Demo needs no key. Live requests and live model quality have to be verified with your account.")
        return 0
    if args.command == "collect":
        packet = research.collect()
        print("Saved sources:", len(packet["sources"]))
        for warning in packet["warnings"]:
            print("WARNING:", warning)
        return 0 if packet["sources"] else 1
    if args.command == "publish":
        from . import publish
        slug, path = publish.publish(args.job, args.slug, args.description)
        print("Built:", path)
        print("Upload the folder publication/bolcash-guides-site/dist to your static host, then share /guides/" + slug + "/")
        return 0
    if args.command == "sources":
        for s in read_json(ROOT / "data/inbox.json")["sources"]:
            print(s["id"], "|", s["title"], "|", s["published_at"] or "date unknown")
        return 0
    if args.command == "add-url":
        import hashlib
        from urllib.parse import urlsplit
        from .settings import write_json
        inbox = ROOT / "data/inbox.json"
        packet = read_json(inbox) if inbox.exists() else {"sources": [], "warnings": []}
        previous = next((s for s in packet["sources"] if s["url"] == args.url), {})
        text = research.fetch_approved_page.invoke({"url": args.url})
        source = {"id": hashlib.sha256(args.url.encode()).hexdigest()[:12], "url": args.url,
                  "title": args.title, "publisher": previous.get("publisher", urlsplit(args.url).hostname),
                  "text": text, "published_at": previous.get("published_at"),
                  "retrieved_at": datetime.now(ZoneInfo("UTC")).isoformat(),
                  "kind": "manually selected extracted page; feed date retained if known, verify against original"}
        packet["sources"] = [s for s in packet["sources"] if s["id"] != source["id"]] + [source]
        write_json(inbox, packet)
        print("Added source:", source["id"])
        return 0
    with SqliteSaver.from_conn_string(str(ROOT / "data/checkpoints.sqlite")) as saver:
        graph = build_graph(saver)
        if args.command == "scheduled":
            product_facts(live=True)
            scheduled(graph, args.slot)
            return 0
        if args.command == "demo":
            source = {"id": "demo_source", "title": "Fictional training ledger", "publisher": "Tutorial fixture",
                      "url": "local:editorial_notes.md", "published_at": None, "kind": "fictional demo",
                      "text": (ROOT / "editorial_notes.md").read_text(encoding="utf-8")}
            begin(graph, args.job, "How to record a fictional partial payment", [source], demo=True)
            return 0
        if args.command == "start":
            sources = read_json(ROOT / "data/inbox.json")["sources"]
            selected = [s for s in sources if s["id"] == args.source]
            if not selected:
                raise ValueError("Source ID not found. Run collect then sources first.")
            begin(graph, args.job, args.topic, selected)
            return 0
        cfg = config(args.job)
        snapshot = graph.get_state(cfg)
        if not snapshot.values:
            initial = reserved_initial(args.job)
            if initial and args.command == "retry":
                graph.invoke(initial, cfg)
                show(graph.get_state(cfg))
                return 0
            if initial:
                raise ValueError(f"Job reserved but no checkpoint exists. Run: python -m cashbot retry --job {args.job}")
            raise ValueError("Job not found.")
        if args.command == "status":
            show(snapshot)
            return 0
        if args.command == "retry":
            if not snapshot.next or snapshot.values.get("status") == "awaiting_review":
                raise ValueError("Nothing failed to retry. Use status, revise or check-edits instead.")
            graph.invoke(None, cfg)
        elif args.command == "check-edits":
            if snapshot.values.get("status") not in ("blocked", "awaiting_review"):
                raise ValueError("Only blocked or awaiting-review drafts may be edited. Start a new job for approved content.")
            text = paths(snapshot.values)[0].read_text(encoding="utf-8")
            graph.update_state(cfg, {"draft": text, "attempts": 3, "approved_sha": "",
                                     "status": "checking_edits"}, as_node="draft")
            graph.invoke(None, cfg)
        else:
            if snapshot.values.get("status") != "awaiting_review":
                raise ValueError("This job is not awaiting review. Fix blocked drafts with check-edits first.")
            decision = {"action": {"approve": "approve", "revise": "revise", "reject": "reject"}[args.command]}
            if args.command == "approve":
                checked = snapshot.values["draft"]
                on_disk = paths(snapshot.values)[0].read_text(encoding="utf-8")
                if on_disk != checked or args.sha256 != digest(checked):
                    raise ValueError("Draft/hash changed. Run check-edits, review again, then approve with the new hash.")
                decision["sha256"] = args.sha256
            elif args.command == "revise":
                decision["feedback"] = args.feedback
            elif args.command == "reject":
                decision["reason"] = args.reason
            graph.invoke(Command(resume=decision), cfg)
        show(graph.get_state(cfg))
        return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except httpx.HTTPError:
        print("STOPPED: Network request failed. Check your connection/provider status; then retry this job.", file=sys.stderr)
        raise SystemExit(1)
    except (ValueError, OSError, KeyError, sqlite3.Error) as exc:
        print(f"STOPPED: {exc}", file=sys.stderr)
        raise SystemExit(1)
