---
name: linkedin-profile-audit
description: Audit a software engineer's LinkedIn profile against their resume and target roles (read-only first), propose exact prioritized changes, then apply only approved batches in a logged-in browser and verify each saved field. Use when someone wants to improve, optimize, or align their LinkedIn profile.
---

# LinkedIn profile audit

## Inputs
Resume (ideally approved bullets / `candidate-profile.md` from `resume-bullets`), target titles and level, specialization, locations and work modes, career stage (experienced / new grad / career changer / returning). Live access: open linkedin.com in the browser tool and **let them log in themselves**. Never ask for passwords, codes, or cookies. Without a browser: work from pasted text or screenshots, and mark live-only fields "unavailable".

Also ask (skip what's known): Open to Work public or recruiters-only? Is the current employer safe to show? Anything private (salary, internal project names, job-search status)? Are live edits allowed after approval, or recommendations only?

## Rules
- Start **read-only**. Profile-edit approval does **not** cover posts, messages, invitations, follows, applications, or job alerts. Each needs its own approval.
- Before any change, say whether it may notify their network or reveal job-search intent.
- Record the current value before each change. Preserve unrelated fields. Stop if anything unexpected changes.
- Never invent credentials, levels, location flexibility, or skills. Don't add a skill just because a job post lists it.

## Audit, in order
1. **Basics:** name, photo/banner (professional, legible, no misused employer branding), clean URL, location = real target market, industry, working contact/portfolio links.
2. **Headline:** recognizable target title + specialty + a few supported skills/domains; no unearned level/title/cert; new grads distinguish target from earned. Give 2–3 options only for genuinely different positioning, and recommend one.
3. **About:** the first two lines say who they are and which roles they fit; strongest recent evidence early; skills tied to work; no keyword dumps. May be broader than the resume, never contradictory. New grads: internships, projects, open source, research, described honestly.
4. **Experience (each entry):** employer, title, type, location, and dates match the resume; opens with product/system context; ownership and metrics qualified (same rules as `resume-bullets`); tech actually used there; programs and volunteering not shown as jobs.
5. **Skills:** all true and evidence-backed; core target skills use LinkedIn's standard names; check which display first and which are attached to each role; drop off-target ones.
6. **Open to Work and preferences:** titles not too broad, locations, work modes, start date, visibility (explain public vs. recruiters-only).
7. **Saved resumes and application answers:** stale or contradictory versions; outdated salary/location/sponsorship answers. Never delete without approval.
8. **Featured, education, certifications** (exact status; planned ≠ earned), projects, recommendations: support the target role, with working links. Mark controls missing in their account "unavailable".
9. **Privacy:** visibility, contact exposure, no confidential code/architecture/customer data/unreleased results in text or activity.
10. **Baseline:** search appearances, profile/recruiter views, the titles they're found for. Paywalled → "unavailable"; never estimate.

Add a **resume ↔ LinkedIn consistency table** (name, target identity, employers/titles, dates, locations, skills, key metrics, education, links), with a decision per mismatch. Facts must agree; wording can differ.

## Recommendations
```
ID · Priority (P0 factual mismatch / privacy / recruiter-filter field / stale data; P1 headline, About, Experience, skills; P2 polish)
Field · Current · Problem · Evidence · Exact new value · Notification/privacy effect · Status (proposed/approved/applied/verified/failed)
```

## Apply in batches
Order: (1) identity, titles, dates, location, privacy; (2) Open to Work, preferences, saved resumes; (3) skills; (4) headline, About, experience text; (5) Featured and optional sections; (6) job alerts, only with separate approval. Before each: show the exact changes and effects, then wait for "approved". After each: reopen every edited field, compare it to the approved text, check links and formatting, and record verified or failed.

## Finish
Before/after for every changed field; what's unverified or unavailable; open questions; an updated `candidate-profile.md`; a re-check date 2–4 weeks out for the baseline numbers.
