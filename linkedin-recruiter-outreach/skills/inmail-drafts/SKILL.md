---
name: inmail-drafts
description: Write personalized recruiter InMails grounded in the candidate's verified profile and each recruiter's enrichment, then type them into LinkedIn Sales Navigator composers in separate tabs WITHOUT sending. Use when the user wants outreach messages drafted or staged for review.
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

Template: `<plugin root>/templates/inmail.md`. Also save all drafts to `outreach/drafts.md`.

## Typing drafts into Sales Navigator (unsent)
1. Open each recruiter's lead page in a **new tab** (one tab per draft; navigating away loses the draft).
2. Click the **Message** button (button whose text is exactly `Message`). Wait ~3 s; retry once if the composer isn't there.
3. If the composer says *"the recipient has disabled all communications"*, close the tab, tell the user, and use the next recruiter.
4. Run `<plugin root>/scripts/fill-inmail.js` with the subject and body. It uses `document.execCommand('insertText')` on the Subject input and the `textarea`. Typing long text keystroke by keystroke timed out; setting `.value` directly isn't picked up by the app.
5. Confirm that `Send` is enabled and the composer shows "Use 1 of N credits". **Never click Send.**
6. Tell the user which tab holds which draft, and remind them each send costs one credit.

## When the profile changes
If the user corrects a fact, re-fill every open draft. Select all + `insertText` replaces the content cleanly.

> `<plugin root>` = the `linkedin-recruiter-outreach` folder two levels above this SKILL.md (resolve symlinks).
