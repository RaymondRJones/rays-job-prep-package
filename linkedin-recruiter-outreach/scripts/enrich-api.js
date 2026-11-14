// Bulk lead enrichment through Sales Navigator's own data API (the same requests a lead page makes).
// ~8 s per lead, no page loads, and it returns things the page hides until you open the composer:
//   lastMsg (date you last messaged them -> "already contacted"), inmailRestriction (DISABLED = no InMail),
//   badges.openLink (Open Profile = free InMail), degree (-1 = out of network, name may be blank), mutuals,
//   positions with role descriptions, About, posts/comments from the last ~88 days.
//
// 1. Open any https://www.linkedin.com/sales/... page in the logged-in browser and stay on it.
// 2. Seed the queue with lead ids (the part after /sales/lead/ and before the first comma), one expression:
//      localStorage.enrq=JSON.stringify([...ids]); localStorage.enr2='{}'; JSON.parse(localStorage.enrq).length
// 3. Run THIS file as one expression. It returns 'started' and keeps running in the page (don't navigate).
// 4. Poll: (()=>({left:JSON.parse(localStorage.enrq).length, done:Object.keys(JSON.parse(localStorage.enr2)).length,
//            running:window._enrRunning, err:window._enrErr}))()
//    Stop early with window._enrStop=true. Re-running resumes the queue and retries rows that had errors.
// 5. Export localStorage.enr2 as a file download (Blob + <a download>), then run triage_enrichment.py.
//
// Gotchas learned the hard way: every profile decoration must include entityUrn (else HTTP 500); the profile URN in
// the posts query must have ( ) , percent-encoded (else 400); the posts window must be < 89 days (else 400).
// Stops on HTTP 429/999. Pace stays human (~3-7 s between leads). Stop on any warning and wait a day.
(()=>{
if(window._enrRunning) return 'already running';
window._enrRunning=true;
const csrf=document.cookie.match(/JSESSIONID="?([^";]+)/)[1];
const H={headers:{'csrf-token':csrf,'x-restli-protocol-version':'2.0.0'},credentials:'include'};
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
const D1='%28entityUrn%2CfullName%2Cheadline%2Cdegree%2Clocation%2Csummary%2CdefaultPosition%2CcontactInfo%2CpendingInvitation%2CflagshipProfileUrl%2Cpositions*%28companyName%2Ccurrent%2Cdescription%2CendedOn%2CstartedOn%2Ctitle%2Clocation%29%29';
const D2='%28entityUrn%2CmemberBadges%2CnumOfConnections%2CnumOfSharedConnections%2CinmailRestriction%2ClastMessagingActivity%2ClatestTouchPointActivity%2Ceducations*%28eduId%2CschoolName%2Cdegree%29%29';
const DH='%28sharedConnection%28sharedConnectionUrns*~fs_salesProfile%28fullName%29%29%2CsharedEducations*%28overlapInfo%2CentityUrn~fs_salesSchool%28name%29%29%2CsharedExperiences*%28overlapInfo%2CentityUrn~fs_salesCompany%28name%29%29%29';
const get=async u=>{const r=await fetch(u,H);if(r.status===429||r.status===999)throw new Error('RATE '+r.status);return r.ok?r.json():{_status:r.status}};
(async()=>{
  let q=JSON.parse(localStorage.enrq||'[]');const _d=Object.keys(JSON.parse(localStorage.enr2||'{}')).filter(k=>JSON.parse(localStorage.enr2)[k].err.length);q=_d.concat(q.filter(x=>!_d.includes(x)));localStorage.enrq=JSON.stringify(q);window._enrStop=false;
  while(q.length){
    const id=q[0];
    try{
      const P=`(profileId:${id},authType:undefined,authToken:undefined)`;
      const urn=encodeURIComponent(`urn:li:fs_salesProfile:(${id},undefined,undefined)`).replace(/\(/g,'%28').replace(/\)/g,'%29');
      const now=Date.now();
      const a=await get(`/sales-api/salesApiProfiles/${P}?decoration=${D1}`);
      await sleep(400+Math.random()*600);
      const b=await get(`/sales-api/salesApiProfiles/${P}?decoration=${D2}`);
      await sleep(400+Math.random()*600);
      const ins=await get(`/sales-api/salesApiInsightsV2?insightTypes=List(LEAD_POST,LEAD_COMMENT)&q=findByMember&profile=${urn}&timeRange=(start:${now-88*864e5},end:${now})&start=0&count=6`);
      await sleep(400+Math.random()*600);
      const h=await get(`/sales-api/salesApiProfileHighlights/${id}?decoration=${DH}`);
      const posts=(ins.elements||[]).map(e=>{const u=e.activityUnion||{};const k=Object.keys(u)[0];const x=u[k]||{};return {kind:k,at:new Date(e.createdAt).toISOString().slice(0,10),text:((x.commentary||{}).text||(x.text||{}).text||JSON.stringify(x).match(/"text":"([^"]{20,})/)?.[1]||'').slice(0,500),url:x.activityUrl||''}});
      const sc=h.sharedConnection||{};const scr=sc.sharedConnectionUrnsResolutionResults||{};
      const rec={id,name:a.fullName,headline:a.headline,degree:a.degree,location:a.location,summary:(a.summary||'').slice(0,900),
        positions:(a.positions||[]).slice(0,6).map(p=>({co:p.companyName,title:p.title,current:p.current,start:p.startedOn,end:p.endedOn,loc:p.location,desc:(p.description||'').slice(0,700)})),
        websites:((a.contactInfo||{}).websites||[]).map(w=>w.url),pendingInvite:a.pendingInvitation,linkedin:a.flagshipProfileUrl,
        badges:b.memberBadges,conns:b.numOfConnections,shared:b.numOfSharedConnections,inmailRestriction:b.inmailRestriction,
        lastMsg:b.lastMessagingActivity?new Date(b.lastMessagingActivity.lastMessageSentAt).toISOString().slice(0,10):null,
        touch:b.latestTouchPointActivity,edu:(b.educations||[]).map(e=>e.schoolName),
        mutuals:Object.values(scr).map(x=>x.fullName),
        sharedEdu:(h.sharedEducations||[]).map(x=>(x.entityUrnResolutionResult||{}).name),
        sharedExp:(h.sharedExperiences||[]).map(x=>(x.entityUrnResolutionResult||{}).name),
        posts,err:[a,b,ins,h].filter(x=>x._status).map(x=>x._status)};
      const all=JSON.parse(localStorage.enr2||'{}');all[id]=rec;localStorage.enr2=JSON.stringify(all);
      q.shift();localStorage.enrq=JSON.stringify(q);window._enrLast=rec.name;
    }catch(e){window._enrErr=String(e);break;}
    if(window._enrStop)break;
    await sleep(3000+Math.random()*4000);
  }
  window._enrRunning=false;
})();
return 'started';
})()
