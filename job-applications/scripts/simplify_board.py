#!/usr/bin/env python3
"""Find jobs on Simplify's job board (simplify.jobs/jobs) that fit you, and add them to the queue.

Simplify lists far more companies than the public Greenhouse/Lever/Ashby boards that find_jobs.py reads,
including employers on Workday, SmartRecruiters and their own sites. This script:

  1. Searches the board the same way the simplify.jobs page does (no login): full-time software, backend
     and full-stack roles at the levels and work arrangement you choose (remote US by default).
  2. Opens each posting's public page for its requirements, skills, salary and location notes.
  3. Scores the fit against the "fit" block of job-search.json: years of experience asked for, skills you
     have, clearance and location limits, salary floor. Jobs outside your range are dropped with a reason.
     It also reads the company's stack out of the posting text (languages, frameworks, datastores, cloud)
     and checks each item against fit.skills, which should hold everything on your resume and LinkedIn.
     Stack languages you don't have lower the score and are listed, so you know before you apply.
  4. Resolves Simplify's apply link to the employer's own form and appends the keepers to job-queue.csv.
     Every kept and dropped job, with the reasons, goes to simplify-matches.csv.

This uses the search key that simplify.jobs ships to every browser. It is not an official API, so it can
change without notice; the script reads it from the live page each time it stops working. Keep runs small
(the defaults fetch at most 60 posting pages, one at a time).

Files, all in --dir (default ./outreach):
  job-search.json      title terms, exclusions, skip list (shared with find_jobs.py) plus a "fit" block
  job-queue.csv        new matches are appended with status "queued"
  simplify-matches.csv every job checked this run: fit score, years asked, matched/missing skills, reasons
  applications.csv     read only, so jobs already applied to are never queued again

Usage:
  simplify_board.py --dry-run                 # preview remote US mid/senior matches, write nothing
  simplify_board.py                           # add matches to the queue
  simplify_board.py --where bay-area --days 7 # Bay Area roles (on-site, hybrid or remote) from the last week
  simplify_board.py --limit 120 --min-fit 50  # look at more postings, keep only strong fits
"""
import argparse
import csv
import html
import json
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from find_jobs import DEFAULT_SEARCH, QUEUE_FIELDS, known_jobs, role_key, url_key, word  # noqa: E402

UA = {"User-Agent": "Mozilla/5.0 (compatible; rays-job-prep-package simplify-board; personal job search)"}
SITE = "https://simplify.jobs"
SEARCH_HOST = "https://js-ha.simplify.jobs"
KEY_FILE = ".simplify-search-key"
FUNCTIONS = ["Software Engineering", "Backend Engineering", "Full-Stack Engineering"]
LEVELS = {"junior": "Junior", "mid": "Mid Level", "senior": "Senior", "expert": "Expert or higher"}
BAY_AREA = ["San Francisco", "Bay Area", "San Jose", "Oakland", "Palo Alto", "Mountain View", "Menlo Park",
            "Sunnyvale", "Santa Clara", "San Mateo", "Redwood City", "Foster City", "Burlingame", "South San Francisco",
            "Cupertino", "Fremont", "Emeryville", "Berkeley", "Los Gatos", "Milpitas"]
DEFAULT_FIT = {
    "years": 6,                     # your professional years
    "min_required_years": 2,        # drop jobs asking for fewer years than this (junior roles)
    "max_required_years": 8,        # drop jobs asking for more years than this
    "levels": ["mid", "senior"],
    "home_state": "California",     # remote roles limited to other states are dropped
    "min_salary": 0,                # drop jobs whose top of range is below this (0 = no floor)
    "min_fit": 30,                  # drop jobs scoring below this (0-100)
    "skills": [],                   # your skills; matched against each posting's skill list
    "reject_terms": ["security clearance", "ts/sci", "top secret", "secret clearance", "polygraph",
                     "active clearance", "public trust clearance"],
}
ALIASES = {"golang": "go", "js": "javascript", "ts": "typescript", "postgres": "postgresql", "k8s": "kubernetes",
           "amazon web services": "aws", "aws lambda": "lambda", "amazon dynamodb": "dynamodb", "amazon s3": "s3",
           "amazon sqs": "sqs", "azure cosmos db": "cosmos db", "cosmosdb": "cosmos db", "spring boot": "spring",
           "node.js": "node", "nodejs": "node", "react.js": "react", "reactjs": "react", "large language models": "llm",
           "llms": "llm", "retrieval augmented generation": "rag", "model context protocol": "mcp", "restful apis": "rest",
           "rest apis": "rest", "rest api": "rest", "microservices architecture": "microservices", "sql databases": "sql"}
