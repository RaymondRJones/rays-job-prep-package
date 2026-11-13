#!/usr/bin/env python3
"""Build a deduplicated, tiered recruiters.csv from Sales Navigator search rows.

Input: one row per line, " | "-separated:
    company | name | title | location | tenure | leadUrl | ACTIVE(optional)

Usage:
    python3 build_list.py raw_rows.txt recruiters.csv \
        --home "Seattle|Bellevue|Redmond" --countries "United States"
"""
import argparse
import csv
import re
from collections import Counter

# Titles that usually can't place a software engineer. Tune per candidate.
EXCLUDE_TITLE = (r"universit|early (career|in profession)|emerging talent|intern|campus|gtm|go-to-market|"
                 r"sales|business recruit|finance|\bhr\b|human resources|hardware|vlsi|silicon|"
                 r"coordinator|contract recruiter|tutor|legal|marketing|production|studio|creative|"
                 r"executive assistant|apac|emea")
SOFTWARE = r"software|engineer|infra|cloud|\bai\b|\bml\b|machine learning|platform|data|technical"
SENIOR = r"\b(senior|sr\.?|staff|principal|lead)\b"

# Common corporate email patterns. GUESSES ONLY: verify before sending.
EMAIL_PATTERNS = {
    "apple": "{f}_{l}@apple.com",
    "nvidia": "{fi}{l}@nvidia.com",
    "stripe": "{f}@stripe.com",
    "netflix": "{fi}{l}@netflix.com",
    "google": None,      # internal aliases, not guessable
    "microsoft": None,   # internal aliases, not guessable
}


def clean_name(n: str) -> str:
    n = re.sub(r"\s+(is online|was last active.*)$", "", n)
    n = re.sub(r"\(.*?\)|,.*$", "", n)
    n = re.sub(r"[^\w\s.'-]", "", n)
    return re.sub(r"\s+", " ", n).strip()


def email_guess(company: str, name: str) -> str:
    key = company.lower()
    if key not in EMAIL_PATTERNS:
        return ""
    pat = EMAIL_PATTERNS[key]
    if pat is None:
        return "internal alias, not guessable"
    parts = name.split()
    if len(parts) < 2 or parts[-1].endswith("."):
        return "need full last name"
    f, l = parts[0].lower(), re.sub(r"[^a-z-]", "", parts[-1].lower())
    return pat.format(f=f, l=l, fi=f[0])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("infile")
    ap.add_argument("outfile")
    ap.add_argument("--home", default="", help="regex for the candidate's home metro (+1 score)")
    ap.add_argument("--countries", default="United States", help="regex of allowed countries")
    ap.add_argument("--exclude-title", default=EXCLUDE_TITLE)
    args = ap.parse_args()

    allowed = re.compile(args.countries + r"|Bay Area|Greater .* Area|Metropolitan", re.I)
    excl = re.compile(args.exclude_title, re.I)
    home = re.compile(args.home, re.I) if args.home else None

    seen, rows = set(), []
    for line in open(args.infile, encoding="utf-8"):
        p = [x.strip() for x in line.split(" | ")]
        if len(p) < 6 or not p[5]:
            continue
        company, name, title, loc, tenure, url = p[:6]
        active = "ACTIVE" if "ACTIVE" in p[6:] else ""
        if url in seen:
            continue
        seen.add(url)
        title = re.sub(r"\s{2,}" + re.escape(company) + r".*$", "", title, flags=re.I).strip(" ,-")
        if excl.search(title) or not allowed.search(loc):
            continue
        name = clean_name(name)
        score = (2 if re.search(SOFTWARE, title, re.I) else 0) + (1 if active else 0) \
            + (1 if home and home.search(loc) else 0) + (1 if re.search(SENIOR, title, re.I) else 0)
        if score == 0:
            continue
        rows.append({
            "tier": "A" if score >= 4 else "B" if score == 3 else "C",
            "company": company, "name": name, "title": title, "location": loc,
            "tenure": tenure.replace(" in role", "").split("  ")[0], "active": active,
            "email_guess (verify!)": email_guess(company, name), "fit": "", "url": url,
        })

    rows.sort(key=lambda r: (r["tier"], r["company"], r["name"]))
    with open(args.outfile, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()) if rows else ["tier"])
        w.writeheader()
        w.writerows(rows)
    print(len(rows), "recruiters |", dict(Counter(r["tier"] for r in rows)), "|", dict(Counter(r["company"] for r in rows)))


if __name__ == "__main__":
    main()
