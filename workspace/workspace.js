const $=id=>document.getElementById(id);
let directoryData=null;

const esc=s=>String(s??"")
  .replaceAll("&","&amp;")
  .replaceAll("<","&lt;")
  .replaceAll(">","&gt;")
  .replaceAll('"',"&quot;")
  .replaceAll("'","&#039;");

const slug=s=>String(s||"")
  .toLowerCase()
  .replace(/[^a-z0-9]+/g,"-")
  .replace(/(^-|-$)/g,"");

function option(select,value){
  const o=document.createElement("option");
  o.value=value;
  o.textContent=value;
  select.append(o);
}

function searchable(r){
  return [r.title,r.why,r.how,r.status,r.audience,r.type,r.source]
    .join(" ")
    .toLowerCase();
}

function renderDirectory(){
  if(!directoryData) return;
  const q=$("search").value.trim().toLowerCase();
  const category=$("category").value;
  const status=$("status").value;
  const audience=$("audience").value;
  let shown=0;

  for(const g of directoryData.groups){
    const group=document.getElementById("group-"+g.id);
    if(!group) continue;
    let count=0;

    group.querySelectorAll(".resource").forEach(card=>{
      const r=directoryData.resources.find(x=>x.id===card.dataset.id);
      const ok=r &&
        (!q||searchable(r).includes(q)) &&
        (!category||r.group===category) &&
        (!status||r.status===status) &&
        (!audience||r.audience.includes(audience));
      card.hidden=!ok;
      if(ok){count++;shown++;}
    });

    group.hidden=count===0;
  }

  $("result-count").textContent=shown+" resource"+(shown===1?"":"s")+" shown";
}

function directoryCard(r){
  const cls=r.status.toLowerCase();
  return '<article class="resource" data-id="'+esc(r.id)+'">'+
    '<div class="resource-meta"><span>'+esc(r.type)+'</span><span class="badge '+esc(cls)+'">'+esc(r.status)+'</span></div>'+
    '<h3><a href="'+esc(r.url)+'">'+esc(r.title)+'</a></h3>'+
    '<p>'+esc(r.why)+'</p>'+
    '<p class="how"><strong>How to use: </strong>'+esc(r.how)+'</p>'+
    '<p class="metadata">'+esc(r.audience)+'</p>'+
    '<p class="state-note">Source: '+esc(r.source)+'</p>'+
    '<a class="open" href="'+esc(r.url)+'">Open '+esc(r.title)+' →</a>'+
  '</article>';
}

async function loadDirectory(){
  try{
    const r=await fetch("./links.json?v="+Date.now(),{cache:"no-store"});
    if(!r.ok) throw new Error("Resource directory unavailable.");
    directoryData=await r.json();

    $("total-count").textContent=directoryData.resources.length;
    $("updated").textContent=directoryData.updated+" · "+directoryData.timezone;

    for(const g of directoryData.groups) option($("category"),g.id);
    $("category").querySelectorAll("option").forEach(o=>{
      const g=directoryData.groups.find(x=>x.id===o.value);
      if(g) o.textContent=g.label;
    });

    [...new Set(directoryData.resources.map(r=>r.status))]
      .sort()
      .forEach(v=>option($("status"),v));

    const audiences=new Set();
    directoryData.resources.forEach(r=>
      r.audience
        .split("/")
        .map(x=>x.trim())
        .filter(Boolean)
        .forEach(x=>audiences.add(x))
    );
    [...audiences].sort().forEach(v=>option($("audience"),v));

    $("directory-nav").innerHTML=directoryData.groups
      .map(g=>'<a href="#group-'+esc(g.id)+'">'+esc(g.label)+'</a>')
      .join("");

    $("directory").innerHTML=directoryData.groups
      .map(g=>
        '<section class="group" id="group-'+esc(g.id)+'">'+
          '<div class="group-head"><h2>'+esc(g.label)+'</h2><p>'+esc(g.description)+'</p></div>'+
          '<div class="cards">'+directoryData.resources.filter(r=>r.group===g.id).map(directoryCard).join("")+'</div>'+
        '</section>'
      )
      .join("");

    ["search","category","status","audience"].forEach(id=>
      $(id).addEventListener(id==="search"?"input":"change",renderDirectory)
    );
    renderDirectory();
  }catch(e){
    $("load-status").textContent=e.message;
  }
}

