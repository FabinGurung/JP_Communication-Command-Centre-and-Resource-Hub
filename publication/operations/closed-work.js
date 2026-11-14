"use strict";
/* Only source-validated, approved closure decisions can populate this view. */
const el=id=>document.getElementById(id);
const node=(tag,value,cls)=>{const n=document.createElement(tag);n.textContent=String(value??"");if(cls)n.className=cls;return n};
let archive;
const dateLabel=value=>{if(!value)return "Not recorded";const d=new Date(value+"T12:00:00+05:45");return Number.isNaN(+d)?String(value):new Intl.DateTimeFormat("en-GB",{timeZone:"Asia/Kathmandu",day:"numeric",month:"short",year:"numeric"}).format(d)};
function render(){
 if(!archive)return;
 const site=el("closed-project").value,decision=el("closed-decision").value;
 const list=archive.records.filter(x=>(!site||x.project_id===site)&&(!decision||x.decision===decision));
 const root=el("closed-records");root.replaceChildren();
 if(!list.length){
   root.append(node("p",archive.total===0?
      "No source-approved closures have been recorded yet. The older notifications and reported work are not automatically treated as completed or unnecessary.":
      "No approved closed items match this selection.","closure-empty"));
   return;
 }
 for(const r of list){
   const card=node("article","","closure-item");
   const heading=node("div","","closure-item-head");
   heading.append(node("strong",r.project_name+" · "+r.project_id),node("span",r.decision_label,"closure-pill"));
   card.append(heading,node("p",r.summary));
   const meta=node("p",r.kind+" · "+(r.category||"Work")+
     " · Recorded: "+dateLabel(r.source_date)+" · Closure approved: "+dateLabel(r.closed_on),"closure-meta");
   const link=node("a","Open source owner");
   link.href=r.kind==="Instruction"?
    "https://docs.google.com/spreadsheets/d/1ZPtTos8t9Cym_qnpiUhiyuTxndSc6sGzzv390ahAw4I/edit":
    "https://docs.google.com/spreadsheets/d/17YPRpaXIdHloH5-lzsjUpNvXLbsDfrIrlsn2jZ-7KKc/edit";
   card.append(meta,node("small","Stable record: "+r.id+" · Closure reviewer, reason and evidence remain in the original restricted register."),link);
   root.append(card);
 }
}
fetch("./closed-work.json",{cache:"no-store"})
.then(response=>{if(!response.ok)throw Error("Closed-work snapshot unavailable");return response.json()})
.then(data=>{
 if(data.kind!=="SOURCE_REVIEWED_CLOSED_WORK"||!Array.isArray(data.records)||data.total!==data.records.length)
   throw Error("Invalid archive projection");
 if(data.records.some(x=>!["COMPLETED","NOT_REQUIRED","CANCELLED","SUPERSEDED"].includes(x.decision)))
   throw Error("Unknown closure in archive");
 archive=data;
 el("closed-total").textContent=String(data.total);
 el("closed-completed").textContent=String(data.decisions.COMPLETED||0);
 el("closed-unneeded").textContent=String((data.decisions.NOT_REQUIRED||0)+(data.decisions.CANCELLED||0)+(data.decisions.SUPERSEDED||0));
 const byProject=new Map(data.records.map(r=>[r.project_id,r.project_name]));
 for(const [id,name] of [...byProject].sort((a,b)=>a[1].localeCompare(b[1])))
   el("closed-project").append(new Option(name+" · "+id,id));
 const requested=new URLSearchParams(location.search).get("project");
 if(byProject.has(requested))el("closed-project").value=requested;
 el("closed-readback").textContent="Last source readback: "+(data.readback_at_npt||"Not supplied")+
   ". Reviewed closure decisions only; no item is archived by age or due date.";
 el("closed-project").addEventListener("change",render);
 el("closed-decision").addEventListener("change",render);
 render();
}).catch(()=>{
 el("closed-readback").textContent="Verified closed-work snapshot unavailable. No inferred closure history is displayed.";
 el("closed-records").replaceChildren(node("p","The owning source register remains authoritative. Check the latest GitHub Actions publication.","closure-empty"));
});
