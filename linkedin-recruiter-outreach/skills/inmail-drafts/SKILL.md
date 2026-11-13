---
name: inmail-drafts
description: Write personalized recruiter outreach (Sales Navigator InMails, or emails when a recruiter publishes an address or has InMail disabled) grounded in the candidate's verified profile and each recruiter's enrichment, then stage InMails WITHOUT sending, either typed into browser tabs or via a launcher page + fill bookmarklet in the user's own browser. Use when the user wants recruiter messages drafted, rewritten, or staged for review.
---

# Recruiter outreach drafts

**Inputs:** `candidate-profile.md` (the only facts you may claim), enrichment for each recruiter (desk, recent posts, fit 🟢/🟡/🔴).
**Outputs:** `outreach/drafts.md`, plus staged InMails (tabs or launcher). Nothing is ever sent by you.

## 1. Write for the person who reads it

The first reader is a recruiter skimming dozens of messages on a phone, usually not an engineer. In a few seconds they decide:
1. Does this person fit a role I have open?
2. Is there credible proof they're good?
3. Are they low-risk to put in front of a hiring manager (ready now, passed similar bars)?
4. What exactly do they want from me?

Every sentence should answer one of those. Anything else gets cut.

### Structure (about 100 words; 80–130 max)
| Part | Length | What it does |
|---|---|---|
| **Hook** | 1 sentence | Something specific to *this* recruiter: a role they posted, the team they hire for, a post of theirs. Not reusable for anyone else. |
| **Proof** | 2 sentences | One result from the current job, one from a past job, chosen for their desk. |
| **Signal** | 1 sentence | The strongest verified "low-risk, ready now" fact (see below). |
| **Ask** | 1 sentence | One request they can answer yes to. |

Subject under 60 characters, specific, not salesy: `Re: your <Role> post`, `<Background> engineer for <Team>`.

### Plain language
- **Outcomes, not mechanisms.** "Cut database query times in half and saved about $60K a year", not "cut Cosmos DB p50 latency 50% via partition-aware access patterns".
- **No tool or vendor names** (Cosmos DB, Chroma, GPT-4, Spring, Kafka) and **no insider jargon** (deterministic evals, multi-tenant, sharding). The resume carries the technical detail.
- **Keep 1–2 keywords that match their reqs** (AI, LLM, search, backend, cloud, infrastructure). Recruiters scan for them.
- **One number per result.** Three numbers in one sentence reads as noise.
- Read each sentence as a non-engineer: if they'd need to look something up, rewrite it.

> **Before:** "I'm a backend engineer on Walmart's delivery-pricing systems, where I cut Azure Cosmos DB query latency 50% and work on deterministic evals across 100,000+ active deliveries. Before that I founded a company and built a HIPAA-compliant AI document platform with a GPT-4 + Chroma RAG pipeline that cut attorney review time 50%."
>
> **After:** "I'm a Bay Area backend engineer at Walmart, where I cut database query times in half and saved about $60K a year. Before that I founded a company and built an AI tool that reads and summarizes legal documents, cutting a law firm's review time in half."

### Choosing proof for their desk
| Recruiter's desk | Lead with |
|---|---|
| Databases, infrastructure, performance | speed and cost wins, large migrations |
| AI / ML / LLM / search | the AI product the candidate built and its business impact (say "AI search tool that answers questions about documents" for retrieval/search teams) |
| Payments, pricing, finance | correctness: tricky bugs found, testing at scale |
| Generalist SWE | the cleanest, biggest-number result |

### The signal line
Use the single strongest verified fact that says "already passed a comparable bar" or "ready to move now". In order of strength:
1. **A recently cleared big-tech interview loop.** Use only the user's approved wording. If the role fell through, explain in a few words ("before a headcount change closed the role"). Never call it an offer, never say "paused" if it's closed, and state the level only if the user wants it.
2. A competing process with a real deadline (only if true and the user wants it used).
3. A ranking, teaching or audience credential, with a number only if verified.

