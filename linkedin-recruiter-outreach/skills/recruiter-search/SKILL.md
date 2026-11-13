---
name: recruiter-search
description: Find technical recruiters at target companies and locations in LinkedIn Sales Navigator, extract the results, and build a deduplicated, tiered recruiters.csv. Use when building a recruiter list for job outreach.
---

# Recruiter search (Sales Navigator)

## 0. Login
Open `https://www.linkedin.com/sales/home` in the browser tool. If it redirects to `/sales/login`, ask the user to log in themselves in that tab and tell you when they're done. Never type credentials. Reuse that same logged-in browser profile for everything after.

## 1. Build search URLs (no clicking through filters needed)
Lead search accepts a `query=` param. Company filtering by **text** works; keyword search does not (searching "xAI" as a keyword returned people *named* Xai).

```
https://www.linkedin.com/sales/search/people?query=(filters:List(
  (type:CURRENT_COMPANY,values:List((text:Stripe,selectionType:INCLUDED))),
  (type:CURRENT_TITLE,values:List((text:technical%20recruiter,selectionType:INCLUDED))),
  (type:REGION,values:List(
     (id:90000084,text:San%20Francisco%20Bay%20Area,selectionType:INCLUDED),
     (id:90000091,text:Greater%20Seattle%20Area,selectionType:INCLUDED)))))
```
(Put it on one line.)
- **Title:** use `technical recruiter` for big companies (thousands of recruiters). Use plain `recruiter` for small companies (<100 results).
- **Region IDs** confirmed: `90000084` SF Bay Area, `90000091` Greater Seattle. Use only the candidate's target metros; mixing regions dilutes big companies (Google returned 9 Bay Area leads mixed with Seattle vs 89 Bay-only). For other metros, apply the Geography filter once by hand, then read the `id:` from the resulting URL.
- Without a region filter, big companies return many India/EMEA recruiters on page 1.
- The page header shows the total ("121 results"). Page 1 = 25 leads. Add `&page=2` for more.

## 2. Extract each results page
Results render lazily. Scroll `#search-results-container` before reading. Use `<plugin root>/scripts/extract-search-results.js`: set `COMPANY`, run it as one expression in the page. It appends rows to `localStorage.rx` (which survives navigation) and returns a count plus a preview.

Gotchas:
- Tool output is capped (~64 KB). Prefer exporting as a **file download** (Blob + `<a download>` click in the page); the agent browser reports the saved path (T3: `preview_status().downloads[].path`). Otherwise export `localStorage.rx` filtered by company or in halves.
- To page through many searches with few tool calls, keep a queue in `localStorage` (`[[company,title,page],...]`): each call extracts the current page, enqueues pages 2..N from the result count (cap ~4 pages = 100 leads per company), then sets `location.href` to the next item. Re-run the same expression until it returns DONE.
- Names can carry suffixes like "is online" or "was last active 11 minutes ago"; `build_list.py` strips both.
- Out-of-network leads repeat the name where the title should be; "Viewed" badges insert extra lines. The script strips both.
- This site's CSP blocks `eval()` **inside** async code. Inline the function in each call rather than eval-ing stored code.
- Wait ~4 s after navigation, and leave a few seconds between companies.

## 3. Build the CSV
Save the exported rows as `outreach/raw_rows.txt` (one `company | name | title | location | tenure | url | ACTIVE` per line), then run:
```bash
python3 <plugin root>/scripts/build_list.py outreach/raw_rows.txt outreach/recruiters.csv \
  --home "Seattle|Bellevue|Redmond|Kirkland" --countries "United States"
```
It dedupes by lead URL, drops non-target titles (university, early career, GTM/sales, hardware, HR, contract, coordinator, non-target countries), scores rows (covers software/infra/AI +2, posted recently +1, home metro +1, senior +1), tiers them (A ≥4, B 3, C ≤2), and adds **unverified** email-pattern guesses.

## 4. Report
Give counts per company and per tier. Name a few standout A-tier recruiters and why they stand out. Remind the user that email guesses must be verified (e.g. Hunter) before use.

> `<plugin root>` = the `linkedin-recruiter-outreach` folder two levels above this SKILL.md (resolve symlinks).
