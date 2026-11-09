"use strict";
const byId = id => document.getElementById(id);
const tabs = ["map", "notifications", "progress"];
let data;
let map;
let markerLayer;
const node = (tag, label) => {
  const element = document.createElement(tag);
  element.textContent = label;
  return element;
};
const card = (title, caption, detail) => {
  const element = node("article", "");
  element.className = "card";
  element.append(node("h3", title), node("p", caption));
  if (detail) element.append(node("p", detail));
  return element;
};
function displayList(id, cards) {
  byId(id).replaceChildren(...(cards.length ? cards : [node("p", "No public records for this selection.")]));
}
function render() {
  const active = tabs.includes(location.hash.slice(1)) ? location.hash.slice(1) : "map";
  tabs.forEach(id => {
    byId(id).hidden = id !== active;
    const link = document.querySelector('nav a[href="#' + id + '"]');
    if (id === active) link.setAttribute("aria-current", "page");
    else link.removeAttribute("aria-current");
  });
  if (!data) return;
  const id = byId("project-filter").value;
  const matches = r => !id || (r.project_id || r.id) === id;
  const names = Object.fromEntries(data.projects.map(p => [p.id, p.name]));
  const projects = data.projects.filter(matches);
  if (active === "map" && window.L) {
    if (!map) {
      map = L.map("map-canvas").setView([28.21, 83.99], 12);
      L.tileLayer("https://tile.openstreetmap.org/{z}/{x}/{y}.png", {
        maxZoom: 19, attribution: "&copy; OpenStreetMap contributors"
      }).addTo(map);
      markerLayer = L.featureGroup().addTo(map);
    }
    map.invalidateSize();
    markerLayer.clearLayers();
    for (const p of projects.filter(p => Number.isFinite(p.lat) && Number.isFinite(p.lng))) {
      L.marker([p.lat, p.lng], {title: p.name}).bindPopup(node("strong", p.name)).addTo(markerLayer);
    }
    if (markerLayer.getLayers().length) map.fitBounds(markerLayer.getBounds(), {padding: [28, 28], maxZoom: 16});
  }
  displayList("project-list", projects.map(p => {
    const element = card(p.name, [p.id, p.ward ? "Ward " + p.ward : "", p.status].filter(Boolean).join(" · "),
      Number.isFinite(p.lat) ? "" : "No public map pin.");
    if (map && Number.isFinite(p.lat)) {
      const button = node("button", "Locate on map");
      button.type = "button";
      button.className = "map-select";
      button.onclick = () => map.setView([p.lat, p.lng], 16);
      element.append(button);
    }
    return element;
  }));
  displayList("notice-list", data.notices.filter(matches).map(n =>
    card(n.instruction, [names[n.project_id], n.category, n.date].join(" · "), n.due_date ? "Due " + n.due_date : "")));
  displayList("progress-list", data.progress.filter(matches).map(p =>
    card(p.work, [names[p.project_id], p.date, p.status].filter(Boolean).join(" · "), "Source verification: " + p.verification)));
}
window.addEventListener("hashchange", render);
byId("project-filter").addEventListener("change", render);
render();
fetch("./operations.json", {cache: "no-cache"}).then(r => {
  if (!r.ok) throw Error();
  return r.json();
}).then(payload => {
  data = payload;
  const select = byId("project-filter");
  for (const p of data.projects) select.append(new Option(p.name + " · " + p.id, p.id));
  const requested = new URLSearchParams(location.search).get("project");
  const project = data.projects.find(p => p.id === requested || p.site === requested);
  if (project) select.value = project.id;
  byId("receipt").textContent = "Sheets readback · " + data.refreshed_at_npt;
  render();
}).catch(() => {byId("receipt").textContent = "The published Operations snapshot is unavailable.";});
