---
name: apply-to-jobs
description: Fill job applications in the user's Chrome using the Simplify extension's autofill, check every field, answer the leftover questions from the verified candidate profile and a saved answer bank, ask the user for anything unknown and remember it for next time, then stop for review before Submit. Logs every application. Use when someone wants to "apply to jobs", "fill out this application", "use Simplify to apply", or batch-apply to a list of job links.
---

# Apply to jobs (Simplify + answer bank)

Simplify fills the standard fields. You check its work, answer what it leaves blank from facts the user has confirmed, ask for the rest, and remember every answer so the next application needs fewer questions.

**Inputs:** job links (or a search to pick from), `outreach/candidate-profile.md` (from `resume-bullets` / `candidate-profile`), the approved resume file, and the user's LinkedIn profile text if the profile file doesn't cover a question.
**Outputs:** `outreach/application-answers.md` (the answer bank; start from `templates/application-answers.md`) and `outreach/applications.csv` (the log).
**Needs:** the user's own Chrome with the Simplify extension installed and signed in, driven by a browser agent that works inside that Chrome (for example Claude in Chrome). A separate or headless browser won't have the extension.

## Rules
- **Never submit without approval for that application.** Fill, show the review summary, and stop. The user presses Submit, or tells you "submit" for that one application. Approval for one application never carries to the next.
- **Never invent an answer.** Every value comes from the candidate profile, the answer bank, or the user. No guessed dates, numbers, skills, or "yes" to a requirement that isn't supported.
- **Never guess a legal or personal answer:** work authorization, sponsorship, citizenship, clearance, criminal history, non-competes, disability, veteran status, gender, race, age, salary. Saved answer or ask.
- **The user does these themselves:** logins, account creation, passwords, verification codes, CAPTCHAs, e-signatures, and the final "I certify this is true" box. Never try to get past a CAPTCHA or bot check; stop and say so.
- Check `applications.csv` first and never apply twice to the same job. Skip companies on the profile's skip list.
- The answer bank holds sensitive data. Keep it in local files, and type it only into the application form it answers.
- Human pace: a few seconds per page, about 10 applications per session unless the user sets another limit.

## Setup (first run)
1. **Simplify check.** Open a supported job page and confirm the Simplify panel appears and is signed in. Compare Simplify's saved profile (name, contact, links, each employer, title, dates, education, the uploaded resume) with `candidate-profile.md`. Simplify fills from its own copy, so any difference there ends up in every application. List the differences and let the user fix them in Simplify.
2. **Answer bank.** Create `outreach/application-answers.md` from the template. Ask the standing questions it lists in one batch (work authorization, sponsorship, relocation, start date, salary wording, work mode, demographic choices, how to answer "how did you hear about us"). The user may answer "ask me every time" or "leave blank" for any of them; save that as the answer.

## Finding jobs (when the user gives a search instead of links)
1. In a logged-in LinkedIn tab, run `scripts/linkedin-job-links.js` (edit the `SEARCH` block: keywords, location, date posted, level). It is read-only and returns each job's company, role, location and off-site apply link.
2. Keep jobs whose apply type is `OffsiteApply`. Easy Apply jobs stay inside LinkedIn and have no outside form.
3. Drop skip-list companies, companies the user is already interviewing with, staffing marketplaces, and anything already in `applications.csv`.
4. Save the rest to `outreach/job-queue.csv` (`found, company, role, location, system, linkedin_job_id, apply_url, status`), show the list, and let the user pick or reorder before applying.

Greenhouse, Ashby and Lever forms are single-page and quickest. Workday needs an account per employer, which the user creates.

## Without Simplify
If the browser you control doesn't have the extension, skip the autofill step and fill every field from the profile and answer bank. Everything else stays the same: one batch of questions, the review summary, the user submits.

