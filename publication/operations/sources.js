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
      ["Drive modified-time metadata", p.provider_modified_at_status || "Not available"]
    ];
    const dl = node("dl", "", "source-date-grid");
    for (const [label, value] of labels) dl.append(node("dt", label), node("dd", value || "Not published"));
    const identityText = node("p", "", "identity-note");
    identityText.textContent = "Current public projects: " + data.projects.length +
      ". Historical Git identity index: " + (identity.historical_git_index_count ?? "unknown") +
      ". Added public IDs since historical index: " +
      (identity.public_ids_added_since_historical_index?.join(", ") || "none") +
      ". Nonpublic and retired rows excluded.";
    byId("source-dates").replaceChildren(dl, identityText);
  })
  .catch(() => {byId("source-summary").textContent = "Source readback unavailable. Consult the publication workflow for the latest result.";});
