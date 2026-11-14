"use strict";
/* Source-reviewed site updates: public projections only, no provider scraping. */
const get = id => document.getElementById(id);
const el = (tag, content = "", cls = "") => {
  const n = document.createElement(tag);
  if (content != null) n.textContent = String(content);
  if (cls) n.className = cls;
  return n;
};
const dateLabel = value => {
  if (!value) return "Not recorded";
  const d = new Date(String(value).slice(0, 10) + "T12:00:00+05:45");
  if (Number.isNaN(+d)) return String(value);
  return new Intl.DateTimeFormat("en-GB", {timeZone:"Asia/Kathmandu",day:"numeric",month:"short",year:"numeric"}).format(d);
};
const set = (id, value) => { get(id).textContent = value; };
let details, publicData;
function line(label, value) {
  const item = el("div", "", "updates-stat");
  item.append(el("strong", value), el("span", label));
  return item;
}
function advice(text, type) {
  return el("p", text, "updates-advice" + (type ? " " + type : ""));
}
function recordCard(label, description, date, status, href) {
  const card = el("article", "", "updates-record");
  const meta = el("div", "", "updates-record-meta");
  meta.append(el("span", label), el("time", dateLabel(date)));
  card.append(meta, el("p", description));
  const bottom = el("div", "", "updates-record-bottom");
  if (status) bottom.append(el("span", status));
  if (href) {
    const a = el("a", "Open source-linked site");
    a.href = href;
    bottom.append(a);
  }
  card.append(bottom);
  return card;
}
function render() {
  if (!details || !publicData) return;
  const id = get("updates-project").value;
  const site = details.site_summaries.find(s => s.project_id === id);
  const all = details.summary;
  const stats = get("updates-stats");
  const meaning = get("updates-meaning");
  const sites = get("updates-sites");
  const records = get("updates-records");
  stats.replaceChildren();
  meaning.replaceChildren();
  sites.replaceChildren();
  records.replaceChildren();
  const notices = (publicData.notices || []).filter(n => !id || n.project_id === id);
  const reports = (publicData.progress || []).filter(r => !id || r.project_id === id);
  if (!site) {
    set("updates-headline", "Published information from " + all.public_site_count + " approved sites.");
    stats.append(line("Reviewed instructions", all.reviewed_notice_count),
                 line("Recorded work reports", all.published_work_report_count),
                 line("Unverified work reports", all.unverified_work_report_count));
    const cats = Object.entries(all.notice_categories || {}).filter(([k,v])=>v>0).map(([k,v])=>k + ": " + v).join(" · ");
    meaning.append(advice(all.registered_message_source_count + " original message source record(s) underpin the reviewed notification register. Different instructions are not necessarily separate chat messages."),
                   advice(cats ? "Reviewed instruction categories: " + cats + ". These are topics, not confirmed shortages or completed tasks." : "No reviewed instruction categories published."),
                   advice(all.unverified_work_report_count + " work report(s) lack verified completion. These are historical reports, not confirmed construction progress.","caution"),
                   advice("Latest reviewed message: " + dateLabel(all.latest_notice_date) +
                     ". Latest reported work: " + dateLabel(all.latest_work_date) + ". No newer public site record is established by this snapshot."));
    const affected = details.site_summaries.filter(s => s.reviewed_notice_count || s.published_report_count).slice(0,8);
    if (!affected.length) sites.append(advice("No source-approved site activity is published. This does not establish that no work occurred."));
    for (const s of affected) sites.append(siteRow(s));
    if (details.site_summaries.length > affected.length)
      sites.append(el("p", "Other public sites remain accessible through the map; absence of a record is not proof of inactivity.", "help"));
  } else {
    set("updates-headline", site.name + " · " + site.project_id);
    stats.append(line("Reviewed instructions", site.reviewed_notice_count),
                 line("Recorded work reports", site.published_report_count),
                 line("Unverified work reports", site.unverified_report_count));
    meaning.append(advice(site.notice_meaning),
                   advice(site.work_meaning, site.unverified_report_count ? "caution" : ""),
                   advice("Latest notice: " + dateLabel(site.last_notice_date) +
                       " · Latest work report: " + dateLabel(site.last_report_date)));
    const actions = el("div", "", "updates-actions");
    const mapLink = el("a", "View site on map");
    mapLink.href = "./?project=" + encodeURIComponent(site.project_id) + "#map";
    const noticesLink = el("a", "Site notifications");
    noticesLink.href = "./?project=" + encodeURIComponent(site.project_id) + "#notifications";
    actions.append(mapLink, noticesLink);
    sites.append(actions);
  }
  const maxNotices = id ? notices.length : Math.min(notices.length, 5);
  for (const notice of notices.slice(0, maxNotices)) {
    const p = publicData.projects.find(p => p.id === notice.project_id);
    const label = (p ? p.name + " · " : "") + (notice.category || "Instruction");
    records.append(recordCard(label, notice.instruction, notice.date, "Closure not verified",
      "./?project=" + encodeURIComponent(notice.project_id) + "#notifications"));
  }
  for (const report of reports.slice(0, id ? 12 : 3)) {
    const p = publicData.projects.find(p => p.id === report.project_id);
    records.append(recordCard((p ? p.name + " · " : "") + "Work report",
      report.work || "Work description not available",
      report.date, report.verification === "VERIFIED" ? "Recorded as verified" : "Verification not confirmed",
      "./?project=" + encodeURIComponent(report.project_id) + "#map"));
  }
  if (maxNotices < notices.length) records.append(el("p", "Showing the first " + maxNotices +
    " reviewed notices. Choose a site or open Notifications to see the full approved register.", "help"));
  if (!notices.length && !reports.length) records.append(advice("No published records for this selection. It does not establish that site work or instructions are absent."));
}
function siteRow(s) {
  const a = el("a", "", "updates-site");
  a.href = "./extraction.html?project=" + encodeURIComponent(s.project_id);
  a.append(el("strong", s.name));
  const n = s.reviewed_notice_count + " reviewed instructions · " +
            s.published_report_count + " work reports";
  a.append(el("span", n));
  const latest = [s.last_notice_date, s.last_report_date].filter(Boolean).sort().pop();
  a.append(el("small", "Latest recorded: " + dateLabel(latest)));
  a.addEventListener("click", event => {
    event.preventDefault();
    get("updates-project").value = s.project_id;
    history.replaceState(null, "", "./extraction.html?project=" + encodeURIComponent(s.project_id));
    render();
    get("updates-summary-title").scrollIntoView({behavior:"smooth",block:"start"});
  });
  return a;
}
Promise.all([
  fetch("./operations.json", {cache:"no-cache"}).then(r=>{if(!r.ok)throw Error("Approved record projection unavailable");return r.json();}),
  fetch("./site-updates.json", {cache:"no-cache"}).then(r=>{if(!r.ok)throw Error("Derived site updates unavailable");return r.json();})
]).then(([ops, update]) => {
  if (!Array.isArray(ops.projects) || !Array.isArray(ops.notices) ||
      !Array.isArray(ops.progress) || !Array.isArray(update.site_summaries) ||
      update.kind !== "DERIVED_PUBLIC_SITE_INTERPRETATION" ||
      update.summary.public_site_count !== ops.projects.length ||
      update.summary.reviewed_notice_count !== ops.notices.length ||
      update.summary.published_work_report_count !== ops.progress.length)
    throw Error("Update/source projection mismatch");
  publicData = ops; details = update;
  for (const project of [...ops.projects].sort((a,b)=>a.name.localeCompare(b.name)))
    get("updates-project").append(new Option(project.name + " · " + project.id, project.id));
  const requested = new URLSearchParams(location.search).get("project");
  if (update.site_summaries.some(s=>s.project_id === requested))
    get("updates-project").value = requested;
  set("updates-readback", "Source readback: " + (update.readback_at_npt || "Not supplied") +
    ". Source dates are shown separately; publication does not certify site completion.");
  get("updates-project").addEventListener("change", () => {
    const id = get("updates-project").value;
    history.replaceState(null, "", id ? "./extraction.html?project=" + encodeURIComponent(id) : "./extraction.html");
    render();
  });
  render();
}).catch(e=>{
  set("updates-readback","Updates could not be verified against their source projection. Please use the original Google Sheets or check the latest publishing run.");
  set("updates-headline","Verified site updates temporarily unavailable.");
  get("updates-sites").replaceChildren(advice("The published summary failed its cross-check; no totals are shown as current."));
  get("updates-records").replaceChildren();
});
