#!/usr/bin/env python3
"""Find fresh jobs to apply to and add them to the application queue.

No login, no API keys, no browser. Sources:
  1. Public job boards (Greenhouse, Lever, Ashby) for the companies in companies.txt.
     These are also the quickest forms to fill.
  2. Optional: Simplify's public new-grad or internship list (--simplify new-grad|internships).

Files, all in --dir (default ./outreach):
  companies.txt      one company per line; "Name | board | token" once detected (the script fills that in)
  job-search.json    your filters: title terms, exclusions, locations, max age in days, companies to skip
  job-queue.csv      new matches are appended with status "queued"
  applications.csv   read only, so jobs you already applied to are never queued again

Usage:
  find_jobs.py                       # check every company, add new matches to the queue
  find_jobs.py --add "Stripe" "Ramp" # add companies (board is detected automatically)
  find_jobs.py --days 3 --dry-run    # preview without writing
  find_jobs.py --simplify new-grad   # also pull Simplify's new-grad list
"""
import argparse
import csv
import json
import re
import shutil
import sys
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

UA = {"User-Agent": "rays-job-prep-package find-jobs (personal use)"}
BOARDS = {
    "greenhouse": "https://boards-api.greenhouse.io/v1/boards/{token}/jobs",
    "lever": "https://api.lever.co/v0/postings/{token}?mode=json",
    "ashby": "https://api.ashbyhq.com/posting-api/job-board/{token}",
}
SIMPLIFY_LISTS = {
    "new-grad": "https://raw.githubusercontent.com/SimplifyJobs/New-Grad-Positions/dev/.github/scripts/listings.json",
    "internships": "https://raw.githubusercontent.com/SimplifyJobs/Summer2026-Internships/dev/.github/scripts/listings.json",
}
DEFAULT_SEARCH = {
    "titles": ["software engineer", "backend engineer", "backend", "full stack", "platform engineer"],
    "exclude": ["intern", "new grad", "staff", "principal", "manager", "director", "frontend", "ios", "android",
                "embedded", "hardware", "firmware", "security", "solutions", "support", "sales", "recruiter"],
    # A location matches if it contains one of these as a whole word. A bare "Remote" always matches.
    "locations": ["San Francisco", "Bay Area", "United States", "USA", "US"],
    "max_age_days": 7,
    "skip_companies": [],
}
QUEUE_FIELDS = ["found", "company", "role", "location", "system", "linkedin_job_id", "apply_url", "status"]
STARTER = Path(__file__).resolve().parent.parent / "templates" / "companies.txt"


def get_json(url):
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=30) as r:
        return json.load(r)


def parse_time(v):
    if v is None:
        return None
    if isinstance(v, (int, float)):  # epoch: Lever uses ms, Simplify uses seconds
        return datetime.fromtimestamp(v / 1000 if v > 1e11 else v, tz=timezone.utc)
    try:
        t = datetime.fromisoformat(str(v).replace("Z", "+00:00"))
        return t if t.tzinfo else t.replace(tzinfo=timezone.utc)
    except ValueError:
        return None


def detect(company):
    """Try each public board with likely tokens. Returns (board, token) or (None, None)."""
    base = company.lower().strip()
    tokens = dict.fromkeys([re.sub(r"[^a-z0-9]", "", base), re.sub(r"[^a-z0-9]+", "-", base).strip("-")])
    for token in tokens:
        for board, url in BOARDS.items():
            try:
                data = get_json(url.format(token=token))
                if data.get("jobs") if isinstance(data, dict) else data:
                    return board, token
            except (urllib.error.HTTPError, urllib.error.URLError, ValueError, TimeoutError):
                continue
    return None, None


def read_companies(path):
    out = []
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        parts = [p.strip() for p in line.split("|")]
        out.append({"company": parts[0], "board": parts[1] if len(parts) > 2 else "", "token": parts[2] if len(parts) > 2 else ""})
    return out


