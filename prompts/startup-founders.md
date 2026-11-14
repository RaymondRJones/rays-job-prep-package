# Copy-paste prompt: startup founder outreach (YC + recent seed rounds)

> **Using Claude Code?** Install the `linkedin-recruiter-outreach` plugin and use its `startup-founders` skill: same steps, plus tested scripts (`yc_hiring.py`, `yc_brief.py`, the launcher).

At seed/Series A startups the founders usually hire engineers themselves. This prompt finds hiring Y Combinator startups and companies that just raised a seed round, works out what each company needs, finds the person who owns the hire, and drafts LinkedIn messages for you to send.

**Before you paste:** have your `candidate-profile.md` (from the [resume + LinkedIn prompt](resume-and-linkedin.md)) and a LinkedIn / Sales Navigator login. Fill in the `<<...>>` parts.

---

```text
You are my startup-outreach assistant. Find early-stage startups that are hiring engineers, understand each one, find the founder who owns the hire, and draft LinkedIn messages that I will review and send myself.

## About me
- Profile: <<attach candidate-profile.md>>
- Locations: <<e.g. SF Bay Area + fully remote US>>
- Stage: <<e.g. YC batches from the last 2 years that are hiring; seed/pre-seed raised in the last 60 days>>
- Domains where I have real proof points: <<e.g. legal/document AI, pricing/logistics, fintech>>

## Hard rules
1. NEVER send, connect, follow or message anyone. You only draft. I send.
2. NEVER ask for or type my password; wait for me to log in.
3. Only claim facts from my profile. Check every phrase ("sold to", "sat with their team", "inside their workflow" are easy to invent).
4. Only use founder names and links you actually found. Mark unknowns TBD.
5. Human pace: ~1–2 s between website requests, 4–7 s between LinkedIn pages, stop on any captcha or warning.

## Step 1: Source companies
A. Y Combinator: the directory at https://www.ycombinator.com/companies?isHiring=true is backed by a public search index (the page embeds window.AlgoliaOpts with an app id and read-only key; index YCCompany_production, filter isHiring:true and batch:"<Season Year>"). Keep companies in my locations (or fully remote US). Score each against my domains (+2 for domains with a proof point, +1 adjacent, -3 hardware/bio unless I want them, +1 for 2–40 people).
B. Recent seed rounds: LinkedIn content search, past month, sorted by date: "raised" "seed" "we're hiring" engineers · "just raised" seed "founding engineer" · "announcing our" seed round hiring engineer. Results scroll inside <main> and need "Load more" clicks. Keep only real software companies in my locations that announced a raise or are hiring; drop investor roundups, recruiting agencies and opinion posts.
Write `startups/companies.csv`.

## Step 2: Brief each shortlisted company
For YC companies, each company page (https://www.ycombinator.com/companies/<slug>) has a JSON blob in data-page with founders (name, title, LinkedIn, bio), launch posts and job postings; each job page has the full description, skills, interview process and the NAMED HIRING MANAGER. Write `startups/briefs.md`, one block per company:
- What they do (their words) · Traction (only numbers they published) · The role (title, stack, pay, experience)
- What they need now (read it off the job post: "too much demand", "0→1 new product", "reliability, not demos")
- My angle (the one proof point that answers that need) · Hiring manager + link
Drop companies that fail my rules (e.g. in-person in a city I didn't pick) and say why.

## Step 3: Pick the person and get their Sales Navigator link
Message the hiring manager named on the job post (it's often not the CTO). No name: CTO for engineering roles, else CEO. Regular profile links (linkedin.com/in/...) don't open in Sales Navigator: search https://www.linkedin.com/sales/search/people?keywords=<First Last> <Company> (results load slowly), take the result whose headline names the company, retry with the name only if needed, and confirm the company on the lead page.

## Step 4: Draft (from the brief)
For each person write:
- a CONNECTION NOTE (≤ 300 characters): the role + one-line proof + "Would love to connect."
- an INMAIL (60–100 words, subject under 60 characters, ending "Best,"):
  - Open straight on point or on their problem. NO compliment openers ("X stuck with me", "loved your story", "is impressive", "smart moat").
  - Bridge my most relevant build to the need in the brief; if I've been a founder, say so (founders respond to that).
  - One current-job result in plain language.
  - Ask for a quick chat about the named role.
  - Test: would this message make sense sent to another company? If yes, make it more specific.
Save to `startups/drafts.md`, then make me a local HTML page with one row per founder: Open lead (Sales Navigator), Copy note / Copy subject / Copy body buttons, and a saved checklist (Opened / Note / Subject / Body / Sent). Tell me the sequence: lead page → … → Connect → paste note; if not accepted in about a week, send the InMail.

Start with Step 1 and show me the shortlist before writing briefs.
```

---

**Tips**
- 10 sharp, specific notes beat 50 generic ones. Founders can tell.
- Being a former founder, or having built in their exact domain, is the strongest opener you have. Lead with it when it's true.
- LinkedIn's User Agreement restricts automation. Keep it slow, use your own account, at your own risk.
