# LinkedIn Recruiter Outreach (Claude Code plugin)

Turn a resume (or LinkedIn profile) plus a LinkedIn Sales Navigator seat into:

1. **A verified candidate profile:** the only facts the messages are allowed to claim
2. **A ranked list of technical recruiters** at your target companies and locations
3. **Enriched recruiter profiles:** what each one actually hires for, recent posts, mutual connections, and fit
4. **Personalized InMails typed into Sales Navigator but NOT sent**, so you review each one and click Send yourself

Built from a real run: 157 recruiters across 7 companies, 32 enriched, 5 drafted, in one session.

## What you need
- Claude Code with a **browser automation tool** that can navigate, run JavaScript in the page, and take snapshots (for example the T3 Code preview browser, Claude in Chrome, or a Playwright MCP)
- A LinkedIn **Sales Navigator** seat (InMail credits). You log in yourself; Claude never handles your password
- Your resume (PDF/markdown) **or** your LinkedIn profile URL
- Python 3 (for `scripts/build_list.py`)

## Install
```text
/plugin marketplace add RaymondRJones/rays-job-prep-package
/plugin install linkedin-recruiter-outreach@rays-job-prep-package
```
Or symlink the skills: `ln -s "$(pwd)/skills/"* ~/.claude/skills/`

No Claude Code? Use the copy-paste prompt in [`../prompts/recruiter-outreach.md`](../prompts/recruiter-outreach.md).

## Use
In Claude Code, say something like:

> Use the recruiter-outreach skill. Here's my resume: ./resume.pdf. Targets: Stripe, Google, NVIDIA. Locations: Seattle + Bay Area. I've already got processes with Amazon, so skip them.

The orchestrator skill (`recruiter-outreach`) walks through four stage skills:

| Stage | Skill | Output file (in `./outreach/`) |
|---|---|---|
| 1 | `candidate-profile` | `candidate-profile.md` |
| 2 | `recruiter-search` | `recruiters.csv` |
| 3 | `recruiter-enrich` | `enriched.md` + fit column in CSV |
| 4 | `inmail-drafts` | drafts open in Sales Navigator tabs + `drafts.md` + `inmail-launcher.html` |

You can also run any stage on its own ("enrich the A-tier", "draft 5 more").

## Ground rules baked into the skills
- **Never sends anything.** Claude types drafts; you send them. Sales Navigator has no drafts folder, so drafts live in open tabs; the launcher page lets you open and fill as many as you like in your own browser.
- **Never claims anything that isn't in the candidate profile.** In the original run, the first drafts claimed "observability ownership" that wasn't on the resume. The profile step exists to stop that.
- **Paces itself.** Every profile Claude opens shows up as "X viewed your profile", and LinkedIn runs bot detection. The skills enrich in batches of about 30, with pauses.
- **Lists data only to the user.** Recruiter data stays in local files; don't publish it.

LinkedIn's User Agreement restricts automated access. Use this at a human pace, on your own account, at your own risk.

## Files
```
.claude-plugin/plugin.json
skills/
  recruiter-outreach/SKILL.md    orchestrator
  candidate-profile/SKILL.md     resume/LinkedIn → verified facts
  recruiter-search/SKILL.md      Sales Nav search URLs, extraction, ranking
  recruiter-enrich/SKILL.md      lead-page enrichment + fit triage
  inmail-drafts/SKILL.md         message rules + typing drafts unsent
scripts/
  extract-search-results.js      paste into the search page (one company at a time)
  extract-lead.js                paste into a lead page
  fill-inmail.js                 fills subject/body in the open InMail composer
  build_launcher.py              drafts.md + recruiters.csv → launcher page with a fill-InMail bookmarklet
  build_list.py                  dedupe, filter, tier, guess emails → recruiters.csv
templates/
  candidate-profile.md
  inmail.md
```
