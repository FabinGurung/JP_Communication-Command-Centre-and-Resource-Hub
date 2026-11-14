"use strict";
const byId = id => document.getElementById(id);
const show = (id, value) => {byId(id).textContent = String(value ?? "Not published");};
const niceDate = v => {
  if (!v) return "No recorded date";
  const d = new Date(v);
  if (Number.isNaN(d.getTime())) return String(v);
  return new Intl.DateTimeFormat("en-GB",{timeZone:"Asia/Kathmandu",day:"numeric",month:"short",year:"numeric"}).format(d);
};
const niceTime = v => {
  if (!v) return "Unavailable";
  const d = new Date(v);
  if (Number.isNaN(d.getTime())) return String(v);
  return new Intl.DateTimeFormat("en-GB",{timeZone:"Asia/Kathmandu",day:"numeric",month:"short",year:"numeric",hour:"2-digit",minute:"2-digit"}).format(d)+" NPT";
};
fetch("./extraction-status.json",{cache:"no-store"})
  .then(r=>{if(!r.ok)throw Error("Source checkpoint unavailable");return r.json()})
  .then(d=>{
    if(d.schema_version!=="1.0.0"||!d.source_counts||!d.public_counts||!d.source_dates)
      throw Error("Invalid extraction checkpoint");
    show("batch-state","Source batch reconciled");
    show("batch-summary","Last source readback: "+niceTime(d.readback_at_npt)+
      ". This batch checks the existing registers. It does not collect new messages or certify site work.");
    show("intake-count",d.source_counts.message_sources);
    show("evidence-count",d.source_counts.message_sources);
    show("review-notices",d.public_counts.reviewed_notices);
    show("review-unverified",d.public_counts.unverified_work_reports);
    show("review-projects",d.public_counts.projects);
    show("publish-sheets",d.source_counts.workbooks);
    show("publish-projects",d.public_counts.projects);
    show("publish-date",niceTime(d.readback_at_npt));
    show("last-project-date",niceDate(d.source_dates.projects));
    show("last-message-date",niceDate(d.source_dates.notifications));
    show("last-work-date",niceDate(d.source_dates.progress));
    show("handoff-summary","Stopping point: "+d.source_counts.workbooks+
      " original Google workbooks read twice; "+d.public_counts.reviewed_notices+
      " source-approved notifications and "+d.public_counts.unverified_work_reports+
      " unverified work reports reconciled. No new Slack, Discord or Telegram messages were imported. "+
      "Next source batch: capture a bounded project channel or Drive message folder, "+
      "verify original evidence IDs/hashes privately, obtain human approval, then append to the owning original Sheets.");
  })
  .catch(()=>{
    byId("batch-state").textContent="Source readback unavailable";
    byId("batch-state").classList.add("hold");
    show("batch-summary","The extraction checkpoint was not published. Existing source Sheets remain authoritative; inspect the publisher Actions before relying on totals.");
  });