def write_companies(path, companies):
    lines = ["# One company per line. The script fills in the board and token once it finds them."]
    for c in sorted(companies, key=lambda c: c["company"].lower()):
        lines.append(f"{c['company']} | {c['board']} | {c['token']}" if c["board"] else c["company"])
    path.write_text("\n".join(lines) + "\n")


def fetch_board(c):
    board, token = c["board"], c["token"]
    data = get_json(BOARDS[board].format(token=token))
    jobs = []
    if board == "greenhouse":
        for j in data.get("jobs", []):
            # The hosted form is quicker to fill than the copy embedded in the employer's own site.
            jobs.append(dict(role=j.get("title", ""), location=(j.get("location") or {}).get("name", ""),
                             url=f"https://job-boards.greenhouse.io/{token}/jobs/{j['id']}",
                             posted=j.get("first_published") or j.get("updated_at"), system="Greenhouse"))
    elif board == "lever":
        for j in data:
            jobs.append(dict(role=j.get("text", ""), location=(j.get("categories") or {}).get("location", ""),
                             url=j.get("applyUrl") or j.get("hostedUrl", ""), posted=j.get("createdAt"), system="Lever"))
    else:
        for j in data.get("jobs", []):
            if j.get("isListed") is False:
                continue
            loc = (j.get("location") or "") + (" (Remote)" if j.get("isRemote") else "")
            jobs.append(dict(role=j.get("title", ""), location=loc, url=j.get("applyUrl") or j.get("jobUrl", ""),
                             posted=j.get("publishedAt"), system="Ashby"))
    for j in jobs:
        j["company"] = c["company"]
    return jobs


def fetch_simplify(name):
    jobs = []
    for j in get_json(SIMPLIFY_LISTS[name]):
        if j.get("active") and j.get("is_visible", True) and j.get("url"):
            jobs.append(dict(company=j.get("company_name", ""), role=j.get("title", ""),
                             location="; ".join(j.get("locations") or []), url=j["url"],
                             posted=j.get("date_posted"), system=f"Simplify {name} list"))
    return jobs


def word(term):
    return re.compile(r"(?<![A-Za-z0-9])" + re.escape(term) + r"(?![A-Za-z0-9])", re.I)


def wanted(job, s, cutoff):
    if any(word(x).search(job["role"]) for x in s["exclude"]):
        return False
    if s["titles"] and not any(word(x).search(job["role"]) for x in s["titles"]):
        return False
    loc = job["location"]
    bare_remote = not re.sub(r"(?i)remote|[^a-z]", "", loc)
    if s["locations"] and loc and not bare_remote and not any(word(l).search(loc) for l in s["locations"]):
        return False
    posted = parse_time(job["posted"])
    return posted is None or posted >= cutoff


def url_key(url):
    return re.sub(r"/application/?$", "", url.split("?")[0].split("#")[0].rstrip("/")).lower()


def role_key(company, role):
    return re.sub(r"[^a-z0-9]+", " ", f"{company} {role}".lower()).strip()


