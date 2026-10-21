/* JP Request 02: seven destinations, scoped contextual tools, preserved project selection.
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
    ["memory","🧠 Memory Poster","controls/memory-wall.html"],
    ["guide","📘 How-To","guide/"]
  ];
  const url=new URL(location.href);
  const path=decodeURI(url.pathname.startsWith(rootPath)?url.pathname.slice(rootPath.length):url.pathname).replace(/\/+$/,"");
  const section=path==="map.html"?"map":
    path==="site-operations/history.html"?"progress":
    path==="site-operations.html"||path.startsWith("site-operations/")?"checklist":
    path==="resources"||path.startsWith("resources/")?"resources":
    path==="controls/memory-wall.html"?"memory":
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
    memory:[["🧭 Developer Workspace","workspace/"],["📚 Editing hierarchy","docs/website/A9_SITE_TREE_AND_EDIT_LEVELS.v1.md"]],
    developer:[["🗼 Control Towers","controls/"],["📌 Software Backlog","workspace/backlog/"],["🧭 Storage Rules","controls/storage.html"],["🗃️ Archive Policy","controls/archive-formats.html"]],
    guide:[["📄 Quick Start","guide/"],["📖 3-page walkthrough","guide/3-pages/"],["🗂️ 7-page routine","guide/7-pages/"],["📚 15-page reference","guide/15-pages/"]]
  };
  // Department-level navigation must remain visible; replace only the old page-level navigation.
  const oldNav=document.querySelector("nav:not(.depth-nav):not(.a9-subnav), .shell.nav");
  const host=document.createElement("jp-site-header");
  host.setAttribute("data-section",section);
  const shadow=host.attachShadow({mode:"open"});
  const styles=document.createElement("link");
  styles.rel="stylesheet";
  styles.href=local("assets/css/site-shell.css?v=botanical-1");
  shadow.appendChild(styles);
  const shell=document.createElement("div");
  shell.className="jp-frame";
  const mainLinks=pages.map(([key,label,href])=>
    '<a class="jp-link'+(key===section?' active':'')+'" data-jp-route="'+escapeHTML(href)+'"'+
    (key===section?' aria-current="page"':'')+' href="'+local(href)+'">'+escapeHTML(label)+'</a>').join("");
  shell.innerHTML='<a class="jp-skip" href="#jp-main">Skip to content</a><div class="jp-top" data-menu-open="false"><a class="jp-brand" href="'+base.href+
    '"><span aria-hidden="true">🏗️</span><span>JP <small>Operations Hub</small></span></a>'+
    '<button class="jp-menu-toggle" type="button" aria-expanded="false" aria-controls="jp-primary-nav">Menu ☰</button><nav class="jp-nav" id="jp-primary-nav" aria-label="JP primary destinations">'+mainLinks+'</nav>'+
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
  if(isHome)document.querySelector("header.top")?.remove();
  if(oldNav && oldNav.isConnected){
    oldNav.dataset.jpLegacyPrimary="1";
    oldNav.hidden=true;
    oldNav.setAttribute("aria-hidden","true");
    oldNav.style.setProperty("display","none","important");
  }
  // The header belongs to the viewport shell, never a page's narrow content column.
  document.body.prepend(host);
  document.body.dataset.jpSite="1";
  document.body.dataset.jpSection=section;
  const garden=document.createElement("div");
  garden.className="jp-garden";
  garden.setAttribute("aria-hidden","true");
  document.body.appendChild(garden);
  const content=document.querySelector("main")||document.querySelector(".app-shell,.shell,.wrap");
  if(content){
    if(!content.id)content.id="jp-main";
    content.tabIndex=-1;
    shadow.querySelector(".jp-skip").addEventListener("click",e=>{
      e.preventDefault(); content.focus(); content.scrollIntoView({block:"start"});
    });
  }
  const menuToggle=shadow.querySelector(".jp-menu-toggle");
  const top=shadow.querySelector(".jp-top");
  function closeMenu(restoreFocus=false){
    top.dataset.menuOpen="false";
    menuToggle.setAttribute("aria-expanded","false");
    if(restoreFocus)menuToggle.focus();
  }
  menuToggle.addEventListener("click",()=>{
    const open=top.dataset.menuOpen!=="true";
    top.dataset.menuOpen=String(open);
    menuToggle.setAttribute("aria-expanded",String(open));
  });
  shadow.addEventListener("keydown",e=>{
    if(e.key==="Escape"){
      const related=shadow.querySelector(".jp-related[open]");
      if(related){related.open=false;related.querySelector("summary").focus();}
      else closeMenu(true);
    }
  });
  document.addEventListener("click",e=>{
    if(!e.composedPath().includes(host)){
      closeMenu();
      const related=shadow.querySelector(".jp-related");
      if(related)related.open=false;
    }
  });
  // Reflow the map when the mobile menu or header changes height.
  if(section==="map"&&typeof ResizeObserver!=="undefined"){
    new ResizeObserver(()=>window.dispatchEvent(new Event("resize"))).observe(host);
  }
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