LANGUAGES = {"java", "python", "javascript", "typescript", "go", "rust", "c++", "c#", "ruby", "kotlin", "scala",
             "swift", "php", "elixir", "c", "clojure", "haskell", "erlang", "objective-c", "dart", "node"}
# Technologies to look for in the posting text itself (Simplify's skill tags miss the company's actual stack).
# name -> pattern; "go" is matched case-sensitively so the English word doesn't count.
STACK = {
    "java": r"\bjava\b(?!script)", "python": r"\bpython\b", "typescript": r"\btypescript\b", "javascript": r"\bjavascript\b",
    "node": r"\bnode(?:\.js|js)?\b", "go": r"(?-i:\bGo\b)|\bgolang\b", "rust": r"\brust\b", "ruby": r"\bruby\b",
    "rails": r"\brails\b", "elixir": r"\belixir\b", "kotlin": r"\bkotlin\b", "scala": r"\bscala\b", "c#": r"c#|\.net\b",
    "c++": r"c\+\+", "php": r"\bphp\b", "clojure": r"\bclojure\b", "spring": r"\bspring\b", "django": r"\bdjango\b",
    "fastapi": r"\bfastapi\b", "flask": r"\bflask\b", "react": r"\breact\b", "angular": r"\bangular\b", "vue": r"\bvue\b",
    "graphql": r"\bgraphql\b", "grpc": r"\bgrpc\b", "postgresql": r"\bpostgres(?:ql)?\b", "mysql": r"\bmysql\b",
    "dynamodb": r"\bdynamodb\b", "mongodb": r"\bmongo(?:db)?\b", "redis": r"\bredis\b", "kafka": r"\bkafka\b",
    "spark": r"\bspark\b", "flink": r"\bflink\b", "snowflake": r"\bsnowflake\b", "elasticsearch": r"\belasticsearch\b",
    "cassandra": r"\bcassandra\b", "aws": r"\baws\b|amazon web services", "gcp": r"\bgcp\b|google cloud",
    "azure": r"\bazure\b", "kubernetes": r"\bkubernetes\b|\bk8s\b", "docker": r"\bdocker\b", "terraform": r"\bterraform\b",
    "lambda": r"\blambda\b", "llm": r"\bllms?\b|large language model", "rag": r"\brag\b", "langchain": r"\blangchain\b|langgraph",
    "mcp": r"\bmcp\b|model context protocol",
}


# ---------- Simplify access ----------

def fetch(url, data=None, headers=None, timeout=30):
    req = urllib.request.Request(url, data=data, headers={**UA, **(headers or {})})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read().decode("utf-8", "replace")


def search_key(folder, refresh=False):
    """The public search key simplify.jobs gives every browser, cached in the folder."""
    cache = folder / KEY_FILE
    if cache.exists() and not refresh:
        return cache.read_text().strip()
    page = fetch(f"{SITE}/jobs")
    for src in re.findall(r'src="(/[^"]+\.js)"', page):
        js = fetch(SITE + src)
        if "js-ha.simplify.jobs" in js:
            m = re.search(r'js-ha\.simplify\.jobs.{0,400}?apiKey:"([A-Za-z0-9+/=]{40,})"', js, re.S)
            if m:
                cache.write_text(m.group(1))
                return m.group(1)
    raise RuntimeError("Could not find the search key on simplify.jobs; the page may have changed.")


def search(folder, filter_by, page, per_page=100):
    params = {"q": "*", "query_by": "title", "filter_by": filter_by, "sort_by": "start_date:desc",
              "page": page, "per_page": per_page}
    url = f"{SEARCH_HOST}/collections/jobs/documents/search?{urllib.parse.urlencode(params)}"
    for attempt in (0, 1):
        try:
            return json.loads(fetch(url, headers={"X-TYPESENSE-API-KEY": search_key(folder, refresh=attempt == 1)}))
        except urllib.error.HTTPError as e:
            if e.code not in (401, 403) or attempt:
                raise


def posting(job_id):
    page = fetch(f"{SITE}/p/{job_id}")
    m = re.search(r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>', page, re.S)
    return json.loads(m.group(1))["props"]["pageProps"].get("jobPosting") if m else None


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *a, **k):
        return None


