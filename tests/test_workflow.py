import json
import sqlite3
import shutil
from datetime import datetime
from pathlib import Path

import httpx
import pytest
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.types import Command

from cashbot import __main__ as cli
from cashbot import llm, research, settings, workflow

PROJECT = Path(__file__).resolve().parents[1]


@pytest.fixture
def root(tmp_path, monkeypatch):
    for name in ("app_facts.json", "sources.json", "schedule.json", "guide_topics.json",
                 "editorial_notes.md", "demo_article.md"):
        (tmp_path / name).write_bytes((PROJECT / name).read_bytes())
    shutil.copytree(PROJECT / "notes", tmp_path / "notes")
    for module in (settings, cli, llm, research, workflow, workflow.learning):
        monkeypatch.setattr(module, "ROOT", tmp_path)
    facts = settings.read_json(tmp_path / "app_facts.json")
    facts["owner_verified"] = False
    settings.write_json(tmp_path / "app_facts.json", facts)
    settings.ensure_dirs()
    return tmp_path


def make_demo(root, identifier="test-001"):
    source = {"id": "demo_source", "title": "Fictional source", "url": "local:editorial_notes.md",
              "publisher": "Fixture", "text": (root / "editorial_notes.md").read_text()}
    return {"job_id": identifier, "topic": "Partial payments", "format": "guide", "sources": [source],
            "facts": settings.product_facts(), "demo": True, "attempts": 0, "issues": [], "notes": []}


def test_pause_restart_and_hash_bound_export(root):
    cfg = cli.config("test-001")
    with SqliteSaver.from_conn_string(str(root / "data/checkpoints.sqlite")) as saver:
        graph = workflow.build_graph(saver)
        graph.invoke(make_demo(root), cfg)
        state = graph.get_state(cfg)
        assert state.values["status"] == "awaiting_review"
        assert state.next == ("human_review",)
        assert not list((root / "approved").iterdir())
    # A new process/connection can resume the saved interrupt.
    with SqliteSaver.from_conn_string(str(root / "data/checkpoints.sqlite")) as saver:
        graph = workflow.build_graph(saver)
        text = graph.get_state(cfg).values["draft"]
        graph.invoke(Command(resume={"action": "approve", "sha256": workflow.digest(text)}), cfg)
        assert graph.get_state(cfg).values["status"] == "approved"
    approved = (root / "approved/test-001.md").read_text()
    assert "NOT FOR PUBLICATION" in approved
    assert "## Sources" in approved


def test_reject_never_exports(root):
    assert cli.main(["demo", "--job", "reject-001"]) == 0
    assert cli.main(["reject", "--job", "reject-001"]) == 0
    assert not list((root / "approved").iterdir())


def test_changed_draft_cannot_be_approved_with_old_hash(root):
    cli.main(["demo", "--job", "edit-001"])
    path = root / "drafts/edit-001.md"
    original = path.read_text()
    path.write_text(original + "\nOwner changed this sentence.")
    with pytest.raises(ValueError, match="Draft/hash changed"):
        cli.main(["approve", "--job", "edit-001", "--reviewed", "--sha256", workflow.digest(original)])
    assert not list((root / "approved").iterdir())


def test_check_edits_replaces_checked_hash_and_repauses(root):
    cli.main(["demo", "--job", "edit-002"])
    path = root / "drafts/edit-002.md"
    revised = path.read_text() + "\nThis extra sentence is an owner edit to a fictional demonstration."
    path.write_text(revised)
    cli.main(["check-edits", "--job", "edit-002"])
    cli.main(["approve", "--job", "edit-002", "--reviewed", "--sha256", workflow.digest(revised)])
    assert "owner edit" in (root / "approved/edit-002.md").read_text()


def test_invalid_citation_blocks_edit_approval(root):
    cli.main(["demo", "--job", "bad-edit"])
    path = root / "drafts/bad-edit.md"
    path.write_text(path.read_text().replace("[demo_source]", "[invented_source]"))
    cli.main(["check-edits", "--job", "bad-edit"])
    with SqliteSaver.from_conn_string(str(root / "data/checkpoints.sqlite")) as saver:
        state = workflow.build_graph(saver).get_state(cli.config("bad-edit")).values
        assert state["status"] == "blocked"
    assert not list((root / "approved").iterdir())


