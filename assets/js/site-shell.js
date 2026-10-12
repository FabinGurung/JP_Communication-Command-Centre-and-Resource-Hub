/* JP AEC Request 02: six destinations, scoped contextual tools, preserved project selection.
   Presentation-only. No provider/Drive reads, writes, local checklist updates or progress mutations. */
(() => {
  "use strict";
  const script=document.currentScript;
  const root=new URL("../../",script.src);
  const rootPath=root.pathname;
  const base=new URL("index.html",root);
  const pages=[
    ["map","🗺️ Map","map.html"],
    ["checklist","☑️ Daily Checklist","site-operations.html"],
    ["progress","📊 Progress Report","site-operations/history.html"],
    ["resources","📐 Resources","resources/"],
    ["developer","🛠️ Developer Workspace","workspace/"],
    ["guide","📘 How-To","guide/"]
  ];
  const url=new URL(location.href);
  const path=decodeURI(url.pathname.startsWith(rootPath)?url.pathname.slice(rootPath.length):url.pathname).replace(/\/+$/,"");
  const section=path==="map.html"?"map":
    path==="site-operations/history.html"?"progress":
    path==="site-operations.html"||path.startsWith("site-operations/")?"checklist":
    path==="resources"||path.startsWith("resources/")?"resources":
    path==="workspace"||path.startsWith("workspace/")||path==="controls"||path.startsWith("controls/")?"developer":
    path==="guide"||path.startsWith("guide/")?"guide":"overview";
  const escapeHTML=x=>String(x).replace(/[&<>"']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
  const local=href=>new URL(href,root).href;
  const supportsProject=href=>[
    "site-operations.html","site-operations/history.html","site-operations/coordination.html",
    "site-operations/questions.html","site-operations/schedule.html","site-operations/project.html","resources/"
  ].includes(href);
  function selectedProject(){
    const choice=document.getElementById("project");
    const ready=choice instanceof HTMLSelectElement&&choice.options.length>1;
    const fromSelect=ready?choice.value:"";
    // Clearing a loaded project filter means All projects; do not revive a stale URL FK.
    const fromQuery=ready?"":url.searchParams.get("project")||"";
    const fromPopup=(()=>{const a=document.querySelector('.leaflet-popup-content a[href*="project="]');try{
      return a?new URL(a.href,location.href).searchParams.get("project"):"";
    }catch{return "";}})();
    const pid=fromSelect||fromQuery||fromPopup||"";
    return /^P[0-9]{3,6}$/.test(pid)?pid:"";
  }
  const choices={
    overview:[],
    map:[["🏗️ Site Coordination","site-operations/coordination.html"],["🗓️ Work & Holds","site-operations/schedule.html"]],
    checklist:[["🏗️ Site Coordination","site-operations/coordination.html"],["🗓️ Work & Holds","site-operations/schedule.html"],["📝 Engineer Questions","site-operations/questions.html"]],
    progress:[["🏗️ Site Coordination","site-operations/coordination.html"],["🗓️ Work & Holds","site-operations/schedule.html"]],
    resources:[["🏗️ Site Coordination","site-operations/coordination.html"]],
    developer:[["🗼 Control Towers","controls/"],["📌 Software Backlog","workspace/backlog/"],["🧭 Storage Rules","controls/storage.html"],["🗃️ Archive Policy","controls/archive-formats.html"]],
    guide:[["📄 Quick Start","guide/"],["📖 3-page walkthrough","guide/3-pages/"],["🗂️ 7-page routine","guide/7-pages/"],["📚 15-page reference","guide/15-pages/"]]
  };
  const oldNav=document.querySelector("nav:not(.depth-nav)");
  const host=document.createElement("jp-site-header");
  host.setAttribute("data-section",section);
  const shadow=host.attachShadow({mode:"open"});
  const styles=document.createElement("link");
  styles.rel="stylesheet";
  styles.href=local("assets/css/site-shell.css?v=2");
  shadow.appendChild(styles);
  const shell=document.createElement("div");
  shell.className="jp-frame";
  const mainLinks=pages.map(([key,label,href])=>
    '<a class="jp-link'+(key===section?' active':'')+'" data-jp-route="'+escapeHTML(href)+'"'+
    (key===section?' aria-current="page"':'')+' href="'+local(href)+'">'+escapeHTML(label)+'</a>').join("");
  shell.innerHTML='<div class="jp-top"><a class="jp-brand" href="'+base.href+
    '"><span aria-hidden="true">🏗️</span><span>JP AEC <small>Operations Hub</small></span></a>'+
    '<nav aria-label="JP AEC six primary sections">'+mainLinks+'</nav>'+
    '<div class="jp-more-slot"></div></div>';
  shadow.appendChild(shell);
  const more=shell.querySelector(".jp-more-slot");
  function routeURL(target,pid){
    const link=new URL(target,root);
    if(pid&&supportsProject(target))link.searchParams.set("project",pid);
    return link.href;
  }
  let lastMenuProject=null;
  function syncRoutes(rebuildMenu=true){
    const pid=selectedProject();
    shell.querySelectorAll("a[data-jp-route]").forEach(a=>{
      a.href=routeURL(a.getAttribute("data-jp-route"),pid);
    });
    if(!rebuildMenu||lastMenuProject===pid)return;
    lastMenuProject=pid;
    const options=[...choices[section]];
    if(pid&&["map","checklist","progress","resources"].includes(section))
      options.push(["🗂️ Project Brief","site-operations/project.html"]);
    if(!options.length){more.replaceChildren();return;}
    const state=more.querySelector("details")?.open||false;
    const details=document.createElement("details");
    details.className="jp-related";
    details.open=state;
    const summary=document.createElement("summary");
    summary.textContent="More tools ▾";
    const menu=document.createElement("div");
    for(const [label,href]of options){
      if(path===href.replace(/\/+$/,"")||path===href+"index.html")continue;
      const link=document.createElement("a");
      link.textContent=label;
      link.href=routeURL(href,pid);
      link.setAttribute("data-jp-route",href);
      menu.appendChild(link);
    }
    if(!menu.childElementCount){more.replaceChildren();return;}
    details.append(summary,menu);
    more.replaceChildren(details);
  }
  const isHome=path===""||path==="index.html";
  if(isHome&&document.querySelector("header.top")){
    document.querySelector("header.top").replaceWith(host);
  }else if(oldNav){
    oldNav.before(host);
    oldNav.dataset.jpLegacyPrimary="1";
    oldNav.hidden=true;
    oldNav.setAttribute("aria-hidden","true");
    oldNav.style.setProperty("display","none","important");
  }else{
    document.body.prepend(host);
  }
  document.body.dataset.jpSite="1";
  document.body.dataset.jpSection=section;
  const pageStyles=document.createElement("link");
  pageStyles.rel="stylesheet";
  pageStyles.href=local("assets/css/site-shell.css?v=2");
  document.head.appendChild(pageStyles);
  syncRoutes();
  const projectChoice=document.getElementById("project");
  if(projectChoice){
    const observer=new MutationObserver(()=>syncRoutes());
    observer.observe(projectChoice,{childList:true,subtree:true});
  }
  document.addEventListener("change",e=>{
    if(e.target?.id==="project")syncRoutes();
  },true);
  // Refresh before mouse, touch and keyboard navigation, including deep links
  // when project options were loaded asynchronously after this script.
  shadow.addEventListener("pointerdown",()=>syncRoutes(false),true);
  shadow.addEventListener("focusin",()=>syncRoutes(false),true);
  shadow.addEventListener("click",e=>{
    if(e.target?.closest("a"))syncRoutes(false);
  },true);
})();