def apply_url(click_url):
    """Simplify's apply link redirects to the employer's form; return that form's address without tracking."""
    try:
        urllib.request.build_opener(_NoRedirect).open(urllib.request.Request(click_url, headers=UA), timeout=20)
    except urllib.error.HTTPError as e:
        loc = e.headers.get("Location")
        if e.code in (301, 302, 303, 307, 308) and loc:
            parts = urllib.parse.urlsplit(loc)
            query = [(k, v) for k, v in urllib.parse.parse_qsl(parts.query) if not k.lower().startswith(("utm_", "gh_src"))]
            return urllib.parse.urlunsplit(parts._replace(query=urllib.parse.urlencode(query)))
    except (urllib.error.URLError, TimeoutError):
        pass
    return click_url


def system_of(url):
    host = urllib.parse.urlsplit(url).netloc.lower()
    for key, name in (("greenhouse", "Greenhouse"), ("ashbyhq", "Ashby"), ("lever.co", "Lever"),
                      ("myworkdayjobs", "Workday"), ("smartrecruiters", "SmartRecruiters"), ("icims", "iCIMS"),
                      ("workable", "Workable"), ("jobvite", "Jobvite"), ("bamboohr", "BambooHR"),
                      ("simplify.jobs", "Simplify link")):
        if key in host:
            return name
    return host or "unknown"


# ---------- fit ----------

def norm(skill):
    s = re.sub(r"\s+", " ", skill.lower().strip())
    return ALIASES.get(s, s)


def text_of(p):
    parts = [html.unescape(re.sub(r"<[^>]+>", " ", p.get("description") or ""))]
    parts += [str(x) for x in (p.get("requirements") or []) + (p.get("additional_requirements") or [])]
    parts.append(p.get("additional_location_info") or "")
    return " ".join(parts)


YEARS = re.compile(r"(\d{1,2})\s*(?:\+|plus)?\s*(?:(?:-|–|to)\s*(\d{1,2})\s*\+?)?\s*(?:years|yrs)", re.I)


def years_asked(p):
    """Smallest years figure in each requirement that mentions experience; the largest of those binds."""
    found = []
    for line in [str(x) for x in p.get("requirements") or []] or re.split(r"(?<=[.;])\s|<li>", p.get("description") or ""):
        if re.search(r"experience|exp\b|professional|industry", line, re.I):
            found += [int(m.group(1)) for m in YEARS.finditer(line) if 0 < int(m.group(1)) < 30]
    return max(found) if found else None


def location_ok(doc, p, fit):
    """Remote roles must be open to the US as a whole or to your home state."""
    state = fit["home_state"].lower()
    abbrev = {"california": "ca"}.get(state, "")
    locs = [str(l) for l in doc.get("locations") or []] + [str(l) for l in doc.get("remote_locations") or []]
    note = (p.get("additional_location_info") or "").lower()
    limit = re.search(r"must (?:live|reside|be located|be based)(?: in| within)?(.{0,80})", note)
    if limit and not re.search(r"united states|\bu\.?s\.?a?\b|" + state + (r"|\b" + abbrev + r"\b" if abbrev else ""), limit.group(1)):
        return False, f"location limited: {p.get('additional_location_info')}"
    remote_only = [l for l in locs if l.lower().startswith("remote in")]
    if remote_only and not any(re.search(r"usa|united states|" + state + (r"|\b" + abbrev + r"\b" if abbrev else ""), l, re.I)
                               for l in remote_only):
        return False, "remote only in " + ", ".join(remote_only)
    return True, ""