function parseCsv(text){
  const rows=[];
  let row=[],field="",quoted=false;

  for(let i=0;i<text.length;i++){
    const ch=text[i];

    if(quoted){
      if(ch==='"' && text[i+1]==='"'){
        field+='"';
        i++;
      }else if(ch==='"'){
        quoted=false;
      }else{
        field+=ch;
      }
      continue;
    }

    if(ch==='"'){
      quoted=true;
    }else if(ch===","){
      row.push(field);
      field="";
    }else if(ch==="\n"){
      row.push(field);
      rows.push(row);
      row=[];
      field="";
    }else if(ch!=="\r"){
      field+=ch;
    }
  }

  if(field.length||row.length){
    row.push(field);
    rows.push(row);
  }

  if(!rows.length) return [];
  const headers=rows[0].map(h=>h.replace(/^\uFEFF/,"").trim());

  return rows.slice(1)
    .filter(r=>r.some(v=>String(v).trim()!==""))
    .map(r=>Object.fromEntries(headers.map((h,i)=>[h,r[i]??""])));
}

function deriveOpsSignal(ops){
  const work=Array.isArray(ops.todays_work)?ops.todays_work:[];
  const executions=work.map(w=>w.execution_status).filter(Boolean);

  if(ops.overall_readiness==="HOLD") return "HOLD";
  if(ops.overall_readiness==="NOT_READY") return "NOT_READY";
  if(executions.includes("BLOCKED")) return "BLOCKED";
  if(ops.conflict_state==="UNRESOLVED") return "NEEDS_INPUT";
  if(executions.includes("NEEDS_INPUT")) return "NEEDS_INPUT";
  if(ops.overall_readiness==="READY_WITH_CONDITION") return "CONDITION";
  if(ops.overall_readiness==="READY") return "READY";
  if(executions.includes("ONGOING")) return "ONGOING";
  if(executions.includes("PARTIAL")) return "PARTIAL";
  if(executions.includes("PLAN")||executions.includes("NOT_STARTED")) return "PLAN";
  return ops.overall_readiness||executions[0]||"UNSET";
}

function formatSignal(value){
  return String(value||"UNSET").replaceAll("_"," ");
}

function signalClass(value){
  return slug(value||"unset");
}

function projectCard(item){
  const p=item.opsProject;
  const ops=p.daily_ops||{};
  const master=item.master||{};
  const work=Array.isArray(ops.todays_work)?ops.todays_work:[];
  const primary=work[0]||{};
  const signal=deriveOpsSignal(ops);
  const extra=work.length>1?" · +"+(work.length-1)+" more":"";
  const masterStatus=master.status||"UNKNOWN";
  const display=master.display_name||p.display_name||p.project_id;
  const company=master.company_project_code||p.company_project_code||"";
  const normalized=master.project_id||p.map_project_id||"";
  const blocker=primary.blocker||
    (Array.isArray(ops.blockers)&&ops.blockers[0]&&ops.blockers[0].blocker)||
    "No blocker statement is recorded in the current Daily Ops item.";
  const activity=primary.activity||"No current work item recorded.";
  const reconciled=ops.last_reconciled_at||"Unknown";
  const projection=ops.projection_status?.website||"UNKNOWN";
  const href="../site-operations/project.html?project="+encodeURIComponent(p.project_id);

  return '<article class="project-card">'+
    '<div class="project-card-head">'+
      '<div><h3>'+esc(display)+'</h3><div class="ids">'+esc(p.project_id)+' · '+esc(normalized)+(company?' · '+esc(company):'')+'</div></div>'+
      '<span class="signal '+esc(signalClass(signal))+'">'+esc(formatSignal(signal))+'</span>'+
    '</div>'+
    '<div class="project-status-row">'+
      '<span class="signal '+esc(signalClass(masterStatus))+'">Master: '+esc(masterStatus)+'</span>'+
      '<span class="signal '+esc(signalClass(projection))+'">Web: '+esc(projection)+'</span>'+
    '</div>'+
    '<div class="activity"><strong>Current:</strong> '+esc(activity)+esc(extra)+'</div>'+
    '<div class="blocker"><strong>Follow-up:</strong> '+esc(blocker)+'</div>'+
    '<div class="meta-line">Ops date: '+esc(ops.date||"Unknown")+' · Last reconciled: '+esc(reconciled)+'</div>'+
    '<a class="open-project" href="'+esc(href)+'">Open project operations →</a>'+
  '</article>';
}

