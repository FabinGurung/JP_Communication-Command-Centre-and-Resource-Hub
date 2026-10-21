(()=>{"use strict";
const holder=document.getElementById("field-sources"),stamp=document.getElementById("field-freshness"),company=document.getElementById("field-company"),search=document.getElementById("field-search");
let records=[],blueprints=new Map(),links=new Map();
const el=(tag,text,cls)=>{const x=document.createElement(tag);if(text!==undefined)x.textContent=String(text);if(cls)x.className=cls;return x;};
function paint(){const needle=search.value.trim().toLowerCase(),matches=records.filter(r=>(!company.value||company.value===r.company)&&(!needle||[r.department,r.company,r.title,r.note,blueprints.get(r.source_key)?.visualization_options?.join(" ")].join(" ").toLowerCase().includes(needle)));
holder.replaceChildren();if(!matches.length){holder.append(el("p","No matching Field Resources sources.","a9-empty"));return;}
const grid=el("div",undefined,"a9-card-grid");for(const r of matches){const bp=blueprints.get(r.source_key),card=el("article",undefined,"a9-source-card");card.id="field-"+r.source_key.toLowerCase();
card.append(el("div",r.department+" · "+r.company+" · L3 dashboard","a9-type"));
const h=el("h3");const contact=["SRC-01","SRC-02"].includes(r.source_key);
if(contact){const a=el("a",r.title+" ↗","a9-panel-title-link");a.href="contacts/?source="+encodeURIComponent(r.source_key);a.setAttribute("aria-label","Open searchable "+r.title+" contact directory");h.append(a);}else{h.textContent=r.title;}
card.append(h,el("p",r.note),el("small",contact?"Dedicated searchable contact page · name, role, project and phone":"Original data remains in the Google Sheet","a9-type"));
if(contact){const detail=el("a","Open searchable people directory →","a9-view-directory");detail.href="contacts/?source="+encodeURIComponent(r.source_key);card.append(detail);}
const original=links.get(r.source_key);if(original){const a=el("a","Open original Google Sheet ↗","a9-source-link");a.href=original.url;a.target="_blank";a.rel="noopener noreferrer";a.referrerPolicy="no-referrer";card.append(a);}
if(bp){const details=el("details",undefined,"a9-blueprint");details.append(el("summary","View available visualization designs"));const ul=el("ul");bp.visualization_options.forEach(x=>ul.append(el("li",x)));details.append(ul);card.append(details);}
grid.append(card);}holder.append(grid);}
async function start(){try{const paths=["../../ops/data/a9-field-source-catalog-public.v1.0.json","../../ops/control/a9-field-visualization-plan.v1.0.json","../../ops/data/a9-field-source-links-public.v1.0.json"];const a=await Promise.all(paths.map(x=>fetch(x,{cache:"no-store"})));if(a.some(r=>!r.ok))throw Error("source metadata unavailable");
const [meta,plan,sources]=await Promise.all(a.map(r=>r.json()));
if(meta.sheets_count!==10||meta.sources?.length!==10||meta.public_source_file_ids_included!==false||meta.published_rows!==0)throw Error("invalid registry");
if(plan.individual_sheet_count!==10||plan.dashboards?.length!==10||plan.record_level_data_included!==false)throw Error("invalid blueprint");
if(sources.registry_id!=="A9_FIELD_SOURCE_LINKS_PUBLIC_20261021"||sources.source_count!==10||sources.google_sheet_urls?.length!==10||sources.source_records_copied!==0)throw Error("invalid links");
records=meta.sources;blueprints=new Map(plan.dashboards.map(x=>[x.source_key,x]));links=new Map(sources.google_sheet_urls.map(x=>[x.source_key,x]));
if(records.some(x=>!blueprints.has(x.source_key)||!links.has(x.source_key))||links.size!==10)throw Error("missing stable references");
stamp.textContent="10 original Sheets · 2 dedicated searchable contact views · restricted data only in original Sheets or explicitly approved public directory snapshots";paint();
}catch(e){stamp.textContent="Source catalog temporarily unavailable";holder.replaceChildren(el("p","Could not load the controlled source directory.","a9-empty"));}}
company.addEventListener("change",paint);search.addEventListener("input",paint);start();
})();