def score(doc, p, fit, mine):
    reasons, gaps = [], []
    asked = years_asked(p)
    if asked is not None and asked > fit["max_required_years"]:
        reasons.append(f"asks {asked}+ years (above {fit['max_required_years']})")
    if asked is not None and asked < fit["min_required_years"]:
        reasons.append(f"asks {asked}+ years (junior)")
    body = text_of(p).lower()
    hit = next((t for t in fit["reject_terms"] if t in body), None)
    if hit:
        reasons.append(f"requires {hit}")
    ok, why = location_ok(doc, p, fit)
    if not ok:
        reasons.append(why)
    top = p.get("max_salary") or p.get("min_salary")
    if fit["min_salary"] and top and (p.get("salary_period") in (None, "", 1, "year", "yearly")) and top < fit["min_salary"]:
        reasons.append(f"pays up to {int(top):,}")

    # The company's stack as written in the posting, checked against the skills on your resume and LinkedIn.
    stack = stack_of(text_of(p))
    stack_have = sorted(t for t in stack if t in mine)
    stack_gap = sorted(t for t in stack if t not in mine)
    skills = [s.get("name", "") for s in p.get("skills") or [] if s.get("name")]
    theirs = {norm(s) for s in skills} | stack
    matched = sorted({norm(s) for s in skills if norm(s) in mine} | set(stack_have))
    missing = sorted({norm(s) for s in skills if norm(s) not in mine} | set(stack_gap))
    langs = {s for s in theirs if s in LANGUAGES}
    if langs and not langs & mine:
        gaps.append("no stack language on your resume: " + ", ".join(sorted(langs)))
    elif langs - mine:
        gaps.append("stack not on your resume: " + ", ".join(sorted(langs - mine)))
    # Skills overlap is most of the score; a years figure inside your range adds confidence;
    # stack languages you don't have pull it down.
    fit_score = round(85 * len(matched) / max(4, len(theirs))) if theirs else 40
    if asked is not None and fit["min_required_years"] <= asked <= fit["years"]:
        fit_score += 15
    elif asked is None:
        fit_score += 5
    if langs and not langs & mine:
        fit_score -= 25
    else:
        fit_score -= 5 * min(3, len(langs - mine))
    return max(0, min(100, fit_score)), asked, matched, missing, reasons, gaps, stack_have, stack_gap


def stack_of(text):
    return {name for name, pat in STACK.items() if re.search(pat, text, re.I)}


# ---------- main ----------

def filter_for(where, levels, cutoff):
    lv = ",".join(f"`{LEVELS[l]}`" for l in levels)
    fn = ",".join(f"`{f}`" for f in FUNCTIONS)
    parts = [f"functions:=[{fn}]", f"experience_level:=[{lv}]", "type:=Full-Time",
             "physical_countries:=[`United States`]", f"start_date:>={int(cutoff.timestamp())}"]
    if where == "remote":
        parts.append("travel_requirements:=Remote")
    return " && ".join(parts)


