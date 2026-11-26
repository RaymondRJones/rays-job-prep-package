---
name: recruiter-screen-prep
description: Prepare a candidate for a recruiter phone screen at one company. Pulls what was sent with the application (answers, essays, resume file), re-reads the posting, researches the company with dated sources, maps each requirement to proof from the verified profile, lists the gaps the recruiter will probe, and writes a short brief with talking points, a compensation position and questions to ask. Use when someone says "I have a recruiter screen with X", "prep me for my call with X", "what did we tell X when we applied", or asks for a company brief before an interview.
---

# Recruiter screen prep

A recruiter screen checks four things: the story matches the application, the basics fit (level, location, pay, timing), the candidate knows what the company does, and they can explain their own work in two minutes. The brief covers those and nothing else. Technical interview prep is out of scope.

**Inputs:** the company and role; `outreach/applications.csv` and `outreach/applications/` (from `apply-to-jobs`); `outreach/application-answers.md`; `outreach/candidate-profile.md`; the resume file that was sent; anything the user knows about the call (recruiter's name, date, length, what the invite says).
**Output:** `outreach/interviews/<company>-recruiter-screen.md`.

## Rules
1. Every statement about the candidate comes from the profile, the resume, the answer bank or the user. No invented projects, numbers, motives or enthusiasm. Where the honest answer is the user's to give (why they're leaving, what pay they want, how deep a skill goes), leave a marked blank with the question to answer; don't write it for them.
2. Every statement about the company carries its source and date. Mark anything from anonymous reviews, estimates or undated pages as unverified. Leave out what you couldn't confirm instead of smoothing it over.
3. Talking points are what the user will say out loud. Write them as short spoken sentences they can say in their own voice, and keep each answer under about 45 seconds.
4. Don't contact anyone, and don't open the user's email or calendar unless they ask.

## Steps
1. **What we sent.** Find the row in `applications.csv` and the file in `outreach/applications/`. List every question and answer, word for word for free text. If there is no application record (older applications), rebuild it: the log notes, the matching answer-bank entries ("Seen as: <company>"), and the form's question list from the live posting. Say which answers are rebuilt and which are on file.
2. **The posting.** Use the saved snapshot first. Then open the live posting to see if it changed. If the link is dead, look for the same title on the company's board: reposts get a new ID. Greenhouse boards answer at `https://boards-api.greenhouse.io/v1/boards/<company>/jobs/<id>?questions=true&pay_transparency=true` with the text, the form questions and the pay range. Note the date and whether you are reading the original or a repost.
3. **What the recruiter has in front of them.** Read the resume file that was sent, not the profile. List every difference between the resume, the LinkedIn profile and the application answers that a recruiter could notice: dates, employer names, titles, numbers, a skill in the job title that isn't on the resume. These come up in screens.
4. **The company.** What it sells and who pays; named customers; size, revenue, funding and whether it is growing or cutting; news from the last 12 months; the product area of this team; the stack; the stated mission and values; office policy; pay range for this role. Then the interview process as others report it, marked unverified.
5. **Fit map.** One row per requirement in the posting: the proof from the profile (with the number), or "gap". For each gap, write the honest answer and the nearest real experience. Pick the two or three stories that cover the most requirements; those are what the user leads with.
6. **Likely questions.** Walk me through your background · why are you looking / why leave now · why this company · why this role · the skill in the title · what are you looking for in pay · where else are you interviewing and how far along · office days, location, start date, work authorization. Give a talking point for each from the facts, or a marked blank.
7. **Pay.** The posted range, what the answer bank says to answer, and the decision the user has to make before the call. Don't choose a number for them.
8. **Questions to ask.** Five or fewer, specific to this team and to what the research left open (the process and timeline, why the role is open, how the team is set up, what the first months look like).

## The brief
Start with a half page the user can read five minutes before the call: the role in one line, three things to say, the gaps and the answer to each, the pay position, and the open decisions. Then the detail: what we sent, the posting, the fit map, company facts with sources, likely questions, questions to ask, and a list of everything unverified.

Finish by telling the user which blanks only they can fill.

## After the call
When the user reports back, add a "Call notes" section: what was asked, what they answered, what the recruiter said about process, pay and timeline, and the next step. Save any new standing answer (pay stated, start date, notice period) to the answer bank so later screens stay consistent with it, and update the row in `applications.csv`.
