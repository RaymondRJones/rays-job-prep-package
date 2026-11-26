---
name: linkedin-banner
description: Design a LinkedIn banner (background image) for a job seeker from their verified resume achievements, built for a recruiter who looks at the profile for about five seconds. Picks the target role line and the two or three strongest numbers, shows options, then renders an exact 1584 x 396 PNG from an HTML template and checks it against the profile photo and at phone size. Use when someone asks for a LinkedIn banner, cover image, background photo or header, or wants their profile to look stronger to recruiters at a glance.
---

# LinkedIn banner

A recruiter opening a profile sees the photo, the name, the headline and the banner before reading a word of the experience section. The banner is the largest of the four and most people leave it blank. Its job is to answer two questions in five seconds: **what role is this person for, and is there proof they're good at it?**

**Inputs:** `outreach/candidate-profile.md` (from `resume-bullets` / `candidate-profile`) or the resume; the target role; the current LinkedIn headline if known.
**Outputs:** `outreach/linkedin-banner/banner.html` and `banner.png` (1584 x 396).
**Needs:** Google Chrome, Chromium or Edge for `scripts/render_banner.py`. Without one, hand the user the HTML file and the text, and they can screenshot it or rebuild it in Canva or Figma at 1584 x 396.

## Rules
1. Every number and name on the banner is on the resume, with the same value as the resume and the LinkedIn experience section. A recruiter who sees "−50%" on the banner and "−40%" below it stops trusting both.
2. The role line names a title the candidate has held or is plainly qualified for. No "Senior", "Staff" or "Lead" they haven't had.
3. Ask before showing a current employer's name or numbers if the profile doesn't already show them publicly.
4. Text only for company names. No company logos, no product screenshots.
5. No contact details (they get scraped), no "open to work" or "hire me" lines, no quotes, no skill clouds, no words like passionate, driven, ninja or guru.

## 1. Choose what goes on it
At most three lines, about twenty words in total:

- **Role line (six words or fewer):** the title a recruiter would search for, then the specialty. "Backend Engineer · Payments & APIs". It should add to the headline under the name, not repeat it word for word.
- **Proof (two or three numbers):** from the ranked proof points in the profile. Choose numbers that:
  - matter for the target role;
  - a recruiter who isn't an engineer can understand without context ("−50% query latency", not "p99 on the partition-aware read path");
  - show different things: one for scale, one for speed or cost, one for scope or users;
  - are safe to show in public.
  Each gets a label of five words or fewer saying what the number measures. Two strong numbers beat three with a weak one.
- **Where line:** the best-known employers, or the core stack, or both, as plain text.

A candidate with no metrics (new grad, career changer) uses concrete facts instead: "3 internships", "2 shipped apps", "1,200 GitHub stars", the degree and school.

Write two or three options that position the candidate differently (for example backend-platform vs. applied-AI), say which one you recommend and why, and get the user's approval of the exact text before rendering.

## 2. Build it
Copy `templates/linkedin-banner.html` to `outreach/linkedin-banner/banner.html` and change only the text and the five colors at the top.

- **The left third stays empty.** The profile photo covers the lower-left corner on desktop and more of it on a phone. All text sits in the template's content area, to the right of the photo and away from the edges.
- **Sizes.** A phone shows the banner at about a quarter of its pixel width. The role line and the numbers have to be readable there, so keep them at the template's sizes or larger. If a line doesn't fit, cut words; don't shrink the font.
- **Color.** Dark background with light text, or the reverse. One accent color. Offer a second color scheme only if the user asks or the first clashes with their photo.
- Don't add icons, illustrations or an AI-generated picture behind the text unless the user asks. If they do, it sits on the left or far right at low contrast, and never contains text.

## 3. Render and check
```
python3 scripts/render_banner.py outreach/linkedin-banner/banner.html --preview
```
This writes `banner.png` and `banner-preview.png`. Open the preview and check:

1. No red outline. A red outline means a line runs past the safe area.
2. Nothing sits under the photo circle.
3. In the phone-size version, the role line and the numbers are readable. The small labels may not be; that is acceptable.
4. Read it for five seconds, look away, and say what the person does and one number. If you can't, cut content.

Show the user the image, not a description of it.

## 4. Upload
The user uploads it (profile → the pencil on the banner), or you do it in their logged-in browser after they approve this image. LinkedIn may crop on upload; keep the crop box at full width. Then look at the live profile on desktop and at a narrow window width, and confirm the photo covers nothing. If something is covered, move the content area and render again.

## Finish
Give the file path, the text that is on the banner, and where each number came from in the resume. If the banner's role line and the LinkedIn headline now say the same thing, suggest a headline change through `linkedin-profile-audit`.
