---
name: startup-founders
description: Build a pipeline of early-stage startups that are hiring (recent Y Combinator batches with open roles, and companies that just announced a seed/pre-seed round), find their CEO/CTO founders, score fit against the candidate's verified profile, and draft LinkedIn outreach (300-character connection note + short InMail) staged in a launcher with a progress checklist. Never sends. Use for "find YC startups hiring", "startups that just raised", "reach out to founders/CTOs", or founder outreach.
---

# Startup founder pipeline

Founders at seed/Series A companies often hire engineers themselves, and a short, specific note from a credible builder gets read. This skill finds them and drafts the notes; the user sends.

**Inputs:** `candidate-profile.md` (only facts you may claim), target metros (+ remote?), stage window, channel (LinkedIn by default).
**Outputs** in `outreach/startups/`: `companies.csv`, `founders.csv` (status per person), `drafts.md`, `founder-launcher.html`.

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

## 2. Pick the right person
- Engineering hire → the **CTO** first (they own the role), else the **CEO**. Small teams (≤ 5): the CEO is fine.
- One person per company per wave. Record both founders in `companies.csv` for later.
- Check for prior contact (existing LinkedIn thread / "Messaged:" in Sales Navigator).

## 3. Write for founders
Founders read differently from recruiters: they want someone who can **build and ship end to end with little direction**, ideally in their problem space.

| Part | Content |
|---|---|
| Hook | Their open role by name + one specific thing about the product (from the one-liner/description) |
| Proof | The candidate's most relevant build for *their* problem (e.g. "as a founder I built AI that reads and summarizes legal documents, cutting a law firm's review time in half"), plus one current-job result |
| Ask | "Would you be open to a quick chat about the founding role?" |

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

## 4. Stage
`python3 <plugin root>/scripts/build_launcher.py outreach/startups/drafts.md - outreach/startups/founder-launcher.html`
(`-` = use each draft's `**Profile:**` link.) Rows get **Copy note / Copy subject / Copy body** and the progress checklist. Tell the user the sequence: open profile → **Connect → Add a note** → paste → send; if not accepted in ~a week, send the InMail. Update `founders.csv` `status` (drafted → noted → inmailed → replied) when the user reports back.

## Rules
- Never send, connect, follow or message for the user.
- Only claims from `candidate-profile.md`; only founder names/URLs you actually found.
- Pace web requests (YC: ~1–2 s per company page; LinkedIn: ≤ 6 searches per run, stop on any captcha/warning).

> `<plugin root>` = the `linkedin-recruiter-outreach` folder two levels above this SKILL.md (resolve symlinks).
