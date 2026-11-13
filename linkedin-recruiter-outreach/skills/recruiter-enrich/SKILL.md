---
name: recruiter-enrich
description: Enrich a list of recruiters from their Sales Navigator lead pages (role scope, recent posts, mutual connections, past employers, connection degree) and triage fit for the candidate. Use after recruiter-search and before drafting InMails.
---

# Recruiter enrichment

Why: in the original run only 10 of 32 "A-tier" recruiters were real fits. Others hired exclusively Staff+, camera hardware, pentesters, Azure silicon, design, or HR interns. Enrichment saves credits and gives each message a specific hook.

## Pace and visibility
- Every lead page you open shows them "X viewed your profile". That's fine and even warms them up, but tell the user first.
- Do **≤30 per batch**, one page at a time, with ~4–7 s of randomized wait (the script waits for you). Stop on any captcha or warning.

## Per lead
1. Navigate to the lead URL (`/sales/lead/...`).
2. Run `<plugin root>/scripts/extract-lead.js` as one expression. It scrolls, then stores into `localStorage.enr[url]`:
   `name, degree, headline, about, currentRole (description!), posts[] (last 90 days), common (mutual connections / shared experience), mutuals, experience, education, interests, openProfile`.
   Messaging-disabled only shows when you open the composer (see `inmail-drafts`).
3. Export `localStorage.enr` in halves (output cap) and save `outreach/enriched.json`.

## Connection degree: verify, don't guess
The degree sits on the line under the name, often next to pronouns: `"(She/Her)  2nd"`. A naive `\n1st\n` regex matched a *mutual connection's* "1st" and mislabeled 9 recruiters as 1st-degree in the original run. `extract-lead.js` reads the header block only. If anything says 1st, spot-check it before telling the user it's a free message.

## Fit triage (write it to `outreach/enriched.md`)
Rate against `candidate-profile.md`:
- 🟢 **Strong:** their role description, About, or recent posts mention the candidate's area (backend, infra, cloud, AI platform, a specific org), or they recently posted a matching role.
- 🟡 **Caveat:** generalist, or they hire one level up/down, or their current desk is adjacent (data science, PM-heavy). Use a "this role or the right person" ask.
- 🔴 **Wrong desk:** "exclusively Staff+", hardware/silicon/camera, security pentest, design, G&A/HR, university, executive search. Use a "who should I talk to?" note only, prioritizing those with many mutuals.
- Flag **messaging disabled** (Sales Nav composer says "the recipient has disabled all communications"). Use email or an intro instead.

For each person, record: **hook** (the most specific, recent thing to reference), **mutuals** (names, but don't use them in messages unless the user knows them), **fit + one-line reason**.

## Also surface warm paths
- Mutual connections that recur across many recruiters (ask the user if they know them).
- 1st-degree connections who are recruiters at the target companies (free messages, and good for intros).
- Recruiters with the "Open Profile" badge (free InMail).

Update `recruiters.csv` with a `fit` column.

> `<plugin root>` = the `linkedin-recruiter-outreach` folder two levels above this SKILL.md (resolve symlinks).
