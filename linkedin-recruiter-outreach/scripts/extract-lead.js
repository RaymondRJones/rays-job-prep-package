// Run as ONE expression on a Sales Navigator lead page (/sales/lead/...).
// Waits a randomized 4–6.5 s (human pacing), scrolls, extracts, and stores into
// localStorage.enr keyed by lead URL. Returns a one-line summary.
(async () => {
  const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
  await sleep(4000 + Math.random() * 2500);
  for (let y = 0; y < 4000; y += 800) { window.scrollTo(0, y); await sleep(400); }

  const T = document.body.innerText;
  const between = (a, b, max = 1500) => {
    const i = T.indexOf(a); if (i < 0) return '';
    const j = b ? T.indexOf(b, i + a.length) : -1;
    return T.slice(i + a.length, j > 0 ? j : i + a.length + max).trim();
  };
  const name = (T.match(/Basic lead information for (.+)/) || [])[1] || '';
  const first = name.split(' ')[0];

  // Header block = the lines right after the name: "(She/Her)  2nd", headline, location.
  // Read the degree ONLY from here; elsewhere "1st" belongs to mutual connections.
  const header = (T.split('Basic lead information for ' + name)[1] || '').split('\n').slice(1, 6);
  const degreeLine = header.find((l) => /\b(1st|2nd|3rd)\b/.test(l)) || '';
  const degree = (degreeLine.match(/\b(1st|2nd|3rd)\b/) || [''])[0];
  const headline = header.find((l) => l && l !== name && !/\b(1st|2nd|3rd)\b|Viewed|First time view/.test(l)) || '';

  const about = between('About\n', 'Relationship', 800).replace(/\s+/g, ' ');
  const currentRole = between('Current role', 'Contact information', 600).replace(/\s+/g, ' ');
  let activity = between('Posts by, comments from, and news mentions about ' + first, 'What you share in common');
  if (!activity) activity = between('Recent activity on LinkedIn', 'What you share in common');
  const posts = [...new Set(activity.split('\n').map((s) => s.trim()).filter((s) => s.length > 80))].slice(0, 4).map((s) => s.slice(0, 450));
  const common = between('Shared interest, groups, and past experience with ' + first, 'Get introduced', 400).replace(/\s+/g, ' ');
  const experience = between('experience\n', 'Education', 1500).split('\n').map((s) => s.trim()).filter(Boolean).join(' ; ').slice(0, 900);
  const education = between('Education\n', 'Interests', 300).replace(/\s+/g, ' ');
  const interests = between('Interests\n', 'See all interests', 600).split('\n').filter((s) => s && !/followers/.test(s)).join(', ').slice(0, 300);
  const mutuals = (T.match(/(\d+) mutual connections?/) || [''])[0];

  const rec = { url: location.href.split('?')[0], name, degree, headline, about, currentRole, posts, common, mutuals, experience, education, interests, openProfile: /Open Profile/i.test(T) };
  const all = JSON.parse(localStorage.getItem('enr') || '{}');
  all[rec.url] = rec;
  localStorage.setItem('enr', JSON.stringify(all));
  return JSON.stringify({ name, degree, headline: headline.slice(0, 80), posts: posts.length, mutuals, common: common.slice(0, 90) });
})()

// Export in halves (tool output cap ~64 KB):
// JSON.stringify(Object.values(JSON.parse(localStorage.getItem('enr'))).slice(0, 16))
