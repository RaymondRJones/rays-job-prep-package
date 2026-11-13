#!/usr/bin/env python3
"""Watchlist + public job-board checker for the hiring monitor.

No login, no API keys: uses the public Greenhouse, Lever and Ashby job-board APIs.
State lives in a folder (default ./monitor):
  watchlist.json  [{"company": "Stripe", "board": "greenhouse", "token": "stripe"}, ...]
  settings.json   {"roles": [...], "focus": [...], "exclude": [...], "locations": [...]}
  seen.json       {"<job id>": "<first seen ISO time>", ...}

Commands:
  job_boards.py add "Stripe" [--board greenhouse --token stripe]   # auto-detects board if omitted
  job_boards.py remove "Stripe"
  job_boards.py list
  job_boards.py check [--since-days 7] [--mark-seen]                # prints NEW matching jobs as JSON
"""
import argparse
import json
import re
import sys
import urllib.error
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path

UA = {"User-Agent": "rays-job-prep-package hiring-monitor (personal use)"}
BOARDS = {
    "greenhouse": "https://boards-api.greenhouse.io/v1/boards/{token}/jobs",
    "lever": "https://api.lever.co/v0/postings/{token}?mode=json",
    "ashby": "https://api.ashbyhq.com/posting-api/job-board/{token}",
}
DEFAULT_SETTINGS = {
    # A job must match one ROLE term; FOCUS terms don't filter, they're reported for fit scoring.
    "roles": ["engineer", "developer", "SWE"],
    "focus": ["backend", "infrastructure", "platform", "distributed", "AI", "ML", "LLM", "data"],
    "exclude": ["intern", "new grad", "manager", "director", "sales", "recruiter", "hardware",
                "solutions architect", "solutions engineer", "support engineer", "counsel"],
    "locations": ["Remote", "United States", "Seattle", "San Francisco", "Bay Area", "New York"],
}


def get_json(url):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def load(path, default):
    return json.loads(path.read_text()) if path.exists() else default


def save(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2))


def slug_candidates(company):
    base = company.lower().strip()
    return list(dict.fromkeys([re.sub(r"[^a-z0-9]", "", base), re.sub(r"[^a-z0-9]+", "-", base).strip("-")]))


def detect(company):
    """Try each public board with likely tokens. Returns (board, token) or (None, None)."""
    for token in slug_candidates(company):
        for board, url in BOARDS.items():
            try:
                data = get_json(url.format(token=token))
                jobs = data.get("jobs") if isinstance(data, dict) else data
                if jobs:
                    return board, token
            except (urllib.error.HTTPError, urllib.error.URLError, ValueError, TimeoutError):
                continue
    return None, None


def parse_time(v):
    if v is None:
        return None
    if isinstance(v, (int, float)):  # Lever: epoch ms
        return datetime.fromtimestamp(v / 1000, tz=timezone.utc)
    try:
        return datetime.fromisoformat(str(v).replace("Z", "+00:00"))
    except ValueError:
        return None


def fetch(entry):
    board, token, company = entry["board"], entry["token"], entry["company"]
    data = get_json(BOARDS[board].format(token=token))
    out = []
    if board == "greenhouse":
        for j in data.get("jobs", []):
            out.append(dict(id=f"gh:{token}:{j['id']}", title=j.get("title", ""), location=(j.get("location") or {}).get("name", ""),
                            url=j.get("absolute_url", ""), posted=j.get("first_published") or j.get("updated_at")))
    elif board == "lever":
        for j in data:
            cat = j.get("categories") or {}
            out.append(dict(id=f"lv:{token}:{j['id']}", title=j.get("text", ""), location=cat.get("location", ""),
                            team=cat.get("team", ""), url=j.get("hostedUrl", ""), posted=j.get("createdAt")))
    elif board == "ashby":
        for j in data.get("jobs", []):
            loc = j.get("location", "") + (" (Remote)" if j.get("isRemote") else "")
            out.append(dict(id=f"ab:{token}:{j.get('id') or j.get('jobUrl')}", title=j.get("title", ""), location=loc,
                            team=j.get("team", "") or j.get("department", ""), url=j.get("jobUrl", ""), posted=j.get("publishedAt")))
    for j in out:
        j["company"] = company
        j["source"] = f"{board} job board"
    return out


def word(term):
    return re.compile(r"(?<![A-Za-z0-9])" + re.escape(term) + r"(?![A-Za-z0-9])", re.I)


def matches(job, s):
    text = f"{job['title']} {job.get('team', '')}"
    if any(word(x).search(text) for x in s["exclude"]):
        return False
    if s.get("roles") and not any(word(k).search(text) for k in s["roles"]):
        return False
    if s["locations"] and job["location"] and not any(re.search(re.escape(l), job["location"], re.I) for l in s["locations"]):
        return False
    return True


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", default="monitor")
    sub = ap.add_subparsers(dest="cmd", required=True)
    a = sub.add_parser("add"); a.add_argument("company"); a.add_argument("--board", choices=BOARDS); a.add_argument("--token")
    r = sub.add_parser("remove"); r.add_argument("company")
    sub.add_parser("list")
    c = sub.add_parser("check"); c.add_argument("--since-days", type=float, default=7); c.add_argument("--mark-seen", action="store_true")
    args = ap.parse_args()

    d = Path(args.dir)
    wl_path, st_path, seen_path = d / "watchlist.json", d / "settings.json", d / "seen.json"
    wl = load(wl_path, [])
    if not st_path.exists():
        save(st_path, DEFAULT_SETTINGS)

    if args.cmd == "add":
        if any(e["company"].lower() == args.company.lower() for e in wl):
            print(f"{args.company} is already on the watchlist"); return
        board, token = (args.board, args.token) if args.board and args.token else detect(args.company)
        wl.append({"company": args.company, "board": board, "token": token})
        save(wl_path, wl)
        print(f"Added {args.company}: " + (f"{board} board '{token}'" if board else
              "no public Greenhouse/Lever/Ashby board found; the agent should use the careers site + web search"))
    elif args.cmd == "remove":
        new = [e for e in wl if e["company"].lower() != args.company.lower()]
        save(wl_path, new)
        print(f"Removed {args.company}" if len(new) < len(wl) else f"{args.company} was not on the watchlist")
    elif args.cmd == "list":
        for e in wl:
            print(f"- {e['company']}: " + (f"{e['board']} ({e['token']})" if e.get("board") else "careers site + web search"))
        if not wl:
            print("(watchlist is empty)")
    elif args.cmd == "check":
        s = load(st_path, DEFAULT_SETTINGS)
        seen = load(seen_path, {})
        cutoff = datetime.now(timezone.utc) - timedelta(days=args.since_days)
        new, errors, no_board = [], [], []
        for e in wl:
            if not e.get("board"):
                no_board.append(e["company"]); continue
            try:
                for j in fetch(e):
                    t = parse_time(j["posted"])
                    if j["id"] in seen or (t and t < cutoff) or not matches(j, s):
                        continue
                    j["posted"] = t.isoformat() if t else None
                    j["focus_hits"] = [f for f in s.get("focus", []) if word(f).search(f"{j['title']} {j.get('team', '')}")]
                    new.append(j)
            except Exception as ex:  # one broken board shouldn't stop the run
                errors.append(f"{e['company']}: {ex}")
        if args.mark_seen:
            now = datetime.now(timezone.utc).isoformat()
            seen.update({j["id"]: now for j in new})
            save(seen_path, seen)
        json.dump({"new_jobs": new, "needs_web_search": no_board, "errors": errors}, sys.stdout, indent=2)
        print()


if __name__ == "__main__":
    main()
