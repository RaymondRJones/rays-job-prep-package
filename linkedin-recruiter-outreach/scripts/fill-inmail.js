// Run as ONE expression on a Sales Navigator lead page. Opens the InMail composer
// if needed and fills Subject + body. NEVER clicks Send.
// Replace SUBJECT and BODY. End BODY with "Best," (Sales Nav appends the signature).
(async () => {
  const SUBJECT = 'CHANGE_ME';
  const BODY = `Hi NAME,

CHANGE_ME

Best,`;
  const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

  for (let i = 0; i < 3 && !document.querySelector('textarea'); i++) {
    if (/disabled all communications/i.test(document.body.innerText)) break;
    const btn = [...document.querySelectorAll('button')].find((b) => b.innerText.trim() === 'Message');
    btn && btn.click();
    await sleep(3000);
  }
  if (/disabled all communications/i.test(document.body.innerText)) return 'BLOCKED: recipient has disabled all communications';

  const subject = [...document.querySelectorAll('input')].find((i) => /Subject/i.test(i.placeholder || ''));
  const body = document.querySelector('textarea');
  if (!subject || !body) return 'Composer not found. Take a snapshot and check.';

  // execCommand('insertText') goes through the app's input handling; setting .value does not,
  // and per-keystroke typing of long text times out.
  subject.focus(); subject.select(); document.execCommand('insertText', false, SUBJECT);
  body.focus(); body.select(); document.execCommand('insertText', false, BODY);
  await sleep(1000);

  const send = [...document.querySelectorAll('button')].find((b) => b.innerText.trim() === 'Send');
  const credits = (document.body.innerText.match(/Use \d+ of \d+ credits/) || [''])[0];
  return JSON.stringify({ subject: subject.value, bodyChars: body.value.length, sendEnabled: !!send && !send.disabled, credits });
})()
