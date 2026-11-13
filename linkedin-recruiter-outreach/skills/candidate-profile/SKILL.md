---
name: candidate-profile
description: Turn a job seeker's resume (PDF/markdown/text) or LinkedIn profile into a verified facts file that outreach messages are allowed to use, with metrics, target role, and a "do not claim" list. Use before writing any recruiter, referral, or cover message.
---

# Candidate profile

Goal: one file, `outreach/candidate-profile.md`, that is the **only** source of claims for every message. In the original run, messages drafted from memory claimed experience that wasn't on the resume. This step prevents that.

## Inputs
- **Resume file:** read it directly (use the PDF skill/tool for PDFs).
- **LinkedIn profile:** with the user logged in, open `https://www.linkedin.com/in/me/` (resolves to their profile), then `…/details/experience/`. Scroll to load everything, then read `document.querySelector('main').innerText`. Also capture the headline, location, About, follower count, and "Open to work" settings.
- If both exist, use both and flag disagreements to the user.

## Write the file using `<plugin root>/templates/candidate-profile.md`
Include:
1. **Headline facts:** current title/company, location, years of experience (from the first full-time role's start date), and the target role in their own words (the About section often says it).
2. **Per role:** dates, stack, and **metric-bearing bullets copied faithfully** (e.g. "cut Cosmos DB latency 50%, $60K/yr"). Keep the numbers exact.
3. **Proof points ranked:** the 5–6 strongest, most specific, most impressive facts. These open the messages.
4. **Audience/credentials:** followers, subscribers, rankings, talks. Only numbers that appear on the profile or that the user confirms. If several numbers conflict (e.g. "top 1%" vs "top 3%"), use the one on the profile and note the conflict.
5. **Angle map:** which proof point fits which kind of team (infra/performance → latency wins; AI teams → LLM/RAG work; payments → fintech roles).
6. **Do-not-claim list:** anything the user said earlier, or that appeared in old drafts, that the profile doesn't support. Also note overstated generalizations (e.g. "6 years of distributed systems" when one job was front-end).

## Then
Show the user the proof points and the do-not-claim list in chat, and ask them to correct anything. Update the file before drafting messages.

> `<plugin root>` = the `linkedin-recruiter-outreach` folder two levels above this SKILL.md (resolve symlinks).
