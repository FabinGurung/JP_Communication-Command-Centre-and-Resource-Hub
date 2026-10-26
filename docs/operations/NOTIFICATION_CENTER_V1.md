# Notification Center — source-linked planner instructions

The existing `site-operations.html` URL now opens Notification Center. Old project links and browser-local personal reminders remain usable.

## Message template

Send a message or a selected chat/Slack/Discord source link. A long paragraph is acceptable. The requested intake process is:

1. Read the selected source, its date, author and project context. Match the project to the live Projects and Locations Sheet.
2. Save the unchanged message text in its own folder under `01_JP / 06 Notification Center — Original Messages`. Capture each revision separately; never replace the original with an interpretation. Preserve attachments in that source's own folder when provided.
3. Record the message in the dedicated Message Sources Sheet, including its original permalink, Drive original, source version and checksum. For direct chat without a share link, identify it as direct chat and retain the Drive original; never invent a chat URL.
4. Derive separate bullets in the Site Notifications Sheet: Work, Materials and Supervision. Keep explicit quantities, units, dates and conditions. Do not convert plans into completed work or potential needs into completed purchases. Missing quantities remain “estimate required”; unresolved technical details remain flagged. A named person's approval is not invented.
5. Keep a source quote on every derived row. ChatGPT performs the requested semantic editing; deterministic validators check identity, links, quotes, source hashes, approved versions and public fields. This is not a universal automated summarizer in Actions.
6. Publish the reviewed, user-authorized source/version. Join both Sheets in the repository publishing workbook. Build the public notification projection from that workbook's readback into the same validated JSON bundle as the map and resource catalogue. Raw originals, source quotes and private author details stay out of public GitHub.
7. Send a prominently formatted exact notification URL to the original channel only when the user requests it. Local “read” controls are browser-local; they are not team receipt or engineering completion records.

## Implemented example

The selected 26 October 2026 Slack message in `#fbl-proj-14-kharika-paudel` resolves to the existing `PRJ-000020 / FBL-019 / P020` project. The original text was saved in its own Drive folder and downloaded again for checksum comparison. Its 22 reviewed bullets comprise 4 Work, 9 Materials and 9 Supervision items. The curing instruction retains its source date, 26 October 2026. The original ratios, wall sizes and minimum 18-day scaffolding statement are retained as planner instructions; missing quantities and connection/reinforcement details remain explicit.

The two dedicated source Sheets have their own manifests, version history and central per-source archive folders. The master gained two tabs; its existing fourteen core tables and Project Resources were not rewritten for this intake. The retired empty checklist feed remains available in Git history and as its unchanged data file; it no longer competes with the new notification feed on the page.

## Work on both streams

`system/notification-center` is a registered temporary feature branch. It requires a pull request into `feature/daily-ops-current-work` and cannot deploy Pages directly. The existing working branch can continue Sheets authentication work. Merge only reviewed feature changes and retain concurrent authentication changes. Git branches isolate code, not live Google Sheets: these notification subjects use separate owners and additive publishing tabs.

## Release scope

The UI and the manually reviewed notification example can be tested and deployed now. The full Sheets automation milestone remains unready until the dedicated Google identity is configured and an Actions run with `require_live_sheets=true` proves the complete source → joined Sheet → validated JSON → Pages path. Remaining historical page-to-Sheet migrations must either be completed or explicitly excluded from a narrower release scope. No new milestone tag is created by this implementation; existing `v2.2.0` remains immutable. Colab V8 inventory execution is separate from publication and authentication.

No background Slack or Discord collector is enabled by this feature. The existing Discord collector remains paused. Intake Staging remains excluded.
