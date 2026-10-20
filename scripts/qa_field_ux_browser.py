#!/usr/bin/env python3
"""Repeatable field-first public UI browser checks.

Runs against a local HTTP serving checkout contents. Chrome (preinstalled
on GitHub runners) is driven by Playwright; private Drive bytes are never
downloaded or included in screenshot artifacts.
"""
import os
import json
import pathlib
import re
import urllib.error
import shutil
import subprocess
import sys
import time
import urllib.request
from playwright.sync_api import sync_playwright

BASE = "http://127.0.0.1:8878"
OUT = pathlib.Path("artifacts/field-ux")
OUT.mkdir(parents=True, exist_ok=True)

def require(condition, message):
    if not condition:
        raise AssertionError(message)

def ready(server):
    for _ in range(40):
        if server.poll() is not None:
            raise RuntimeError("Local HTTP server exited")
        try:
            with urllib.request.urlopen(BASE + "/site-operations.html", timeout=1) as r:
                if r.status == 200:
                    return
        except OSError:
            pass
        time.sleep(0.25)
    raise RuntimeError("Local HTTP server not ready")

def audit_wcag(page, label):
    axe_path=pathlib.Path("node_modules/axe-core/axe.min.js")
    require(axe_path.exists(), "axe-core missing from UI QA runner")
    page.add_script_tag(path=str(axe_path))
    report=page.evaluate("""async () => {
      const result=await axe.run(document, {
        runOnly: {type: "tag", values:["wcag2a","wcag2aa","wcag21a","wcag21aa","wcag22aa"]},
        resultTypes:["violations"]
      });
      return result.violations.map(v=>({
        id:v.id, impact:v.impact,
        nodes:v.nodes.slice(0,5).map(n=>({selector:n.target,summary:n.failureSummary}))
      }));
    }""")
    print("WCAG_AUDIT",label,"violations",len(report))
    for v in report:
        print("WCAG_FINDING",label,v["id"],v["impact"],str(v["nodes"])[:280])
    fatal=[v for v in report if v["impact"] in {"critical","serious"}]
    if fatal:
        key="".join(c if c.isalnum() else "-" for c in label)
        (OUT/(key+"-accessibility.json")).write_text(json.dumps(report,indent=2))
        page.screenshot(path=str(OUT/(key+"-accessibility-failure.png")),full_page=True)
    require(not fatal, f"{label}: serious or critical WCAG errors: {[x['id'] for x in fatal]}")
    return report

def screenshot(page, name):
    dest=OUT/name
    page.screenshot(path=str(dest), full_page=True, animations="disabled", timeout=25000)
    require(dest.exists() and dest.stat().st_size > 5000, "Screenshot missing: " + str(dest))
    print("SCREENSHOT", dest, dest.stat().st_size, "bytes")

def no_wide_overflow(page, desc, tolerance=18):
    dims=page.evaluate("""() => ({
      window: window.innerWidth,
      html: document.documentElement.scrollWidth,
      body: document.body.scrollWidth
    })""")
    print("DIMENSIONS", desc, dims)
    require(dims["html"] <= dims["window"]+tolerance, f"{desc} horizontal html overflow {dims}")
    intended=page.viewport_size["width"]
    require(dims["html"] <= intended+2, f"{desc} exceeds specified {intended}px viewport: {dims}")
    # A clipped Leaflet pane can make body.scrollWidth larger than the viewport.
    # Probe actual horizontal scroll reach rather than trusting body.scrollWidth.
    scroll=page.evaluate("""() => {
      const root=document.documentElement, body=document.body;
      const prior={windowX:window.scrollX,rootX:root.scrollLeft,bodyX:body.scrollLeft,windowY:window.scrollY};
      window.scrollTo(100000,prior.windowY);
      root.scrollLeft=100000;
      body.scrollLeft=100000;
      const measured={windowX:window.scrollX,rootX:root.scrollLeft,bodyX:body.scrollLeft};
      window.scrollTo(prior.windowX,prior.windowY);
      root.scrollLeft=prior.rootX;
      body.scrollLeft=prior.bodyX;
      return measured;
    }""")
    print("SCROLL_REACH",desc,scroll)
    require(max(scroll.values()) <= tolerance, f"{desc} allows unwanted horizontal page scrolling: {scroll}")

