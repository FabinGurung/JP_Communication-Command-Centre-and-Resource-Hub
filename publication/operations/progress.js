"use strict";
/* Daily Progress lives on its own internal route; data remain Sheets-owned. */
const byId = id => document.getElementById(id);
const el = (tag, content = "", cls = "") => {
  const node = document.createElement(tag);
  node.textContent = content;
  if (cls) node.className = cls;
  return node;
};
const statusLabel = value => String(value || "Not stated").replaceAll("_", " ");
const nameOf = (data, id) => data.projects.find(p => p.id === id)?.name || id;
function renderTrend(rows) {
  const counts = new Map();
  for (const r of rows) counts.set(r.date, (counts.get(r.date) || 0) + 1);
  const dates = [...counts.keys()].sort().reverse().slice(0, 7).reverse();
  const max = Math.max(1, ...dates.map(d => counts.get(d)));
  const cards = dates.map(date => {
    const row = el("div", "", "trend-row");
    const track = el("div", "", "trend-track");
    const bar = el("div", "", "trend-fill");
    bar.style.width = (counts.get(date) / max * 100).toFixed(1) + "%";
    track.setAttribute("aria-label", counts.get(date) + " reports on " + date);
    track.append(bar);
    row.append(el("span", date.slice(5)), track, el("strong", String(counts.get(date))));
    return row;
  });
  byId("report-trend").replaceChildren(...(cards.length ? cards : [el("p", "No public reports for this selection.", "help")]));
}
function render(data) {
  const project = byId("progress-project").value;
  const date = byId("progress-date").value;
  const rows = data.progress.filter(x => (!project || x.project_id === project) && (!date || x.date === date));
  byId("report-count").textContent = String(rows.length);
  byId("latest-date").textContent = "Latest recorded: " + (rows.length ? rows[0].date : "None");
  renderTrend(rows);
  const cards = rows.map(r => {
    const card = el("article", "", "card");
    const top = el("div", "", "card-tags");
    top.append(el("span", statusLabel(r.status), "tag"));
    const verified = r.verification === "VERIFIED";
    top.append(el("span", "Sheet verification: " + statusLabel(r.verification || "UNVERIFIED"),
      "tag " + (verified ? "verified" : "pending")));
    const link = el("a", "Open site notifications", "quiet-link");
    link.href = "./?project=" + encodeURIComponent(r.project_id) + "#notifications";
    card.append(el("h3", r.work || "Work description not published"),
      el("p", nameOf(data, r.project_id) + " · " + r.date, "card-meta"), top,
      el("p", "Reported activity only. No certified quantity, payment or engineering acceptance is implied."), link);
    return card;
  });
  byId("progress-list").replaceChildren(...(cards.length ? cards : [el("p", "No approved work reports match these filters.", "help")]));
}
fetch("./operations.json", {cache:"no-cache"})
  .then(r => {if (!r.ok) throw Error("Public projection unavailable"); return r.json();})
  .then(data => {
    if (!Array.isArray(data.projects) || !Array.isArray(data.progress)) throw Error("Invalid projection");
    for (const project of data.projects) byId("progress-project").append(new Option(project.name + " · " + project.id, project.id));
    const requested = new URLSearchParams(location.search).get("project");
    if (data.projects.some(p => p.id === requested || p.site === requested)) {
      const match = data.projects.find(p => p.id === requested || p.site === requested);
      byId("progress-project").value = match.id;
    }
    byId("progress-project").addEventListener("change", () => render(data));
    byId("progress-date").addEventListener("change", () => render(data));
    byId("progress-reset").addEventListener("click", () => {
      byId("progress-project").value = "";
      byId("progress-date").value = "";
      render(data);
    });
    render(data);
  })
  .catch(() => {
    byId("report-count").textContent = "—";
    byId("progress-list").textContent = "Public reports unavailable; check source publication and try again.";
  });
