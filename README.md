# Ray's Job Prep Package

AI-agent tools for a tech job search. Bring your resume; your AI does the legwork; you stay in control of anything that gets sent.

## What's inside

| Package | What it does |
|---|---|
| [`linkedin-recruiter-outreach`](linkedin-recruiter-outreach/) | Finds technical recruiters at your target companies in LinkedIn Sales Navigator, researches what each one actually hires for, and types personalized InMail drafts (unsent) grounded in your real resume |

## Two ways to use it

### 1. Copy-paste prompt (any AI agent with a browser)
Open [`PROMPT.md`](PROMPT.md), fill in your details, and paste it into Claude Code, Claude in Chrome, Codex, ChatGPT agent mode, or any agent that can control a browser.

### 2. Claude Code plugin (recommended for Claude Code users)
```text
/plugin marketplace add RaymondRJones/rays-job-prep-package
/plugin install linkedin-recruiter-outreach@rays-job-prep-package
```
Then say:
> Use recruiter-outreach. My resume is ./resume.pdf. Targets: Stripe, Google, NVIDIA. Locations: Seattle + Bay Area. Skip Amazon.

The plugin adds 5 skills (`recruiter-outreach`, `candidate-profile`, `recruiter-search`, `recruiter-enrich`, `inmail-drafts`) plus helper scripts. Details: [`linkedin-recruiter-outreach/README.md`](linkedin-recruiter-outreach/README.md).

## Results from the first real run
- 157 US technical recruiters found across 7 companies
- 32 top-tier recruiters researched. Only 10 were real fits; the rest hired for hardware, Staff+ only, security, or HR, which saved about 20 wasted credits
- 5 personalized drafts staged for review in Sales Navigator, each opening with something specific the recruiter had posted

## Ground rules
- The AI **never sends** messages, connects, or follows. You do.
- It **never claims anything** that isn't on your resume.
- It browses **at a human pace**. LinkedIn restricts automation in its User Agreement; use this on your own account, slowly, at your own risk.

## Requirements
- LinkedIn Sales Navigator (for InMail credits and lead search)
- An AI agent with browser control
- Python 3 (optional, for the list-building script)