def known_jobs(folder):
    """URLs and company+role pairs already queued or applied to."""
    urls, roles = set(), set()
    for name, url_col in (("job-queue.csv", "apply_url"), ("applications.csv", "url")):
        p = folder / name
        if p.exists():
            for row in csv.DictReader(p.open(newline="")):
                if row.get(url_col):
                    urls.add(url_key(row[url_col]))
                roles.add(role_key(row.get("company", ""), row.get("role", "")))
    return urls, roles


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--dir", default="outreach")
    ap.add_argument("--add", nargs="+", metavar="COMPANY", help="add companies to companies.txt, then run")
    ap.add_argument("--days", type=float, help="only jobs posted within this many days (overrides job-search.json)")
    ap.add_argument("--simplify", choices=SIMPLIFY_LISTS, help="also pull one of Simplify's public lists")
    ap.add_argument("--dry-run", action="store_true", help="show matches without writing the queue")
    args = ap.parse_args()

    folder = Path(args.dir).expanduser()
    folder.mkdir(parents=True, exist_ok=True)
    companies_path, search_path, queue_path = folder / "companies.txt", folder / "job-search.json", folder / "job-queue.csv"
    if not companies_path.exists():
        shutil.copy(STARTER, companies_path) if STARTER.exists() else companies_path.write_text("")
        print(f"Created {companies_path} from the starter list. Edit it to match the companies you want.", file=sys.stderr)
    if not search_path.exists():
        search_path.write_text(json.dumps(DEFAULT_SEARCH, indent=2) + "\n")
        print(f"Created {search_path} with default filters. Edit titles, locations and exclusions to fit you.", file=sys.stderr)
    search = {**DEFAULT_SEARCH, **json.loads(search_path.read_text())}
    cutoff = datetime.now(timezone.utc) - timedelta(days=args.days or search["max_age_days"])

    companies = read_companies(companies_path)
    names = {c["company"].lower() for c in companies}
    companies += [{"company": n, "board": "", "token": ""} for n in args.add or [] if n.lower() not in names]
    todo = [c for c in companies if not c["board"]]
    with ThreadPoolExecutor(max_workers=8) as pool:
        for c, (board, token) in zip(todo, pool.map(lambda c: detect(c["company"]), todo)):
            c["board"], c["token"] = board or "", token or ""
    not_found = [c["company"] for c in todo if not c["board"]]
    write_companies(companies_path, companies)

    skip = {s.lower() for s in search["skip_companies"]}
    jobs, failed = [], []
    with ThreadPoolExecutor(max_workers=8) as pool:
        active = [c for c in companies if c["board"] and c["company"].lower() not in skip]
        for c, result in zip(active, pool.map(lambda c: _safe(fetch_board, c), active)):
            (failed.append(c["company"]) if result is None else jobs.extend(result))
    if args.simplify:
        listed = _safe(fetch_simplify, args.simplify)
        (failed.append(f"Simplify {args.simplify}") if listed is None else jobs.extend(j for j in listed if j["company"].lower() not in skip))

    urls, roles = known_jobs(folder)
    new = []
    for j in jobs:
        if not j["url"] or not wanted(j, search, cutoff):
            continue
        uk, rk = url_key(j["url"]), role_key(j["company"], j["role"])
        if uk in urls or rk in roles:
            continue
        urls.add(uk), roles.add(rk)
        new.append(j)
    new.sort(key=lambda j: parse_time(j["posted"]) or cutoff, reverse=True)

    if new and not args.dry_run:
        fields = QUEUE_FIELDS
        if queue_path.exists():
            fields = next(csv.reader(queue_path.open(newline="")), QUEUE_FIELDS)
        with queue_path.open("a", newline="") as f:
            w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
            if f.tell() == 0:
                w.writeheader()
            for j in new:
                w.writerow({"found": date.today().isoformat(), "company": j["company"], "role": j["role"],
                            "location": j["location"], "system": j["system"], "apply_url": j["url"], "status": "queued"})

    for j in new:
        posted = parse_time(j["posted"])
        print(f"{str(posted.date()) if posted else '?':<10}  {j['company']:<18.18}  {j['role']:<58.58}  {j['location']:<28.28}  {j['url']}")
    print(f"\n{len(new)} new job(s) {'found (dry run, nothing written)' if args.dry_run else 'added to ' + str(queue_path)}"
          f" from {len(active)} companies, {len(jobs)} open postings checked.", file=sys.stderr)
    if not_found:
        print("No public Greenhouse/Lever/Ashby board found for: " + ", ".join(not_found)
              + ". Use the LinkedIn search for these.", file=sys.stderr)
    if failed:
        print("Could not read: " + ", ".join(failed), file=sys.stderr)


def _safe(fn, arg):
    try:
        return fn(arg)
    except (urllib.error.HTTPError, urllib.error.URLError, ValueError, TimeoutError, KeyError):
        return None


if __name__ == "__main__":
    main()
