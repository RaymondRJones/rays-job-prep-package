# Copy-paste prompt: LinkedIn banner from your resume

> **Using Claude Code?** Install the `resume-linkedin-review` plugin and use its `linkedin-banner` skill: same steps, plus a tested template and a script that renders the exact 1584 x 396 image and shows where your photo will cover it.

A recruiter looks at your profile for about five seconds before deciding to read on. The banner is the biggest thing on the page and most people leave it blank. This prompt turns your strongest resume achievements into a banner that says what role you're for and proves it with two or three numbers.

**Before you paste:** have your resume or, better, the `candidate-profile.md` from the [resume + LinkedIn prompt](resume-and-linkedin.md). Fill in the `<<...>>` parts.

---

```text
You are designing my LinkedIn banner (the background image at the top of my profile). A recruiter will look at it for about five seconds. In that time it must tell them what role I'm for and give proof that I'm good at it.

## About me
- Resume or verified profile: <<attach candidate-profile.md or my resume>>
- Role I want recruiters to see me as: <<e.g. Backend Engineer, payments>>
- My current LinkedIn headline: <<paste it, or "none">>
- May the banner name my current employer? <<yes / no>>
- Colors I like, or my photo's background color: <<optional>>

## Rules
1. Use only numbers and names from my resume, with exactly the same values. Never round up or invent one.
2. The role line must be a title I've held or am plainly qualified for. No "Senior" or "Lead" I haven't had.
3. Company names as plain text only. No logos.
4. No contact details, no "open to work" or "hire me", no quotes, no skill clouds, no words like passionate or ninja.

## Step 1: choose the content (show me before designing)
At most three lines, about twenty words in total:
- Role line, six words or fewer: the title a recruiter would search for, then my specialty. It should add to my headline, not repeat it.
- Two or three numbers from my resume, each with a label of five words or fewer. Choose numbers that matter for the role, that a recruiter who isn't an engineer can understand, and that show different things (scale, speed or cost, scope). Two strong numbers beat three with a weak one. If I have no metrics, use concrete facts (internships, shipped projects, degree).
- One line of my best-known employers, my core stack, or both.

Give me two or three options that position me differently, tell me which you recommend and why, and list which resume line each number came from. Wait for me to pick.

## Step 2: design it
Build the banner as a single HTML file sized exactly 1584 x 396 pixels (or an SVG of that size) that I can open in a browser and screenshot.
- Keep the left third empty of text: my profile photo covers the lower-left corner on desktop and more on a phone. Keep text away from the outer edges too.
- A phone shows the banner at about a quarter of that width, so the role line should be about 54 px tall or more and the numbers about 58 px. If a line doesn't fit, cut words instead of shrinking the font.
- Dark background with light text, or the reverse, and one accent color. No icons, stock photos or AI-generated pictures unless I ask.

## Step 3: check it
Show me the result. Then check: nothing is under where the photo sits; the role line and the numbers are readable when the image is shrunk to 390 px wide; and after five seconds someone could say what I do and one number. Fix anything that fails.

## Step 4: hand over
Give me the file, the exact text on it, and upload steps (profile → pencil on the banner → upload → keep the crop at full width). Remind me to check the live profile on my computer and my phone, and to tell you if the photo covers anything.
```
