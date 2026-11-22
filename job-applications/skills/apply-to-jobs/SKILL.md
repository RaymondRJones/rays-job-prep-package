---
name: apply-to-jobs
description: Fill job applications in the user's Chrome using the Simplify extension's autofill, check every field, answer the leftover questions from the verified candidate profile and a saved answer bank, ask the user for anything unknown and remember it for next time, then stop for review before Submit (or submit directly when the user has chosen submit-without-review). Logs every application. Use when someone wants to "apply to jobs", "fill out this application", "use Simplify to apply", or batch-apply to a list of job links.
---

# Apply to jobs (Simplify + answer bank)

Simplify fills the standard fields. You check its work, answer what it leaves blank from facts the user has confirmed, ask for the rest, and remember every answer so the next application needs fewer questions.

**Inputs:** job links (or a search to pick from), `outreach/candidate-profile.md` (from `resume-bullets` / `candidate-profile`), the approved resume file, and the user's LinkedIn profile text if the profile file doesn't cover a question.
**Outputs:** `outreach/application-answers.md` (the answer bank; start from `templates/application-answers.md`) and `outreach/applications.csv` (the log).
**Needs:** the user's own Chrome with the Simplify extension installed and signed in, driven by a browser agent that works inside that Chrome (for example Claude in Chrome). A separate or headless browser won't have the extension. Claude Code started by another app (an SDK or desktop host) loads its Chrome tools only when `CLAUDE_CODE_ENABLE_CFC=1` is set, for example under `env` in `~/.claude/settings.json`; in a terminal, start it with `claude --chrome`.

## Rules
- **Never submit without approval.** The default is per application: fill, show the review summary, and stop. The user presses Submit, or tells you "submit" for that one. If the user says to submit without review ("just submit them"), save that as the submit mode in the answer bank and submit each application once every field is filled from a confirmed source. Even then, stop and hand over any form that has an arbitration agreement, an e-signature, or a "I personally completed this application" certification, and never tick those boxes yourself.
- **Never invent an answer.** Every value comes from the candidate profile, the answer bank, or the user. No guessed dates, numbers, skills, or "yes" to a requirement that isn't supported. This includes personal details: if a form requires something the user won't give (a home address, a legal name), skip that application; don't type a placeholder.
- **Never guess a legal or personal answer:** work authorization, sponsorship, citizenship, clearance, criminal history, non-competes, disability, veteran status, gender, race, age, salary. Saved answer or ask.
- **The user does these themselves:** logins, account creation, passwords, verification codes, CAPTCHAs, e-signatures, and the final "I certify this is true" box. Never try to get past a CAPTCHA or bot check; stop and say so.
- Check `applications.csv` first and never apply twice to the same job. Skip companies on the profile's skip list.
- The answer bank holds sensitive data. Keep it in local files, and type it only into the application form it answers.
- Human pace: a few seconds per page, about 10 applications per session unless the user sets another limit.

## Setup (first run)
1. **Simplify check.** Open the first job's form and confirm the Simplify panel appears and is signed in (it may be collapsed to a small tab on the right edge; click it). Open its Profile tab and compare the saved profile (name, contact, links, each employer, title, dates, bullets, education, the uploaded resume's file name) with `candidate-profile.md` and the current resume. Simplify fills from its own copy, so any difference there ends up in every application. List the differences and let the user fix them in Simplify; don't wait for the fix before starting.
2. **Answer bank.** Create `outreach/application-answers.md` from the template. Don't open with the whole list of standing questions. Run Simplify on the first form and read what it filled: its answers for sponsorship, work authorization, demographics and "how did you hear" are the user's own saved choices, so ask the user to confirm them as standing answers instead of asking from scratch. Ask the remaining standing questions when a form first needs them, and word each one so the answer covers later forms too ("here and on the other Bay Area roles"). The user may answer "ask me every time" or "leave blank"; save that as the answer.

## Finding jobs (when the user gives a search instead of links)
**Remote roles come only from Simplify's job board (source 2).** Don't fill a remote search from company boards or LinkedIn. For on-site and hybrid roles, use the first source that covers what the user wants. All of them write to the same queue, `outreach/job-queue.csv` (`found, company, role, location, system, linkedin_job_id, apply_url, status`), and skip anything already queued or in `applications.csv`.

