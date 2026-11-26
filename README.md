# Ray's Job Prep Package

AI-agent tools for a tech job search. Bring your resume; your AI does the legwork; you stay in control of anything that gets sent.

## The path (do them in order)

| Step | Copy-paste prompt | What you get |
|---|---|---|
| 1 | [**Resume + LinkedIn**](prompts/resume-and-linkedin.md) | Sharper, truthful resume bullets; an audited LinkedIn profile updated in approved batches; and a **facts ledger** of everything you can safely claim |
| 1b | [**LinkedIn banner**](prompts/linkedin-banner.md) | A banner image built from your two or three strongest resume numbers, so a recruiter who looks for five seconds sees the role you're for and proof you're good at it |
| 2 | [**Recruiter outreach**](prompts/recruiter-outreach.md) | Technical recruiters at your target companies found in Sales Navigator, researched for fit, with personalized InMail drafts typed in and left unsent for you to review |
| 3 | [**Hiring-post monitor**](prompts/hiring-post-monitor.md) | Every ~6 hours, finds people at your watchlist companies posting "my team is hiring" on LinkedIn/X (hiring managers, team members, recruiters), keeps the ones that fit your profile in a leads list for later outreach, and flags new matching jobs on public boards. Never contacts anyone. Add or remove companies by chatting |
| 4 | [**Startup founders**](prompts/startup-founders.md) | Hiring YC startups and companies that just raised a seed round, a short brief on what each one needs, the founder who owns the hire (with their Sales Navigator link), and a connection note + InMail drafted for each. Never sends |
| 5 | [**Apply to jobs**](prompts/apply-to-jobs.md) | Applications filled in your Chrome with the [Simplify](https://simplify.jobs) extension, every field checked against your facts ledger, leftover questions answered from an **answer bank** that grows each time you answer one, and a stop for your review before Submit (or, if you say so, submitted for you and reported back only when one fails). Includes a job finder that fills your queue with fresh postings from company job boards, Simplify's job board (with a fit score for each role), or a LinkedIn search |

Fill in the `<<...>>` parts and paste the prompt into any AI assistant. Step 1 works in plain chat; LinkedIn edits and step 2 need an agent that can control a browser (Claude Code with a browser tool, Claude in Chrome, Codex, ChatGPT agent mode). Step 5 needs an agent that works inside your own Chrome, because that is where the Simplify extension lives.

## Prompt or skill?
Every step comes in two forms with the same instructions:

- **Copy-paste prompt** (`prompts/`): works in any AI assistant, no install. Best for step 1, which is a conversation.
- **Claude Code skills** (plugins below): install once, they trigger automatically, update when you reinstall, and include **tested scripts**. Recommended for steps 2 and 3: the outreach scripts already handle Sales Navigator's quirks, and the monitor's job-board checker is real code with tracking of already-seen jobs.

### Install the skills (Claude Code)
```text
/plugin marketplace add RaymondRJones/rays-job-prep-package
/plugin install resume-linkedin-review@rays-job-prep-package
/plugin install linkedin-recruiter-outreach@rays-job-prep-package
/plugin install hiring-monitor@rays-job-prep-package
/plugin install job-applications@rays-job-prep-package
```

| Plugin | Skills / commands | Try saying |
|---|---|---|
| `resume-linkedin-review` | `resume-bullets`, `linkedin-profile-audit`, `linkedin-banner` | "Review my resume at ./resume.pdf for senior backend roles" · "Make me a LinkedIn banner from my resume" |
| `linkedin-recruiter-outreach` | `recruiter-outreach`, `candidate-profile`, `recruiter-search`, `recruiter-enrich`, `inmail-drafts`, `startup-founders` | "Use recruiter-outreach. Targets: Stripe, Google, NVIDIA. Seattle + Bay Area. Skip Amazon." |
| `hiring-monitor` | `hiring-monitor`, `/hiring-monitor add\|remove\|list\|run\|leads\|pause` | "/hiring-monitor add Databricks", then "/loop 6h /hiring-monitor run" |
| `job-applications` | `apply-to-jobs`, `recruiter-screen-prep` | "Find new backend jobs posted this week and apply to them" · "I have a recruiter screen with Stripe on Thursday, prep me" |

The `SKILL.md` folders follow the open Agent Skills format, so other agents that support skills can use them by copying the folder into their skills directory.

## Results from the first real run
- 157 US technical recruiters found across 7 companies
- 32 top-tier recruiters researched. Only 10 were real fits; the rest hired for hardware, Staff+ only, security, or HR, which saved about 20 wasted credits
- 5 personalized drafts staged for review in Sales Navigator, each opening with something specific the recruiter had posted

## Ground rules
- The AI **never sends** messages, connects, or follows. You do.
- It **never submits an application** without your approval for that one application, and never guesses legal, salary, or demographic answers.
- It **never claims anything** that isn't on your resume.
- It browses **at a human pace**. LinkedIn restricts automation in its User Agreement; use this on your own account, slowly, at your own risk.

## Requirements
- LinkedIn Sales Navigator (for InMail credits and lead search)
- An AI agent with browser control
- Google Chrome with the Simplify extension, signed in (step 5 only)
- If Claude Code runs inside another app and can't see Chrome, add `"env": {"CLAUDE_CODE_ENABLE_CFC": "1"}` to `~/.claude/settings.json` and start a new session (in a terminal, `claude --chrome` does the same)
- Python 3 (optional, for the list-building script)
