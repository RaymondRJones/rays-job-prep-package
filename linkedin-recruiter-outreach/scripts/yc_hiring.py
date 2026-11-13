#!/usr/bin/env python3
"""Find hiring Y Combinator startups, score them for a candidate, and pull founders + open roles.

Uses the same public search the YC company directory (ycombinator.com/companies) uses: the page embeds a
read-only search key, which this script reads fresh each run. Then it fetches each shortlisted company page
for founders (name, title, LinkedIn, bio) and job postings. Polite: ~1-2 s between company pages.

Usage:
  python3 yc_hiring.py OUTDIR --since "Fall 2024" \
      --metro "San Francisco|Bay Area|Palo Alto|Mountain View|San Jose|Oakland|Berkeley|Redwood City" \
      --remote-us --top 60 \
      --keywords keywords.json        # optional: [[regex, weight, label], ...] tuned to the candidate

Writes OUTDIR/yc_hiring.json (all matches), OUTDIR/yc_enriched.json (top N with founders/jobs),
OUTDIR/companies.csv and OUTDIR/founders.csv (CTO + CEO per company with an engineering opening).
"""
import argparse, csv, html, json, os, random, re, time, urllib.parse, urllib.request

UA = {"User-Agent": "Mozilla/5.0"}
SEASONS = ["Winter", "Spring", "Summer", "Fall"]
DEFAULT_KEYWORDS = [
    [r"\b(AI|LLM|agent|agents|agentic|RAG|retrieval|search)\b", 2, "AI/LLM"],
    [r"backend|infrastructure|infra\b|developer|API|platform|database|data pipeline", 1, "backend/infra"],
    [r"fintech|payments|billing|insurance|accounting", 1, "fintech"],
]
NEGATIVE = r"hardware|robot|biotech|drug|chip|semiconductor|satellite|battery|materials|molecule|wet lab|manufactur"
ENG = re.compile(r"engineer|developer|swe|backend|full.?stack|software|infrastructure|platform|founding engineer|member of technical staff", re.I)
NOT_ENG = re.compile(r"sales|account exec|marketing|design|recruit|operations|success|strategist|GTM|business dev", re.I)


def get(url, data=None, headers=None):
    req = urllib.request.Request(url, data=data, headers={**UA, **(headers or {})})
    return urllib.request.urlopen(req, timeout=30).read().decode()