Ask the user before using any of these for the first time, and record the approved wording in `candidate-profile.md`.

### The ask
- 🟢 "Would you be open to me sending my resume for that role, or anything similar on <team>?"
- 🟡/🔴 "Could I send my resume, or would you point me to the recruiter who covers <area>?"

### Never
- Claim anything not in `candidate-profile.md` ("owned X", "led Y", a location, a level).
- Name a mutual connection unless the user confirms they know them.
- Mention an offer that was rescinded, or a company the user doesn't want to discuss.
- Flatter generically ("I've always admired <Co>").

### Channel differences
| | InMail (Sales Navigator) | Email (published address, or InMail disabled) |
|---|---|---|
| Sign-off | End at `Best,` (Sales Nav appends the signature) | `Best,` + full name + LinkedIn URL |
| Subject | Required, < 60 chars | Same |
| Extras | none | One line: "Resume attached" if the user will attach it |
| Staging | Section 3 | Save to `drafts.md` under `### N. Name (email: addr)`; don't stage, the user sends from their mail client |

Only email an address the recruiter published themselves or the user verified. Never send a guessed address without verification.

## 2. Save and self-check

Save every draft to `outreach/drafts.md` (the launcher parses this format):
```
### 3. Parisa Derogari: NVIDIA, AI talent for Software Engineering 🟢
**Subject:** Pricing-systems engineer interested in NVIDIA

Hi Parisa,
...
Best,
```

Run a check over the file before staging and fix anything it flags:
- word count 80–130 per body, subject < 60 chars
- grep for tool names and jargon you know are in the profile (e.g. `Cosmos|GPT|Chroma|RAG|deterministic|multi-tenant|Java|Spring`)
- every number and claim traceable to `candidate-profile.md`
- each hook mentions something only this recruiter has

When the user sends one, append ` ✅ SENT <date>` to its heading so it drops out of the launcher. When a fact changes, update `drafts.md`, refill open tabs, and rebuild the launcher.

## 3. Stage InMails (never send)

**Before staging:** open the Sales Navigator inbox and confirm none of the recipients already have a thread. Note the balance ("InMail credits: N left").

**Sales Navigator facts that shape this:**
- **No InMail drafts folder.** A draft exists only while its composer tab is open. Tell the user: *the open tabs are the drafts.*
- **Agent browsers cap tabs** (T3 preview: about 8).
- **"Free to Open Profile"** in the composer header = no credit; "Use 1 of N credits" = one credit; neither visible = assume one.
- Lead pages sometimes render blank or show **Message** late: wait, then reload once.

**Option A: type into tabs** (≤ ~7 drafts, or the user wants them staged now)
1. One new tab per recruiter's lead page.
2. Run `<plugin root>/scripts/fill-inmail.js` with the subject and body (build them with `JSON.stringify`). It opens the composer, fills both fields with `execCommand('insertText')`, and returns `{subjectOK, bodyOK, sendEnabled, cost}`.
3. BLOCKED ("recipient has disabled all communications") → close the tab, tell the user, offer an email draft if an address is published.
4. Report which tab holds which draft and its cost. Never close or reload a tab with an unsent draft unless the user says so.

**Option B: launcher page** (default for larger batches; runs in the user's own browser)
1. `python3 <plugin root>/scripts/build_launcher.py outreach/drafts.md outreach/recruiters.csv outreach/inmail-launcher.html [--staged "Name,Name"]` (`--staged` fades rows already open in agent tabs).
2. Open it in the user's browser (macOS: `open -a "Google Chrome" <file>`).
3. Tell the user: drag **Fill InMail** to the bookmarks bar → **Open all leads** (allow pop-ups) → click the bookmark in each tab → review → Send. Copy buttons are the fallback.
4. The bookmark embeds the drafts: after any rebuild, the user must drag it again.

**Never click Send**, in either option.

> `<plugin root>` = the `linkedin-recruiter-outreach` folder two levels above this SKILL.md (resolve symlinks).
