const $=id=>document.getElementById(id);
let data=null;
const esc=s=>String(s??"").replaceAll("&","&amp;").replaceAll("<","&lt;").replaceAll(">","&gt;").replaceAll('"',"&quot;").replaceAll("'","&#039;");
const slug=s=>String(s||"").toLowerCase().replace(/[^a-z0-9]+/g,"-").replace(/(^-|-$)/g,"");
function option(select,value){const o=document.createElement("option");o.value=value;o.textContent=value;select.append(o);}
function searchable(r){return [r.title,r.why,r.how,r.status,r.audience,r.type,r.source].join(" ").toLowerCase();}
function render(){
  const q=$("search").value.trim().toLowerCase(),category=$("category").value,status=$("status").value,audience=$("audience").value;
  let shown=0;
  for(const g of data.groups){
    const group=document.getElementById("group-"+g.id);let count=0;
    group.querySelectorAll(".resource").forEach(card=>{
      const r=data.resources.find(x=>x.id===card.dataset.id);
      const ok=(!q||searchable(r).includes(q))&&(!category||r.group===category)&&(!status||r.status===status)&&(!audience||r.audience.includes(audience));
      card.hidden=!ok;if(ok){count++;shown++;}
    });
    group.hidden=count===0;
  }
  $("result-count").textContent=shown+" resource"+(shown===1?"":"s")+" shown";
}
function card(r){
  const cls=r.status.toLowerCase();
  return '<article class="resource" data-id="'+esc(r.id)+'"><div class="resource-meta"><span>'+esc(r.type)+'</span><span class="badge '+esc(cls)+'">'+esc(r.status)+'</span></div>'+
  '<h3><a href="'+esc(r.url)+'">'+esc(r.title)+'</a></h3><p>'+esc(r.why)+'</p><p class="how"><strong>How to use: </strong>'+esc(r.how)+'</p>'+
  '<p class="metadata">'+esc(r.audience)+'</p><p class="state-note">Source: '+esc(r.source)+'</p><a class="open" href="'+esc(r.url)+'">Open '+esc(r.title)+' →</a></article>';
}
async function load(){
  try{
    const r=await fetch("./links.json?v="+Date.now(),{cache:"no-store"});if(!r.ok)throw new Error("Resource directory unavailable.");
    data=await r.json();$("total-count").textContent=data.resources.length;$("updated").textContent=data.updated+" · "+data.timezone;
    for(const g of data.groups){option($("category"),g.id);}
    $("category").querySelectorAll("option").forEach(o=>{const g=data.groups.find(x=>x.id===o.value);if(g)o.textContent=g.label;});
    [...new Set(data.resources.map(r=>r.status))].sort().forEach(v=>option($("status"),v));
    const audiences=new Set();data.resources.forEach(r=>r.audience.split("/").map(x=>x.trim()).filter(Boolean).forEach(x=>audiences.add(x)));[...audiences].sort().forEach(v=>option($("audience"),v));
    $("directory-nav").innerHTML=data.groups.map(g=>'<a href="#group-'+esc(g.id)+'">'+esc(g.label)+'</a>').join("");
    $("directory").innerHTML=data.groups.map(g=>'<section class="group" id="group-'+esc(g.id)+'"><div class="group-head"><h2>'+esc(g.label)+'</h2><p>'+esc(g.description)+'</p></div><div class="cards">'+data.resources.filter(r=>r.group===g.id).map(card).join("")+'</div></section>').join("");
    ["search","category","status","audience"].forEach(id=>$(id).addEventListener(id==="search"?"input":"change",render));render();
  }catch(e){$("load-status").textContent=e.message;}
}
$("copy-link").addEventListener("click",async()=>{try{await navigator.clipboard.writeText(location.href);$("share-status").textContent="Workspace link copied.";}catch{$("share-status").textContent="Copy the address from your browser.";}});load();
