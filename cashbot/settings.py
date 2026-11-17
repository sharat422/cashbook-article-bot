import json
import os
import re
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(os.environ.get("CASHBOT_ROOT", Path(__file__).resolve().parents[1])).resolve()
load_dotenv(ROOT / ".env")
# Keep tracing off in this tutorial. Source text and drafts stay out of trace services.
os.environ["LANGSMITH_TRACING"] = "false"


def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def write_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, indent=2, ensure_ascii=False), encoding="utf-8")
    temporary.replace(path)


def job_id(value):
    if not re.fullmatch(r"[a-z0-9][a-z0-9_-]{0,79}", value):
        raise ValueError("Job ID: use 1-80 lowercase letters, digits, hyphens or underscores.")
    return value


def product_facts(live=False):
    facts = read_json(ROOT / "app_facts.json")
    if live and not facts.get("owner_verified"):
        raise ValueError("Review app_facts.json; set owner_verified=true only after checking it.")
    return facts


def ensure_dirs():
    for name in ("data", "drafts", "approved", "logs"):
        (ROOT / name).mkdir(parents=True, exist_ok=True)
