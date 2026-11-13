// Run as ONE expression on a LinkedIn content-search page
// (https://www.linkedin.com/search/results/content/?keywords=...&datePosted=%22past-week%22&sortBy=%22date_posted%22).
// Drives a queue of searches stored in localStorage:
//   localStorage.hq = JSON array of keyword strings still to run
//   localStorage.hp = {key: post} collected so far (deduped)
// Each call: extract posts from the current page, shift the queue, navigate to the next search
// (2.5 s later, after returning). Re-run until it returns "DONE", then export localStorage.hp.
// Keep total runtime under ~12 s: some agent browsers time out evaluate calls at 15 s.
//
// Seed it first (one expression):
//   const qs=['Acme "my team" hiring','Acme "join my team"'];localStorage.hq=JSON.stringify(qs);localStorage.hp='{}';
//   location.href='https://www.linkedin.com/search/results/content/?keywords='+encodeURIComponent(qs[0])+'&datePosted=%22past-week%22&sortBy=%22date_posted%22'
(async () => {
  const DATE = '%22past-week%22'; // or %22past-24h%22 for scheduled runs, %22past-month%22 for a first run
  const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
  let q = JSON.parse(localStorage.getItem('hq') || '[]');
  if (!q.length) return 'DONE';
  await sleep(3500);
  for (let i = 0; i < 6; i++) { window.scrollBy(0, 1500); await sleep(700); }
  if (/captcha|security verification|unusual activity/i.test(document.body.innerText.slice(0, 1500))) return 'BLOCKED: stop LinkedIn for 24 h';

  // Each result has a visually-hidden "Feed post" heading. Climb to the card that holds the author link.
  // Post permalinks are NOT in the DOM; keep the author's profile URL + post text instead.
  const heads = [...document.querySelectorAll('h2,h3,span')].filter((e) => e.textContent.trim() === 'Feed post');
  const cards = new Set(); const posts = [];
  for (const h of heads) {
    let c = h;
    for (let i = 0; i < 10 && c.parentElement; i++) {
      c = c.parentElement;
      if (c.querySelector('a[href*="/in/"],a[href*="/company/"]') && c.innerText.length > 200) break;
    }
    if (cards.has(c)) continue; cards.add(c);
    const lines = c.innerText.split('\n').map((s) => s.trim())
      .filter((s) => s && s !== 'Feed post' && !/^•/.test(s) && s !== 'Follow' && s !== 'Connect');
    const name = lines[0] || '';
    const headline = lines.find((s, i) => i > 0 && s !== name && !/^(1st|2nd|3rd)|3rd\+|^\d+\s?(h|d|w|mo|yr)\b/.test(s)) || '';
    const age = lines.find((s) => /^\d+\s?(h|d|w|mo|m|yr)\b/.test(s)) || '';
    const degree = (c.innerText.match(/•\s*(1st|2nd|3rd\+?)/) || [, ''])[1];
    const profile = ((c.querySelector('a[href*="/in/"]') || c.querySelector('a[href*="/company/"]') || {}).href || '').split('?')[0];
    posts.push({ name, headline, degree, age, profile, text: c.innerText.replace(/\s+/g, ' ').slice(0, 900), query: q[0] });
  }

  const all = JSON.parse(localStorage.getItem('hp') || '{}'); let added = 0;
  for (const p of posts) { const k = p.profile + '|' + p.text.slice(80, 160); if (!all[k]) { all[k] = p; added++; } }
  localStorage.setItem('hp', JSON.stringify(all));
  const done = q.shift(); localStorage.setItem('hq', JSON.stringify(q));
  if (q.length) setTimeout(() => {
    location.href = 'https://www.linkedin.com/search/results/content/?keywords=' + encodeURIComponent(q[0]) + '&datePosted=' + DATE + '&sortBy=%22date_posted%22';
  }, 2500);
  return `${done}: ${posts.length} posts, ${added} new, total ${Object.keys(all).length}, left ${q.length}`;
})()
