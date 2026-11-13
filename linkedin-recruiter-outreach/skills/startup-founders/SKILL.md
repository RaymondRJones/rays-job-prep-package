---
name: startup-founders
description: Build a pipeline of early-stage startups that are hiring (recent Y Combinator batches with open roles, and companies that just announced a seed/pre-seed round), find their CEO/CTO founders, score fit against the candidate's verified profile, and draft LinkedIn outreach (300-character connection note + short InMail) staged in a launcher with a progress checklist. Never sends. Use for "find YC startups hiring", "startups that just raised", "reach out to founders/CTOs", or founder outreach.
---

# Startup founder pipeline

Founders at seed/Series A companies often hire engineers themselves, and a short, specific note from a credible builder gets read. This skill finds them and drafts the notes; the user sends.

**Inputs:** `candidate-profile.md` (only facts you may claim), target metros (+ remote?), stage window, channel (LinkedIn by default).
**Outputs** in `outreach/startups/`: `companies.csv`, `founders.csv` (status per person), `briefs_raw.json` + `briefs.md`, `drafts.md`, `founder-launcher.html`.

## 1. Source companies

**A. Y Combinator, hiring now.** Run:
```
python3 <plugin root>/scripts/yc_hiring.py outreach/startups --since "<first batch, ~2 years back>" \
  --metro "<metro regex>" [--remote-us] --top 60 [--keywords keywords.json]
```
Write `keywords.json` from the candidate's profile first (`[[regex, weight, label], …]`): weight 2 for domains where they have a proof point (e.g. legal/document AI, pricing/logistics), 1 for adjacent ones. The script reads YC's public directory search (fresh key each run), keeps hiring companies in the metros, scores them, then pulls founders (name, title, LinkedIn, bio) and open roles for the top N. Companies without an engineering opening are dropped from the CSVs.

**B. Recently funded (seed/pre-seed), any accelerator.** In a logged-in browser, run the hiring-monitor's `scripts/linkedin-posts.js` (in the `hiring-monitor` plugin) with past-month queries such as:
`"raised" "seed" "we're hiring" engineers` · `"just raised" seed "founding engineer"` · `"announcing our" seed round hiring engineer` · `"pre-seed" OR "seed" raised "hiring" "backend"`.
LinkedIn search results scroll inside `<main>` and need **Load more** clicks; the script handles both. Keep a post only if it names a real company in the target metros/remote, in software (drop hardware/space/climate-hardware unless asked), and it's a raise announcement or hiring post, not an investor roundup, recruiting agency or opinion piece. Then find founders: from the post itself, the company's LinkedIn "People" tab, or its website team page. Mark unknowns `TBD`; never guess names or URLs.

## 2. Write a brief for each shortlisted company
`python3 <plugin root>/scripts/yc_brief.py outreach/startups <slug> [<slug> ...]` pulls each company's YC launch posts, news, and every engineering job's **full description, skills, interview process and named hiring manager** into `briefs_raw.json`. From it, write `outreach/startups/briefs.md`, one block per company:
- **What they do** (one line, their words) · **Traction** (customers, growth, ARR, raise, team size: only numbers they published)
- **The role** (title, stack, pay, experience) · **What they need now** (read it off the job post: "too much demand", "0→1 new product", "reliability, not demos")
- **Your angle** (the one proof point from the profile that answers that need) · **Hiring manager** + profile link
Also apply hard filters here (e.g. in-person in a non-target city → drop, and say why).

## 3. Pick the right person
- **Message the hiring manager named on the job post.** In the first run it differed from the obvious CTO/CEO pick at 7 of 11 companies.
- No named manager: engineering hire → the **CTO**, else the **CEO**. Small teams (≤ 5): the CEO is fine.
- One person per company per wave. Record both founders in `companies.csv` for later.
- Check for prior contact (existing LinkedIn thread / "Messaged:" in Sales Navigator).

## 4. Write for founders (from the brief)
Founders read differently from recruiters: they want someone who can **build and ship end to end with little direction**, ideally in their problem space.

| Part | Content |
|---|---|
| Hook | Something only *they* wrote: a line from their launch post or job post ("reliability and correctness, not just demos", "manpower of thousands of paralegals"), a traction number, a founder story. Quote or closely paraphrase; never invent. |
| Bridge | Tie the candidate's most relevant build to the need in the brief ("you're asking for someone who was a founder before. I was: …") |
| Proof | That build + one current-job result, one number each |
| Ask | A quick chat about the named role; optionally reflect their need back ("You mentioned more demand than you can handle…") |

**Engaging = specific + about them.** Before saving, check: would this message make sense sent to any other company? If yes, rewrite the hook. Re-check every candidate claim word by word: phrases like "sold it to", "sat with their team" or "inside their workflow" are easy to invent and usually aren't in the profile.

- **Being a former founder is the strongest hook** if the profile supports it; lead with it for founder audiences.
- Technical terms are fine for CTOs (OCR, RAG, extraction) when they mirror the company's own description; keep it plain for non-technical CEOs. Still no vendor names.
- **Connection note ≤ 300 characters** (hard LinkedIn limit): role + one-line proof + "Would love to connect."
- **InMail 60–100 words**, subject < 60 chars, ends at `Best,`.
- Interview-loop signals matter less to founders; leave them out unless the user asks.

Save to `outreach/startups/drafts.md`:
```
### 1. Sohil Bhatia: Kalinda (YC S25), CTO
**Profile:** https://www.linkedin.com/in/...
**Note:** Hi Sohil, saw Kalinda is hiring a founding engineer. ...
**Subject:** ...

Hi Sohil,
...
Best,
```
Run the same self-checks as `inmail-drafts` (lengths, facts traceable to the profile, hook unique to them).

## 5. Get Sales Navigator lead links
YC and post sources give regular profile links (`linkedin.com/in/…`), which don't open in Sales Navigator and can't take the Fill InMail bookmark. For each recipient, run a Sales Navigator people search `https://www.linkedin.com/sales/search/people?keywords=<First Last> <Company>` (results load slowly: wait for `a[href*="/sales/lead/"]` up to ~10 s), take the result whose headline names the company, and save its `/sales/lead/<id>` URL as `**Profile:**` (keep the `/in/` link as `**LinkedIn:**`) and in `founders.csv` `sales_nav`. No result → retry with the name only; if the top hit's headline shows another company, open the lead page and confirm the company in their experience before using it. Drive it with a `localStorage` queue like the other scripts.

## 6. Stage
`python3 <plugin root>/scripts/build_launcher.py outreach/startups/drafts.md - outreach/startups/founder-launcher.html`
(`-` = use each draft's `**Profile:**` link.) Rows get **Copy note / Copy subject / Copy body**, the progress checklist, and work with the Fill InMail bookmark. Tell the user the sequence: lead page → **… → Connect** → paste note → send; if not accepted in ~a week, send the InMail. Update `founders.csv` `status` (drafted → noted → inmailed → replied) when the user reports back.

## Rules
- Never send, connect, follow or message for the user.
- Only claims from `candidate-profile.md`; only founder names/URLs you actually found.
- Pace web requests (YC: ~1–2 s per company page; LinkedIn: ≤ 6 searches per run, stop on any captcha/warning).

> `<plugin root>` = the `linkedin-recruiter-outreach` folder two levels above this SKILL.md (resolve symlinks).
