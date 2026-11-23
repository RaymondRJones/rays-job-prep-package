// Collect job postings and their off-site apply links from a LinkedIn job search.
// Run in a logged-in linkedin.com tab (paste into the console, or run through a
// browser agent's "evaluate JavaScript" tool). Read-only: it applies to nothing.
//
// Note: browser agents with a permission check (e.g. Claude in Chrome) may block this,
// because it calls LinkedIn's internal API with the session token. In that case read the
// normal search results page instead (see SKILL.md, Finding jobs, source 3).
//
// Edit SEARCH, then run. Returns rows of
//   { id, company, role, location, applyType, applyUrl, applied }
// applyType "OffsiteApply" means the application is on the company's own site.
// Anything else (Easy Apply) stays inside LinkedIn and has no outside form.
(async () => {
  const SEARCH = {
    keywords: 'senior backend software engineer',
    geoId: '90000084',        // San Francisco Bay Area; copy geoId from a LinkedIn search URL
    postedWithin: 'r604800',  // seconds: r86400 = 24h, r604800 = 1 week, r2592000 = 1 month
    experience: '4',          // 2 entry, 3 associate, 4 mid-senior, 5 director
    count: 25,
    maxDetails: 15,           // apply links fetched per run; keep this small
  };
  const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
  const csrf = (document.cookie.match(/JSESSIONID="?([^";]+)/) || [])[1];
  if (!csrf) return { error: 'Not logged in to LinkedIn in this tab.' };
  const headers = { 'csrf-token': csrf, 'x-restli-protocol-version': '2.0.0' };

  const query =
    `(origin:JOB_SEARCH_PAGE_JOB_FILTER,keywords:${encodeURIComponent(SEARCH.keywords)},` +
    `locationUnion:(geoId:${SEARCH.geoId}),selectedFilters:(timePostedRange:List(${SEARCH.postedWithin}),` +
    `experience:List(${SEARCH.experience})),spellCorrectionEnabled:true)`;
  const listUrl =
    '/voyager/api/voyagerJobsDashJobCards?decorationId=' +
    'com.linkedin.voyager.dash.deco.jobs.search.JobSearchCardsCollection-220' +
    `&count=${SEARCH.count}&q=jobSearch&query=${query}&start=0`;
  const res = await fetch(listUrl, {
    headers: { ...headers, accept: 'application/vnd.linkedin.normalized+json+2.1' },
    credentials: 'include',
  });
  if (!res.ok) return { error: `Search failed (${res.status}). LinkedIn may have changed this endpoint.` };
  const cards = ((await res.json()).included || []).filter((x) => x.jobPostingTitle);

  const rows = [];
  for (const c of cards.slice(0, SEARCH.maxDetails)) {
    const id = (c.entityUrn.match(/\((\d+),/) || [])[1];
    const row = {
      id,
      company: c.primaryDescription && c.primaryDescription.text,
      role: c.jobPostingTitle,
      location: c.secondaryDescription && c.secondaryDescription.text,
    };
    try {
      const r = await fetch(
        `/voyager/api/jobs/jobPostings/${id}?decorationId=com.linkedin.voyager.deco.jobs.web.shared.WebFullJobPosting-65`,
        { headers: { ...headers, accept: 'application/json' }, credentials: 'include' }
      );
      if (r.ok) {
        const j = await r.json();
        const method = j.applyMethod || {};
        const key = Object.keys(method)[0] || '';
        const value = method[key] || {};
        row.applyType = key.split('.').pop();
        row.applyUrl = value.companyApplyUrl || '';
        row.applied = !!(j.applyingInfo && j.applyingInfo.applied);
      } else {
        row.error = r.status;
      }
    } catch (e) {
      row.error = String(e).slice(0, 80);
    }
    rows.push(row);
    await sleep(1200 + Math.random() * 600); // human pace
  }
  return { found: cards.length, rows };
})();