def test_revisions_are_bounded(root, monkeypatch):
    monkeypatch.setattr(workflow, "basic_checks", lambda *args: ["Unsupported claim"])
    with SqliteSaver.from_conn_string(str(root / "data/test.sqlite")) as saver:
        graph = workflow.build_graph(saver)
        graph.invoke(make_demo(root), cli.config("test-001"))
        state = graph.get_state(cli.config("test-001")).values
        assert state["attempts"] == 3
        assert state["status"] == "blocked"


def test_brief_must_quote_actual_source():
    brief = workflow.Brief(angle="x", claims=[workflow.Claim(statement="x", source_id="s1", quote="Invented quotation")])
    with pytest.raises(ValueError, match="not found"):
        workflow.validate_brief(brief, [{"id": "s1", "text": "Actual source evidence."}])


def test_long_invented_citation_is_blocked(root):
    state = make_demo(root)
    draft = (root / "demo_article.md").read_text(encoding="utf-8") + "\n[approved_product_facts]"
    issues = workflow.basic_checks(draft, state["sources"], state["facts"])
    assert "Unknown source citation marker: approved_product_facts" in issues


def test_no_live_run_without_owner_verified_facts(root):
    with pytest.raises(ValueError, match="owner_verified"):
        cli.main(["scheduled", "--slot", "guide"])


def test_job_and_source_reservations_prevent_duplicate_drafts(root):
    cli.reserve_job("job-a", "source-a")
    with pytest.raises(ValueError, match="already reserved"):
        cli.reserve_job("job-a", "source-b")
    with pytest.raises(ValueError, match="already reserved"):
        cli.reserve_job("job-b", "source-a")


def test_backlog_has_distinct_supporting_notes(root):
    topics = settings.read_json(root / "guide_topics.json")
    assert len(topics) >= 12
    assert len({t["id"] for t in topics}) == len(topics)
    sources = [cli.guide_source(t) for t in topics]
    assert len({s["url"] for s in sources}) == len(topics)
    assert len({s["text"] for s in sources}) == len(topics)
    assert all(len(s["text"]) >= 150 and s["published_at"] is None for s in sources)


def test_scheduled_guide_uses_next_topics_own_notes(root, monkeypatch):
    from types import SimpleNamespace
    monkeypatch.setattr(cli, "used_sources", lambda: {"guide_partial", "guide_upi_unallocated", "guide_dsr_cash",
                                                       "guide_scheme_claim", "guide_credit_limit", "guide_no_overwrite"})
    captured = []
    monkeypatch.setattr(cli, "begin", lambda *args, **kwargs: captured.append(args[3]))
    graph = SimpleNamespace(get_state=lambda cfg: SimpleNamespace(values={}))
    cli.scheduled(graph, "guide")
    source = captured[0][0]
    assert source["id"] == "guide_returns"
    assert source["url"] == "local:notes/goods-returns.md"
    assert "12,000 - 4,200 - 800 = 7,000" in source["text"]
    assert "18,500" not in source["text"]


def test_guide_notes_cannot_escape_project(root):
    with pytest.raises(ValueError):
        cli.guide_source({"id": "bad", "topic": "bad", "notes_file": "../outside.md"})


def test_path_traversal_job_is_rejected():
    with pytest.raises(ValueError):
        settings.job_id("../../outside")


def test_unsafe_or_unapproved_urls_rejected(monkeypatch):
    for url in ("http://pib.gov.in/a", "https://evil.example/a", "https://user:pass@pib.gov.in/a"):
        with pytest.raises(ValueError):
            research.checked_url(url, ["pib.gov.in"])
    monkeypatch.setattr(research.socket, "getaddrinfo", lambda *a, **kw: [(None, None, None, None, ("127.0.0.1", 443))])
    with pytest.raises(ValueError, match="non-public"):
        research.checked_url("https://pib.gov.in/a", ["pib.gov.in"])