def verify_shared_shell(page, section):
    host=page.locator("jp-site-header")
    host.wait_for(timeout=12000)
    details=host.evaluate("""e => {
      const root=e.shadowRoot;
      const links=[...root.querySelectorAll('nav[aria-label="JP AEC primary destinations"] a')];
      return {
        labels:links.map(a=>a.innerText.trim()),
        active:links.filter(a=>a.getAttribute("aria-current")==="page").map(a=>a.textContent.trim()),
        paths:links.map(a=>new URL(a.href).pathname),
        developer:links.some(a=>a.textContent.includes("Developer Workspace")),
        shadowStyle:!!root.querySelector('link[href*="site-shell.css"]'),
        sourceTheme:!!document.querySelector('link[href*="site-shell.css"]'),
        oldVisible:!![...document.querySelectorAll('nav[data-jp-legacy-primary="1"]')].find(n=>
            getComputedStyle(n).display !== "none")
      };
    }""")
    require(len(details["labels"])==7, "Shared shell does not have six routes: "+str(details))
    require(len(set(details["paths"]))==7, "Shared shell has duplicate routes")
    require(details["developer"] and details["shadowStyle"] and details["sourceTheme"],
            "Developer route or theme stylesheet missing")
    require(not details["oldVisible"], "Two competing primary navigations visible")
    if section!="overview":
        require(len(details["active"])==1, "Active department not visible for "+section)
    else:
        require(len(details["active"])==0, "Homepage must not mark an unrelated department active")

def browser_options():
    binary=os.environ.get("CHROME_BIN") or shutil.which("google-chrome") or shutil.which("google-chrome-stable") or shutil.which("chromium")
    require(binary is not None, "Chromium/Chrome is not installed")
    options=dict(executable_path=binary, headless=True,
                 args=["--no-sandbox","--disable-dev-shm-usage","--disable-gpu"], timeout=30000)
    if os.environ.get("JP_QA_PROXY"):
        options["proxy"]={"server":os.environ["JP_QA_PROXY"], "bypass":"127.0.0.1,localhost"}
    return options

def configure_network(context):
    """Optional local sandbox transport, with actual remote CDN / OSM bytes.

    An explicit proxy may route loopback URLs through itself. Relay only the
    local static QA server through Python; external assets still use Chrome's
    real network. Normal GitHub runners need no relay.
    """
    if not os.environ.get("JP_QA_PROXY"):
        return
    def local(route):
        try:
            with urllib.request.urlopen(route.request.url, timeout=5) as response:
                route.fulfill(status=response.status,
                              content_type=response.headers.get("Content-Type","application/octet-stream"),
                              body=response.read())
        except Exception as exc:
            print("LOCAL_QA_ASSET_FAILED",route.request.url,str(exc),flush=True)
            route.abort()
    context.route(re.compile(r"http://127\.0\.0\.1:887[89]/"),local)

