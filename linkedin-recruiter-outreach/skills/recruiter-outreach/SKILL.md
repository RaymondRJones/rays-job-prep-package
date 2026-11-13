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
- **Locations.** Default: the city on their profile + "Remote". Search **only** the metros they want; mixing regions buries the target metro's recruiters.
- **Seniority / role type.** Default: inferred from the resume (years of experience, current title).
- **InMail credits available.** Default: assume ~50 and say so.
- **Their strongest "ready now" signal:** recent interview loops cleared at comparable companies, competing processes with deadlines, rankings. Ask; these often aren't on the resume. Use only with wording they approve, and never mention a process or offer they don't want discussed.

## Stage 1: `candidate-profile`
Produce `outreach/candidate-profile.md`: verified facts, metrics, and a "do not claim" list. Every later message may only use facts from this file. Show the user the 5–6 strongest proof points and ask them to correct anything wrong.

## Stage 2: `recruiter-search`
Ask the user to log into Sales Navigator in the browser tool (**never** ask for or type their password). Search each target company × recruiter titles × locations, extract the results, and build `outreach/recruiters.csv` with tiers A/B/C.

## Stage 3: `recruiter-enrich`
Open A-tier lead pages one at a time (paced), capture role scope, recent posts, mutual connections and past employers, and rate fit 🟢/🟡/🔴. Many "technical recruiters" hire for hardware, Staff+ only, GTM, or university roles. Catching that saves credits.

## Stage 4: `inmail-drafts`
Draft messages for 🟢 (and tuned 🟡) recruiters in **plain language a non-engineer recruiter can skim**: a specific hook, one result per job, one signal line, one ask. No tool names. Emails only for published addresses or InMail-disabled recruiters. Leave everything **unsent**. Sales Navigator has no drafts folder, so a draft lives only in an open composer tab. For up to ~7 drafts, type them into separate tabs; for more, build the launcher page (`scripts/build_launcher.py`) so the user can open and fill any number of tabs in their own browser with a bookmarklet. Report which tabs hold which drafts and which are free (Open Profile). The launcher has a per-lead checklist (Opened / Subject / Body / Sent); afterwards, ask what was sent and mark it in `drafts.md`.

## Also: startup founders
For early-stage companies, skip recruiters and go to the founders with the `startup-founders` skill (YC hiring list + recent seed rounds → CTO/CEO → connection note + InMail).

## Credit plan to suggest
- 🟢 first. 🟡 after hand-tuning. Spend a few credits on 🔴 recruiters only as "who should I talk to?" notes, preferring ones with many mutual connections.
- LinkedIn refunds InMail credits for replies within 90 days, so specific messages pay for themselves.
- Free channels beat credits: 1st-degree connections, ex-coworkers and alumni at the target company (referrals), and recruiters with **Open Profile**.

## Hard rules
- Never click Send, never connect, never follow, never endorse. Drafts only.
- Never state a fact about the candidate that isn't in `candidate-profile.md`.
- Check for prior contact before drafting: an existing inbox thread, or `Messaged: <date>` on the lead page.
- Never name-drop a mutual connection unless the user confirms they actually know them.
- Pace browsing: ~4–7 s per page, enrichment in batches of ≤30, stop if LinkedIn shows a captcha or warning, and tell the user.
- Keep recruiter data local. Don't upload it anywhere.
- Report honestly: if a detection (like connection degree) turns out to be wrong, say so and fix the files.