def test_page_extraction_is_opt_in(root):
    with pytest.raises(ValueError, match="not enabled"):
        research.fetch_page("https://pib.gov.in/example")


def test_add_url_enrichment_preserves_feed_date(root, monkeypatch):
    from types import SimpleNamespace
    import hashlib
    url = "https://www.gov.uk/government/news/example"
    identifier = hashlib.sha256(url.encode()).hexdigest()[:12]
    date = "2026-10-12T13:08:12+00:00"
    settings.write_json(root / "data/inbox.json", {"sources": [{
        "id": identifier, "url": url, "publisher": "GOV.UK India news",
        "published_at": date, "text": "Short feed summary"}], "warnings": []})
    monkeypatch.setattr(research, "fetch_approved_page", SimpleNamespace(invoke=lambda args: "Verified page text"))
    assert cli.main(["add-url", "--url", url, "--title", "Official release"]) == 0
    sources = settings.read_json(root / "data/inbox.json")["sources"]
    assert len(sources) == 1
    assert sources[0]["published_at"] == date
    assert sources[0]["publisher"] == "GOV.UK India news"
    assert sources[0]["text"] == "Verified page text"
    assert sources[0]["retrieved_at"]


def test_robots_denial_prevents_download(root, monkeypatch):
    monkeypatch.setattr(research, "allowed_by_robots", lambda *a: False)
    monkeypatch.setattr(research, "get_text", lambda *a: pytest.fail("Denied page must not be fetched"))
    rule = [{"enabled": True, "full_text_allowed": True, "hosts": ["pib.gov.in"]}]
    with pytest.raises(ValueError, match="deny"):
        research.fetch_page("https://pib.gov.in/a", rule)



def test_request_limit_covers_failed_attempts(root, monkeypatch):
    monkeypatch.setenv("MAX_API_CALLS_PER_DAY", "1")
    llm.reserve_call()
    with pytest.raises(ValueError, match="limit reached"):
        llm.reserve_call()


def test_feed_collection_deduplicates_links_and_preserves_unknown_dates(root, monkeypatch):
    rss = '''<rss version="2.0"><channel><title>Test</title>
      <item><title>UPI update</title><link>https://pib.gov.in/test</link><description>A useful summary.</description></item>
      <item><title>UPI update again</title><link>https://pib.gov.in/test</link><description>A useful summary.</description></item>
    </channel></rss>'''
    settings.write_json(root / "sources.json", [{"name": "Fixture", "enabled": True,
                        "hosts": ["pib.gov.in"], "feed_url": "https://pib.gov.in/rss", "full_text_allowed": False}])
    monkeypatch.setattr(research, "allowed_by_robots", lambda *a: True)
    monkeypatch.setattr(research, "get_text", lambda *a: (rss, "https://pib.gov.in/rss"))
    monkeypatch.setattr(research, "checked_url", lambda url, hosts: url)
    packet = research.collect()
    assert len(packet["sources"]) == 1
    assert packet["sources"][0]["published_at"] is None


def test_invalid_model_json_does_not_produce_export(root, monkeypatch):
    monkeypatch.setattr(llm, "ask", lambda *a: "not valid JSON")
    state = make_demo(root)
    state["demo"] = False
    with SqliteSaver.from_conn_string(str(root / "data/test.sqlite")) as saver:
        graph = workflow.build_graph(saver)
        with pytest.raises(ValueError):
            graph.invoke(state, cli.config("test-001"))
    assert not list((root / "approved").iterdir())


def test_export_sanitizes_model_html(root):
    state = make_demo(root)
    state["draft"] = (root / "demo_article.md").read_text() + '\n<script>alert(1)</script>\n<a href="javascript:alert(1)">bad link</a>'
    state["approved_sha"] = workflow.digest(state["draft"])
    workflow.paths(state)[0].write_text(state["draft"])
    workflow.export_approved(state)
    preview = (root / "approved/test-001.html").read_text()
    assert "<script" not in preview
    assert "javascript:" not in preview