1. **Company job boards (default; no login, no browser).** Run `python3 scripts/find_jobs.py --dir outreach`. It reads the public Greenhouse, Lever and Ashby boards for every company in `outreach/companies.txt`, keeps postings that match `outreach/job-search.json` (title terms, exclusions, locations, maximum age in days, companies to skip), and appends the new ones as `queued` with a direct link to the form. The first run creates both files from defaults: set the filters from the candidate profile's target role and locations, and put the skip list and any company the user is already interviewing with in `skip_companies`. Add companies with `--add "Name" "Name"`; preview with `--dry-run`. Run it again whenever the queue runs low.
2. **Simplify's job board (every remote search, plus companies without a public board).** Run `python3 scripts/simplify_board.py --dir outreach --dry-run`, check the list with the user, then run it again without `--dry-run`. It searches simplify.jobs the way the site does (no login): full-time software, backend and full-stack roles at the levels in the `fit` block of `job-search.json`, remote US by default (`--where bay-area` for Bay Area roles of any arrangement). It opens each posting for the years asked, skills, salary and location limits, scores the fit (0-100) against the candidate's skills, drops roles outside the years range, needing a clearance, or limited to other states, resolves the apply link to the employer's own form, and appends the keepers to the queue. It also reads the company's stack from the posting text and checks each item against `fit.skills`, so a role built on a language the candidate doesn't have scores low and says why ("stack not on your resume: node"). Every job it checked, with the stack on and off the resume and the reasons for drops, goes to `outreach/simplify-matches.csv`. Set `fit` first: years, home state, salary floor, and `skills` holding every language, framework, datastore, cloud service and AI tool on the resume AND the LinkedIn profile (the union; a skill on neither stays off the list). `--easy-forms` keeps only Greenhouse, Ashby and Lever forms; `--limit` caps how many postings it opens (default 60). It relies on the search key simplify.jobs gives every browser, so it can break when the site changes; keep runs small. For new grads and interns, `find_jobs.py --simplify new-grad|internships` reads Simplify's public lists instead.
3. **LinkedIn search (companies without a public board, or a broader sweep).** In a logged-in LinkedIn tab, run `scripts/linkedin-job-links.js` (edit its `SEARCH` block). Keep jobs whose apply type is `OffsiteApply`; Easy Apply jobs have no outside form. Drop staffing marketplaces, then append the rest to the queue.

Show the new rows and let the user remove any before applying. Greenhouse, Ashby and Lever forms are single-page and quickest. Workday needs an account per employer, which the user creates.

## Without Simplify
If the browser you control doesn't have the extension, skip the autofill step and fill every field from the profile and answer bank. Everything else stays the same: one batch of questions, the review summary, the user submits.

## Each application
1. **Read the posting.** Title, level, location, work mode, and hard requirements (clearance, citizenship, years, on-site only). If one conflicts with the profile or the answer bank, say so before filling anything and let the user decide. Some postings also cap applications (for example "2 roles per 90 days"); tell the user before using one up, and record the limit in the log.
   **Check the company's stack against the resume and LinkedIn.** List the languages, frameworks, datastores and cloud the posting names (the "our stack is…" line and the requirements, not just Simplify's skill tags), and mark each one as on the resume, on LinkedIn only, or on neither. Say it in one line before filling ("Stack: Node, TypeScript, Elixir, MySQL. On resume: TypeScript, MySQL. Not on resume or LinkedIn: Node, Elixir"). If none of the stack's languages are on either, tell the user and let them decide before filling. If the user has said to apply despite gaps, apply, but never claim a gap skill anywhere: "Do you have experience with Node?" is No (or ask), "years of Node" is 0 unless the user says otherwise, and free-text answers lead with the stack items the candidate does have. Log the gaps in the application's notes.
2. **Open the form.** If it needs a login or a new account, wait for the user. Many career sites show the form inside an embedded frame from the application system (Greenhouse, Ashby, Lever); read and fill the fields in that frame, and list every question, required or optional, before filling. If the frame can't be read, or the company's own apply link is broken, open the application system's direct form instead: Greenhouse `https://job-boards.greenhouse.io/embed/job_app?for=<company>&token=<job id>`, Ashby `<job URL>/application`. Simplify works on those pages.
3. **Run Simplify's autofill** and wait for it to finish. If you can't press its button, ask the user to. If Simplify doesn't support the site, fill the standard fields from the profile yourself.
4. **Read back every field, including the ones Simplify filled.** Common misses: dropdowns left on the default, "current employer" checkbox, date formats, "today's date" off by a day or in the wrong format, a "legal name as on your ID" field filled with the short name, duplicated or missing experience entries, the wrong resume file, location autocomplete picking a different city. Fix them from the profile. Also list every consent, acknowledgement and certification box Simplify ticked (arbitration, "I certify", text messages, marketing, talent pool); a ticked box is an answer the user has to have given, so untick or ask unless the answer bank covers it.
5. **Answer what's left** using the table below. Reuse a saved answer only when the question means the same thing (see Matching).
6. **Ask once.** Collect every question you can't answer and every draft that needs approval, and ask the user in one batch: the company and role, the question exactly as written, the answer options, and your suggested answer with its source if you have one. Show a free-text draft in full. While an answer is pending, start reading and filling the next application in another tab instead of waiting.
7. **Review summary.** A table of every field: value, source (Simplify / profile / answer bank / you just told me / draft), and anything left blank on purpose. Then stop. In submit-without-review mode, skip the stop: submit, and put the same table in the end-of-session report only for fields you changed or answered yourself.
8. **After submitting,** confirm it went through before logging `submitted`: a confirmation page or URL (Greenhouse `/confirmation`), a success banner (Ashby), or a confirmation email. If the form scrolls back up instead, read the page for a validation error or a request for an emailed verification code; a code is the user's to enter, so log `blocked` with "needs verification code" and leave the tab open. Then update the log and the answer bank.
9. **Leave unfinished forms open.** Keep each filled-but-unsubmitted application in its own tab and tell the user which tab needs what. Log the direct form URL so the form can be reopened if the tab is lost.

