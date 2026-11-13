---
name: inmail-drafts
description: Write personalized recruiter InMails grounded in the candidate's verified profile and each recruiter's enrichment, then stage them in LinkedIn Sales Navigator composers WITHOUT sending, either typed into browser tabs or via a launcher page + fill bookmarklet in the user's own browser. Use when the user wants outreach messages drafted or staged for review.
---

# InMail drafts

## Message rules
- **Only facts from `candidate-profile.md`.** Re-read it before drafting. No "owned X" unless the profile says so.
- **Open with the recruiter's hook** from enrichment: a role they posted, the org they hire for, or a post of theirs. Be specific ("your Azure Core Senior SWE post"), not generic flattery.
- **Then 2–3 proof points** chosen by the angle map (performance teams → latency/cost wins; AI teams → LLM/RAG work).
- **One credential line** (ranking, teaching, audience), using a number only if verified.
- **One clear ask:** "Could I send you my resume for that role, or anything similar on <team>?" For 🟡/🔴: "…or point me to the right recruiter?"
- **80–130 words.** Subject under 60 characters, specific and not salesy.
- **Don't name mutual connections** unless the user confirms they know them.
- **Don't claim a location** the profile doesn't show (e.g. "I'm local").
- **End with "Best,"** because Sales Navigator appends the user's signature automatically, so "Best, Name" would sign twice.

Template: `<plugin root>/templates/inmail.md`. Save all drafts to `outreach/drafts.md` in the format below (the launcher parses it):

```
### 3. Parisa Derogari: NVIDIA, AI talent for Software Engineering
**Subject:** Pricing-systems engineer interested in NVIDIA

Hi Parisa,
...
Best,
```

When the user says they sent one, append ` ✅ SENT <date>` to its `###` heading so it's excluded from the launcher and nobody gets messaged twice.

## Before staging: check for duplicates
Open the Sales Navigator inbox and check that none of the recipients already have a thread (earlier outreach may have used a different template). Report the credits balance shown there ("InMail credits: N left").

## Facts about Sales Navigator that shape the flow
- **There is no InMail drafts folder.** A draft exists only while its composer is open; closing or navigating the tab loses it. Tell the user this up front: *the open tabs are the drafts.*
- **Agent-controlled browsers cap open tabs** (T3 Code preview: about 8). For more drafts than that, use the launcher (option B) or stage in batches.
- **"Free to Open Profile"** in the composer header means the InMail costs no credit. "Use 1 of N credits" means one credit. Neither visible → assume 1 credit. Report the cost per tab.
- Freshly opened lead pages sometimes render blank or show the Message button late. Wait for it; if the body is empty, reload the tab and retry.

## Staging, option A: type into tabs (agent browser)
Use when there are ≤ ~7 drafts or the user wants them staged right now.
1. Open each recruiter's lead page in a **new tab** (one tab per draft).
2. Run `<plugin root>/scripts/fill-inmail.js` with the subject and body (build them with `JSON.stringify`). It waits for the **Message** button, opens the composer, fills both fields with `document.execCommand('insertText')` (typing keystroke by keystroke timed out; setting `.value` isn't picked up by the app), and returns `{subjectOK, bodyOK, sendEnabled, cost}`.
3. If it returns BLOCKED (*"recipient has disabled all communications"*), close the tab, tell the user, and use the next recruiter.
4. **Never click Send.**
5. Tell the user which tab holds which draft and its cost. Never close or reload a tab holding an unsent draft unless the user says so.

## Staging, option B: launcher page (user's own browser), the default for larger batches
Use when there are more drafts than the tab cap, or the user wants to review and send at their own pace in their normal browser.
1. `python3 <plugin root>/scripts/build_launcher.py outreach/drafts.md outreach/recruiters.csv outreach/inmail-launcher.html [--staged "Name,Name"]`. `--staged` fades rows already open as drafts in the agent browser.
2. Open the HTML file in the user's browser (macOS: `open -a "Google Chrome" <file>`).
3. Tell the user: drag **Fill InMail** to the bookmarks bar → click **Open all leads** (allow pop-ups) → click the bookmark in each tab → review → Send themselves. "Copy subject/body" buttons are the manual fallback.
4. If drafts change, rebuild the launcher; the user must re-drag the bookmark (it embeds the drafts).

## When the profile changes
If the user corrects a fact, update `drafts.md`, re-fill every open draft (select all + `insertText` replaces cleanly), and rebuild the launcher.

> `<plugin root>` = the `linkedin-recruiter-outreach` folder two levels above this SKILL.md (resolve symlinks).
