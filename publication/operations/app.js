"use strict";
/* Public read-only projection: never merge raw provider messages into this page. */
const byId = id => document.getElementById(id);
const make = (tag, content = "", className = "") => {
  const e = document.createElement(tag);
  e.textContent = content;
  if (className) e.className = className;
  return e;
};
const withChildren = (parent, ...children) => {
  parent.append(...children);
  return parent;
};
const safeList = (target, elements, empty) => {
  byId(target).replaceChildren(...(elements.length ? elements : [make("p", empty, "help")]));
};
let dataset = null;
let map = null;
let markerLayer = null;
const hasPin = p => Number.isFinite(p.lat) && Number.isFinite(p.lng);
const readable = value => String(value || "").replaceAll("_", " ").trim();
const projectName = id => (dataset.projects.find(p => p.id === id) || {}).name || id;
const selectedProject = () => byId("project-filter").value;
const selectedCompany = () => byId("company-filter").value;
const filteredProjects = () => dataset.projects.filter(p =>
  (!selectedProject() || p.id === selectedProject()) &&
  (!selectedCompany() || p.company_id === selectedCompany()));
const filterByProject = r => filteredProjects().some(p => p.id === r.project_id);
const filteredProgress = () => dataset.progress.filter(r =>
  filterByProject(r) && (!byId("report-date").value || r.date === byId("report-date").value));
const filteredNotices = () => dataset.notices.filter(filterByProject);

function chooseProject(id, focusMap = false) {
  byId("project-filter").value = id;
  render();
  const p = dataset.projects.find(project => project.id === id);
  if (focusMap && p && hasPin(p) && map) {
    map.setView([p.lat, p.lng], Math.max(map.getZoom(), 15));
    byId("map").scrollIntoView({behavior: "smooth", block: "start"});
  }
}

function drawMap(projects) {
  if (!window.L) {
    byId("map-fallback").hidden = false;
    return;
  }
  if (!map) {
    map = L.map("map-canvas", {scrollWheelZoom: false}).setView([28.21, 83.99], 12);
    L.tileLayer("https://tile.openstreetmap.org/{z}/{x}/{y}.png", {
      maxZoom: 19, attribution: "&copy; OpenStreetMap contributors"
    }).addTo(map);
    markerLayer = L.featureGroup().addTo(map);
  }
  markerLayer.clearLayers();
  for (const p of projects.filter(hasPin)) {
    const marker = L.marker([p.lat, p.lng], {title: p.name});
    const popup = make("div");
    withChildren(popup, make("strong", p.name), make("p", p.id));
    const select = make("button", "View project", "quiet");
    select.type = "button";
    select.addEventListener("click", () => chooseProject(p.id));
    popup.append(select);
    marker.bindPopup(popup);
    marker.on("click", () => updateContext(p.id));
    marker.addTo(markerLayer);
  }
  if (markerLayer.getLayers().length) {
    map.fitBounds(markerLayer.getBounds(), {padding: [32, 32], maxZoom: 15});
  }
  map.invalidateSize();
}

function updateProjectIndex(projects) {
  byId("project-count").textContent = String(projects.length);
  const nodes = projects.map(p => {
    const button = make("button", "", "project-entry");
    button.type = "button";
    button.setAttribute("aria-pressed", selectedProject() === p.id ? "true" : "false");
    if (selectedProject() === p.id) button.classList.add("active");
    withChildren(button, make("strong", p.name),
      make("span", [p.id, p.ward ? "Ward " + p.ward : "", hasPin(p) ? "Map pin" : "No public pin"].filter(Boolean).join(" · ")));
    button.addEventListener("click", () => chooseProject(p.id, true));
    return button;
  });
  safeList("project-list", nodes, "No public projects match these filters.");
}

function updateContext(overrideId) {
  const p = dataset.projects.find(x => x.id === (overrideId || selectedProject()));
  const root = byId("context-card");
  if (!p) {
    root.replaceChildren(make("h3", "All public projects"),
      make("p", "Choose a project or tap an approved map pin to see its site-level context."),
      make("p", "No private source messages, payments or unapproved coordinates are displayed."));
    return;
  }
  const reports = dataset.progress.filter(r => r.project_id === p.id);
  const notices = dataset.notices.filter(n => n.project_id === p.id);
  const detail = make("dl");
  const pairs = [
    ["Project ID", p.id],
    ["Executing organization", p.company || "Not public"],
    ["Location", p.ward ? "Ward " + p.ward : "Not published"],
    ["Map pin", hasPin(p) ? "Approved" : "Not published"],
    ["Reported work entries", String(reports.length)],
    ["Reviewed instructions", String(notices.length)],
    ["Latest report", reports.length ? reports[0].date : "No public report"]
  ];
  for (const [label, value] of pairs) withChildren(detail, make("dt", label), make("dd", value));
  root.replaceChildren(make("h3", p.name), make("p", p.status ? "Listed status: " + p.status : "No public status"),
    detail, make("p", "Listed status and reporting records do not certify completed work.", "help"));
}