## How to answer each kind of question
| Kind | Examples | Answer from |
|---|---|---|
| Facts | contact details, links, employers, titles, dates, degree | `candidate-profile.md`, copied exactly |
| Standing answers | work authorization, sponsorship, relocation, start date, notice period, work mode, "previously employed here?", "how did you hear?" | Answer bank only. Missing → ask, then save |
| Legal attestations | criminal history, clearance, export-control citizenship, non-compete, financial licenses (FINRA), employment by the company's auditor | Answer bank if the user saved one; otherwise ask every time |
| Consents | text or WhatsApp messages, marketing email, "keep my details for future roles", storing demographic answers, fraud or identity review | Answer bank; ask once and save. If the only option is "Yes" and the field is required, say so when asking |
| Workplace | days in office, relocation, "do you plan to work remotely", commute distance, unusual schedules (six-day weeks, on-call) | Answer bank for the same city and number of days. More days, another city, or a schedule question is a new question |
| Demographic (voluntary) | gender, race, veteran, disability | The user's saved choice for each, which may be "decline to answer" |
| Salary | expected salary, current salary | The user's saved wording. Never give current salary unless they saved one |
| Experience counts | "years of Java", "years of backend experience" | Add up the roles in the profile where it was real work, show the arithmetic, never round up. Save as DERIVED until the user confirms |
| Yes/no skills | "Do you have experience with Kubernetes?" | Yes only if the profile ties it to real work; otherwise ask |
| Free text | "Why us?", "Describe a hard project", cover letter | Draft from ranked proof points plus the posting, within the form's limit (default 60–150 words), in plain language. DRAFT until approved |
| Anything else | | Ask |

If Simplify offers its own AI-written answer for a free-text question, treat it as a draft: check every claim against the profile before showing it to the user.

**Don't embellish free-text answers.** Fluent drafting slips in plausible details that aren't facts. Before typing or submitting any free-text answer (including in submit-without-review mode), reread it sentence by sentence and tie each claim to a line in the profile, resume or LinkedIn. Cut or rewrite anything that isn't there:
- invented process or habits ("I write a spec with acceptance criteria first", "I run parallel agent sessions", "I now flag this in reviews")
- invented outcomes or context ("so nothing broke", "before release", "the lesson I learned")
- motives or trade-offs the profile doesn't state ("instead of adding throughput")
- stack overclaims ("your stack is mine" when one of their tools is missing; name only the overlap)
- a specific feature credited to a tool or method when the profile doesn't say so (don't claim a feature was "built with coding agents" unless that's on record)

If the question asks for a story the profile doesn't have (a failure, a lesson, an agent-built feature), answer with the closest real fact and say less, or ask the user. A shorter true answer beats a richer invented one. Save the checked answer to the answer bank so the next form reuses it.

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
- Write to the answer bank and the log after each application, not at the end of the session, so nothing is lost if the browser or session drops.
- A DERIVED answer the user confirms becomes CONFIRMED.

## The log
`outreach/applications.csv`: `date, company, role, location, url, ats, status, resume_file, new_questions, notes`. Status is one of `filled-awaiting-review`, `submitted`, `skipped` (with the reason), `blocked` (login, CAPTCHA, verification code, unsupported form). In `notes`, say exactly what the user has to do for anything not submitted. Write `submitted` only after seeing the confirmation.

## Finish
Report: applications submitted, filled and waiting, skipped or blocked with reasons; new questions learned this session; answers still DRAFT or DERIVED; Simplify profile fixes worth making; and how many questions per application needed the user (it should fall over time).
