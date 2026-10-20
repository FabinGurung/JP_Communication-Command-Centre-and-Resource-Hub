(()=>{"use strict";
const holder=document.getElementById("a9-manual-progress"),count=document.getElementById("a9-manual-progress-count");
const project=document.getElementById("project"),search=document.getElementById("search");let rows=[];
const el=(tag,text,className)=>{const n=document.createElement(tag);if(text!==undefined)n.textContent=String(text);if(className)n.className=className;return n;};
function paint(){if(!holder)return;const pid=project?.value||"",q=(search?.value||"").trim().toLowerCase();
const filtered=rows.filter(x=>(!pid||x.project_id===pid)&&(!q||[x.project_id,x.source_provider,x.verbatim_text].join(" ").toLowerCase().includes(q)));
holder.replaceChildren();count.textContent=filtered.length+" reviewed, verbatim public message(s) · no automatic derivation";
if(!filtered.length){holder.append(el("p","No new source messages are publicly admitted. Originals remain in their authorized Slack/Discord or private Drive records; automatic interpretation is off.","a9-empty"));return;}
for(const x of filtered){const card=el("article",undefined,"a9-source-card");card.append(el("div",x.date_npt+" · "+x.project_id+" · "+x.source_provider+" · reviewed verbatim","a9-type"));
const body=el("p",x.verbatim_text,"a9-verbatim-message");card.append(body);
card.append(el("small","Source receipt: "+x.source_receipt_key+" · recorded wording, not verified completion","a9-type"));holder.append(card);}}
async function load(){try{const r=await fetch("../ops/data/a9-reviewed-progress-public.v1.0.json",{cache:"no-store"});if(!r.ok)throw Error("no approved feed");
const s=await r.json();if(s.kind!=="MANUALLY_REVIEWED_PROGRESS_PUBLICATION_QUEUE"||s.render_mode!=="VERBATIM_FIRST_NO_AUTO_DERIVATION"||s.derived_data_requires_explicit_new_user_prompt!==true||s.automatic_polling!==false||s.historical_records_preserved!==37||!Array.isArray(s.records)||s.records.length!==s.published_new_record_count)throw Error("invalid review contract");
if(s.records.some(x=>!x.record_id||!/^P[0-9]{3,6}$/.test(x.project_id)||!x.date_npt||!x.source_provider||!x.source_receipt_key||typeof x.verbatim_text!=="string"||!x.privacy_review_id||x.public_verbatim_approved!==true))throw Error("unapproved raw message");rows=s.records;paint();
}catch{count.textContent="Public verbatim feed unavailable";holder.replaceChildren(el("p","Verbatim public projection unavailable; historical records remain unchanged.","a9-empty"));}}
project?.addEventListener("change",paint);search?.addEventListener("input",paint);load();
})();