function renderTrend(rows) {
  const tally = new Map();
  for (const r of rows) tally.set(r.date, (tally.get(r.date) || 0) + 1);
  const dates = [...tally.keys()].sort().reverse().slice(0, 7).reverse();
  const max = Math.max(1, ...dates.map(d => tally.get(d)));
  const items = dates.map(date => {
    const row = make("div", "", "trend-row");
    const track = make("div", "", "trend-track");
    const bar = make("div", "", "trend-fill");
    bar.style.width = (tally.get(date) / max * 100).toFixed(1) + "%";
    track.setAttribute("aria-label", tally.get(date) + " reports on " + date);
    track.append(bar);
    return withChildren(row, make("span", date.slice(5)), track, make("strong", String(tally.get(date))));
  });
  safeList("report-trend", items, "No public reports for this selection.");
}

function reportCard(r) {
  const wrapper = make("article", "", "card");
  const meta = make("p", [projectName(r.project_id), r.date].filter(Boolean).join(" · "), "card-meta");
  const tags = make("div", "", "card-tags");
  const verified = r.verification === "VERIFIED";
  withChildren(tags, make("span", readable(r.status) || "Not stated", "tag"),
    make("span", "Sheet verification: " + readable(r.verification || "UNVERIFIED"),
      "tag " + (verified ? "verified" : "pending")));
  return withChildren(wrapper, make("h3", r.work || "Work description not provided"), meta, tags,
    make("p", "Reported activity only · No engineer acceptance or certified quantity is implied."));
}

function noticeCard(n) {
  const wrapper = make("article", "", "card");
  const p = make("p", [projectName(n.project_id), n.category, n.date].filter(Boolean).join(" · "), "card-meta");
  withChildren(wrapper, make("h3", n.instruction || "Instruction not published"), p);
  if (n.due_date) wrapper.append(make("p", "Due: " + n.due_date));
  return wrapper;
}

function render() {
  if (!dataset) return;
  const projects = filteredProjects();
  const progress = filteredProgress();
  const notices = filteredNotices();
  byId("metric-projects").textContent = String(projects.length);
  byId("metric-pins").textContent = String(projects.filter(hasPin).length);
  byId("metric-progress").textContent = String(progress.length);
  byId("metric-notices").textContent = String(notices.length);
  updateProjectIndex(projects);
  drawMap(projects);
  updateContext();
  renderTrend(progress);
  safeList("progress-list", progress.map(reportCard), "No public work reports for this selection.");
  safeList("notice-list", notices.map(noticeCard), "No reviewed instructions for this selection.");
  byId("latest-date").textContent = "Latest report: " +
    (progress.length ? progress[0].date : "No published report");
}

function load(payload) {
  if (!payload || !Array.isArray(payload.projects) || !Array.isArray(payload.progress) ||
      !Array.isArray(payload.notices)) throw Error("Invalid Operations projection");
  dataset = payload;
  const companyLabels = new Map();
  for (const p of dataset.projects) if (p.company_id && p.company) companyLabels.set(p.company_id, p.company);
  for (const [id, name] of [...companyLabels].sort((a, b) => a[1].localeCompare(b[1])))
    byId("company-filter").append(new Option(name, id));
  for (const p of dataset.projects) byId("project-filter").append(new Option(p.name + " · " + p.id, p.id));
  const requested = new URLSearchParams(location.search).get("project");
  const p = dataset.projects.find(item => item.id === requested || item.site === requested);
  if (p) byId("project-filter").value = p.id;
  byId("receipt").textContent = payload.refreshed_at_npt || "Read time not supplied";
  const provenance = payload.provenance || {};
  byId("source-summary").textContent =
    "Five governed Google Sheets feed this read-only public snapshot. Last source read: " +
    (provenance.source_readback_at_npt || payload.refreshed_at_npt || "unknown") +
    ". Latest published work report: " + (provenance.latest_public_report_date || "none") +
    ". Slack is not collected directly by this publisher; Discord collection is on hold. No billing or engineering certification is inferred.";
  render();
}
for (const id of ["project-filter", "company-filter", "report-date"])
  byId(id).addEventListener("change", render);
byId("reset-filters").addEventListener("click", () => {
  byId("project-filter").value = "";
  byId("company-filter").value = "";
  byId("report-date").value = "";
  render();
});
fetch("./operations.json", {cache: "no-cache"})
  .then(response => {if (!response.ok) throw Error("Published projection unavailable");return response.json();})
  .then(load)
  .catch(() => {
    byId("receipt").textContent = "Snapshot unavailable";
    byId("project-list").textContent = "The source-backed public projection could not be loaded.";
    byId("progress-list").textContent = "Progress unavailable until the next successful source readback.";
    byId("notice-list").textContent = "Instructions unavailable until the next successful source readback.";
    byId("map-fallback").hidden = false;
  });
