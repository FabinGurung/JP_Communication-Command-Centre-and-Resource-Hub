/* Playwright synthetic mobile+desktop QA of Sheets-V2 project-status controls. */
"use strict";
const assert = require("node:assert/strict");
const {chromium} = require("playwright");
const ORIGIN = process.env.QA_BASE || "http://127.0.0.1:8766";
const seen = [];
function check(msg){seen.push(msg);console.log("PASS "+msg)}
const stubLeaflet = () => {
  window.__qaMarkerCount = 0;
  window.__qaMarkers = [];
  window.__qaMapHandlers = {};
  window.__qaFitBoundsCalls = 0;
  window.L = {
    map(){return {setView(){return this},getZoom(){return 12},fitBounds(){window.__qaFitBoundsCalls++;return this},invalidateSize(){return this},on(name,handler){window.__qaMapHandlers[name]=handler;return this}}},
    tileLayer(){return {addTo(){return this}}},
    featureGroup(){return {
      addTo(){return this},clearLayers(){window.__qaMarkerCount=0;window.__qaMarkers=[];return this},
      getLayers(){return Array.from({length:window.__qaMarkerCount},()=>({}))},
      getBounds(){return [[28.2,83.9],[28.4,84.1]]}
    }},
    divIcon(x){return x},
    marker(coords, options){return {bindPopup(){return this},on(type, fn){
      if (type==="click") this.handler = fn; return this;
    },addTo(){window.__qaMarkerCount++; window.__qaMarkers.push({
      title:options.title, click:this.handler
    });return this}}}
  };
};
async function ready(page){
  await page.addInitScript(stubLeaflet);
  await page.route("https://unpkg.com/**",r=>r.abort());
  await page.goto(ORIGIN+"/", {waitUntil:"domcontentloaded"});
  await page.waitForFunction(()=>document.querySelector("#project-count")?.textContent==="5");
}
async function statusInfo(page){
  return await page.evaluate(()=>({
    projectCount:document.querySelector("#project-count").textContent,
    cards:document.querySelectorAll("#project-list button.project-entry").length,
    pins:window.__qaMarkerCount,
    filter:document.querySelector("#status-filter").value,
    active:[...document.querySelectorAll("[data-project-status][aria-pressed=true]")].map(e=>e.dataset.projectStatus),
    summary:document.querySelector("#status-filter-summary").textContent,
  }));
}
(async()=>{
  const browser = await chromium.launch({headless:true,args:["--no-sandbox"]});
  try {
    const mobile = await browser.newPage({viewport:{width:390,height:844},isMobile:true,deviceScaleFactor:1,hasTouch:true});
    await ready(mobile);
    assert.equal(await mobile.locator(".mobile-status-filter").isVisible(),true);
    assert.equal(await mobile.locator("#status-filter").isVisible(),false);
    assert.equal(await mobile.locator("[data-project-status]").count(),6);
    assert.deepEqual((await statusInfo(mobile)).active,["all"]);
    assert.equal((await statusInfo(mobile)).pins,5);
    const counts = await mobile.locator("[data-status-count]").allTextContents();
    assert.deepEqual(counts,["5","1","1","1","1","1"]);
    check("390px phone shows six accessible source-counted buttons, five approved pins and hidden desktop select");

    for(const [status,count] of [["Completed",1],["Approval",1],["Construction",1],["Maintenance",1],["unpublished",1],["all",5]]){
      await mobile.locator('[data-project-status="'+status+'"]').click();
      const info=await statusInfo(mobile);
      assert.equal(info.projectCount,String(count),status);
      assert.equal(info.cards,count,status);
      assert.equal(info.pins,count,status);
      assert.equal(info.filter,status,status);
      assert.deepEqual(info.active,[status],status);
      assert.ok(info.summary.includes(status==="unpublished"?"Not stated":status==="all"?"All public":status==="Construction"?"Under construction":status));
      const button = mobile.locator('[data-project-status="'+status+'"]');
      assert.ok((await button.boundingBox()).height>=44,"Touch target below 44px");
    }
    check("touch controls switch actual map marker counts and project lists; show/not-stated preserved");

    await mobile.locator('[data-project-status="Approval"]').focus();
    await mobile.keyboard.press("Enter");
    assert.equal((await statusInfo(mobile)).filter,"Approval");
    await mobile.locator(".advanced-map-settings summary").click();
    await mobile.locator('[data-map-mode="work"]').click();
    assert.equal((await statusInfo(mobile)).projectCount,"1");
    check("keyboard activation and map-layer switching preserve status");

    await mobile.locator("#reset-filters").click();
    assert.equal((await statusInfo(mobile)).projectCount,"5");
    assert.equal((await statusInfo(mobile)).filter,"all");
    assert.ok(await mobile.evaluate(()=>document.documentElement.scrollWidth <= window.innerWidth+2));
    assert.equal(await mobile.locator("#project-list").isVisible(),false);
    await mobile.locator("#directory-toggle").click();
    assert.equal(await mobile.locator("#project-list").isVisible(),true);
    await mobile.locator("#directory-toggle").click();
    assert.equal(await mobile.locator("#project-list").isVisible(),false);
    check("clear filters resets both controls; no horizontal page overflow");

    const remote = await mobile.request.get(ORIGIN+"/operations.json");
    const raw=await remote.text();
    assert.ok(!raw.includes("HIDDEN_RAW_STATUS_DO_NOT_PUBLISH"));
    assert.ok(!raw.includes("PRIVATE DEMO MUST NEVER PUBLISH"));
    check("private row and unapproved lifecycle status excluded in publication fixture");

    const desk=await browser.newPage({viewport:{width:1280,height:800}});
    await ready(desk);
    assert.equal(await desk.locator("#status-filter").isVisible(),true);
    assert.equal(await desk.locator("#navigation-panel").evaluate(el=>getComputedStyle(el).position),"sticky");
    check("desktop site navigator stays sticky while content scrolls");

    assert.equal(await desk.locator(".mobile-status-filter").isVisible(),false);
    await desk.locator("#status-filter").selectOption("Completed");
    assert.equal((await statusInfo(desk)).projectCount,"1");
    assert.equal((await statusInfo(desk)).pins,1);
    await desk.locator("#status-filter").selectOption("unpublished");
    assert.equal((await statusInfo(desk)).projectCount,"1");
    await desk.locator("#project-filter").selectOption("PRJ-999901");
    assert.equal((await statusInfo(desk)).filter,"all");
    assert.equal((await statusInfo(desk)).projectCount,"1");
    check("1280px desktop select matches mobile categories; direct project selection clears conflicting status");

    await mobile.locator("#reset-filters").click();
    assert.equal(await mobile.locator("#notice-total").textContent(),"3");
    assert.ok(await mobile.locator("#map").evaluate(el => el.compareDocumentPosition(document.querySelector("#notifications")) & Node.DOCUMENT_POSITION_FOLLOWING));
    assert.equal(await mobile.locator("#notifications").isVisible(),false);
    assert.equal(await mobile.locator("#notice-list .notice-item").count(),3);
    assert.deepEqual(await mobile.locator("[data-notice-count]").allTextContents(),["3","1","1","1"]);
    check("Map is first, source notice detail hidden until site selection");

    await mobile.locator('nav a[href="./#notifications"]').click();
    assert.equal(await mobile.locator("#notifications").isVisible(),true);
    await mobile.locator('[data-notice-category="Materials"]').click();
    assert.equal(await mobile.locator("#notice-list .notice-item").count(),1);
    assert.ok((await mobile.locator("#notice-list").textContent()).includes("Synthetic materials instruction"));
    await mobile.locator('[data-notice-category="all"]').click();
    await mobile.locator("#notice-site").selectOption("PRJ-999901");
    assert.equal((await statusInfo(mobile)).pins,1);
    assert.equal(await mobile.locator("#notice-list .notice-item").count(),2);
    assert.equal(await mobile.locator("#notice-focus-title").textContent(),"Demo construction");
    await mobile.locator('[data-notice-category="Work"]').click();
    assert.equal(await mobile.locator("#notice-list .notice-item").count(),1);
    check("site selection and category filtering show only reviewed notifications for that site");

    await mobile.locator('[data-notice-category="all"]').click();
    await mobile.locator("#reset-filters").click();
    await mobile.evaluate(() => {
      const pin = window.__qaMarkers.find(x => x.title.includes("Demo approval"));
      if (!pin || typeof pin.click !== "function") throw Error("Map marker test hook missing");
      pin.click();
    });
    assert.equal(await mobile.locator("#project-filter").inputValue(),"");
    assert.equal((await statusInfo(mobile)).pins,5);
    assert.equal(await mobile.locator("#notice-site").inputValue(),"PRJ-999903");
    assert.equal(await mobile.locator("#notice-list .notice-item").count(),1);
    assert.ok((await mobile.locator("#notice-list").textContent()).includes("Synthetic materials instruction"));
    check("clicking map marker opens site notice desk without removing adjacent pins");
    assert.equal(await mobile.locator("#notifications").isVisible(),true);
    const fitsBefore=await mobile.evaluate(()=>window.__qaFitBoundsCalls);
    await mobile.evaluate(()=>window.__qaMapHandlers.click());
    assert.equal(await mobile.locator("#notifications").isVisible(),false);
    assert.equal((await statusInfo(mobile)).pins,5);
    assert.equal(await mobile.evaluate(()=>window.__qaFitBoundsCalls),fitsBefore);
    check("tapping blank map dismisses detail without recentering the camera");
    await mobile.evaluate(() => window.__qaMarkers.find(x=>x.title.includes("Demo approval")).click());
    await mobile.keyboard.press("Escape");
    assert.equal(await mobile.locator("#notifications").isVisible(),false);
    check("Escape closes selected details and preserves all map markers");
    await mobile.evaluate(() => window.__qaMarkers.find(x=>x.title.includes("Demo approval")).click());
    await mobile.locator("#back-to-sites").click();
    assert.equal(await mobile.locator("#notifications").isVisible(),false);
    assert.equal((await statusInfo(mobile)).pins,5);
    check("explicit Back to all sites returns to map");

    const progResponse = await mobile.request.get(ORIGIN+"/progress.html");
    const srcResponse = await mobile.request.get(ORIGIN+"/sources.html");
    assert.equal(progResponse.status(),200);
    assert.equal(srcResponse.status(),200);
    const prog=await browser.newPage({viewport:{width:390,height:844},isMobile:true});
    await prog.goto(ORIGIN+"/progress.html?project=PRJ-999901",{waitUntil:"domcontentloaded"});
    await prog.waitForFunction(()=>document.querySelector("#report-count")?.textContent==="1");
    assert.equal(await prog.locator("#progress-project").inputValue(),"PRJ-999901");
    assert.equal(await prog.locator("#progress-list .card").count(),1);
    assert.equal(await prog.locator('#progress').count(),1);
    check("Daily Progress opens on a separate internal page with project query preservation");
    await prog.locator('nav a[href="./sources.html"]').click();
    await prog.waitForFunction(()=>document.querySelector("#source-project-count")?.textContent==="5");
    assert.ok((await prog.locator("#source-notice-count").textContent()).includes("3 reviewed notifications"));
    assert.equal(await prog.locator("nav a[aria-current=page]").textContent(),"Sources & history");
    check("Sources & History is a separate internal page with sourced counts and page navigation");
    await prog.close();

    assert.equal(await desk.request.get(ORIGIN+"/memory-wall.html").then(r=>r.status()),200);
    check("published Memory Wall route available in static QA artifact");
    await mobile.close();await desk.close();
    console.log("STATUS_BROWSER_QA_PASS checks="+seen.length);
  } finally {await browser.close()}
})().catch(error=>{console.error(error.stack||error);process.exit(1)});
