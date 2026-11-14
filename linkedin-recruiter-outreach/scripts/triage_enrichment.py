#!/usr/bin/env python3
"""Triage enrichment from enrich-api.js against recruiters.csv.

Usage: python3 triage_enrichment.py enr.json outreach/recruiters.csv outreach/ [--metro "San Francisco|Bay Area|..."]
Writes outreach/enriched2.json, outreach/enriched.md, and adds columns to recruiters.csv:
fit2 (green/yellow/red), reason2, flags, open_profile, degree, mutuals, hook, last_messaged, linkedin.

Rules: already messaged -> red. No current role at the target company -> red (left). Job title names a wrong desk
(university, exec, hardware, non-engineering, security, coordinator, research) and no engineering keyword -> red.
Title says staff/principal/exec -> yellow. Engineering keyword in title -> green; only in description/About/posts ->
green with "desc:" (weaker). Otherwise yellow (generalist). Mixed desks are noted as "also mentions", never downgraded.
Location: profile location, else the current job's location, must match --metro.
Tune GOOD/BAD/COS for the candidate and target companies."""
import argparse, csv, json, re, sys
from collections import Counter

BAY = re.compile(r"San Francisco|Bay Area|San Jose|Mountain View|Santa Clara|Cupertino|Menlo Park|Palo Alto|Sunnyvale|"
                 r"Fremont|Oakland|Berkeley|San Mateo|Redwood City|Los Gatos|Los Altos|Milpitas|Saratoga|Hayward|"
                 r"Walnut Creek|San Ramon|Dublin|Pleasanton|Livermore|Belmont|Burlingame|Foster City|Daly City|"
                 r"San Bruno|Millbrae|Campbell|Newark|Union City|Alameda|Concord|Lafayette|Richmond|San Leandro|"
                 r"Morgan Hill|Stanford|La Honda|Santa Cruz|Aptos|Petaluma|Novato|San Rafael|Emeryville|Half Moon Bay|"
                 r"Danville|Orinda|Moraga|Pacifica|Brisbane|South San Francisco|Mill Valley|Sausalito|Woodside|Atherton|Portola Valley", re.I)
GOOD = re.compile(r"software|\bSWE\b|backend|back-end|infrastructure|\binfra\b|cloud|\bAI\b|\bML\b|machine learning|"
                  r"\bLLM|gen ?AI|generative|platform|distributed|data engineer|full.?stack|engineering|developer|"
                  r"\bsearch|\bads\b|payments|fintech|siri|services engineering|core os|applied ai|technical staff", re.I)
BAD = [  # (pattern, reason)
    (r"universit|campus|early.?career|new grad|intern(ship)?s?\b|emerging talent", "university / early career"),
    (r"executive (search|recruit)|exec(utive)? recruit|leadership hiring|\bVP\b.*hiring|director.?level|L8|L9|senior leadership", "executive / leadership hiring"),
    (r"hardware|silicon|ASIC|\bchip|semiconductor|\bSoC\b|analog|RF\b|camera|optic|mechanical|manufactur|supply chain|"
     r"product design|industrial design|display|battery|thermal|electrical engineer", "hardware / silicon"),
    (r"\bG&A\b|\bHR\b|human resources|people ops|finance|legal|corporate functions|accounting|go.to.market|\bGTM\b|"
     r"\bsales\b|marketing|business recruit|non.?tech|retail|creative|content|studio|operations recruit", "non-engineering desk"),
    (r"security engineer|pentest|red team|offensive security", "security"),
    (r"coordinator|scheduler|recruiting operations|sourcing operations|talent operations|\bRPO\b", "coordinator / ops"),
    (r"research scientist|research recruit|PhD", "research scientists"),
]
STAFF = re.compile(r"staff\+|principal|distinguished|senior staff|\bL7\b|\bE7\b|\bIC6\b|senior leaders?|executive", re.I)
COS = {"Google": r"Google|Alphabet|DeepMind", "Apple": r"Apple", "Meta": r"Meta|Facebook|Instagram|Reality Labs",
       "NVIDIA": r"NVIDIA", "Zoox": r"Zoox", "Anthropic": r"Anthropic", "Microsoft": r"Microsoft|LinkedIn|GitHub",
       "OpenAI": r"OpenAI", "Scale AI": r"Scale", "Databricks": r"Databricks", "Stripe": r"Stripe", "Netflix": r"Netflix",
       "xAI": r"xAI|X\.AI|\bX\b"}
