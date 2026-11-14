"use strict";
/* Human-readable public provenance. Technical source state stays in the
 * versioned JSON rather than leaking protocol enums into phone layouts. */
const byId = id => document.getElementById(id);
const node = (tag, text, className = "") => {
  const n = document.createElement(tag);
  n.textContent = text;
  if (className) n.className = className;
  return n;
};
const prettyDate = value => {
  if (!value) return "No published date";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return String(value);
  return new Intl.DateTimeFormat("en-GB", {
    timeZone:"Asia/Kathmandu",year:"numeric",month:"short",day:"numeric"
  }).format(date);
};
const prettyStamp = value => {
  if (!value) return "Unavailable";
  const dt = new Date(value);
  if (Number.isNaN(dt.getTime())) return String(value);
  return new Intl.DateTimeFormat("en-GB", {
    timeZone:"Asia/Kathmandu",day:"numeric",month:"short",year:"numeric",
    hour:"2-digit",minute:"2-digit"
  }).format(dt) + " NPT";
};
fetch("./operations.json", {cache:"no-cache"})
  .then(r => {if (!r.ok) throw Error("Published projection unavailable"); return r.json();})
  .then(data => {
    if (!Array.isArray(data.projects)||!Array.isArray(data.progress)||!Array.isArray(data.notices))
      throw Error("Invalid source projection");
    const p = data.provenance || {}, dates = p.source_dates || {};
    byId("source-project-count").textContent = String(data.projects.length);
    byId("source-notice-count").textContent = data.notices.length + " reviewed notifications";
    byId("source-work-count").textContent = data.progress.length + " reported work entries";
    byId("source-summary").textContent =
      "This page explains the approved sources behind the map. The website last checked its seven registered Google workbooks on " +
      prettyStamp(p.source_readback_at_npt || data.refreshed_at_npt) +
      ". That check does not mean that construction work happened on the same day.";
    const details = [
      ["Project register: last recorded change", prettyDate(dates.projects?.latest_public_record_date)],
      ["Notifications: latest linked source date", prettyDate(dates.notifications?.latest_public_record_date)],
      ["Field work: latest reported date", prettyDate(dates.progress?.latest_public_record_date)],
      ["Website data readback", prettyStamp(p.source_readback_at_npt || data.refreshed_at_npt)]
    ];
    const dl = node("dl", "", "source-date-grid");
    for (const [label, value] of details)
      dl.append(node("dt",label), node("dd",value));
    byId("source-dates").replaceChildren(dl,
      node("p", String(data.projects.length) +
        " approved public projects. Private and retired records are excluded. " +
        "Original Sheet modification times are not part of this public source readback.",
        "identity-note"));
  })
  .catch(() => {
    byId("source-summary").textContent =
      "The source readback is currently unavailable. Check the GitHub Actions publisher; the original Google Sheets remain authoritative.";
    byId("source-dates").replaceChildren(node("p","Source dates unavailable.","help"));
  });
