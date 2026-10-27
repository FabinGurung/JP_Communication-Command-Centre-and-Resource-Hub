#!/usr/bin/env python3
"""Playwright smoke for new A9 departments and project/manual status on mobile/desktop."""
import os
import shutil
import pathlib
import subprocess
import time
import urllib.request
import sys
from playwright.sync_api import sync_playwright
BASE="http://127.0.0.1:8879"
ROOT=pathlib.Path(__file__).resolve().parents[1]
OUT=ROOT/"artifacts/field-ux"
OUT.mkdir(parents=True,exist_ok=True)
def check(ok,msg):
    if not ok: raise AssertionError(msg)
server=subprocess.Popen([sys.executable,"-m","http.server","8879","--bind","127.0.0.1"],cwd=ROOT,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
try:
    for i in range(50):
        try:
            urllib.request.urlopen(BASE+"/resources/field/",timeout=2)
            break
        except Exception:
            time.sleep(.15)
    else: raise AssertionError("Local site server failed")
    with sync_playwright() as p:
        binary=os.environ.get("CHROME_BIN") or shutil.which("google-chrome") or shutil.which("google-chrome-stable") or shutil.which("chromium")
        check(binary is not None,"Installed system Chromium unavailable")
        options={"executable_path":binary,"headless":True,"args":["--no-sandbox","--disable-dev-shm-usage","--disable-gpu"]}
        if os.environ.get("JP_QA_PROXY"): options["proxy"]={"server":os.environ["JP_QA_PROXY"],"bypass":"127.0.0.1,localhost"}
        browser=p.chromium.launch(**options)
        for width in (390,1440):
            page=browser.new_page(viewport={"width":width,"height":850},device_scale_factor=1)
            errors=[]
            page.on("pageerror",lambda e:errors.append(str(e)))
            page.goto(BASE+"/resources/field/",wait_until="load")
            page.wait_for_function("document.querySelectorAll('.a9-source-card').length === 14",timeout=9000)
            check(page.locator(".a9-contact-card").count()==0,"People tables must not remain embedded in the overview")
            check(page.locator(".a9-contact-table").count()==0,"Contact data must not be rendered on overview")
            check(page.locator(".a9-panel-title-link").count()==2,"Expected two clickable company heading links")
            hrefs={x.get_attribute("href") for x in page.locator(".a9-panel-title-link").all()}
            check(hrefs=={"contacts/?source=SRC-01","contacts/?source=SRC-02"},"Company panel header routes mismatched")
            links=page.locator(".a9-source-link").all()
            check(len(links)==14,"Every source card must have a direct Google Sheets link")
            check(len({x.get_attribute("href") for x in links})==14,"Google Sheet links must be unique")
            for link in links:
                check(link.get_attribute("href").startswith("https://docs.google.com/spreadsheets/d/"),"Untrusted source link host")
                check(link.get_attribute("href").endswith("/edit"),"Google Sheet link malformed")
                check(link.get_attribute("target")=="_blank" and link.get_attribute("rel")=="noopener noreferrer","Source-link security attributes missing")
            check(page.locator("a[href='../']").count()>=1,"Desk resource navigation missing")
            check("original data remains" in page.locator("#field-sources").inner_text().lower(),"Source-owner disclaimer missing")
            check("14" in page.locator("#field-freshness").inner_text().lower() or "fourteen" in page.locator("#field-freshness").inner_text().lower(),"Metadata source count absent")
            page.locator("#field-company").select_option("Rohini")
            check(page.locator(".a9-source-card").count()==4,"Company filter not scoped")
            check(page.locator(".a9-panel-title-link").count()==1,"Rohini directory tile missing when scoped")
            page.locator("#field-search").fill("contacts")
            check(page.locator(".a9-source-card").count()==1,"Search and company filtering not combined")
            check(page.locator(".a9-source-link").count()==1,"Source filtering must retain its unique Google Sheet link")
            page.screenshot(path=str(OUT/f"a9-field-resources-{width}.png"),full_page=True)
            for source,expected in (("SRC-01",7),("SRC-02",19)):
                page.goto(BASE+"/resources/field/contacts/?source="+source,wait_until="load")
                page.wait_for_function("document.querySelector('#contact-count').textContent.includes(' of ')",timeout=9000)
                check(page.locator(".a9-person-card").count()==expected,"Company-specific directory contact count incorrect")
                check(page.locator(".a9-person-phone").count()==expected,"Contact phone values not rendered")
                check(all(x.get_attribute("href").startswith("tel:+977") for x in page.locator(".a9-person-phone").all()),"Invalid phone dialing link")
                page.locator("#contact-query").fill("Plumber")
                check(page.locator(".a9-person-card").count()>=1,"Role search Plumber missing")
                page.locator("#contact-query").fill("Hari" if source=="SRC-01" else "Sharada")
                check(page.locator(".a9-person-card").count()>=1,"Name or project search failed")
                page.locator("#contact-query").fill("")
                page.locator("#contact-role").select_option(label="Contractor")
                check(page.locator(".a9-person-card").count()>=1,"Role filter failed")
                page.locator("#contact-role").select_option("")
                check(page.locator(".a9-person-card").count()==expected,"Clear filter failed")
                page.screenshot(path=str(OUT/f"a9-contact-directory-{source.lower()}-{width}.png"),full_page=True)
                dim=page.evaluate("() => [document.documentElement.scrollWidth,window.innerWidth]")
                check(dim[0]<=dim[1]+18,"Contact directory horizontal overflow")
            page.goto(BASE+"/resources/field/",wait_until="load")
            page.goto(BASE+"/site-operations.html",wait_until="load")
            page.locator("#notification-status").wait_for(timeout=9000)
            page.wait_for_function("document.querySelector('#notification-status').textContent.includes('22 source-linked')",timeout=9000)
            check(page.locator("h1").inner_text()=="Notification Center","Notification Center heading missing")
            check(page.locator(".notification-group li").count()==22,"Notification bullets missing")
            check(page.locator(".notification-group[data-category='Work'] li").count()==4,"Work group incorrect")
            check(page.locator(".notification-group[data-category='Materials'] li").count()==9,"Material group incorrect")
            check(page.locator(".notification-group[data-category='Supervision'] li").count()==9,"Supervision group incorrect")
            check(page.locator(".notification-group li>a").count()==22,"Each bullet needs a source link")
            check(page.locator(".notification-links a").count()==3,"Original, Drive and editable owner Sheet links missing")
            check(page.locator(".notification-source-entry a").count()==1,"Prominent editing Sheet link missing")
            check(page.locator("#notification-company option").count()==3,"Company options must come from the two source organizations")
            page.locator("#notification-company").select_option("Rohini")
            check(page.locator(".notification-group li").count()==0,"Fishtail instructions leaked into Rohini filter")
            check(page.locator("#notification-project option[value='P001']").count()==1,"Rohini project missing")
            check(page.locator("#notification-project option[value='P020']").count()==0,"Fishtail project leaked into Rohini list")
            page.locator("#notification-company").select_option("Fishtail")
            check(page.locator(".notification-group li").count()==22,"Fishtail company filter failed")
            check(page.locator("#notification-project option[value='P001']").count()==0,"Rohini project leaked into Fishtail list")
            page.locator("#notification-company").select_option("")
            page.locator("#notification-category").select_option("Materials")
            check(page.locator(".notification-group li").count()==9,"Category filter failed")
            page.locator("#notification-search").fill("windows")
            check(page.locator(".notification-group li").count()==1,"Combined material search failed")
            page.locator("#notification-search").fill("")
            page.locator("#notification-category").select_option("")
            page.locator(".notification-read").click()
            check(page.locator(".notification-read").get_attribute("aria-pressed")=="true","Read acknowledgement failed")
            page.reload(wait_until="load")
            page.wait_for_function("document.querySelector('.notification-read')?.getAttribute('aria-pressed') === 'true'",timeout=9000)
            page.locator(".notification-read").click()
            page.goto(BASE+"/site-operations.html?project=P020&notice=kharika-paudel-2026-10-26#notifications",wait_until="load")
            page.wait_for_function("document.querySelector('#notification-project').value === 'P020'",timeout=9000)
            check(page.locator(".notification-target").count()==1,"Exact notice deep link failed")
            check(page.locator("#new-task").count()==1,"Personal checklist overwritten")
            dimensions=page.evaluate("() => [document.documentElement.scrollWidth,window.innerWidth]")
            check(dimensions[0]<=dimensions[1]+18,"Notification Center horizontal overflow")
            page.screenshot(path=str(OUT/f"notification-center-{width}.png"),full_page=True)
            page.goto(BASE+"/site-operations/history.html",wait_until="load")
            page.wait_for_function("document.querySelector('#a9-manual-progress-count').textContent.includes('0 reviewed')",timeout=9000)
            check(page.locator("#history").count()==1,"Frozen history missing")
            page.goto(BASE+"/workspace/",wait_until="load")
            check(page.locator("#memory-poster-board a[href='../controls/memory-wall.html#memory-contents']").count()==1,"Memory contents link absent")
            page.goto(BASE+"/controls/memory-wall.html",wait_until="load")
            check(page.locator("#website-level-tree .hierarchy-roof").count()==1,"L0 poster missing")
            check(page.locator("#website-level-tree .hierarchy-node").count()==8,"L1 poster destinations missing")
            check("L5" in page.locator("#website-level-tree").inner_text(),"Source/data level absent")
            check("on hold" in page.locator("#website-level-tree").inner_text().lower() or "paused" in page.locator("body").inner_text().lower(),"Discord pause notice missing")
            page.screenshot(path=str(OUT/f"a9-memory-board-{width}.png"),full_page=True)
            dimensions=page.evaluate("() => [document.documentElement.scrollWidth,window.innerWidth]")
            check(dimensions[0] <= dimensions[1]+18,f"Workspace horizontal overflow {dimensions}")
            check(not errors,f"JavaScript page errors: {errors}")
            page.close()
        browser.close()
    print("A9_MANUAL_BROWSER_PASS: overview plus 2 full contact directories × 2 widths; 26 phone links, name/role/project search, source privacy notes and preserved memory/progress.")
finally:
    server.terminate()
    server.wait(timeout=8)
