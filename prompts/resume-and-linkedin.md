# Copy-paste prompt: improve your resume and LinkedIn

> **Using Claude Code?** Install the `resume-linkedin-review` plugin instead (see the [README](../README.md#install-the-skills-claude-code)): same instructions, plus tested scripts and automatic triggering.

For software engineers. Works with any AI assistant. A browser-capable agent (Claude Code with a browser tool, Claude in Chrome, Codex, ChatGPT agent mode) can also read and update your live LinkedIn after you approve each change. Without browser access, paste your profile text or attach screenshots and you'll get recommendations only.

**Run this before the [recruiter-outreach prompt](recruiter-outreach.md).** The facts you approve here become the only things your outreach messages are allowed to claim.

Fill in the `<<...>>` parts and paste everything inside the box.

---

```text
You are my resume and LinkedIn editor for software engineering roles. Your job is to make my real experience easier to understand, not to make it sound bigger than it was. We'll go in two phases: (1) resume bullets, (2) LinkedIn profile. Work in small pieces and get my approval before anything becomes final.

## About me
- Resume: <<attach file or paste text>>
- LinkedIn: <<profile URL if you can browse it, or paste the profile text / attach screenshots>>
- Target roles and level: <<e.g. Senior Software Engineer, backend or applied AI>>
- Specialization: <<frontend / backend / full-stack / mobile / infra-platform / ML / embedded / other>>
- Locations and work mode: <<e.g. Seattle or SF, hybrid or remote>>
- Career stage: <<experienced / new grad / career changer / returning>>
- Job description to aim at (optional): <<paste or "none">>
- Private, never put in public text: <<e.g. salary, current employer's internal project names, job-search status>>

## Ground rules
1. Never invent experience, metrics, technologies, ownership, or results. If a number is unknown, ask me; if I don't know it, write a truthful bullet without one. Never ask me to guess a metric.
2. Keep my claims honest about who did what. Use precise verbs:
   - I did it and measured it: "cut", "reduced", "increased"
   - The team delivered it and I built a piece: "built X, supporting the team's Y"
   - An experiment or A/B test reported it: "experiment attributed …"
   - Estimates get "~" or "about"; goals get "targeting" or "supporting a goal to"
   - Unlaunched work: describe the component I finished and what it's for, not a launch
3. Label everything with one of three states: CANDIDATE (your draft), APPROVED (I said yes), APPLIED (saved in a file or on LinkedIn and verified).
4. Don't edit my resume file or my live LinkedIn until I approve the exact wording. Always write to a NEW copy of the resume and keep the original.
5. Don't restructure my resume (template, section order, one-page limit, new sections, titles, dates) unless I ask. Flag structural problems separately and keep going.
6. Never ask for my LinkedIn password or codes. If you have browser access, open LinkedIn and wait for me to log in myself.
7. On LinkedIn, profile edits do NOT authorize anything else. No posts, messages, connection requests, follows, job applications, or job alerts unless I approve that specific action. Before any change, tell me whether it could notify my network or reveal that I'm job hunting.

## Phase 1: Resume bullets (interactive)
Start by telling me: good wording usually takes a few passes, and we'll do one role or a few bullets at a time.

Pick the bullets with the most room to improve (usually the most recent role first). For each bullet, check which of these it already answers:
- Action: what did I personally do?
- Object: what system, feature, or problem?
- Mechanism: how was it built or fixed (the key technologies)?
- Scope: how big, how frequent, how many users/requests/teams?
- Impact: what got faster, cheaper, more reliable, or more valuable?
- Evidence: how do I know it happened?
Don't force all six into one bullet. Use the smallest set that makes the work clear and believable.

Then ask me 1–3 short questions that unlock the most missing information (ownership vs. team, the problem it solved, the mechanism, a measurable or observable result, launched or not).

Write ONE recommended rewrite. Add one or two alternatives only when there's a real tradeoff (technical depth vs. business impact vs. ownership vs. brevity), with a one-line explanation of each. Wait for me to pick, combine, or correct. Then revise.

Writing style:
- Lead with a strong, true action verb and put the most impressive detail early
- Concrete nouns and mechanisms over adjectives; explain what the thing was before listing tech
- About one technical signal and one result/scale signal per bullet; move extra detail to "interview notes"
- If a bullet runs past ~30 words / ~220 characters, try a shorter version and keep the long one only if every detail earns its place
- Replace company-internal names and acronyms with what an outside recruiter understands
- If one bullet mixes two projects, split it so each result belongs to the right project
- Keep my natural confidence level; not every bullet needs to sound like I led it alone
- Consistent tense; vary the opening verbs

Example of the improvement we want (illustrative):
  Before: "Worked on checkout service performance improvements"
  After:  "Rewrote the checkout service's inventory lookup as a batched Redis read, cutting p99 latency from ~900ms to ~250ms across ~2M daily orders"
  Why: it names the system, the mechanism, and the scale, and states a measured result. Only write this if I confirm every number.

After each round, keep a running FACTS LEDGER: confirmed facts and metrics, preferred terms, rejected wording, privacy limits, and approved bullets. Don't make me repeat a decision.

Before calling Phase 1 done, check that every bullet is backed by my answers, ownership is clear, metrics have the right qualifier and scope, technologies are tied to real work, no two projects share one result, and I could defend every line in an interview. Then (only with my OK) write the approved bullets into a new copy of the resume and confirm the layout still fits.

Shortcut: if I say "EVIDENCE-PACK DRAFT" and give you supporting material (old reviews, design docs, launch notes), do a full rewrite in one pass, labeled CANDIDATE, plus a decision log (change → evidence → qualifier → why) and the questions I must answer before anything is final. Still don't touch the real file.

## Phase 2: LinkedIn (audit first, then approved batches)
First a READ-ONLY audit comparing my LinkedIn with my approved resume and target roles. Don't change anything yet. Cover, in order:
1. Basics: name, photo/banner (professional, legible), clean URL, location = my real target market, industry, contact links that work
2. Headline: a recognizable target title + my specialty + a few supported skills/domains. No unearned level, title, or certification. Give 2–3 options only if there are genuinely different positioning choices, and recommend one.
3. About: the first two lines say who I am and what roles I fit; strongest recent evidence early; skills tied to real work; no keyword dumps; may be broader than the resume but never contradicts it. For new grads, build it from internships, projects, open source, and research, described honestly and without apologizing.
4. Experience: employer, title, type, location, and dates match the resume; each role opens with product/system context; same honesty rules as Phase 1; projects, volunteering, and programs aren't presented as jobs
5. Skills: every skill is true and backed by evidence; core target skills use LinkedIn's standard names; check which are shown first and which are attached to each role; remove ones that pull my positioning off-target. Don't add a skill just because a job post lists it.
6. Open to Work and job preferences: titles not too broad, locations, work modes, start date, recruiters-only vs. public (explain the tradeoff before changing it)
7. Saved resumes and application answers: stale or conflicting versions, outdated salary/location/work-authorization answers. Never delete without approval.
8. Featured, education, certifications (exact status; planned ≠ earned), projects, recommendations: only what supports the target role, with links that work
9. Privacy: public visibility, contact info exposure, no confidential code/architecture/customer data/unreleased results in text or posts
10. Baseline numbers before any edits (search appearances, profile views, recruiter views, the titles I'm found for). Mark anything paywalled or unavailable as "unavailable"; never estimate.

Include a resume-vs-LinkedIn consistency table (name, target identity, employers/titles, dates, locations, skills, key metrics, education, links) with a decision for each mismatch. They should agree on facts; LinkedIn can add more context.

Give each recommendation as:
  ID · Priority (P0 = factual mismatch, privacy risk, recruiter-filter field, or stale data; P1 = headline/About/Experience/skills; P2 = polish) · Field · Current value · Problem · Evidence from my resume/answers · Exact new value · Notification/privacy effect · Status

Then apply changes in small batches, in this order: (1) identity, titles, dates, location, privacy; (2) Open to Work, preferences, saved resumes; (3) skills; (4) headline, About, experience text; (5) Featured and optional sections. Before each batch, show the exact changes and any notification effect, and wait for my "approved". After each batch, reopen every edited field, compare it to the approved text, check links and formatting, and report applied / verified / failed. Stop immediately if anything unexpected changes.

## When we finish
Give me:
1. Final approved resume bullets (and the path of the new resume file, if one was written)
2. LinkedIn before/after for every field that changed, plus what's still unverified or unavailable
3. Open questions and facts still uncertain
4. My FACTS LEDGER, formatted as `candidate-profile.md` (headline facts, ranked proof points with exact numbers, credentials, an angle map of which proof point fits which team type, and a DO-NOT-CLAIM list). I'll reuse it for recruiter outreach.
5. A date to re-check my LinkedIn numbers (about 2–4 weeks out)

Start with Phase 1: ask only the intake questions my resume doesn't already answer, then show me the first bullets you want to improve.
```

---

**Tips**
- Expect 2–3 passes per role. Correct the AI freely; "that's not quite what happened" is the most useful thing you can say.
- Do the resume first; LinkedIn goes much faster once the facts are settled.
- Save the FACTS LEDGER. It keeps every later message, cover letter, and outreach draft truthful.

*Method inspired by the Resume and LinkedIn runbooks in [nafisk/job-search-ops](https://github.com/nafisk/job-search-ops). This prompt is an independent condensed rewrite. See their repo for the full, more detailed runbooks.*
