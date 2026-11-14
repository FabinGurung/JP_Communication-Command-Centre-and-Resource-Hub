"use strict";
/* Sources are displayed on an internal route; no raw provider records here. */
const byId = id => document.getElementById(id);
const node = (tag, text, className = "") => {
  const n = document.createElement(tag);
  n.textContent = text;
  if (className) n.className = className;
  return n;
};
fetch("./operations.json", {cache:"no-cache"})
  .then(r => {if (!r.ok) throw Error("Published projection unavailable"); return r.json();})
  .then(data => {
    if (!Array.isArray(data.projects) || !Array.isArray(data.progress) || !Array.isArray(data.notices))
      throw Error("Invalid public projection");
    const p = data.provenance || {}, times = p.source_dates || {}, identity = data.identity || {};
    byId("source-project-count").textContent = String(data.projects.length);
    byId("source-notice-count").textContent = data.notices.length + " reviewed notifications";
    byId("source-work-count").textContent = data.progress.length + " work reports";
    byId("source-summary").textContent =
      "Seven registered Google workbooks are read into this public projection. Latest publisher readback (NPT): " +
      (p.source_readback_at_npt || data.refreshed_at_npt || "Not supplied") +
      ". The published dates below describe source rows, not Google Drive workbook modifications.";
    const labels = [
      ["Projects / latest listed row date", times.projects?.latest_public_record_date],
      ["Reviewed notifications / message date", times.notifications?.latest_public_record_date],
      ["Reported work / latest row date", times.progress?.latest_public_record_date],
      ["Sheets double-read completed (NPT)", p.source_readback_at_npt || data.refreshed_at_npt],
      ["Drive modified-time metadata", "Not provided by current Sheets-only connection"]
    ];
    const dl = node("dl", "", "source-date-grid");
    for (const [label, value] of labels) dl.append(node("dt", label), node("dd", value || "Not published"));
    const identityText = node("p", "", "identity-note");
    identityText.textContent = "Current approved public projects: " + data.projects.length +
      ". The current Projects and Locations Google Sheet is authoritative. " +
      "Retired aliases and rows without publication permission are excluded. " +
      "Source row dates may predate the most recent website build.";
    byId("source-dates").replaceChildren(dl, identityText);
  })
  .catch(() => {byId("source-summary").textContent = "Source readback unavailable. Consult the publication workflow for the latest result.";});