def batches_since(start):
    season, year = start.split()
    out, y, i = [], int(year), SEASONS.index(season)
    while y <= time.gmtime().tm_year + 1:
        out.append(f"{SEASONS[i]} {y}")
        i += 1
        if i == 4: i, y = 0, y + 1
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("outdir")
    ap.add_argument("--since", default="Fall 2024", help='first batch to include, e.g. "Fall 2024"')
    ap.add_argument("--metro", default="San Francisco|Bay Area", help="regex matched against company locations")
    ap.add_argument("--remote-us", action="store_true", help="also keep fully-remote US companies")
    ap.add_argument("--top", type=int, default=60, help="how many top-scored companies to fetch founders for")
    ap.add_argument("--keywords", help="JSON file of [regex, weight, label] tuned to the candidate")
    a = ap.parse_args()
    os.makedirs(a.outdir, exist_ok=True)

    page = get("https://www.ycombinator.com/companies?isHiring=true")
    opts = json.loads(re.search(r"window\.AlgoliaOpts\s*=\s*(\{.*?\});", page).group(1))
    app, key = opts["app"], opts["key"]
    metro = re.compile(a.metro, re.I)
    kw = json.load(open(a.keywords)) if a.keywords else DEFAULT_KEYWORDS

    hits = []
    for b in batches_since(a.since):
        n = 0
        while True:
            params = urllib.parse.urlencode({"query": "", "hitsPerPage": 1000, "page": n,
                                             "facetFilters": json.dumps([["isHiring:true"], [f"batch:{b}"]])})
            d = json.loads(get(f"https://{app}-dsn.algolia.net/1/indexes/YCCompany_production/query",
                               data=json.dumps({"params": params}).encode(),
                               headers={"X-Algolia-Application-Id": app, "X-Algolia-API-Key": key, "Content-Type": "application/json"}))
            hits += d["hits"]; n += 1
            if n >= d.get("nbPages", 0): break

    keep = []
    for h in hits:
        regs = h.get("regions") or []
        remote_us = ("Fully Remote" in regs or "Remote" in regs) and ("United States of America" in regs or "America / Canada" in regs)
        in_metro = bool(metro.search(h.get("all_locations") or ""))
        if not (in_metro or (a.remote_us and remote_us)): continue
        txt = " ".join([h.get("one_liner") or "", h.get("long_description") or "", " ".join(h.get("tags") or [])])
        score, why = 0, []
        for pat, w, lab in kw:
            if re.search(pat, txt, re.I): score += w; why.append(lab)
        if re.search(NEGATIVE, txt, re.I): score -= 3; why.append("-hardware/bio")
        if 2 <= (h.get("team_size") or 0) <= 40: score += 1
        keep.append({k: h.get(k) for k in ["name", "slug", "website", "all_locations", "one_liner", "long_description", "team_size", "industry", "batch", "tags", "regions"]}
                    | {"where": "metro" if in_metro else "remote-US", "score": score, "why": ", ".join(why)})
    keep.sort(key=lambda c: -c["score"])
    json.dump(keep, open(os.path.join(a.outdir, "yc_hiring.json"), "w"), indent=1)
    print(f"{len(hits)} hiring YC companies since {a.since}; {len(keep)} in metro/remote")

    enriched = []
    for c in keep[:a.top]:
        try:
            p = get(f"https://www.ycombinator.com/companies/{c['slug']}")
            d = json.loads(html.unescape(re.search(r'data-page="([^"]+)"', p).group(1)))["props"]
        except Exception as e:
            print("skip", c["slug"], e); continue
        co = d["company"]
        c["founders"] = [{k: (f.get(k) or "").strip() for k in ["full_name", "title", "linkedin_url", "twitter_url", "founder_bio"]} for f in co.get("founders", [])]
        c["jobs"] = [{k: j.get(k) for k in ["title", "location", "salaryRange", "minExperience", "createdAt", "url"]} for j in (d.get("jobPostings") or [])]
        c["eng_jobs"] = [j for j in c["jobs"] if ENG.search(j["title"] or "") and not NOT_ENG.search(j["title"] or "")]
        c["city"] = co.get("city")
        enriched.append(c)
        time.sleep(1 + random.random())
    json.dump(enriched, open(os.path.join(a.outdir, "yc_enriched.json"), "w"), indent=1)

    comp, fnd = [], []
    for c in enriched:
        if not c["eng_jobs"]: continue
        roles = "; ".join(f"{j['title']} ({j.get('salaryRange') or 'n/a'}, posted {j.get('createdAt') or '?'} ago)" for j in c["eng_jobs"][:3])
        comp.append({"company": c["name"], "source": f"YC {c['batch']}", "where": c["where"], "city": c.get("city") or "",
                     "team_size": c.get("team_size") or "", "one_liner": c.get("one_liner") or "", "eng_roles": roles,
                     "fit": c["score"], "why": c["why"], "website": c.get("website") or "",
                     "yc_url": f"https://www.ycombinator.com/companies/{c['slug']}",
                     "founders": "; ".join(f"{f['full_name']} ({f['title']})" for f in c["founders"])})
        cto = [f for f in c["founders"] if re.search(r"CTO|Chief Technology", f["title"], re.I)]
        ceo = [f for f in c["founders"] if re.search(r"CEO", f["title"], re.I)]
        for f in (cto[:1] + ceo[:1]) or c["founders"][:1]:
            fnd.append({"company": c["name"], "source": f"YC {c['batch']}", "name": f["full_name"], "title": f["title"],
                        "linkedin": f["linkedin_url"], "x": f["twitter_url"], "bio": f["founder_bio"].replace("\n", " ")[:400],
                        "company_one_liner": c.get("one_liner") or "", "open_eng_role": c["eng_jobs"][0]["title"],
                        "fit": c["score"], "why": c["why"], "status": "new", "notes": ""})
    for name, rows in (("companies.csv", comp), ("founders.csv", fnd)):
        if rows:
            with open(os.path.join(a.outdir, name), "w", newline="") as f:
                w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
    print(f"{len(enriched)} enriched; {len(comp)} with engineering openings; {len(fnd)} founder targets")


if __name__ == "__main__":
    main()
