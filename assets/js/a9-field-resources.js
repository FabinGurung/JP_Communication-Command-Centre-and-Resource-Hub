(()=>{"use strict";
const holder=document.getElementById("field-sources"),stamp=document.getElementById("field-freshness"),company=document.getElementById("field-company"),search=document.getElementById("field-search");let records=[],blueprints=new Map();
const el=(tag,text,className)=>{const x=document.createElement(tag);if(text!==undefined)x.textContent=String(text);if(className)x.className=className;return x;};
function paint(){const needle=search.value.trim().toLowerCase(),matches=records.filter(r=>(!company.value||company.value===r.company)&&(!needle||[r.department,r.company,r.title,r.note,blueprints.get(r.source_key)?.visualization_options?.join(" ")].join(" ").toLowerCase().includes(needle)));holder.replaceChildren();
if(!matches.length){holder.append(el("p","No matching Sheet dashboards. Private data has not been queried.","a9-empty"));return;}
const grid=el("div",undefined,"a9-card-grid");matches.forEach(r=>{const bp=blueprints.get(r.source_key),card=el("article",undefined,"a9-source-card");card.id="field-"+r.source_key.toLowerCase();
card.append(el("div",r.department+" · "+r.company+" · L3 dashboard","a9-type"),el("h3",r.title),el("p",r.note));
card.append(el("small","Restricted source · no individual data published","a9-type"));
if(bp){const details=el("details",undefined,"a9-blueprint");details.append(el("summary","View available visualization designs (not live data)"));
const list=el("ul");bp.visualization_options.forEach(v=>list.append(el("li",v)));details.append(list);
details.append(el("p","Existing Sheet tabs/fact views: "+bp.source_tab_groups.join(" · "),"a9-muted"));
details.append(el("p","Status: design specified; record-level dashboard requires authenticated source access and explicit projection review.","a9-muted"));card.append(details);}
grid.append(card);});holder.append(grid);}
async function start(){try{const [a,b]=await Promise.all([fetch("../../ops/data/a9-field-source-catalog-public.v1.0.json",{cache:"no-store"}),fetch("../../ops/control/a9-field-visualization-plan.v1.0.json",{cache:"no-store"})]);
if(!a.ok||!b.ok)throw Error("source registry unavailable");const data=await a.json(),plan=await b.json();
if(data.kind!=="PUBLIC_SAFE_SOURCE_CATEGORY_INDEX"||data.sheets_count!==10||data.sources?.length!==10||data.public_source_file_ids_included!==false||data.published_rows!==0)throw Error("unsafe catalog");
if(plan.plan_id!=="A9_FIELDS_ALL_TEN_SHEET_WEB_VIEW_CATALOG_20261020"||plan.individual_sheet_count!==10||plan.dashboards?.length!==10||plan.record_level_data_included!==false||plan.private_source_urls_included!==false)throw Error("unapproved source blueprint");
records=data.sources;blueprints=new Map(plan.dashboards.map(x=>[x.source_key,x]));if(blueprints.size!==10||records.some(x=>!blueprints.has(x.source_key)))throw Error("source/dashboard identity mismatch");
stamp.textContent="Ten authoritative Sheets · "+data.reviewed_on_npt+" · 10 planned L3 dashboards · 0 private rows copied";paint();
}catch{stamp.textContent="Metadata visualization plan unavailable — no source records were inferred";holder.replaceChildren(el("p","Safe field resource metadata could not be loaded.","a9-empty"));}}
company.addEventListener("change",paint);search.addEventListener("input",paint);start();
})();