def in_bay_area(doc):
    return any(any(c.lower() in str(l).lower() for c in BAY_AREA) for l in doc.get("locations") or [])


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--dir", default="outreach")
    ap.add_argument("--where", choices=["remote", "bay-area"], default="remote",
                    help="remote: remote US roles (default); bay-area: any arrangement with a Bay Area location")
    ap.add_argument("--days", type=float, help="posted within this many days (default: job-search.json max_age_days)")
    ap.add_argument("--limit", type=int, default=60, help="most posting pages to open (default 60)")
    ap.add_argument("--min-fit", type=int, help="keep jobs scoring at least this (default: fit.min_fit)")
    ap.add_argument("--easy-forms", action="store_true",
                    help="keep only Greenhouse, Ashby and Lever forms (single page, no account needed)")
    ap.add_argument("--dry-run", action="store_true", help="show matches without writing the queue")
    args = ap.parse_args()

    folder = Path(args.dir).expanduser()
    folder.mkdir(parents=True, exist_ok=True)
    search_path, queue_path, report_path = folder / "job-search.json", folder / "job-queue.csv", folder / "simplify-matches.csv"
    saved = json.loads(search_path.read_text()) if search_path.exists() else {}
    s = {**DEFAULT_SEARCH, **saved}
    fit = {**DEFAULT_FIT, **saved.get("fit", {})}
    if "fit" not in saved:
        print(f"No \"fit\" block in {search_path}; using defaults. Add your years and skills there for better scores.",
              file=sys.stderr)
    min_fit = fit["min_fit"] if args.min_fit is None else args.min_fit
    mine = {norm(x) for x in fit["skills"]}
    cutoff = datetime.now(timezone.utc) - timedelta(days=args.days or s["max_age_days"])
    skip = {c.lower() for c in s["skip_companies"]}
    urls, roles = known_jobs(folder)

    # 1. Candidates from the board, newest first, passing the shared title filters.
    filt, candidates, page, found = filter_for(args.where, fit["levels"], cutoff), [], 1, 0
    while len(candidates) < args.limit:
        res = search(folder, filt, page)
        found = res.get("found", 0)
        for hit in res.get("hits", []):
            d = hit["document"]
            title, company = d.get("title", ""), d.get("company_name", "")
            if company.lower() in skip or role_key(company, title) in roles:
                continue
            if any(word(x).search(title) for x in s["exclude"]) or not any(word(x).search(title) for x in s["titles"]):
                continue
            if args.where == "bay-area" and not in_bay_area(d):
                continue
            candidates.append(d)
        if not res.get("hits") or page * 100 >= found:
            break
        page += 1
        time.sleep(0.5)
    candidates = candidates[:args.limit]

    # 2-3. Open each posting, score it.
    rows, kept = [], []
    for i, d in enumerate(candidates, 1):
        print(f"\rChecking {i}/{len(candidates)}: {d.get('company_name', '')[:30]:<30}", end="", file=sys.stderr)
        try:
            p = posting(d["id"])
        except (urllib.error.URLError, ValueError, KeyError, TimeoutError):
            p = None
        time.sleep(0.4)
        if not p or not p.get("active", True):
            continue
        fit_score, asked, matched, missing, reasons, gaps, stack_have, stack_gap = score(d, p, fit, mine)
        if fit_score < min_fit and not reasons:
            reasons.append(f"fit {fit_score} below {min_fit}")
        salary = ""
        if p.get("min_salary") or p.get("max_salary"):
            salary = "-".join(f"{int(x):,}" for x in (p.get("min_salary"), p.get("max_salary")) if x)
        row = {"checked": date.today().isoformat(), "company": d.get("company_name", ""), "role": d.get("title", ""),
               "location": "; ".join(str(l) for l in d.get("locations") or []),
               "arrangement": d.get("travel_requirements", ""), "fit": fit_score,
               "years_asked": "" if asked is None else asked, "salary": salary,
               "stack_on_resume": ", ".join(stack_have), "stack_not_on_resume": ", ".join(stack_gap),
               "matched_skills": ", ".join(matched), "missing_skills": ", ".join(missing),
               "notes": "; ".join(gaps), "dropped_because": "; ".join(reasons),
               "simplify_url": f"{SITE}/p/{d['id']}", "apply_url": "", "posted": ""}
        posted = datetime.fromtimestamp(d["start_date"], tz=timezone.utc).date().isoformat() if d.get("start_date") else ""
        row["posted"] = posted
        if not reasons:
            row["apply_url"] = apply_url(p.get("url") or f"{SITE}/jobs/click/{d['id']}")
            time.sleep(0.3)
            if url_key(row["apply_url"]) in urls:
                continue
            if args.easy_forms and system_of(row["apply_url"]) not in ("Greenhouse", "Ashby", "Lever"):
                row["dropped_because"] = f"form on {system_of(row['apply_url'])} (--easy-forms)"
                rows.append(row)
                continue
            urls.add(url_key(row["apply_url"]))
            kept.append(row)
        rows.append(row)
    print(file=sys.stderr)
    kept.sort(key=lambda r: r["posted"], reverse=True)
    kept.sort(key=lambda r: r["fit"], reverse=True)

    # 4. Write.
    if not args.dry_run:
        if rows:
            old = list(csv.DictReader(report_path.open(newline=""))) if report_path.exists() else []
            fields = list(dict.fromkeys([*(old[0].keys() if old else []), *rows[0].keys()]))
            with report_path.open("w", newline="") as f:
                w = csv.DictWriter(f, fieldnames=fields, restval="")
                w.writeheader()
                w.writerows(old + rows)
        if kept:
            fields = next(csv.reader(queue_path.open(newline="")), QUEUE_FIELDS) if queue_path.exists() else QUEUE_FIELDS
            with queue_path.open("a", newline="") as f:
                w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
                if f.tell() == 0:
                    w.writeheader()
                for r in kept:
                    w.writerow({"found": r["checked"], "company": r["company"], "role": r["role"],
                                "location": r["location"] or r["arrangement"], "system": system_of(r["apply_url"]),
                                "apply_url": r["apply_url"], "status": "queued"})

    for r in kept:
        print(f"{r['fit']:>3}  {r['posted']:<10}  {r['company']:<22.22}  {r['role']:<52.52}  "
              f"{str(r['years_asked']) + '+ yrs' if r['years_asked'] != '' else '':<7}  {system_of(r['apply_url']):<15.15}  "
              f"{r['notes']}")
    dropped = [r for r in rows if r["dropped_because"]]
    print(f"\n{found} jobs on the board match the search; {len(candidates)} opened, {len(kept)} kept"
          f"{' (dry run, nothing written)' if args.dry_run else ' and added to ' + str(queue_path)}, {len(dropped)} dropped"
          f"{'' if args.dry_run else ' (reasons in ' + str(report_path) + ')'}.", file=sys.stderr)
    if args.dry_run and dropped:
        for r in dropped[:15]:
            print(f"  dropped: {r['company']} - {r['role'][:50]}: {r['dropped_because']}", file=sys.stderr)


if __name__ == "__main__":
    main()
