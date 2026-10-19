(()=>{"use strict";
const root=document.getElementById("doc-status-rows"),label=document.getElementById("doc-status-count");
const project=document.getElementById("project"),search=document.getElementById("search");
let records=[];
function node(tag,content,cls){
 const e=document.createElement(tag);
 if(content!==undefined&&content!==null)e.textContent=String(content);
 if(cls)e.className=cls;
 return e;
}
function render(){
 const requested=new URLSearchParams(location.search).get("project")||"";
 const pid=project&&project.value?project.value:(project&&project.options.length<=1?requested:"");
 const q=(search?.value||"").trim().toLowerCase();
 const shown=records.filter(r=>(!pid||r.project_id===pid)&&(!q||[r.project_id,r.title,r.description,r.current_status].join(" ").toLowerCase().includes(q)));
 root.replaceChildren();
 label.textContent=shown.length+" / "+records.length+" project-level document records · not software tasks";
 if(!shown.length){root.append(node("p","No matching project document statuses. Absence does not mean engineer approval.","empty"));return;}
 for(const r of shown){
  const card=node("article",null,"doc-status-card");
  card.append(node("h3",r.title),node("p",r.description));
  card.append(node("b","Document issue/revision: unverified · "+r.dated_on_npt));
  const links=node("div",null,"links");
  const a=node("a","Review project source links ↗");
  a.href="../resources/?project="+encodeURIComponent(r.project_id);
  links.append(a);card.append(links);root.append(card);
 }
}
async function load(){
 try{
  const response=await fetch("../ops/data/project-document-review-public.v1.0.json",{cache:"no-store"});
  if(!response.ok)throw Error("Status projection not available");
  const d=await response.json();
  if(d.kind!=="PUBLIC_SAFE_PROJECT_DOCUMENT_PROGRESS"||d.software_release_blocker!==false||!Array.isArray(d.records)||d.records.length!==3)throw Error("Project status schema mismatch");
  if(d.records.some(x=>!/^P00[127]$/.test(x.project_id)||x.issuer_confirmation!==false||x.verification_state!=="OPEN_PROJECT_RECORD_NOT_SOFTWARE_BLOCKER"))throw Error("Project status source gate failed");
  records=d.records;render();
 }catch(e){
  label.textContent="Project review status unavailable";
  root.replaceChildren(node("p","Unable to load project review records. No approval is inferred.","empty"));
 }
}
project?.addEventListener("change",render);
search?.addEventListener("input",render);
load();
})();