## Each application
1. **Read the posting.** Title, level, location, work mode, and hard requirements (clearance, citizenship, years, on-site only). If one conflicts with the profile or the answer bank, say so before filling anything and let the user decide.
2. **Open the form.** If it needs a login or a new account, wait for the user. Many career sites show the form inside an embedded frame from the application system (Greenhouse, Ashby, Lever); read and fill the fields in that frame, and list every question, required or optional, before filling.
3. **Run Simplify's autofill** and wait for it to finish. If you can't press its button, ask the user to. If Simplify doesn't support the site, fill the standard fields from the profile yourself.
4. **Read back every field, including the ones Simplify filled.** Common misses: dropdowns left on the default, "current employer" checkbox, date formats, duplicated or missing experience entries, the wrong resume file, location autocomplete picking a different city. Fix them from the profile.
5. **Answer what's left** using the table below. Reuse a saved answer only when the question means the same thing (see Matching).
6. **Ask once.** Collect every question you can't answer and every draft that needs approval, and ask the user in one batch: the question exactly as written, the answer options, and your suggested answer with its source if you have one.
7. **Review summary.** A table of every field: value, source (Simplify / profile / answer bank / you just told me / draft), and anything left blank on purpose. Then stop.
8. **After the user submits,** confirm the confirmation page or email notice appeared, then update the log and the answer bank.

## How to answer each kind of question
| Kind | Examples | Answer from |
|---|---|---|
| Facts | contact details, links, employers, titles, dates, degree | `candidate-profile.md`, copied exactly |
| Standing answers | work authorization, sponsorship, relocation, start date, notice period, work mode, "previously employed here?", "how did you hear?" | Answer bank only. Missing → ask, then save |
| Legal attestations | criminal history, clearance, export-control citizenship, non-compete | Answer bank if the user saved one; otherwise ask every time |
| Demographic (voluntary) | gender, race, veteran, disability | The user's saved choice for each, which may be "decline to answer" |
| Salary | expected salary, current salary | The user's saved wording. Never give current salary unless they saved one |
| Experience counts | "years of Java", "years of backend experience" | Add up the roles in the profile where it was real work, show the arithmetic, never round up. Save as DERIVED until the user confirms |
| Yes/no skills | "Do you have experience with Kubernetes?" | Yes only if the profile ties it to real work; otherwise ask |
| Free text | "Why us?", "Describe a hard project", cover letter | Draft from ranked proof points plus the posting, within the form's limit (default 60–150 words), in plain language. DRAFT until approved |
| Anything else | | Ask |

If Simplify offers its own AI-written answer for a free-text question, treat it as a draft: check every claim against the profile before showing it to the user.

## The answer bank
One entry per question:

```
### <question in plain words>
- Answer: <exact value, or "ask me every time" / "leave blank">
- Status: CONFIRMED (user said it) | DERIVED (computed; show source) | DRAFT (not approved)
- Applies to: all | <company or role type>
- Seen as: "<wording 1>" · "<wording 2>"
- Source / date: <user, 2026-11-20> or <profile: Walmart Mar 2025–present>
```

**Matching.** Reuse a CONFIRMED answer when the new question asks the same thing in different words, and add the new wording to "Seen as". Treat it as a new question when the wording changes the meaning: "authorized to work now" vs. "will you now or in the future require sponsorship", "willing to relocate" vs. "willing to relocate at your own cost", "years of experience" vs. "years of professional experience". When unsure, ask.

**Learning.**
- Save every new question and its answer after each application, including "leave blank" decisions.
- When the user corrects an answer, replace it and note the date; never keep two answers for one question.
- Approved free-text answers are saved by theme (why this kind of company, hardest bug, leadership example). Reuse the factual core and rewrite the company-specific sentences each time; the rewrite is a DRAFT again.
- Re-confirm answers that go stale (start date, notice period, salary, location) if they're more than about 30 days old.
- Keep a "Simplify misses" list of fields it gets wrong or skips repeatedly, and suggest the user add or fix them in their Simplify profile.
- A DERIVED answer the user confirms becomes CONFIRMED.

## The log
`outreach/applications.csv`: `date, company, role, location, url, ats, status, resume_file, new_questions, notes`. Status is one of `filled-awaiting-review`, `submitted`, `skipped` (with the reason), `blocked` (login, CAPTCHA, unsupported form). Write `submitted` only after seeing the confirmation.

## Finish
Report: applications submitted, filled and waiting, skipped or blocked with reasons; new questions learned this session; answers still DRAFT or DERIVED; Simplify profile fixes worth making; and how many questions per application needed the user (it should fall over time).