HIRE = re.compile(r"hiring|we're looking|we are looking|open role|join (my|our) team|reach out|apply|job|opening|"
                  r"looking for|req\b|roles?\b", re.I)


def main(enr_path, csv_path, out_dir):
    enr = json.load(open(enr_path))
    rows = list(csv.DictReader(open(csv_path)))
    by_id = {r["url"].split("/lead/")[1].split(",")[0]: r for r in rows}
    out = []
    for lid, row in by_id.items():
        e = enr.get(lid)
        if not e:
            row.update(fit2="?", reason2="not enriched"); continue
        cur = [p for p in e["positions"] if p.get("current")]
        co_re = re.compile(COS.get(row["company"], re.escape(row["company"])), re.I)
        at_co = [p for p in cur if co_re.search(p.get("co") or "")]
        role = at_co[0] if at_co else (cur[0] if cur else {})
        desk = " ".join([e.get("headline") or "", role.get("title") or "", role.get("desc") or "", (e.get("summary") or "")[:500]])
        own_posts = [p for p in e["posts"] if p["kind"] != "commentActivity" and p["text"]]
        posts_txt = " ".join(p["text"] for p in e["posts"])
        loc = e.get("location") or row["location"]
        flags, fit, reason = [], "", ""
        if e.get("lastMsg"):
            fit, reason = "red", f"already messaged {e['lastMsg']}"
        elif not at_co:
            fit, reason = "red", f"left {row['company']} (now: {(cur[0]['co'] + ' ' + cur[0]['title']) if cur else 'no current role'})"
        else:
            title = (role.get("title") or "") + " | " + (e.get("headline") or "")
            body = (role.get("desc") or "") + " " + (e.get("summary") or "")[:500] + " " + posts_txt
            t_good, t_bad = GOOD.search(title), next((why for pat, why in BAD if re.search(pat, title, re.I)), None)
            also = sorted({why for pat, why in BAD if re.search(pat, body, re.I)} - {t_bad})
            if t_bad and not t_good:
                fit, reason = "red", t_bad
            elif STAFF.search(title):
                fit, reason = "yellow", "senior/staff-level focus"
            elif t_good:
                fit, reason = "green", t_good.group(0)
            elif GOOD.search(body):
                fit, reason = "green", "desc: " + GOOD.search(body).group(0)
            else:
                fit, reason = "yellow", "generalist / desk unclear"
            if t_bad and t_good: also.insert(0, t_bad)
            if also and fit != "red": reason += " (also mentions: " + ", ".join(also) + ")"
        job_locs = " ".join(p.get("loc") or "" for p in cur)
        if not BAY.search(loc or "") and not BAY.search(job_locs):
            flags.append(f"location: {loc} (no Bay Area job location)")
        elif not BAY.search(loc or ""):
            loc = next(p["loc"] for p in cur if BAY.search(p.get("loc") or ""))
        if e.get("inmailRestriction") not in (None, "NO_RESTRICTION"):
            flags.append("InMail: " + e["inmailRestriction"])
        openp = bool((e.get("badges") or {}).get("openLink"))
        hook = ""
        hp = [p for p in own_posts if HIRE.search(p["text"])] or own_posts
        if hp:
            hook = f"post {hp[0]['at']}: {hp[0]['text'][:220]}"
        elif role.get("desc"):
            hook = "role: " + role["desc"][:220]
        rec = {"name": e["name"] or row["name"], "company": row["company"], "tier": row["tier"], "fit": fit, "reason": reason, "flags": flags,
               "title": role.get("title"), "team": role.get("co"), "since": role.get("start"), "location": loc,
               "degree": e.get("degree"), "open_profile": openp, "mutuals": e.get("mutuals") or [],
               "shared": (e.get("sharedEdu") or []) + (e.get("sharedExp") or []), "hook": hook, "headline": e.get("headline"),
               "posts": e["posts"][:4], "role_desc": role.get("desc"), "linkedin": e.get("linkedin"), "url": row["url"],
               "last_messaged": e.get("lastMsg")}
        out.append(rec)
        row.update(fit2=fit, reason2=reason, flags="; ".join(flags), open_profile="yes" if openp else "",
                   degree=e.get("degree") or "", mutuals=", ".join(rec["mutuals"][:5]), hook=hook.replace("\n", " "),
                   last_messaged=e.get("lastMsg") or "", location=loc, linkedin=e.get("linkedin") or "")
    json.dump(out, open(f"{out_dir}/enriched2.json", "w"), indent=1)
    keys = list(rows[0].keys())
    for r in rows:
        for k in r:
            if k not in keys: keys.append(k)
    with open(csv_path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=keys, restval=""); w.writeheader(); w.writerows(rows)

    # report
    order = {"green": 0, "yellow": 1, "red": 2}
    out.sort(key=lambda r: (order.get(r["fit"], 3), r["company"], -len(r["posts"])))
    c = Counter(r["fit"] for r in out)
    L = [f"# Recruiters: enrichment (Sales Navigator, {len(out)} people)\n",
         f"🟢 {c['green']} · 🟡 {c['yellow']} · 🔴 {c['red']}\n"]
    L.append("\n## By company\n\n| Company | 🟢 | 🟡 | 🔴 |\n|---|---|---|---|")
    for co in sorted({r['company'] for r in out}):
        cc = Counter(r["fit"] for r in out if r["company"] == co)
        L.append(f"| {co} | {cc['green']} | {cc['yellow']} | {cc['red']} |")
    red = Counter(r["reason"].split(" (")[0] if not r["reason"].startswith("already") else "already messaged" for r in out if r["fit"] == "red")
    L.append("\n## Why 🔴\n" + "\n".join(f"- {k}: {v}" for k, v in red.most_common()))
    msg = [r for r in out if r["last_messaged"]]
    L.append(f"\n## Already messaged ({len(msg)})\n" + "\n".join(f"- {r['name']} ({r['company']}) on {r['last_messaged']}" for r in msg))
    flagged = [r for r in out if r["flags"]]
    L.append(f"\n## Flags ({len(flagged)})\n" + "\n".join(f"- {r['name']} ({r['company']}): {'; '.join(r['flags'])}" for r in flagged))
    op = [r for r in out if r["open_profile"] and r["fit"] != "red"]
    L.append(f"\n## Open Profile = free InMail ({len(op)})\n" + "\n".join(f"- {r['name']} ({r['company']}, {r['fit']})" for r in op))
    first = [r for r in out if r["degree"] == 1]
    L.append(f"\n## 1st-degree connections ({len(first)})\n" + "\n".join(f"- {r['name']} ({r['company']}, {r['fit']})" for r in first))
    mc = Counter(m for r in out for m in r["mutuals"])
    L.append("\n## Mutual connections that recur\n" + "\n".join(f"- {m}: {n}" for m, n in mc.most_common(12) if n > 2))
    for fit in ("green", "yellow"):
        L.append(f"\n## {'🟢 Strong' if fit == 'green' else '🟡 Caveat'}\n")
        for r in [x for x in out if x["fit"] == fit]:
            L.append(f"- **{r['name']}** ({r['company']}, {r['title']}) · {r['reason']}"
                     + (" · Open Profile" if r["open_profile"] else "") + (f" · {len(r['mutuals'])} mutuals" if r["mutuals"] else "")
                     + (f"\n  - {r['hook'][:200]}" if r["hook"] else ""))
    L.append("\n## 🔴 Skip\n" + "\n".join(f"- {r['name']} ({r['company']}): {r['reason']}" for r in out if r["fit"] == "red"))
    open(f"{out_dir}/enriched.md", "w").write("\n".join(L) + "\n")
    print(dict(c), "messaged:", len(msg), "flags:", len(flagged), "open:", len(op), "1st:", len(first))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("enr"); ap.add_argument("csv"); ap.add_argument("outdir")
    ap.add_argument("--metro", help="regex of target-metro place names (default: SF Bay Area)")
    a = ap.parse_args()
    if a.metro: BAY = re.compile(a.metro, re.I)
    main(a.enr, a.csv, a.outdir)
