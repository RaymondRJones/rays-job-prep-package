#!/usr/bin/env python3
"""Build a local InMail launcher page from drafts.md + recruiters.csv.

The page lets the user stage any number of drafts in their OWN browser:
  - "Open all leads" opens each recruiter's Sales Navigator lead page in a tab
  - a "Fill InMail" bookmarklet (drag to bookmarks bar) opens the composer on the
    current lead page and types that recruiter's subject + body. It never sends.
  - per-row "Copy subject" / "Copy body" buttons as a manual fallback

Why: Sales Navigator has no InMail drafts folder (a closed composer is lost), and
agent-controlled browsers cap open tabs (T3 preview: ~8). This removes both limits.

drafts.md format (as written by the inmail-drafts skill):
    ### 3. Parisa Derogari: NVIDIA, ...        <- name is the text before ":"
    **Subject:** Pricing-systems engineer ...
    Hi Parisa,
    ...
    Best,
Sections whose heading contains "SENT" or "(email" are skipped.

recruiters.csv needs `name` and `url` columns (build_list.py output).

Usage:
    python3 build_launcher.py outreach/drafts.md outreach/recruiters.csv outreach/inmail-launcher.html \
        [--staged "Shari Fox,Wil Price"]   # names already open as drafts elsewhere (shown faded)
"""
import argparse
import csv
import html
import json
import re
import sys
import urllib.parse

FILL_JS = r"""(async()=>{const D=__DATA__;const k=Object.keys(D).find(k=>location.href.includes(k));if(!k){alert('No draft for this page. Open a recruiter lead page first.');return}const [S,B]=D[k];const sl=m=>new Promise(r=>setTimeout(r,m));const bs=()=>[...document.querySelectorAll('button')];for(let i=0;i<15&&!document.querySelector('textarea');i++){if(/disabled all communications/i.test(document.body.innerText)){alert('This recruiter has disabled messages.');return}const b=bs().find(b=>b.innerText.trim()==='Message');if(b&&i%4===0)b.click();await sl(1000)}const s=[...document.querySelectorAll('input')].find(i=>/Subject/i.test(i.placeholder||''));const t=document.querySelector('textarea');if(!s||!t){alert('Composer not found. Click Message, then click the bookmark again.');return}s.focus();s.select();document.execCommand('insertText',false,S);t.focus();t.select();document.execCommand('insertText',false,B);t.setSelectionRange(0,0);t.scrollTop=0})()"""


def parse_drafts(text):
    out = []
    for sec in re.split(r"\n### ", text)[1:]:
        heading = sec.split("\n", 1)[0]
        if "SENT" in heading or "(email" in heading:  # sent, or an email draft (not an InMail)
            continue
        m = re.match(r"(?:\d+\.\s*)?([^:]+):", heading)
        subj = re.search(r"\*\*Subject:\*\*\s*(.+)", sec)
        if not (m and subj and "Hi " in sec and "Best," in sec):
            continue
        body = sec[sec.index("Hi "):sec.index("Best,") + len("Best,")]
        out.append({"name": m.group(1).strip(), "subject": subj.group(1).strip(), "body": body})
    return out


