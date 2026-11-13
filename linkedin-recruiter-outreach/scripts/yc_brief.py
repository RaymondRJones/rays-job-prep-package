#!/usr/bin/env python3
"""Pull the raw material for a company brief from YC: launch posts, news, and each engineering
job's full description, skills, interview process and named hiring manager.

Usage: python3 yc_brief.py OUTDIR slug [slug ...]
Writes OUTDIR/briefs_raw.json: {slug: {company, one_liner, description, founders, launches, news,
                                        jobs:[{title, salary, equity, experience, skills, hiring_manager,
                                               description, interview_process, url}]}}
Polite: ~1-2 s between requests. The hiring manager named on the job is usually the right person to message.
"""
import html, json, os, random, re, sys, time, urllib.request

ENG = re.compile(r"engineer|developer|swe|backend|full.?stack|software|infrastructure|platform|technical staff", re.I)
NOT_ENG = re.compile(r"sales|account exec|marketing|design|recruit|operations|success|strategist|GTM|business dev|intern", re.I)


def props(path):
    req = urllib.request.Request("https://www.ycombinator.com" + path, headers={"User-Agent": "Mozilla/5.0"})
    page = urllib.request.urlopen(req, timeout=30).read().decode()
    time.sleep(1 + random.random())
    return json.loads(html.unescape(re.search(r'data-page="([^"]+)"', page).group(1)))["props"]


def clean(md, n):
    md = re.sub(r"<[^>]+>|\*\*|---+| ", " ", md or "")
    return re.sub(r"\s+", " ", md).strip()[:n]


def main():
    outdir, slugs = sys.argv[1], sys.argv[2:]
    path = os.path.join(outdir, "briefs_raw.json")
    out = json.load(open(path)) if os.path.exists(path) else {}
    for slug in slugs:
        try:
            p = props(f"/companies/{slug}")
        except Exception as e:
            print("skip", slug, e); continue
        co = p["company"]
        rec = {"company": co["name"], "batch": co.get("batch_name") or co.get("batch"), "one_liner": co.get("one_liner"),
               "description": clean(co.get("long_description"), 1200), "team_size": co.get("team_size"),
               "website": co.get("website"),
               "founders": [{"name": f.get("full_name"), "title": f.get("title"), "linkedin": (f.get("linkedin_url") or "").strip(),
                             "bio": clean(f.get("founder_bio"), 500)} for f in co.get("founders", [])],
               "launches": [{"title": l.get("title"), "body": clean(l.get("body"), 1500)} for l in (p.get("launches") or [])[:3]],
               "news": [n.get("title") for n in (p.get("newsItems") or [])[:5]], "jobs": []}
        for j in p.get("jobPostings") or []:
            if not (ENG.search(j.get("title") or "") and not NOT_ENG.search(j.get("title") or "")): continue
            try:
                jj = props(j["url"])["job"]
            except Exception as e:
                print("job skip", j.get("url"), e); continue
            hm = jj.get("hiringManager") or {}
            rec["jobs"].append({"title": jj.get("title"), "salary": jj.get("salaryRange"), "equity": jj.get("equityRange"),
                                "experience": jj.get("minExperience"), "skills": jj.get("skills"),
                                "hiring_manager": f"{hm.get('first_name', '')} {hm.get('last_name', '')}".strip(),
                                "description": clean(jj.get("description"), 2500),
                                "interview_process": clean(jj.get("interview_process"), 600),
                                "url": "https://www.ycombinator.com" + j["url"]})
            if len(rec["jobs"]) >= 2: break
        out[slug] = rec
        print(f"{slug}: {len(rec['launches'])} launches, {len(rec['news'])} news, {len(rec['jobs'])} eng jobs, "
              f"hiring manager: {', '.join(j['hiring_manager'] for j in rec['jobs']) or '-'}")
    json.dump(out, open(path, "w"), indent=1)


if __name__ == "__main__":
    main()
