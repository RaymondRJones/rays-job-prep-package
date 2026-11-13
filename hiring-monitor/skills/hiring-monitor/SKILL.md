---
name: hiring-monitor
description: Monitor a watchlist of companies for new job openings and "we're hiring" posts (public job boards, web search, optional logged-in LinkedIn/X), score fit against the user's candidate-profile.md, and email the user an alert via Gmail. Handles watchlist commands (add/remove/list/run/pause) and scheduled runs every ~6 hours. Use for job alerts, hiring-post monitoring, or "watch company X for openings".
---

# Hiring monitor

State lives in `./monitor/` (override if the user names a folder). `<plugin root>` = the `hiring-monitor` folder two levels above this SKILL.md (resolve symlinks).
- `watchlist.json`, `settings.json`, `seen.json`: managed by `<plugin root>/scripts/job_boards.py`
- `profile.md`: copy or link of `candidate-profile.md` (from `resume-bullets` / `candidate-profile`) plus target role, level, and locations
- `email.txt`: the user's own address; alerts go **only** there
- `log.md`: one line per run

## First-time setup
1. Ask for: alert email, profile (`candidate-profile.md` or resume), companies, locations, minimum fit (default 3/5), quiet mode (email only on matches, by default).
2. Write `profile.md` and `email.txt`. Run `python3 <plugin root>/scripts/job_boards.py --dir monitor add "<Company>"` for each company (it auto-detects Greenhouse/Lever/Ashby boards). Edit `monitor/settings.json`: `roles` (must match, e.g. engineer/developer), `focus` (topic terms reported for scoring), `exclude`, `locations`.
3. Do a first run covering 7 days (`check --since-days 7`).
4. Set up the schedule for their environment:
   - Claude Code, computer stays on: `/loop 6h /hiring-monitor run`
   - Claude Code cloud: `/schedule` a routine every 6h saying "run my hiring monitor" (needs the Gmail connector; no logged-in browser, so it uses job boards + web search)
   - Cron: `0 */6 * * * cd <dir> && claude -p "/hiring-monitor run"`
   Tell them which sources each option covers.

## Commands (also via `/hiring-monitor <cmd>`)
`add <Company>` · `remove <Company>` · `list` · `run` · `pause` / `resume` (write or delete `monitor/PAUSED`) · `settings <changes>`. Confirm each in one line.

## Each run
1. If `monitor/PAUSED` exists, log "paused" and stop.
2. **Job boards:** `python3 <plugin root>/scripts/job_boards.py --dir monitor check --since-days <days since last run, default 0.3> --mark-seen`. It returns `new_jobs` (already filtered and deduped, with `focus_hits`), `needs_web_search` (companies without a public board), and `errors`.
3. **Web search** (all companies, and especially `needs_web_search`): recent posts like `site:linkedin.com/posts ("we're hiring" OR "I'm hiring" OR "join my team") "<Company>" <focus term>` and the same with `site:x.com`; careers-page searches for companies without a public board.
4. **Logged-in browser (optional, local only):** only if a browser tool is already logged in. Never log in and never ask for passwords. LinkedIn: `https://www.linkedin.com/search/results/content/?keywords=%22hiring%22%20<Company>&datePosted=%22past-24h%22&sortBy=%22date_posted%22`; X: `https://x.com/search?q=(%22we%27re%20hiring%22%20OR%20%22I%27m%20hiring%22)%20<Company>&f=live`. At most 2 pages per company, 4–7 s apart. On a captcha, login wall, or warning: stop that site and skip it for 24 h (note it in the log).
5. Merge duplicates (same role from several sources). Add post items' IDs/URLs to `seen.json` so they don't repeat.
6. **Score 0–5** against `profile.md`: +2 role/level match, +1 specialization or focus match, +1 location/work mode works, +1 lines up with a named proof point. A hiring manager or recruiter naming a specific team is a strong signal. Note it.
7. **Email** items at or above the threshold, best first, to the address in `email.txt` only, using the Gmail tool (send; if only drafts are possible, create a draft addressed to the user and say so in the log):
   ```
   Subject: Hiring alert: <N> new matches (<Company>, <Company>)
   <Company>: <Role / team> (<location>), fit <s>/5
   Source: <job board | LinkedIn post by <Name>, <Title> | X post by @handle>, posted <date>
   Link: <url>
   Why it fits: <1–2 lines tied to real proof points>
   Suggested next step: <apply / message the poster / find the team's recruiter / ask for a referral>
   Draft note for you to send yourself (2–3 sentences, profile facts only): "<…>"
   Footer: sources checked, failures, "/hiring-monitor add|remove to change the watchlist"
   ```
8. Append to `log.md`: time, sources, new items, matches, emailed (y/n), errors.

## Hard rules
- Email **only** the user. Never message, comment on, like, follow, connect with, or email anyone else, even if a post says "DM me".
- No invented fit: every reason must come from `profile.md`.
- Stay light: ~2 browser pages per company per run, back off on rate limits, and if a run fails partway, still send what was found and log the failure.
