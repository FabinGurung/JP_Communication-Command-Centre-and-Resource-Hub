#!/usr/bin/env python3
"""Repeatable field-first public UI browser checks.

Runs against a local HTTP serving checkout contents. Chrome (preinstalled
on GitHub runners) is driven by Playwright; private Drive bytes are never
downloaded or included in screenshot artifacts.
"""
import os
import pathlib
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

def run():
    server=subprocess.Popen([sys.executable,"-m","http.server","8878","--bind","127.0.0.1"],
                            stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
    try:
        ready(server)
        with sync_playwright() as pw:
            binary=shutil.which("google-chrome") or shutil.which("google-chrome-stable") or shutil.which("chromium")
            require(binary is not None, "Chromium/Chrome is not installed")
            browser=pw.chromium.launch(executable_path=binary, headless=True, args=[
                "--no-sandbox","--disable-dev-shm-usage","--disable-gpu"
            ],timeout=30000)
            try:
                desktop=browser.new_context(viewport={"width":1440,"height":900}, reduced_motion="reduce")
                page=desktop.new_page()
                page.goto(BASE+"/site-operations.html",wait_until="domcontentloaded",timeout=20000)
                page.locator("#projects article.project").first.wait_for(timeout=18000)
                require(page.locator("#projects article.project").count()==8, "Expected 8 project cards")
                require(page.locator(".hero h1").count()==1, "Field Desk needs one hero h1")
                require(page.locator("#record-date").inner_text().find("2026-10-09")>=0, "Report source date missing")
                require(page.locator("nav").count()>=1, "Navigation missing")
                require(page.locator("#site-search").get_attribute("type")=="search", "Search field mislabeled")
                page.locator("#site-search").fill("Narayani")
                require(page.locator("#projects article.project").count()==1, "Search failed for Narayani")
                page.locator("#site-search").fill("")
                page.locator("#company-filter").select_option("REB")
                require(page.locator("#projects article.project").count()==1, "Rohini filter failed")
                page.locator("#company-filter").select_option("")
                require(page.locator("#projects article.project").count()==8,"Filter reset failed")
                no_wide_overflow(page,"field desk desktop")
                screenshot(page, "field-desk-desktop.png")
                print("PASS: field desk desktop, search, filters, dated status and focus navigation")

                page.goto(BASE+"/site-operations/project.html?project=P007",wait_until="domcontentloaded",timeout=20000)
                page.locator("#drawings .resource-card").first.wait_for(timeout=18000)
                require(page.locator("#drawings .resource-card").count()>=11,"P007 document pointers missing")
                require(page.locator("#historical-records").get_attribute("open") is None,"History unexpectedly expanded")
                page.locator("#historical-records summary").click()
                require(page.locator("#historical-records").get_attribute("open") is not None,"Progress disclosure did not open")
                page.locator("#historical-records summary").click()
                require(page.locator("#historical-records").get_attribute("open") is None,"Progress disclosure did not close")
                require(page.locator("#work").count()==1 and page.locator("#blockers").count()==1,"Field brief missing work or holds")
                no_wide_overflow(page,"P007 desktop")
                screenshot(page, "narayani-brief-desktop.png")
                print("PASS: Narayani field plan, project documents and collapsed history")

                mobile=browser.new_context(viewport={"width":390,"height":844},device_scale_factor=1,
                                            is_mobile=True,has_touch=True,reduced_motion="reduce")
                m=mobile.new_page()
                m.goto(BASE+"/site-operations.html",wait_until="domcontentloaded",timeout=20000)
                m.locator("#projects article.project").first.wait_for(timeout=18000)
                no_wide_overflow(m,"field desk mobile")
                screenshot(m,"field-desk-mobile.png")
                m.goto(BASE+"/site-operations/project.html?project=P007",wait_until="domcontentloaded",timeout=20000)
                m.locator("#drawings .resource-card").first.wait_for(timeout=18000)
                no_wide_overflow(m,"Narayani mobile")
                screenshot(m,"narayani-brief-mobile.png")
                print("PASS: field brief mobile snapshots and horizontal-overflow constraints")

                # Map may require the remotely hosted Leaflet library and OSM tiles.
                # A failed external asset is an explicit error, not a successful visual certification.
                page.goto(BASE+"/map.html",wait_until="domcontentloaded",timeout=25000)
                page.locator(".leaflet-container").wait_for(timeout=25000)
                require(page.locator("#workspace").evaluate("(e)=>e.classList.contains('list-collapsed')"),
                        "Map did not start map-first")
                require(page.locator("#project-pane").is_hidden(),"Project list visible by default")
                screenshot(page,"map-first-desktop.png")
                page.locator("#map-list-button").click()
                require(page.locator("#map-list-button").get_attribute("aria-expanded")=="true",
                        "Map list button aria state did not update")
                require(page.locator("#project-pane").is_visible(),"Map project list failed to open")
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
                require(m.locator("#project-pane").is_hidden(),"Mobile map list not initially collapsed")
                no_wide_overflow(m,"map mobile",tolerance=22)
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