def test_retry_recovers_reservation_before_first_checkpoint(root, monkeypatch):
    real_build = cli.build_graph
    with monkeypatch.context() as patch:
        def interrupted_build(saver):
            graph = real_build(saver)
            def crash(*args, **kwargs):
                raise RuntimeError("Process stopped before first checkpoint")
            patch.setattr(graph, "invoke", crash)
            return graph
        patch.setattr(cli, "build_graph", interrupted_build)
        with pytest.raises(RuntimeError, match="before first checkpoint"):
            cli.main(["demo", "--job", "crashed"])

    with SqliteSaver.from_conn_string(str(root / "data/checkpoints.sqlite")) as saver:
        assert not real_build(saver).get_state(cli.config("crashed")).values
    assert cli.reserved_initial("crashed")["demo"] is True
    with pytest.raises(ValueError, match="already reserved"):
        cli.main(["demo", "--job", "different-job"])
    assert cli.main(["retry", "--job", "crashed"]) == 0
    with SqliteSaver.from_conn_string(str(root / "data/checkpoints.sqlite")) as saver:
        assert real_build(saver).get_state(cli.config("crashed")).values["status"] == "awaiting_review"
    with pytest.raises(ValueError, match="already reserved"):
        cli.main(["demo", "--job", "crashed"])
    assert not list((root / "approved").iterdir())


def test_reservations_upgrade_existing_database(root):
    with sqlite3.connect(root / "data/jobs.sqlite") as db:
        db.execute("CREATE TABLE jobs(id TEXT PRIMARY KEY, source_id TEXT UNIQUE)")
        db.execute("INSERT INTO jobs VALUES('old-job', 'old-source')")
    cli.reserve_job("new-job", "new-source", {"job_id": "new-job"})
    assert cli.reserved_initial("new-job") == {"job_id": "new-job"}
    assert cli.reserved_initial("old-job") is None
    with pytest.raises(ValueError, match="already reserved"):
        cli.reserve_job("other-job", "old-source")


def test_human_revision_sends_previous_draft_and_feedback(root, monkeypatch):
    cfg = cli.config("revision")
    with SqliteSaver.from_conn_string(str(root / "data/checkpoints.sqlite")) as saver:
        graph = workflow.build_graph(saver)
        graph.invoke(make_demo(root, "revision"), cfg)
        previous = graph.get_state(cfg).values["draft"]
        graph.update_state(cfg, {"demo": False})
        calls = []
        def answer(system, payload, **kwargs):
            calls.append(payload)
            if "previous_draft" in payload:
                return previous + "\nA clearer opening."
            return json.dumps({"issues": [], "notes": []})
        monkeypatch.setattr(llm, "ask", answer)
        graph.invoke(Command(resume={"action": "revise", "feedback": "Shorten the opening"}), cfg)
        assert calls[0]["previous_draft"] == previous
        assert calls[0]["feedback"] == "Shorten the opening"
        assert graph.get_state(cfg).values["status"] == "awaiting_review"
        assert not list((root / "approved").iterdir())


def test_automatic_revision_sends_previous_draft_and_issues(root, monkeypatch):
    state = make_demo(root)
    state.update(demo=False, brief={"angle": "Partial payments", "claims": []})
    payloads = []
    def answer(system, payload, **kwargs):
        payloads.append(payload)
        return "# Revised article"
    monkeypatch.setattr(llm, "ask", answer)
    state.update(workflow.write_draft(state))
    assert payloads[0]["previous_draft"] == ""
    state["issues"] = ["Label the example as fictional"]
    workflow.write_draft(state)
    assert payloads[1]["previous_draft"] == "# Revised article"
    assert payloads[1]["issues"] == state["issues"]


