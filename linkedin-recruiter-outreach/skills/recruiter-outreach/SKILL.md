---
name: recruiter-outreach
description: End-to-end LinkedIn recruiter outreach for a job seeker. Builds a verified profile from their resume or LinkedIn, finds technical recruiters at target companies in Sales Navigator, enriches them, and types personalized InMail drafts for the human to review and send. Use when someone wants to "find recruiters", "use my Sales Navigator credits", "reach out to recruiters at X", or run job-search outreach.
---

# Recruiter outreach (orchestrator)

You run a four-stage pipeline. Each stage has its own skill; load it when you reach that stage. Keep all outputs in `./outreach/` (create it) unless the user names another folder.

## Stage 0: Gather inputs (ask once, then proceed)
Collect, using sensible defaults when the user doesn't say:
- **Resume or LinkedIn URL** (required). Without it you can't write truthful messages.
- **Target companies.** Default: ask. Also ask which companies to **skip** (ones they're already interviewing with).
- **Locations.** Default: the city on their profile + "Remote".
- **Seniority / role type.** Default: inferred from the resume (years of experience, current title).
- **InMail credits available.** Default: assume ~50 and say so.
- **Their public numbers** (followers, subscribers, rankings). Use only what's on the profile or what they confirm.

## Stage 1: `candidate-profile`
Produce `outreach/candidate-profile.md`: verified facts, metrics, and a "do not claim" list. Every later message may only use facts from this file. Show the user the 5–6 strongest proof points and ask them to correct anything wrong.

## Stage 2: `recruiter-search`
Ask the user to log into Sales Navigator in the browser tool (**never** ask for or type their password). Search each target company × recruiter titles × locations, extract the results, and build `outreach/recruiters.csv` with tiers A/B/C.

## Stage 3: `recruiter-enrich`
Open A-tier lead pages one at a time (paced), capture role scope, recent posts, mutual connections and past employers, and rate fit 🟢/🟡/🔴. Many "technical recruiters" hire for hardware, Staff+ only, GTM, or university roles. Catching that saves credits.

## Stage 4: `inmail-drafts`
Draft messages for 🟢 recruiters, type them into Sales Navigator composers in **separate tabs**, and leave them **unsent**. Report which tabs hold which drafts.

## Credit plan to suggest
- 🟢 first. 🟡 after hand-tuning. Spend a few credits on 🔴 recruiters only as "who should I talk to?" notes, preferring ones with many mutual connections.
- LinkedIn refunds InMail credits for replies within 90 days, so specific messages pay for themselves.
- Free channels beat credits: 1st-degree connections, ex-coworkers and alumni at the target company (referrals), and recruiters with **Open Profile**.

## Hard rules
- Never click Send, never connect, never follow, never endorse. Drafts only.
- Never state a fact about the candidate that isn't in `candidate-profile.md`.
- Never name-drop a mutual connection unless the user confirms they actually know them.
- Pace browsing: ~4–7 s per page, enrichment in batches of ≤30, stop if LinkedIn shows a captcha or warning, and tell the user.
- Keep recruiter data local. Don't upload it anywhere.
- Report honestly: if a detection (like connection degree) turns out to be wrong, say so and fix the files.
