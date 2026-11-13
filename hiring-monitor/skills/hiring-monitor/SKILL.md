---
name: hiring-monitor
description: Watch target companies for PEOPLE posting that their team is hiring ("my team is looking for…", "I'm hiring", "join my team") on LinkedIn and X, collect the posters into a leads list for later outreach, and also flag new matching jobs on public boards. Handles watchlist commands (add/remove/list/run/pause/settings) and scheduled runs every ~6 hours; alerts go only to the user. Use for "find people hiring at X", hiring-post monitoring, job alerts, or "watch company X".
---

# Hiring monitor

**Goal:** find the humans behind openings, a hiring manager, engineer or recruiter saying *"my team is hiring"*, and add them to a leads list the user can reach out to later. Job-board postings are a secondary signal that helps judge fit and give context.

State lives in `./monitor/` (or a folder the user names). `<plugin root>` = the `hiring-monitor` folder two levels above this SKILL.md (resolve symlinks).

| File | What |
|---|---|
| `hiring-leads.csv` | **The main output.** One row per person: found, company, name, headline, poster_type, role_or_team, post_age, post_summary, profile_url, source, fit, why, status, notes |
| `profile.md` | copy of `candidate-profile.md` + target role, level, metros, and any active interview processes |
| `watchlist.json`, `settings.json`, `seen.json` | managed by `scripts/job_boards.py` (boards) |
| `alerts/<date>.md` | each run's report (also emailed if Gmail is available) |
| `log.md` | one line per run |

## Setup (first time)
Ask once: companies, target role/level, metros, active processes (e.g. "passed Waymo phone screen"), alert email (optional), minimum fit (default 3/5). Then:
1. Write `profile.md`; create `hiring-leads.csv` with the header above.
2. `python3 <plugin root>/scripts/job_boards.py --dir monitor add "<Company>"` for each company; set `settings.json` `locations` to the user's metros only.
3. First run with a **past-month** window for posts and `--since-days 365` for boards (then `--mark-seen`, so later runs only show new jobs).
4. Offer a schedule: `/loop 6h /hiring-monitor run` (local; can use the logged-in browser for LinkedIn), a cloud `/schedule` (boards + web search only, no LinkedIn), or manual.

## Each run
1. Stop if `monitor/PAUSED` exists (log it).
2. **People posts (primary)**, per company, in a logged-in browser only (never log in or ask for passwords):
   - Queries (content search, sorted by date): `<Co> "my team" hiring`, `<Co> "join my team"`, `<Co> "I'm hiring"`, `<Co> "we're hiring" engineer`, `<Co> "is hiring" "<role>"`, `<Co> "looking for" engineers team`. Window: `past-24h` on scheduled runs, `past-week` if runs were missed, `past-month` on the first run.
   - Run `<plugin root>/scripts/linkedin-posts.js` (queue-driven: seed `localStorage.hq`, re-run until DONE), then export `localStorage.hp`.
   - X/Twitter (optional, same rules): `https://x.com/search?q=("my team" OR "I'm hiring" OR "we're hiring") <Co>&f=live`.
   - Without a logged-in browser, use web search: `site:linkedin.com/posts "<Co>" ("my team is hiring" OR "join my team" OR "I'm hiring")`.
   - Pace: ~4–7 s between pages, ≤ 6 searches per company per run. On a captcha, login wall or warning, stop that site for 24 h and log it.
3. **Triage each post.** Keep it only if all of these hold:
   - The poster **works at the target company** (headline says so). Drop aggregators ("5 jobs at…"), people who just *left*, and other companies that mention the name.
   - The role is relevant to the user (engineering for an engineer; drop program/ops/sourcing/hardware roles unless asked).
   - It's in the user's metros or remote.
   Classify `poster_type`: **hiring manager / team member** (best: the decision-maker or an insider), **recruiter** (good), **new joiner** ("just joined team X": not hiring, but a warm insider for referrals; keep with fit ≤ 4).
4. **Score fit 0–5** against `profile.md`: +2 role/level match, +1 team/domain matches a proof point, +1 metro works, +1 poster is the hiring manager or on the team. Write a one-line `why` from real profile facts.
5. **Add new people to `hiring-leads.csv`** (dedupe by `profile_url`; if the person is already there, update `post_age`/`role_or_team` and keep their `status`). New rows get `status=new`.
6. **Boards (secondary):** `python3 <plugin root>/scripts/job_boards.py --dir monitor check --since-days <since last run> --mark-seen`. Mention new matching roles, especially ones that line up with a lead's team.
7. **Report** to `alerts/<date>.md` and email it to the user if Gmail is connected: new leads first (name, title, team, why, profile link, post summary), then new board roles, then sources checked and failures.
8. Append to `log.md`.

## Active-process caution
If `profile.md` says the user is mid-process at a company (e.g. passed a phone screen), note on that company's leads: *"check with your current recruiter before contacting"*. Contacting a second recruiter mid-loop can confuse the process; hiring managers and team members are fine for questions about the team.

## Hard rules
- **Collect, don't contact.** Never message, comment on, like, follow, connect with, or email anyone, even if a post says "DM me". Outreach is a separate step the user starts (e.g. with `inmail-drafts`).
- Email alerts go **only** to the user.
- No invented fit: every `why` comes from `profile.md`.
- Post permalinks aren't available in LinkedIn search results; store the author's `profile_url` and a summary of the post instead of guessing URLs.

## Commands
`add <Co>` · `remove <Co>` · `list` · `run` · `leads` (show `hiring-leads.csv`, best first) · `pause` / `resume` · `settings <changes>`. Confirm each in one line.