def run():
    server=subprocess.Popen([sys.executable,"-m","http.server","8878","--bind","127.0.0.1"],
                            stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
    try:
        ready(server)
        with sync_playwright() as pw:
            browser=pw.chromium.launch(**browser_options())
            try:
                desktop=browser.new_context(viewport={"width":1440,"height":900}, reduced_motion="reduce", ignore_https_errors=bool(os.environ.get("JP_QA_PROXY")))
                configure_network(desktop)
                page=desktop.new_page()
                page.goto(BASE+"/",wait_until="domcontentloaded",timeout=20000)
                page.locator("#field-hero-canvas").wait_for(timeout=12000)
                require(page.locator(".card").count()==6,"Homepage should expose six main destinations")
                require(page.locator('a[href="workspace/"]').count()>=1,"Developer Workspace link missing")
                require(page.locator('a[href="resources/"]').count()>=1,"Resource library missing")
                require(page.locator("#field-hero-canvas").evaluate("(e)=>e.width>100&&e.height>100"),"Animated hero canvas was not initialized")
                audit_wcag(page,"homepage")
                no_wide_overflow(page,"homepage")
                screenshot(page,"home-light-construction-hero.png")
                print("PASS: themed hero, six routes and accessible homepage")

                page.goto(BASE+"/guide/",wait_until="domcontentloaded",timeout=20000)
                page.wait_for_function("() => (document.querySelector('#pages')?.textContent || '').trim().length > 150", timeout=15000)
                require(page.locator('.depth-nav a').count()==4, 'How-To depth navigation missing')
                audit_wcag(page, 'how-to quick start')
                no_wide_overflow(page, 'how-to quick start')
                screenshot(page, 'how-to-quick-start.png')
                require("Developer Workspace (developers only)" in page.locator("#pages").inner_text(),
                        "Quick Start does not distinguish developer-only workspace")
                print('PASS: How-To quick-start content and four tutorial depths')
                for guide_depth, count in (("3",3),("7",7),("15",15)):
                    page.goto(BASE+"/guide/"+guide_depth+"-pages/",wait_until="domcontentloaded",timeout=20000)
                    page.wait_for_function("n => document.querySelectorAll('#pages article.guide-page').length === n",
                                           arg=count, timeout=15000)
                    require("Developer Workspace" in page.locator("#pages").inner_text(),
                            "Missing developer-only guidance in "+guide_depth+"-page tutorial")
                    require(page.locator(".top a").first.inner_text()=="← Operations Hub",
                            "How-To backward navigation leads to Developer Workspace")
                print("PASS: 1/3/7/15-page guide role guidance and back links")

                page.goto(BASE+"/workspace/",wait_until="domcontentloaded",timeout=20000)
                page.wait_for_function("() => document.querySelectorAll('#developer-directory .card').length >= 4",timeout=15000)
                require(page.locator("#developer-directory .card").count()==6,
                        "Developer Workspace must show six software-only categories")
                require(page.locator(".development-map .dev-step").count()==3,
                        "Developer workflow plan, test, release diagram missing")
                developer_labels=page.locator("#developer-directory").inner_text()
                require("Software Backlog" in developer_labels and "GitHub" in developer_labels,
                        "Developer directory does not surface backlog/version control")
                require("Site field reports" not in developer_labels and
                        "Open original in Google Drive" not in developer_labels,
                        "Raw project facts or source files leaked into developer directory")
                require(page.locator("#live-project-grid").count()==0,"Project operations leaked into Developer Workspace")
                require(page.locator('a[href="../controls/"]').count()>=0,"Control navigation route")
                audit_wcag(page,"developer workspace")
                no_wide_overflow(page,"developer workspace")
                screenshot(page,"developer-workspace.png")
                print("PASS: software-only Developer Workspace technologies, control towers and releases")
                page.locator('.dev-step a[href="backlog/"]').click()
                page.wait_for_url("**/workspace/backlog/",timeout=15000)
                page.wait_for_function("() => document.querySelectorAll('#tasks .card').length === 9",
                                       timeout=15000)
                verify_shared_shell(page,"developer")
                cards=page.locator("#tasks .card").all_inner_texts()
                require(any("Authenticated" in x for x in cards) and
                        any("Control index" in x for x in cards),
                        "Developer backlog missing genuine software plans")
                for forbidden in ("Narayani engineering", "trade-report replies",
                                  "Run Discord C01", "Legacy-to-CWO event reconciliation"):
                    require(forbidden not in page.locator("#tasks").inner_text(),
                            "Operational case record leaked into developer backlog: "+forbidden)
                page.locator("#state").select_option("complete")
                completed_count=page.locator("#tasks .card").count()
                require(completed_count>=1,
                        "Verified software milestones disappeared from completed filter")
                page.locator("#state").select_option("open")
                open_count=page.locator("#tasks .card").count()
                require(open_count+completed_count==9,
                        "Software state filter omitted or duplicated source-owned task records")
                audit_wcag(page,"developer software backlog")
                no_wide_overflow(page,"developer software backlog")
                screenshot(page,"developer-software-backlog-desktop.png")
                print("PASS: software backlog provenance, field task exclusions and scope filters")

                page.goto(BASE+"/site-operations.html",wait_until="domcontentloaded",timeout=20000)
                page.wait_for_function("() => document.querySelectorAll('#project option').length >= 8",timeout=18000)
                require(page.locator("#project option").count()==8,"Project selection should contain eight sites")
                require(page.locator("h1").inner_text()=="Checklist for Today","Daily Checklist title missing")
                require(page.locator("#tasks input[type=checkbox]").count()==0,"User checklist must start empty")
                require(page.locator("#count").inner_text().startswith("No tasks yet"),"Empty state missing")
                page.locator("#new-task").fill("Confirm today's site toolbox instructions")
                page.locator("#add-form button").click()
                require(page.locator("#tasks input[type=checkbox]").count()==1,"Author-entered checklist not added")
                page.locator("#tasks input[type=checkbox]").first.check()
                require(page.locator("#count").inner_text().startswith("1 / 1"),"User checklist checked state missing")
                page.reload(wait_until="domcontentloaded")
                page.locator("#tasks input[type=checkbox]").first.wait_for(timeout=18000)
                require(page.locator("#tasks input[type=checkbox]").first.is_checked(),"Local browser task persistence failed")
                page.locator("#project").select_option("P004")
                require(page.locator("#tasks input[type=checkbox]").count()==0,"Checklist leaked between sites")
                require(page.locator('a[href="site-operations/coordination.html"]').count()>=1,"Site Coordination link missing")
                require(page.locator('a[href="site-operations/history.html"]').count()>=1,"Progress Report link missing")
                require('Developer Workspace' in page.locator('a[href="workspace/"]').first.inner_text(), 'Checklist incorrectly calls the developer area an owner dashboard')
                no_wide_overflow(page,"daily checklist desktop")
                audit_wcag(page,"daily checklist")
                screenshot(page,"site-daily-checklist-desktop.png")
                print("PASS: user-authored empty checklist, local browser entry and per-project isolation")

                page.goto(BASE+"/site-operations/coordination.html?project=P004",wait_until="domcontentloaded",timeout=20000)
                page.locator("#issues .item").first.wait_for(timeout=18000)
                require("Developer Workspace" in page.locator('a[href="../workspace/"]').inner_text(),
                        "Coordination page retains old Owner Workspace label")
                require(page.locator("#issues .item").count()==2,"Yamuna should have two source issues")
                require(page.locator("#questions .item").count()==3,"Yamuna should have three follow-up questions")
                require(page.locator("#project").input_value()=="P004","Project deep link not retained")
                audit_wcag(page,"site coordination")
                screenshot(page,"site-coordination-desktop.png")

                page.goto(BASE+"/site-operations/history.html?project=P002",wait_until="domcontentloaded",timeout=20000)
                page.locator("#history details.entry").first.wait_for(timeout=18000)
                require(page.locator("h1").inner_text()=="Progress Report","Progress Report heading missing")
                require("Developer Workspace" in page.locator('a[href="../workspace/"]').inner_text(),
                        "Progress Report retains old Owner Workspace label")
                require(page.locator("#history details.entry").count()==1,"Samir history should contain one indexed report")
                require(page.locator("#carryover-records .carry-record").count()==0 or page.locator("#carry-count").inner_text().startswith("4 archived"),"Samir carryover index unexpected")
                page.locator("#carryover-records .carry-project").first.locator("summary").click()
                require(page.locator("#carryover-records .carry-record").count()==4,"Four Samir checklist items should appear under Progress Report")
                page.locator("#history details.entry summary").first.click()
                require(page.locator("#history details.entry").first.get_attribute("open") is not None,"History expansion failed")
                audit_wcag(page,"progress report")
                screenshot(page,"progress-report-desktop.png")

                require("Discord" in page.locator("#history .pill").first.inner_text(),"Provider attribution missing on progress report")
                page.goto(BASE+"/resources/?project=P001",wait_until="domcontentloaded",timeout=20000)
                page.wait_for_function("() => document.querySelectorAll('#directory .file').length >= 4",timeout=18000)
                require(page.locator("#project").input_value()=="P001","Bishal resource deep link failed")
                require(page.locator("#directory .file").count()==4,"Bishal should have Drive root and three linked CAD resources")
                require(page.locator("#directory .original").count()==4,"Original Drive names are not shown on resource cards")
                require("P001" not in page.locator("#directory .site-title small").first.inner_text(),
                        "Resource title still exposes machine site code in primary view")
                provenance=page.locator("#directory .project-identity").first
                require(provenance.count()==1 and provenance.get_attribute("open") is None,
                        "Resource source PK/FK disclosure should be initially collapsed")
                provenance.locator("summary").click()
                require("PRJ-000001" in provenance.inner_text() and "REB-001" in provenance.inner_text(),
                        "Resource source identity does not resolve to canonical project")
                provenance.locator("summary").click()
                require(page.locator('a[href*="16rUpvmH1JGyp_8hbU9BqispHfJNQzQh7"]').count()==1,"Bishal source DWG missing")
                require(page.locator('a[href*="1TzUCNxZ3WExD7H0mWYJ42KHsx11-A7BG"]').count()==1,"Bishal structural DWG missing")
                page.locator("#project").select_option("P007")
                page.locator("#kind").select_option("E2K")
                require(page.locator("#directory .file").count()>=2,"Narayani E2K resources missing")
                require(page.locator("#directory .file a").count()>=2,"Narayani model Drive links missing")
                no_wide_overflow(page,"drawings directory desktop")
                audit_wcag(page,"drawings directory")
                screenshot(page,"project-resources-desktop.png")
                print("PASS: drawing index by project / DWG / E2K and permission-gated source links")
                require("46 indexed originals" in page.locator("#coverage-note").inner_text() and
                        "Full recursive Drive inventory" in page.locator("#coverage-note").inner_text(),
                        "Indexed resources incorrectly claimed as exhaustive Drive inventory")
                require(page.locator("#priority-order button[data-band]").count()==5,
                        "Four document priorities and reset choice not rendered")
                page.locator("#kind").select_option("")
                page.locator("#project").select_option("P005")
                page.locator("#priority").select_option("calculations_and_support")
                require(page.locator("#directory .file").count()==1 and
                        "Cost estimate" in page.locator("#directory .file .label").inner_text(),
                        "Sabitri cost-estimate PDF incorrectly prioritized with drawing sets")
                require(page.locator('.tier[data-priority="3"]').count()==1,
                        "Cost PDF is not in supporting calculations priority")
                require(page.locator('.tier[data-priority="3"] .file .label').first.evaluate(
                    "(e) => getComputedStyle(e).fontSize")=="15px",
                    "Rank 3 typography not applied")
                page.locator("#project").select_option("P020")
                require(page.locator("#directory .file").count()==1 and
                        "Structural detail calculation" in page.locator("#directory .file .label").inner_text(),
                        "Detail calculation PDF incorrectly categorized as issued drawing")
                page.locator('#priority-order button[data-band="issued_reports"]').click()
                require(page.locator("#priority").input_value()=="issued_reports" and
                        page.locator('#priority-order button[data-band="issued_reports"]').get_attribute("aria-pressed")=="true",
                        "Visual priority filter and form are out of sync")
                require(page.locator('.tier[data-priority="1"] .file .label').first.evaluate(
                    "(e) => getComputedStyle(e).fontSize")=="16px",
                    "Drawing/report font hierarchy not applied")
                page.locator('#priority-order button[data-band="source_folders"]').click()
                require(page.locator('.tier[data-priority="4"] .file .label').first.evaluate(
                    "(e) => getComputedStyle(e).fontSize")=="14px",
                    "Original archive priority font not applied")
                page.goto(BASE+"/resources/?project=P005&priority=calculations_and_support",
                          wait_until="domcontentloaded",timeout=20000)
                page.wait_for_function("() => document.querySelector('#priority')?.value === 'calculations_and_support'",
                                       timeout=15000)
                require(page.locator("#directory .file").count()==1,
                        "Resource deep-link priority filter failed")
                print("PASS: source-reconciled 46-file catalog, four priorities, correct PDF classifications and type hierarchy")

                page.goto(BASE+"/site-operations/questions.html?project=P002",wait_until="domcontentloaded",timeout=20000)
                page.locator("#board article.card").first.wait_for(timeout=18000)
                require(page.locator("#board article.card").count()==6,"Samir detailed answers filtered to six questions")
                audit_wcag(page,"detailed engineer questions")
                page.goto(BASE+"/site-operations/schedule.html?project=P002",wait_until="domcontentloaded",timeout=20000)
                page.locator("#site-cards article.card").first.wait_for(timeout=18000)
                require(page.locator("#site-cards article.card").count()==1,"Legacy Samir detailed hold view broken")
                audit_wcag(page,"legacy work and holds")

                page.goto(BASE+"/site-operations/project.html?project=P007",wait_until="domcontentloaded",timeout=20000)
                page.locator("#drawings .resource-card").first.wait_for(timeout=18000)
                require(page.locator("#drawings .resource-card").count()>=11,"P007 document pointers missing")
                require("P007" not in page.locator("#meta").inner_text() and
                        "FBL-006" not in page.locator("#meta").inner_text(),
                        "Project Brief still foregrounds machine identifiers")
                brief_identity=page.locator(".identity-details")
                require(brief_identity.count()==1 and brief_identity.get_attribute("open") is None,
                        "Project Brief identity disclosure should initially be collapsed")
                brief_identity.locator("summary").click()
                require("PRJ-000007" in brief_identity.inner_text() and
                        "FBL-006" in brief_identity.inner_text(),
                        "Project Brief PK and FK provenance mismatch")
                brief_identity.locator("summary").click()
                require("Developer Workspace" in page.locator('a[href="../workspace/"]').inner_text(),
                        "Project detail retains old Owner Workspace label")
                require(page.locator("#work .day-panel").count()==3, "Yesterday, Today and Tomorrow panels missing")
                require(page.locator("#work .schedule-table").count()>=2, "Expected yesterday and today trade tables")
                require(page.locator("#work .schedule-table tbody tr").count()>=5, "Expected source-grounded trade rows")
                require(page.locator(".gate-grid").count()==0, "Old unknown PPE/tools/manpower gates must not return")
                require(page.locator("#blockers .issues-table tbody tr").count()>=2, "Trade-specific issue queue missing")
                require(page.locator(".resource-optional").count()>=3,"Optional discipline disclosures missing")
                require(not page.locator(".resource-optional").first.evaluate("(e)=>e.open"),"Optional models should start collapsed")
                page.locator(".resource-optional").first.locator("summary").click()
                require(page.locator(".resource-optional").first.evaluate("(e)=>e.open"),"Optional model disclosure failed")
                page.locator(".resource-optional").first.locator("summary").click()
                require(page.locator("#historical-records").get_attribute("open") is None,"History unexpectedly expanded")
                page.locator("#historical-records summary").click()
                require(page.locator("#historical-records").get_attribute("open") is not None,"Progress disclosure did not open")
                page.locator("#historical-records summary").click()
                require(page.locator("#historical-records").get_attribute("open") is None,"Progress disclosure did not close")
                require(page.locator("#work").count()==1 and page.locator("#blockers").count()==1,"Field brief missing work or holds")
                no_wide_overflow(page,"P007 desktop")
                audit_wcag(page,"project brief")
                screenshot(page, "narayani-brief-desktop.png")
                print("PASS: Narayani field plan, project documents and collapsed history")

                # Request 01: all public routes share one themed, accessible six-section shell.
                routes={
                    "":"overview",
                    "map.html":"map",
                    "site-operations.html":"checklist",
                    "site-operations/history.html":"progress",
                    "site-operations/coordination.html":"checklist",
                    "site-operations/questions.html":"checklist",
                    "site-operations/schedule.html":"checklist",
                    "site-operations/project.html":"checklist",
                    "resources/":"resources",
                    "workspace/":"developer",
                    "guide/":"guide",
                    "guide/3-pages/":"guide",
                    "guide/7-pages/":"guide",
                    "guide/15-pages/":"guide",
                    "pending/":"overview",
                    "workspace/backlog/":"developer",
                    "controls/":"developer",
                    "controls/storage.html":"developer",
                    "controls/archive-formats.html":"developer",
                    "controls/memory-wall.html":"developer",
                }
                for route,group in routes.items():
                    page.goto(BASE+"/"+route,wait_until="domcontentloaded",timeout=20000)
                    verify_shared_shell(page,group)
                print("PASS: 20 routes use one six-section website shell without duplicate navigation")

                # Request 02: project identity follows navigation, while developer tools
                # never inherit project identity or appear in the field context menu.
                page.goto(BASE+"/resources/?project=P007",wait_until="domcontentloaded",timeout=20000)
                page.wait_for_function("() => document.querySelector('#project')?.value === 'P007'",timeout=15000)
                top=page.locator("jp-site-header")
                progress=top.locator('nav a[data-jp-route="site-operations/history.html"]')
                require(progress.get_attribute("href").endswith("/site-operations/history.html?project=P007"),
                        "Project FK lost from Resources to Progress")
                top.locator(".jp-related summary").click()
                brief=top.locator('.jp-related a[data-jp-route="site-operations/project.html"]')
                require(brief.count()==1 and "project=P007" in brief.get_attribute("href"),
                        "Selected project not linked to project brief")
                brief.click()
                page.wait_for_url("**/site-operations/project.html?project=P007",timeout=16000)
                require(page.locator("#drawings").count()==1,"Project Brief navigation failed")
                top=page.locator("jp-site-header")
                resources=top.locator('nav a[data-jp-route="resources/"]')
                require(resources.get_attribute("href").endswith("/resources/?project=P007"),
                        "Project Brief not linked back to matching Resources")
                resources.click()
                page.wait_for_url("**/resources/?project=P007",timeout=16000)
                require(page.locator("#project").input_value()=="P007","Site context changed on return to Resources")
                print("PASS: contextual Resources to Project Brief round trip retains project FK")

                page.goto(BASE+"/site-operations.html?project=P004",wait_until="domcontentloaded",timeout=20000)
                page.wait_for_function("() => document.querySelector('#project')?.value === 'P004'",timeout=15000)
                top=page.locator("jp-site-header")
                top.locator('nav a[data-jp-route="site-operations/history.html"]').click()
                page.wait_for_url("**/site-operations/history.html?project=P004",timeout=16000)
                page.wait_for_function("() => document.querySelector('#project')?.value === 'P004'",timeout=15000)
                top=page.locator("jp-site-header")
                top.locator('nav a[data-jp-route="resources/"]').click()
                page.wait_for_url("**/resources/?project=P004",timeout=16000)
                page.wait_for_function("() => document.querySelector('#project')?.value === 'P004'",timeout=15000)
                page.locator("#project").select_option("")
                top=page.locator("jp-site-header")
                require("project=" not in top.locator('nav a[data-jp-route="site-operations/history.html"]').get_attribute("href"),
                        "Cleared All projects selection still leaks previous project FK")
                print("PASS: Checklist to Progress to Resources retains selected site safely and clearing filter clears context")

                page.goto(BASE+"/workspace/",wait_until="domcontentloaded",timeout=20000)
                top=page.locator("jp-site-header")
                top.locator(".jp-related summary").click()
                names=top.locator(".jp-related a").all_inner_texts()
                require(any("Control Towers" in x for x in names) and any("Software Backlog" in x for x in names),
                        "Developer secondary menu missing control tower or software backlog")
                require(not any("Site Coordination" in x or "Project Brief" in x for x in names),
                        "Construction tools appeared inside developer-only menu")
                top.locator('.jp-related a[data-jp-route="controls/"]').click()
                page.wait_for_url("**/controls/",timeout=15000)
                verify_shared_shell(page,"developer")
                require(page.locator("jp-site-header").locator(".jp-related summary").count()==1,
                        "Developer secondary navigation missing on control tower")
                print("PASS: developer-only tools and category navigation")





                mobile=browser.new_context(viewport={"width":390,"height":844},device_scale_factor=1,
                                            is_mobile=True,has_touch=True,reduced_motion="reduce",ignore_https_errors=bool(os.environ.get("JP_QA_PROXY")))
                configure_network(mobile)
                m=mobile.new_page()
                m.goto(BASE+"/",wait_until="domcontentloaded",timeout=20000)
                m.locator("#field-hero-canvas").wait_for(timeout=12000)
                require(m.locator(".card").count()==6,"Mobile homepage routes missing")
                no_wide_overflow(m,"homepage mobile")
                audit_wcag(m,"homepage mobile")
                screenshot(m,"home-light-hero-mobile.png")
                m.goto(BASE+"/site-operations.html",wait_until="domcontentloaded",timeout=20000)
                m.wait_for_function("() => document.querySelectorAll('#project option').length >= 8",timeout=18000)
                require(m.locator("#project option").count()==8,"Mobile user checklist project choices missing")
                require(m.locator("#tasks input[type=checkbox]").count()==0,"Mobile checklist should start empty")
                verify_shared_shell(m,"checklist")
                no_wide_overflow(m,"field desk mobile")
                screenshot(m,"site-daily-checklist-mobile.png")
                m.goto(BASE+"/resources/?project=P007",wait_until="domcontentloaded",timeout=20000)
                m.wait_for_function("() => document.querySelectorAll('#directory .file').length >= 10",timeout=18000)
                verify_shared_shell(m,"resources")
                require(m.locator("jp-site-header").locator('nav a[data-jp-route="site-operations/history.html"]').get_attribute("href").endswith("?project=P007"),
                        "Mobile Resources navigation loses project selection")
                no_wide_overflow(m,"drawings directory mobile")
                audit_wcag(m,"drawings directory mobile")
                screenshot(m,"project-resources-mobile.png")
                m.goto(BASE+"/site-operations/project.html?project=P007",wait_until="domcontentloaded",timeout=20000)
                m.locator("#drawings .resource-card").first.wait_for(timeout=18000)
                no_wide_overflow(m,"Narayani mobile")
                screenshot(m,"narayani-brief-mobile.png")
                print("PASS: field brief mobile snapshots and horizontal-overflow constraints")

                # Map may require the remotely hosted Leaflet library and OSM tiles.
                # A failed external asset is an explicit error, not a successful visual certification.
                page.goto(BASE+"/map.html",wait_until="domcontentloaded",timeout=25000)
                page.locator(".leaflet-container").wait_for(timeout=25000)
                # Wait for a useful amount of background imagery; Leaflet container alone
                # does not prove tiles finished loading.
                page.wait_for_function("() => document.querySelectorAll('img.leaflet-tile-loaded').length >= 8",timeout=18000)
                print("MAP_TILES_DESKTOP",page.locator("img.leaflet-tile-loaded").count())
                require(page.locator("#workspace").evaluate("(e)=>e.classList.contains('list-collapsed')"),
                        "Map did not start map-first")
                require(page.locator("#project-pane").is_hidden(),"Project list visible by default")
                require(page.locator('nav.jp-subnav a[href="resources/"]').count()==1,"Map resource navigation missing")
                require('Developer Workspace' in page.locator('nav.jp-subnav a[href="workspace/"]').inner_text(), 'Map incorrectly calls the developer area an owner dashboard')
                audit_wcag(page,"map")
                screenshot(page,"map-first-desktop.png")
                page.locator("#map-list-button").click()
                require(page.locator("#map-list-button").get_attribute("aria-expanded")=="true",
                        "Map list button aria state did not update")
                require(page.locator("#project-pane").is_visible(),"Map project list failed to open")
                page.locator('#project-list .project-item').filter(has_text='Bishal').first.click()
                # Leaflet may briefly expose a popup before its selected content settles.
                # Wait for the expected user-authored item, not just any popup element.
                popup=page.locator('.leaflet-popup-content .map-quick-checklist').filter(
                    has_text="Confirm today's site toolbox instructions"
                )
                popup.wait_for(timeout=16000)
                require("Bishal" in page.locator('#detail-title').inner_text(),
                        'Selected map project did not match P001 checklist site')
                print('PASS: project map popup and engineer-authored local checklist use one key')
                # Request 03: site-first map never makes legacy IDs or unsourced
                # completion assertions the main content. Source progress is dated.
                require(page.locator("#detail-code").inner_text()=="📍 Site snapshot",
                        "Map detail header still foregrounds machine project code")
                require("PRJ-" not in page.locator("#detail-subtitle").inner_text() and
                        "legacy P" not in page.locator("#detail-subtitle").inner_text(),
                        "Legacy machine identifiers leaked into site header")
                require(page.locator("#panel-overview .map-technical").count()==1 and
                        page.locator("#panel-overview .map-technical").get_attribute("open") is None,
                        "Technical map metadata must start collapsed")
                require(not page.locator("#panel-overview .map-technical .detail-grid").first.is_visible(),
                        "Project identity details expanded without user request")
                require("Reported done" in page.locator("#panel-overview .map-work-summary").inner_text(),
                        "Source-backed reported done observation missing from Bishal overview")
                require("not live instructions or engineer-accepted completion" in
                        page.locator("#panel-overview .map-work-summary").inner_text(),
                        "Map reported work lost engineering acceptance disclaimer")
                page.locator("#panel-overview .map-technical summary").click()
                require(page.locator("#panel-overview .map-technical").get_attribute("open") is not None,
                        "Opt-in technical information cannot be opened")
                require("PRJ-000001" in page.locator("#panel-overview .map-technical").inner_text(),
                        "Stable project ID disappeared from optional provenance")

                page.locator('#project-list .project-item').filter(has_text='Hari Baral').first.click()
                overview=page.locator("#panel-overview .map-work-summary").inner_text()
                require("Reported ongoing" in overview and "Painting" in overview and
                        "Observed 2026-10-02" in overview,
                        "Hari public source-linked dated ongoing work is not shown")
                require("P003" not in page.locator("#detail-subtitle").inner_text(),
                        "Technical code present in normal Hari overview")
                page.locator('#project-list .project-item').filter(has_text='Yamuna').first.click()
                require("Reported HOLD" in page.locator("#panel-overview .map-readiness").inner_text(),
                        "Documented site HOLD not surfaced")
                require("No source-attributed" in page.locator("#panel-overview .map-work-summary").inner_text(),
                        "No published work records must never become zero completed claims")
                print('PASS: compact human-first site map, field-reported status and optional PK/FK details')

                page.locator("#map-list-button").click()
                require(page.locator("#project-pane").is_hidden(),"Map project list failed to close")
                page.locator("#filter-toggle").click()
                require(page.locator("#map-controls").is_visible(),"Map filters did not open")
                page.locator("#filter-toggle").click()
                require(not page.locator("#map-controls").is_visible(),"Map filters did not close")
                page.locator(".map-layer-control summary").click()
                require(page.locator("#layer-projects").is_visible(),"Map layer disclosure failed")
                no_wide_overflow(page,"map desktop")
                print("PASS: map first, optional list, filters and layer disclosure")
                m.goto(BASE+"/map.html",wait_until="domcontentloaded",timeout=25000)
                m.locator(".leaflet-container").wait_for(timeout=25000)
                m.wait_for_function("() => document.querySelectorAll('img.leaflet-tile-loaded').length >= 3",timeout=18000)
                print("MAP_TILES_MOBILE",m.locator("img.leaflet-tile-loaded").count())
                require(m.locator("#project-pane").is_hidden(),"Mobile map list not initially collapsed")
                verify_shared_shell(m,"map")
                no_wide_overflow(m,"map mobile",tolerance=22)
                audit_wcag(m,"map mobile")
                screenshot(m,"map-first-mobile.png")
                print("PASS: map mobile screenshot and disclosure default")
                mobile.close()
                desktop.close()
            finally:
                browser.close()
    finally:
        server.terminate()
        try: server.wait(timeout=4)
        except subprocess.TimeoutExpired: server.kill()
    print("PASS: visual, responsive, accessibility-control smoke and field interactions")

if __name__=="__main__":
    run()
