// Run as ONE expression in a Sales Navigator lead-search results page.
// Set COMPANY first. Appends rows to localStorage.rx (survives navigation) and
// returns "<N results> / stored <n>" plus a short preview.
// Row format: company | name | title | location | tenure | leadUrl | ACTIVE
(async () => {
  const COMPANY = 'CHANGE_ME';
  const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
  await sleep(3500);
  const sc = document.querySelector('#search-results-container');
  for (let i = 0; i < 12; i++) { sc && sc.scrollBy(0, 600); await sleep(600); }

  const items = [...document.querySelectorAll('li')].filter((li) => {
    const a = li.querySelector('a[href*="/sales/lead/"]');
    return a && a.closest('li') === li;
  });
  const rows = items.map((li) => {
    const lines = li.innerText.split('\n').map((s) => s.trim()).filter(Boolean)
      .filter((s) => !s.startsWith('Add ') && s !== 'Saved' && s !== 'Viewed' && !s.startsWith('You’ve already'));
    const name = lines[0];
    const afterDegree = lines.slice(lines.findIndex((s) => s.startsWith('·')) + 1);
    let [title, location, tenure] = afterDegree;
    if (title === name) [title, location, tenure] = [location, tenure, ''];   // out-of-network rows repeat the name
    const url = li.querySelector('a[href*="/sales/lead/"]').href.split('?')[0].split(',')[0];
    return [COMPANY, name, title, location, tenure, url, li.innerText.includes('recent post') ? 'ACTIVE' : ''].join(' | ');
  });

  const all = JSON.parse(localStorage.getItem('rx') || '[]');
  localStorage.setItem('rx', JSON.stringify(all.concat(rows)));
  const total = (document.body.innerText.match(/[\d,K]+\+? results/) || ['?'])[0];
  return `${total} / stored ${rows.length}\n` + rows.slice(0, 4).join('\n');
})()

// Export later (keep under the ~64 KB tool cap; filter by company if needed):
// JSON.parse(localStorage.getItem('rx')).filter(r => r.startsWith('Stripe |')).join('\n')