@pytest.mark.parametrize("status", ["approved", "awaiting_review", "failed", "blocked", "rejected", "reserved"])
def test_scheduled_existing_job_reports_next_step(root, monkeypatch, capsys, status):
    class FixedDate(datetime):
        @classmethod
        def now(cls, tz=None):
            return cls(2026, 11, 6, tzinfo=tz)
    monkeypatch.setattr(cli, "datetime", FixedDate)
    identifier = "guide-2026-w45"
    cfg = cli.config(identifier)
    state = make_demo(root, identifier)
    if status == "failed":
        def fail(state):
            raise ValueError("Provider unavailable")
        monkeypatch.setattr(workflow, "make_brief", fail)
    if status == "blocked":
        monkeypatch.setattr(workflow, "basic_checks", lambda *args: ["Fix this claim"])
    with SqliteSaver.from_conn_string(str(root / "data/checkpoints.sqlite")) as saver:
        graph = workflow.build_graph(saver)
        cli.reserve_job(identifier, "demo_source", state)
        if status == "failed":
            with pytest.raises(ValueError, match="Provider unavailable"):
                graph.invoke(state, cfg)
        elif status != "reserved":
            graph.invoke(state, cfg)
            if status == "approved":
                draft = graph.get_state(cfg).values["draft"]
                graph.invoke(Command(resume={"action": "approve", "sha256": workflow.digest(draft)}), cfg)
            elif status == "rejected":
                graph.invoke(Command(resume={"action": "reject"}), cfg)
        before = graph.get_state(cfg)
        monkeypatch.setattr(cli, "begin", lambda *a, **kw: pytest.fail("Must not start another article"))
        cli.scheduled(graph, "guide")
        output = capsys.readouterr().out
        assert "Status:" in output
        if status == "failed":
            assert "Last execution: failed" in output
        action = "retry" if status in ("failed", "reserved") else "check-edits" if status == "blocked" else "status"
        assert f"python -m cashbot {action} --job {identifier}" in output
        if status not in ("failed", "reserved"):
            assert f"Status: {status}" in output
        assert graph.get_state(cfg) == before


def test_guide_format_rejects_citations_and_stock_phrases():
    src = [{"id": "guide_x", "url": "local:notes/x.md"}]
    body = "# T\n\n" + "Word " * 160 + "It's important to note this [guide_x]."
    issues = workflow.basic_checks(body, src, {}, "practical guide")
    assert any("remove [SOURCE_ID]" in i for i in issues)
    assert any("important to note" in i for i in issues)


def test_learning_remembers_edits_feedback_and_exemplars(root):
    from cashbot import learning
    learning.save_ai_draft("j1", "# T\n\nIt is important to note that balances matter a lot today.")
    learning.record_edits("j1", "# T\n\nBalances matter.")
    learning.remember("j1", "reviewer feedback", "Too formal")
    learning.remember("j1", "reviewer feedback", "Too formal")  # duplicate ignored
    got = learning.lessons()
    assert len(got) == 2 and any("human edit" in g for g in got) and "reviewer feedback: Too formal" in got
    learning.add_exemplar("j1", "practical guide", "# Title\n\nBody")
    assert learning.exemplars("practical guide")[0]["title"] == "Title"
    assert learning.exemplars("source-based explainer") == []


def test_publish_builds_page_index_and_refuses_demo(root, monkeypatch):
    from cashbot import publish
    monkeypatch.setattr(publish, "ROOT", root)
    monkeypatch.setenv("SITE_URL", "https://example.com")
    (root / "approved").mkdir(exist_ok=True)
    (root / "approved/j.html").write_text("<body><h1>Credit limits &amp; DSRs</h1><p>First para.</p></body>")
    settings.write_json(root / "approved/j.approval.json", {"demo": False})
    slug, path = publish.publish("j")
    assert slug == "credit-limits-dsrs" and "<h1>Credit limits" in path.read_text()
    assert "/guides/credit-limits-dsrs/" in (root / "publication/bolcash-guides-site/dist/index.html").read_text()
    assert "sitemap.xml" in (root / "publication/bolcash-guides-site/dist/robots.txt").read_text()
    settings.write_json(root / "approved/j.approval.json", {"demo": True})
    with pytest.raises(ValueError):
        publish.publish("j")
