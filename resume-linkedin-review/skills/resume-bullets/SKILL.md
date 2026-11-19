---
name: resume-bullets
description: Interactively rewrite a software engineer's resume bullets so ownership, mechanism, scale and impact are clear, without inventing anything. One role or a few bullets at a time, approval before any file edit. Ends with a facts ledger (candidate-profile.md) for LinkedIn and outreach. Use when someone wants to improve, tailor, or review their resume.
---

# Resume bullets

Goal: make real experience easier to understand, not bigger than it was.

## Start
1. Read the whole resume. Ask only the intake questions it doesn't answer: target role and level; specialization (frontend/backend/full-stack/mobile/infra-platform/ML/embedded); which role to start with; a target job description (optional, don't block on it); anything that must stay private.
2. Tell the person: good wording usually takes a few passes, and you'll go one role or a few bullets at a time.

## States (label everything)
`CANDIDATE` (your draft) → `APPROVED` (they said yes) → `APPLIED` (written to a new file and checked). Never present a candidate as final.

## Scoring (1–10)
Scores show where things stand and how much each change matters. They are judgment against this rubric, not a prediction of interviews: say so once and never present them as precise.
| Score | Meaning |
|---|---|
| 1–3 | Hurts them: vague, misleading, off-target, or missing |
| 4–6 | Understandable but generic; a recruiter can't tell what they did or how well |
| 7–8 | Clear, specific, defensible; one gap left |
| 9–10 | A recruiter for the target role gets it in one read; nothing to add or cut |

- Score against the target role and level. Every score gets a one-line reason and the one thing that would raise it.
- Every proposed change gets a **Necessity** score (9–10 = a strong result isn't possible without it; 5–8 = clear improvement; 1–4 = cosmetic) and an expected result ("5 → 8 if they confirm the number"). Work in order of necessity.
- At 8+, say "leave it". Don't invent problems to justify edits.
- Never raise a score with anything unconfirmed. A truthful bullet with no number can still score 8.
- Same rubric every time; rescore after approvals so before and after compare. Can't see it → "not scored", never a guess.

**Resume scorecard, before any rewrite:** overall, per role, five qualities (clarity, ownership, evidence, fit to target role, scanability), and a compact table of every bullet (first few words · score · biggest gap · necessity). Start with the highest-necessity bullets, usually low scores in the most recent role.

## Per bullet
Check which of these it already answers, and don't force all six:
| Element | Question |
|---|---|
| Action | What did they personally do? |
| Object | Which system, feature, or problem? |
| Mechanism | How was it built or fixed (key tech)? |
| Scope | How big or how often (users, requests, data, teams)? |
| Impact | What got faster, cheaper, more reliable, or more valuable? |
| Evidence | How do they know? |

Ask **1–3 short questions** that unlock the most (ownership vs. team, the problem, the mechanism, a measured or observed result, launched or not). **Never ask them to guess a metric.** A truthful bullet without a number beats an invented one.

Write **one recommended rewrite**, with score now → expected. Add 1–2 alternatives only for a real tradeoff (depth vs. impact vs. ownership vs. brevity), each with a one-line reason. Wait for them to pick, combine, or correct, then revise.

## Honest claim language
| Situation | Wording |
|---|---|
| They did it and measured it | cut, reduced, increased |
| The team delivered it; they built a part | "built X, supporting the team's Y" |
| An experiment reported it | "experiment attributed …" |
| A tool detected or verified it | identified, measured, verified |
| Approximate | ~, about |
| A goal, not achieved yet | "targeting", "supporting a goal to" |
| Not launched | the finished component + its intended use |

## Style
- Lead with a true action verb and put the strongest detail early. Explain what the thing is before listing tech.
- About one technical signal and one result/scale signal per bullet; extra details go to "interview notes".
- Over ~30 words / ~220 characters → try a shorter version, and keep the long one only if every detail earns its place.
- Translate internal names and acronyms for outside readers. Split bullets that merge two projects. Keep their natural confidence. Consistent tense, varied openings.

Illustrative (not real data):
> Before: "Worked on checkout service performance improvements"
> After: "Rewrote the checkout service's inventory lookup as a batched Redis read, cutting p99 latency from ~900ms to ~250ms across ~2M daily orders". Every number is confirmed by the person.

## Facts ledger
After each round, update `outreach/candidate-profile.md` (format: the `candidate-profile` skill's template, if installed): confirmed facts and metrics, preferred terms, rejected wording, privacy limits, approved bullets, ranked proof points, an angle map, and a DO-NOT-CLAIM list. Never make them repeat a decision.

## Evidence-pack mode (only if they say "EVIDENCE-PACK DRAFT")
With supplied evidence (reviews, design docs, launch notes): one full rewrite labeled CANDIDATE, a decision log (change → evidence → qualifier → why), and the questions they must answer. Still don't touch the real file.

## Scope
Don't change the template, section order, page count, titles, or dates, and don't add sections, unless asked. Flag structural issues separately.

## Finish
Check: every bullet is backed by their answers, ownership is clear, metrics have the right qualifier and scope, tech is tied to real work, no shared results across projects, and they could defend every line in an interview. With their OK, write approved bullets to a **new copy** (keep the original), render it, and confirm the layout fits. Report: state, bullets, before/after scorecard (plus skipped changes and what each is still worth), open questions, next bullets to review. Suggest `linkedin-profile-audit` next.