async function loadLiveProjects(){
  const status=$("live-project-status");
  const grid=$("live-project-grid");

  try{
    const [csvResponse,opsResponse]=await Promise.all([
      fetch("../projects.csv?v="+Date.now(),{cache:"no-store"}),
      fetch("../ops/data/current-works.json?v="+Date.now(),{cache:"no-store"})
    ]);

    if(!csvResponse.ok) throw new Error("projects.csv could not be loaded.");
    if(!opsResponse.ok) throw new Error("current-works.json could not be loaded.");

    const [csvText,opsState]=await Promise.all([
      csvResponse.text(),
      opsResponse.json()
    ]);

    const masterRows=parseCsv(csvText);
    const byMapId=new Map(masterRows.map(r=>[r.project_id,r]));
    const opsProjects=Array.isArray(opsState.projects)?opsState.projects:[];

    const joined=opsProjects.map(opsProject=>({
      opsProject,
      master:byMapId.get(opsProject.map_project_id)||null
    }));

    const unresolvedJoins=joined.filter(x=>!x.master);
    if(unresolvedJoins.length){
      throw new Error("Project master join failed for: "+unresolvedJoins.map(x=>x.opsProject.project_id).join(", "));
    }

    const signals=joined.map(x=>deriveOpsSignal(x.opsProject.daily_ops||{}));
    const needsInput=signals.filter(x=>x==="NEEDS_INPUT").length;
    const holdBlocked=signals.filter(x=>["HOLD","BLOCKED","NOT_READY"].includes(x)).length;
    const latestDate=joined
      .map(x=>x.opsProject.daily_ops?.date)
      .filter(Boolean)
      .sort()
      .at(-1)||"—";

    const statValues=[joined.length,needsInput,holdBlocked,latestDate];
    $("live-project-summary").querySelectorAll("strong").forEach((el,i)=>{
      el.textContent=statValues[i]??"—";
    });

    const priority={HOLD:0,BLOCKED:0,NOT_READY:0,NEEDS_INPUT:1,CONDITION:2,ONGOING:3,PARTIAL:3,PLAN:4,UNSET:5,READY:6};
    joined.sort((a,b)=>{
      const sa=deriveOpsSignal(a.opsProject.daily_ops||{});
      const sb=deriveOpsSignal(b.opsProject.daily_ops||{});
      return (priority[sa]??5)-(priority[sb]??5) ||
        String(a.opsProject.project_id).localeCompare(String(b.opsProject.project_id));
    });

    grid.innerHTML=joined.map(projectCard).join("");
    status.textContent=
      "Live join PASS: "+joined.length+" Daily Ops project"+
      (joined.length===1?"":"s")+
      " resolved to projects.csv. Status cards are derived display only; canonical files remain unchanged.";
  }catch(e){
    grid.innerHTML="";
    status.textContent=
      "Live project/status layer unavailable: "+e.message+
      " Use the static Active project pages directory below; it remains the fallback navigation layer.";
  }
}

$("copy-link").addEventListener("click",async()=>{
  try{
    await navigator.clipboard.writeText(location.href);
    $("share-status").textContent="Workspace link copied.";
  }catch{
    $("share-status").textContent="Copy the address from your browser.";
  }
});

loadDirectory();
loadLiveProjects();
