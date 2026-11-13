// Run as ONE expression on a Sales Navigator lead page. Opens the InMail composer
// if needed and fills Subject + body. NEVER clicks Send.
// Replace SUBJECT and BODY. End BODY with "Best," (Sales Nav appends the signature).
// Tip: build SUBJECT/BODY with JSON.stringify so quotes and newlines are escaped.
(async () => {
  const SUBJECT = 'CHANGE_ME';
  const BODY = `Hi NAME,

CHANGE_ME

Best,`;
  const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
  const buttons = () => [...document.querySelectorAll('button')];

  // Freshly opened lead pages render the Message button late; wait for it.
  for (let i = 0; i < 12 && !buttons().some((b) => b.innerText.trim() === 'Message'); i++) await sleep(1000);

  for (let i = 0; i < 3 && !document.querySelector('textarea'); i++) {
    if (/disabled all communications/i.test(document.body.innerText)) break;
    const btn = buttons().find((b) => b.innerText.trim() === 'Message');
    btn && btn.click();
    await sleep(3000);
  }
  if (/disabled all communications/i.test(document.body.innerText)) return 'BLOCKED: recipient has disabled all communications';

  const subject = [...document.querySelectorAll('input')].find((i) => /Subject/i.test(i.placeholder || ''));
  const body = document.querySelector('textarea');
  if (!subject || !body) return 'Composer not found. Reload the tab (the page sometimes renders blank) and retry.';

  // execCommand('insertText') goes through the app's input handling; setting .value does not,
  // and per-keystroke typing of long text times out.
  subject.focus(); subject.select(); document.execCommand('insertText', false, SUBJECT);
  body.focus(); body.select(); document.execCommand('insertText', false, BODY);
  await sleep(1000);

  const send = buttons().find((b) => b.innerText.trim() === 'Send');
  // "Free to Open Profile" = no credit. "Use 1 of N credits" = costs one. Neither shown: assume 1 credit.
  const cost = (document.body.innerText.match(/Free to Open Profile|Use \d+ of \d+ credits?/) || ['unknown (assume 1 credit)'])[0];
  return JSON.stringify({
    subjectOK: subject.value === SUBJECT,
    bodyOK: body.value === BODY,
    sendEnabled: !!send && !send.disabled,
    cost,
  });
})()