def lead_urls(csv_path):
    urls = {}
    with open(csv_path, newline="") as f:
        for row in csv.DictReader(f):
            url = row.get("url", "")
            if "/sales/lead/" in url:
                urls[row["name"].strip().rstrip(".").lower()] = url
    return urls


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("drafts")
    ap.add_argument("recruiters_csv")
    ap.add_argument("out_html")
    ap.add_argument("--staged", default="", help="comma-separated names already open as drafts")
    a = ap.parse_args()

    drafts = parse_drafts(open(a.drafts).read())
    urls = lead_urls(a.recruiters_csv)
    staged = {s.strip().lower() for s in a.staged.split(",") if s.strip()}
    rows, missing = [], []
    for d in drafts:
        url = urls.get(d["name"].rstrip(".").lower())
        if not url:
            missing.append(d["name"])
            continue
        d["url"] = url
        d["id"] = url.split("/sales/lead/")[1].split(",")[0].split("?")[0]
        d["staged"] = d["name"].lower() in staged
        rows.append(d)

    js = FILL_JS.replace("__DATA__", json.dumps({r["id"]: [r["subject"], r["body"]] for r in rows}))
    bookmarklet = "javascript:" + urllib.parse.quote(js, safe="(){}[];:,'=>!&|.?/+*")
    assert urllib.parse.unquote(bookmarklet[len("javascript:"):]) == js

    e = html.escape
    trs = "".join(
        f'<tr data-id="{e(r["id"])}" class="{"staged" if r["staged"] else ""}"><td><b>{e(r["name"])}</b>'
        + (" <span class=tag>already open elsewhere</span>" if r["staged"] else "")
        + f'<div class=subj>{e(r["subject"])}</div></td>'
        f'<td><a class=btn href="{e(r["url"])}" target="_blank" rel="noopener">Open lead</a></td>'
        f'<td><button data-k=subject data-t="{e(r["subject"])}">Copy subject</button> '
        f'<button data-k=body data-t="{e(r["body"])}">Copy body</button></td>'
        '<td class=prog><span data-s=opened>Opened</span><span data-s=subject>Subject</span><span data-s=body>Body</span>'
        '<label class=sent><input type=checkbox data-s=sent> Sent</label></td></tr>'
        for r in rows
    )
    new = sum(not r["staged"] for r in rows)
    page = f"""<!doctype html><meta charset=utf-8><title>InMail launcher</title>
<style>body{{font:14px system-ui;max-width:960px;margin:32px auto;padding:0 16px;color:#1d2226}}h1{{font-size:22px}}table{{width:100%;border-collapse:collapse}}td{{padding:10px 8px;border-bottom:1px solid #e5e5e5;vertical-align:top}}.subj{{color:#666;font-size:13px;margin-top:3px}}.btn,button{{display:inline-block;padding:6px 12px;border-radius:16px;border:1px solid #0a66c2;color:#0a66c2;background:#fff;text-decoration:none;cursor:pointer;font:inherit;white-space:nowrap}}.bm{{display:inline-block;padding:10px 18px;background:#0a66c2;color:#fff;border-radius:20px;text-decoration:none;font-weight:600}}.staged{{opacity:.55}}.tag{{font-size:11px;background:#eef3f8;padding:2px 6px;border-radius:8px;margin-left:6px}}ol li{{margin:6px 0}}.note{{background:#fff8e6;padding:10px 14px;border-radius:8px}}.prog{{white-space:nowrap}}.prog span{{display:inline-block;font-size:12px;color:#999;border:1px solid #ddd;border-radius:10px;padding:2px 7px;margin-right:4px}}.prog span.on{{color:#1a7f37;border-color:#1a7f37;background:#e7f3ea}}.prog span.on::before{{content:'✓ '}}.sent{{font-weight:600;margin-left:4px;cursor:pointer}}tr.inprog td{{background:#fffbe6}}tr.done td{{background:#eef7f0}}tr.done b{{text-decoration:line-through;color:#666}}#progress{{font-weight:600;margin-left:12px}}</style>
<h1>InMail launcher: {len(rows)} unsent drafts</h1>
<ol>
<li>Drag this button to your bookmarks bar: <a class=bm href="{e(bookmarklet)}">Fill InMail</a></li>
<li>Click <b>Open all leads</b>. If the browser blocks pop-ups, allow them for this file and click again.</li>
<li>In each tab, click the <b>Fill InMail</b> bookmark. It opens the composer and types that recruiter's subject and body.</li>
<li>Review, then click <b>Send</b> yourself. Nothing is ever sent automatically.</li>
</ol>
<p class=note>Keep tabs open until you send: Sales Navigator has no InMail drafts folder, so a closed composer is lost. Click the bookmark again to refill a tab.</p>
<p><button id=all>Open all leads ({new} new)</button> <label><input type=checkbox id=inc> include faded rows</label><span id=progress></span> <button id=reset style="float:right;border-color:#999;color:#666">Reset checklist</button></p>
<table>{trs}</table>
<script>
function legacyCopy(s){{const ta=document.createElement('textarea');ta.value=s;ta.style.position='fixed';ta.style.opacity='0';document.body.appendChild(ta);ta.focus();ta.select();let ok=false;try{{ok=document.execCommand('copy')}}catch(e){{}}ta.remove();return ok}}
async function copyText(s){{try{{await navigator.clipboard.writeText(s);return true}}catch(e){{return legacyCopy(s)}}}}
const KEY='inmail-progress';const st=JSON.parse(localStorage.getItem(KEY)||'{{}}');
function save(){{localStorage.setItem(KEY,JSON.stringify(st))}}
function mark(tr,k,v=true){{const id=tr.dataset.id;(st[id]=st[id]||{{}})[k]=v;save();render(tr)}}
function render(tr){{const s=st[tr.dataset.id]||{{}};tr.querySelectorAll('span[data-s]').forEach(x=>x.classList.toggle('on',!!s[x.dataset.s]));tr.querySelector('input[data-s=sent]').checked=!!s.sent;tr.classList.toggle('done',!!s.sent);tr.classList.toggle('inprog',!s.sent&&!!(s.opened||s.subject||s.body));renderTotal()}}
function renderTotal(){{const trs=[...document.querySelectorAll('tr[data-id]')];const sent=trs.filter(tr=>(st[tr.dataset.id]||{{}}).sent).length;const started=trs.filter(tr=>{{const s=st[tr.dataset.id]||{{}};return !s.sent&&(s.opened||s.subject||s.body)}}).length;document.getElementById('progress').textContent=`${{sent}} of ${{trs.length}} sent · ${{started}} in progress`}}
document.querySelectorAll('button[data-t]').forEach(b=>b.onclick=async()=>{{const o=b.dataset.label||(b.dataset.label=b.textContent);const ok=await copyText(b.dataset.t);b.textContent=ok?'Copied ✓':'Copy failed';b.style.background=ok?'#e7f3ea':'#fdecea';setTimeout(()=>{{b.textContent=o;b.style.background=''}},1500);if(ok)mark(b.closest('tr'),b.dataset.k)}});
document.querySelectorAll('tr[data-id] a.btn').forEach(a=>a.addEventListener('click',()=>mark(a.closest('tr'),'opened')));
document.querySelectorAll('input[data-s=sent]').forEach(c=>c.onchange=()=>mark(c.closest('tr'),'sent',c.checked));
document.querySelectorAll('tr[data-id] span[data-s]').forEach(x=>{{x.style.cursor='pointer';x.title='Click to toggle';x.onclick=()=>{{const tr=x.closest('tr');mark(tr,x.dataset.s,!(st[tr.dataset.id]||{{}})[x.dataset.s])}}}});
document.getElementById('reset').onclick=()=>{{if(confirm('Clear all checkmarks on this page?')){{for(const k in st)delete st[k];save();document.querySelectorAll('tr[data-id]').forEach(render)}}}};
document.querySelectorAll('tr[data-id]').forEach(render);
document.getElementById('all').onclick=()=>{{const inc=document.getElementById('inc').checked;document.querySelectorAll('tr[data-id]').forEach(tr=>{{if(!inc&&tr.classList.contains('staged'))return;if((st[tr.dataset.id]||{{}}).sent)return;window.open(tr.querySelector('a').href,'_blank');mark(tr,'opened')}})}};
</script>"""
    open(a.out_html, "w").write(page)
    print(f"{len(rows)} drafts -> {a.out_html}")
    if missing:
        print("No lead URL in CSV for: " + ", ".join(missing), file=sys.stderr)


if __name__ == "__main__":
    main()
