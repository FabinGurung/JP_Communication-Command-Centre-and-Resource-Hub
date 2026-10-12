/* JP AEC Request 01: shared, presentation-only six-section shell.
   No data fetching, checklist mutations, provider ingestion or Drive writes. */
(() => {
  "use strict";
  const script = document.currentScript;
  const root = new URL("../../", script.src);
  const sectionRoutes = [
    ["map", "🗺️ Map", "map.html"],
    ["checklist", "☑️ Daily Checklist", "site-operations.html"],
    ["progress", "📊 Progress Report", "site-operations/history.html"],
    ["resources", "📐 Resources", "resources/"],
    ["developer", "🛠️ Developer Workspace", "workspace/"],
    ["guide", "📘 How-To", "guide/"]
  ];
  const rootPath = root.pathname;
  const relPath = decodeURI(location.pathname.startsWith(rootPath)
    ? location.pathname.slice(rootPath.length) : location.pathname).replace(/\/+$/, "");
  const section = relPath === "map.html" ? "map"
    : relPath === "site-operations.html" || relPath.startsWith("site-operations/") && !relPath.startsWith("site-operations/history") ? "checklist"
    : relPath.startsWith("site-operations/history") ? "progress"
    : relPath.startsWith("resources") ? "resources"
    : relPath.startsWith("workspace") || relPath.startsWith("controls") || relPath.startsWith("pending") ? "developer"
    : relPath.startsWith("guide") ? "guide" : "overview";
  const escapeHTML = value => String(value).replace(/[&<>"']/g, ch =>
    ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[ch]));
  const home = new URL("index.html", root).href;
  const canonical = new Set(["index.html", ...sectionRoutes.map(x => x[2].replace(/\/$/, "/index.html"))]);
  const route = href => {
    try {
      const u = new URL(href, location.href);
      if (u.origin !== root.origin || !u.pathname.startsWith(rootPath)) return null;
      const p = u.pathname.slice(rootPath.length);
      if (canonical.has(p) || canonical.has(p.endsWith("/") ? p + "index.html" : p)) return null;
      return u;
    } catch { return null; }
  };
  const oldNav = document.querySelector("nav:not(.depth-nav)");
  const contextLinks = [];
  if (oldNav) {
    const visited = new Set();
    oldNav.querySelectorAll("a[href]").forEach(anchor => {
      const u = route(anchor.getAttribute("href"));
      if (!u) return;
      const k = u.pathname + u.search;
      if (visited.has(k)) return;
      visited.add(k);
      // Existing subpage links remain available, but not as duplicated main destinations.
      if (contextLinks.length < 9) {
        const site = new URLSearchParams(location.search).get("project");
        if (site && !u.search && u.pathname.includes("/site-operations/")) u.searchParams.set("project",site);
        contextLinks.push({url:u.href,label:anchor.textContent.trim().replace(/\s+/g," ")});
      }
    });
  }
  const header = document.createElement("jp-site-header");
  header.setAttribute("data-section", section);
  const shadow = header.attachShadow({mode:"open"});
  const stylesheet = document.createElement("link");
  stylesheet.rel="stylesheet";
  stylesheet.href=new URL("assets/css/site-shell.css?v=1",root).href;
  shadow.appendChild(stylesheet);
  const primary = sectionRoutes.map(([key,label,href]) => {
    const active = key === section;
    return '<a class="jp-link'+(active?' active':'')+'" '+(active?'aria-current="page" ':'')+
      'href="'+new URL(href,root).href+'">'+escapeHTML(label)+'</a>';
  }).join("");
  const related = contextLinks.length
    ? '<details class="jp-related"><summary>More tools ▾</summary><div>'+
      contextLinks.map(x=>'<a href="'+escapeHTML(x.url)+'">'+escapeHTML(x.label)+'</a>').join("")+
      '</div></details>' : "";
  const shell = document.createElement("div");
  shell.className="jp-frame";
  shell.innerHTML = '<div class="jp-top"><a class="jp-brand" href="'+home+
    '"><span aria-hidden="true">🏗️</span><span>JP AEC <small>Operations Hub</small></span></a>'+
    '<nav aria-label="JP AEC six primary sections">'+primary+'</nav>'+related+'</div>';
  shadow.appendChild(shell);
  const isHomepage = relPath === "" || relPath === "index.html";
  if (isHomepage && document.querySelector("header.top")) {
    document.querySelector("header.top").replaceWith(header);
  } else if (oldNav) {
    oldNav.before(header);
    oldNav.hidden = true;
    oldNav.setAttribute("aria-hidden","true");
    oldNav.style.setProperty("display","none","important");
  } else {
    document.body.prepend(header);
  }
  document.body.dataset.jpSite="1";
  document.body.dataset.jpSection=section;
  // Preserve printable guide, its 1/3/7/15 depth links and its entire guide DOM.
  const pageStyle = document.createElement("link");
  pageStyle.rel="stylesheet";
  pageStyle.href=new URL("assets/css/site-shell.css?v=1",root).href;
  document.head.appendChild(pageStyle);
})();