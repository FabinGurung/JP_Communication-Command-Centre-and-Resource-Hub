#!/usr/bin/env python3
"""Playwright smoke for new A9 departments and project/manual status on mobile/desktop."""
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
        browser=p.chromium.launch(headless=True)
        for width in (390,1440):
            page=browser.new_page(viewport={"width":width,"height":850},device_scale_factor=1)
            errors=[]
            page.on("pageerror",lambda e:errors.append(str(e)))
            page.goto(BASE+"/resources/field/",wait_until="load")
            page.wait_for_function("document.querySelectorAll('.a9-source-card').length === 10",timeout=9000)
            check(page.locator("a[href='../']").count()>=1,"Desk resource navigation missing")
            check("no individual data published" in page.locator("#field-sources").inner_text().lower(),"Privacy status missing")
            check("10" in page.locator("#field-freshness").inner_text().lower() or "ten" in page.locator("#field-freshness").inner_text().lower(),"Metadata source count absent")
            page.locator("#field-company").select_option("Rohini")
            check(page.locator(".a9-source-card").count()==2,"Company filter not scoped")
            page.locator("#field-search").fill("contacts")
            check(page.locator(".a9-source-card").count()==1,"Search and company filtering not combined")
            page.screenshot(path=str(OUT/f"a9-field-resources-{width}.png"),full_page=True)
            page.goto(BASE+"/site-operations.html",wait_until="load")
            page.locator("#a9-published-count").wait_for(timeout=9000)
            page.wait_for_function("document.querySelector('#a9-published-count').textContent.includes('0 published')",timeout=9000)
            check(page.locator("#new-task").count()==1,"Personal checklist overwritten")
            page.goto(BASE+"/site-operations/history.html",wait_until="load")
            page.wait_for_function("document.querySelector('#a9-manual-progress-count').textContent.includes('0 additional')",timeout=9000)
            check(page.locator("#history").count()==1,"Frozen history missing")
            page.goto(BASE+"/workspace/",wait_until="load")
            page.locator("#memory-poster-board summary").click()
            check(page.locator("iframe[src='../controls/memory-wall.html']").count()==1,"Memory board embed absent")
            check("on hold" in page.locator("#memory-poster-board").inner_text().lower(),"Discord hold warning missing")
            page.screenshot(path=str(OUT/f"a9-memory-board-{width}.png"),full_page=True)
            dimensions=page.evaluate("() => [document.documentElement.scrollWidth,window.innerWidth]")
            check(dimensions[0] <= dimensions[1]+18,f"Workspace horizontal overflow {dimensions}")
            check(not errors,f"JavaScript page errors: {errors}")
            page.close()
        browser.close()
    print("A9_MANUAL_BROWSER_PASS: 4 active pages × 2 widths; filters, private source labels, empty review feeds, Memory Wall embed, no page errors.")
finally:
    server.terminate()
    server.wait(timeout=8)
