(()=>{"use strict";
const holder=document.getElementById("field-sources"),stamp=document.getElementById("field-freshness"),company=document.getElementById("field-company"),search=document.getElementById("field-search");
let records=[],links=new Map();
const el=(tag,text,cls)=>{const x=document.createElement(tag);if(text!==undefined)x.textContent=String(text);if(cls)x.className=cls;return x;};
function paint(){const q=search.value.trim().toLowerCase(),matches=records.filter(r=>(!company.value||company.value===r.company)&&(!q||[r.department,r.company,r.title,r.note].join(" ").toLowerCase().includes(q)));
holder.replaceChildren();if(!matches.length){holder.append(el("p","No matching source Sheets.","a9-empty"));return;}
const grid=el("div",undefined,"a9-card-grid");for(const r of matches){const card=el("article",undefined,"a9-source-card");card.id="field-"+r.source_key.toLowerCase();card.append(el("div",r.department+" · "+r.company,"a9-type"));const h=el("h3"),contact=["SRC-01","SRC-02"].includes(r.source_key);
if(contact){const a=el("a",r.title+" ↗","a9-panel-title-link");a.href="contacts/?source="+encodeURIComponent(r.source_key);h.append(a);}else h.textContent=r.title;
card.append(h,el("p",r.note),el("small","Original data remains in the Google Sheet","a9-type"));
if(contact){const a=el("a","Open searchable people directory →","a9-view-directory");a.href="contacts/?source="+encodeURIComponent(r.source_key);card.append(a);}
const source=links.get(r.source_key),a=el("a","Open Google Sheet ↗","a9-source-link");a.href=source.url;a.target="_blank";a.rel="noopener noreferrer";a.referrerPolicy="no-referrer";card.append(a);grid.append(card);}holder.append(grid);}
async function start(){try{const paths=["../../ops/data/a9-field-source-catalog-public.v1.0.json","../../ops/data/a9-field-source-links-public.v1.0.json"];const responses=await Promise.all(paths.map(x=>fetch(x,{cache:"no-store"})));if(responses.some(r=>!r.ok))throw Error();const [meta,sources]=await Promise.all(responses.map(r=>r.json()));
if(meta.sheets_count!==meta.sources?.length||meta.published_rows!==0||sources.source_count!==sources.google_sheet_urls?.length||sources.source_records_copied!==0)throw Error();
records=meta.sources.filter(r=>r.active!==false);links=new Map(sources.google_sheet_urls.map(x=>[x.source_key,x]));
if(records.some(r=>r.source_key==="SRC-04"||!links.has(r.source_key))||[...links.values()].some(r=>!/^https:\/\/docs\.google\.com\/spreadsheets\/d\/[\w-]+\/edit(?:#gid=\d+)?$/.test(r.url)))throw Error();
stamp.textContent=records.length+" active Sheet tools · Company Project Site Issues is in Notification Center · source permissions remain unchanged";paint();
}catch{stamp.textContent="Source directory unavailable";holder.replaceChildren(el("p","Could not load the source directory.","a9-empty"));}}
company.addEventListener("change",paint);search.addEventListener("input",paint);start();})();
