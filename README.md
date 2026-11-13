# Ray's Job Prep Package

AI-agent tools for a tech job search. Bring your resume; your AI does the legwork; you stay in control of anything that gets sent.

## The path (do them in order)

| Step | Copy-paste prompt | What you get |
|---|---|---|
| 1 | [**Resume + LinkedIn**](prompts/resume-and-linkedin.md) | Sharper, truthful resume bullets; an audited LinkedIn profile updated in approved batches; and a **facts ledger** of everything you can safely claim |
| 2 | [**Recruiter outreach**](prompts/recruiter-outreach.md) | Technical recruiters at your target companies found in Sales Navigator, researched for fit, with personalized InMail drafts typed in and left unsent for you to review |

Fill in the `<<...>>` parts and paste the prompt into any AI assistant. Step 1 works in plain chat; LinkedIn edits and step 2 need an agent that can control a browser (Claude Code with a browser tool, Claude in Chrome, Codex, ChatGPT agent mode).

## Claude Code plugin (optional, for step 2)
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
