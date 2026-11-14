"use strict";
/* Read-only public checkpoint. Browser never collects or mutates provider records. */
const byId = id => document.getElementById(id);
const value = (id, text) => { const n=byId(id); if(n) n.textContent=String(text ?? "Not supplied"); };
const node = (tag, text) => {const n=document.createElement(tag); n.textContent=String(text||"");return n};
fetch("./extraction-status.json", {cache:"no-cache"})
 .then(r=>{if(!r.ok) throw Error("Public checkpoint unavailable"); return r.json()})
 .then(data=>{
   if(data.schema_version!=="1.0.0"||!Array.isArray(data.source_books)||!data.lanes||!data.counts)
     throw Error("Invalid extraction checkpoint");
   value("intake-count",data.source_books.length);
   value("public-site-count",data.public_project_count);
   value("reviewed-notice-count",data.reviewed_notice_count);
   value("lane-message-count",data.counts.messages);
   value("lane-notices-count",data.reviewed_notice_count);
   value("lane-work-count",data.published_work_count);
   value("lane-message-date",data.source_dates.notifications?.latest_public_record_date||"No source date");
   value("lane-notices-date",data.source_dates.notifications?.latest_public_record_date||"No source date");
   value("lane-work-date",data.source_dates.progress?.latest_public_record_date||"No source date");
   value("extract-readback","Readback: "+(data.readback_at_npt||"Unknown")+
     " · Source pointers: "+(data.validation.directory_verified?"Verified":"Unverified")+
     " · Linked-record warnings: "+data.validation.foreign_key_warnings+
     ". Readback is not an inspection or field-report date.");
   value("batch-conclusion",data.validation.foreign_key_warnings
     ? "B001 source inventory and readback complete. Cross-reference warning(s) remain open; no new provider messages were published."
     : "B001 stopped after verifying seven registered workbook reads, source IDs, approved public row counts and source-pointer links. No new Slack/Discord/Telegram records were ingested; older reported work remains historical.");
   const rows=data.source_books.map(s=>{
     const tr=document.createElement("tr");
     const td=document.createElement("td"),a=node("a",s.title);
     a.href=s.url; a.target="_blank";a.rel="noopener noreferrer";
     td.append(a);
     tr.append(td,node("td",s.tab),node("td",String(s.row_count)),node("td",s.role));
     return tr;
   });
   byId("extract-sources").replaceChildren(...rows);
 })
 .catch(err=>{
   value("extract-readback","Checkpoint unavailable. Check the latest GitHub Actions publishing run; the previous source reports are not proof of a current extraction.");
   value("batch-conclusion","Publication/readback not verified at this time. Original Google Sheets remain authoritative.");
   byId("extract-sources").replaceChildren(node("tr","Source inventory unavailable"));
 });
