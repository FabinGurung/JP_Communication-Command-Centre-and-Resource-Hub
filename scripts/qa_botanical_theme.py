#!/usr/bin/env python3
"""All live routes × eight widths; shared-shell, mobile, print and garden QA.

Screenshots include an immutable before checkout, then the current checkout.
Network-dependent map assertions remain mandatory in qa_field_ux_browser.py.
"""
import argparse
import json
import os
import pathlib
import subprocess
import sys
import tempfile
import time
import urllib.request
from playwright.sync_api import sync_playwright
from qa_field_ux_browser import browser_options, configure_network, audit_wcag, require

ROOT=pathlib.Path(__file__).resolve().parents[1]
OUT=ROOT/'artifacts/botanical-theme'
BASE='http://127.0.0.1:8879'
BASELINE='d2963c2380c359dff3ea2f23f4a702c6074cb642'
WIDTHS=(320,375,390,430,768,1024,1440,1920)
ROUTES={
 'home':'', 'map':'map.html', 'checklist':'site-operations.html',
 'progress':'site-operations/history.html','resources':'resources/',
 'developer':'workspace/','backlog':'workspace/backlog/',
 'guide':'guide/','guide3':'guide/3-pages/','guide7':'guide/7-pages/',
 'guide15':'guide/15-pages/','coordination':'site-operations/coordination.html',
 'questions':'site-operations/questions.html','schedule':'site-operations/schedule.html',
 'project':'site-operations/project.html?project=P007', 'controls':'controls/',
 'storage':'controls/storage.html','archive':'controls/archive-formats.html',
 'memory':'controls/memory-wall.html','pending':'pending/'}
PRIMARY=('home','map','checklist','progress','resources','developer','memory','guide')

def serve(folder):
    server=subprocess.Popen([sys.executable,'-m','http.server','8879','--bind','127.0.0.1','--directory',str(folder)],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    for _ in range(40):
        try:
            urllib.request.urlopen(BASE,timeout=1).close()
            return server
        except OSError: time.sleep(.1)
    server.terminate()
    raise RuntimeError('Browser server did not start')

def settled(page,name):
    page.locator('jp-site-header').wait_for()
    selectors={'guide':'#pages article','guide3':'#pages article','guide7':'#pages article','guide15':'#pages article',
               'resources':'#directory .file','developer':'#developer-directory .card','backlog':'#tasks .card',
               'checklist':'#project option[value="P001"]','progress':'#history .entry', 'project':'#drawings .resource-card'}
    if name in selectors:page.locator(selectors[name]).first.wait_for(state='attached',timeout=20000)
    page.evaluate('document.fonts.ready')

def capture(page,phase,name,width):
    dest=OUT/phase/f'{name}-{width}.png'
    dest.parent.mkdir(parents=True,exist_ok=True)
    page.screenshot(path=str(dest),full_page=True,animations='disabled')


def before(browser):
    with tempfile.TemporaryDirectory(prefix='jp-theme-baseline-') as temp:
        # Trust the already-reviewed immutable Git tree; no provider data copied.
        archive=subprocess.Popen(['git','archive',BASELINE],cwd=ROOT,stdout=subprocess.PIPE)
        subprocess.run(['tar','-x','-C',temp],stdin=archive.stdout,check=True)
        archive.stdout.close()
        require(archive.wait()==0,'Unable to unpack frozen baseline')
        server=serve(temp)
        try:
            ctx=browser.new_context(reduced_motion='reduce',ignore_https_errors=bool(os.environ.get('JP_QA_PROXY')))
            configure_network(ctx)
            page=ctx.new_page()
            for width,height in ((1440,900),(768,1024),(390,844)):
                page.set_viewport_size({'width':width,'height':height})
                for name in PRIMARY:
                    page.goto(BASE+'/'+ROUTES[name],wait_until='networkidle',timeout=60000)
                    settled(page,name)
                    capture(page,'before',name,width)
            ctx.close()
        finally: server.terminate();server.wait()


def after(browser):
    server=serve(ROOT)
    results=[]
    try:
        ctx=browser.new_context(reduced_motion='reduce',ignore_https_errors=bool(os.environ.get('JP_QA_PROXY')))
        configure_network(ctx)
        page=ctx.new_page()
        errors=[];failed=[]
        page.on('pageerror',lambda error:errors.append(str(error)))
        page.on('requestfailed',lambda req:failed.append({'url':req.url,'failure':req.failure}))
        page.on('response',lambda r:failed.append({'url':r.url,'failure':'HTTP '+str(r.status)}) if r.status>=400 else None)
        header_heights={}
        for width in WIDTHS:
            page.set_viewport_size({'width':width,'height':900 if width>=1024 else 844})
            header_heights[width]=[]
            for name,route in ROUTES.items():
                print('CHECK',name,width,flush=True)
                errors.clear();failed.clear()
                page.goto(BASE+'/'+route,wait_until='networkidle',timeout=60000)
                settled(page,name)
                host=page.locator('jp-site-header')
                d=host.evaluate('''e=>{
                  const r=e.shadowRoot,n=r.querySelector('.jp-nav');
                  return {parent:e.parentElement.tagName,x:e.getBoundingClientRect().x,
                    width:e.getBoundingClientRect().width,height:e.getBoundingClientRect().height,
                    links:n.querySelectorAll('a').length,navWidth:n.clientWidth,navScroll:n.scrollWidth,
                    canvas:getComputedStyle(document.body).backgroundColor,
                    font:getComputedStyle(document.querySelector('h1')).fontFamily,
                    overflow:document.documentElement.scrollWidth>innerWidth+1,
                    active:[...n.querySelectorAll('[aria-current="page"]')].map(a=>a.dataset.jpRoute),
                    garden:document.querySelector('.jp-garden')?.getAttribute('aria-hidden'),
                    oldVisible:[...document.querySelectorAll('[data-jp-legacy-primary]')].some(n=>getComputedStyle(n).display!=='none')};}''')
                require(d['parent']=='BODY' and d['x']==0 and abs(d['width']-width)<2,f'{name}/{width}: narrow header {d}')
                require(d['links']==7 and not d['oldVisible'],f'{name}: competing or missing navigation')
                require(not d['overflow'],f'{name}/{width}: document overflow')
                require(d['canvas']=='rgb(243, 248, 242)',f'{name}: inconsistent canvas')
                require(d['garden']=='true',f'{name}: decorative accessibility missing')
                require(len(d['active'])==(0 if name in ('home','pending') else 1),f'{name}: active navigation mismatch')
                header_heights[width].append(round(d['height']))
                if width<=1120:
                    toggle=host.locator('.jp-menu-toggle')
                    require(toggle.get_attribute('aria-expanded')=='false','Menu must start collapsed')
                    toggle.click()
                    require(host.locator('nav').is_visible(),'Mobile menu failed to open')
                    require(host.locator('nav a').count()==7,'Mobile links missing')
                    for link in host.locator('nav a').all():
                        box=link.bounding_box()
                        require(box['height']>=44 and box['x']>=0 and box['x']+box['width']<=width+1,'Mobile link clipped / small')
                    toggle.press('Escape')
                    require(toggle.get_attribute('aria-expanded')=='false','Escape did not close menu')
                else:
                    require(d['navScroll']<=d['navWidth']+1,'Desktop nav has horizontal scrolling')
                require(not errors,f'{name}/{width}: JavaScript errors {errors}')
                # Leaflet cancels obsolete tiles during initial fitBounds/header reflow.
                # Certify the current tile set, rather than misclassifying those cancellations.
                unexpected=[x for x in failed if not (name=='map' and '.tile.openstreetmap.org/' in x['url'] and x['failure']=='net::ERR_ABORTED')]
                require(not unexpected,f'{name}/{width}: failed assets {unexpected}')
                if name=='map':
                    page.wait_for_function("document.querySelectorAll('img.leaflet-tile-loaded').length>=3",timeout=20000)
                    page.wait_for_load_state('networkidle')
                if name in PRIMARY and width in (390,768,1440):capture(page,'after',name,width)
                if width in (390,1440):audit_wcag(page,f'{name}/{width}')
                results.append({'route':route,'width':width,'result':'PASS'})
            require(max(header_heights[width])-min(header_heights[width])<=1,f'{width}: inconsistent header heights')
            print('RESPONSIVE_PASS',width,len(ROUTES),'routes',flush=True)
        # Phone landscape: navigation and content remain reachable with a short viewport.
        page.set_viewport_size({'width':844,'height':390})
        for name in PRIMARY:
            page.goto(BASE+'/'+ROUTES[name],wait_until='networkidle',timeout=60000)
            settled(page,name)
            require(page.evaluate('document.documentElement.scrollWidth<=innerWidth+1'),f'{name}: landscape overflow')
            host=page.locator('jp-site-header')
            host.locator('.jp-menu-toggle').click()
            require(host.locator('nav').is_visible(),f'{name}: landscape menu inaccessible')
            host.locator('.jp-menu-toggle').press('Escape')
        page.set_viewport_size({'width':1440,'height':900})
        # Native keyboard focus crosses the shadow boundary through skip-to-content.
        page.goto(BASE+'/site-operations.html?project=P004',wait_until='networkidle')
        settled(page,'checklist')
        page.keyboard.press('Tab')
        page.keyboard.press('Enter')
        require(page.evaluate('document.activeElement.tagName')=='MAIN','Skip to content did not focus main')
        host=page.locator('jp-site-header')
        require('project=P004' in host.locator('a[data-jp-route="resources/"]').get_attribute('href'),'Project selection lost')
        # Clipboard, remove and date isolation complement the existing add/check/reload tests.
        ctx.grant_permissions(['clipboard-read','clipboard-write'],origin=BASE)
        page.locator('#new-task').fill('Botanical QA local reminder')
        page.locator('#add-form button').click()
        page.locator('#copy').click()
        page.wait_for_function("document.querySelector('#copy-status').textContent.includes('Copied')")
        require('Botanical QA local reminder' in page.evaluate('navigator.clipboard.readText()'),'Checklist copy lost task')
        from datetime import datetime,timezone,timedelta
        now=datetime.now(timezone.utc)
        page.clock.set_fixed_time(now+timedelta(days=1))
        page.reload(wait_until='networkidle');settled(page,'checklist')
        require(page.locator('#tasks input[type=checkbox]').count()==0,'Checklist leaked between Nepal dates')
        page.clock.set_fixed_time(now)
        page.reload(wait_until='networkidle');settled(page,'checklist')
        require(page.locator('#tasks input[type=checkbox]').count()==1,'Original dated checklist disappeared')
        page.on('dialog',lambda d:d.accept())
        page.locator('#tasks .remove').click()
        require(page.locator('#tasks input[type=checkbox]').count()==0,'Checklist removal failed')
        for name in ('guide','guide3','guide7','guide15'):
            page.goto(BASE+'/'+ROUTES[name],wait_until='networkidle');settled(page,name)
            page.emulate_media(media='print')
            require(page.locator('jp-site-header').is_hidden(),'Navigation printed')
            require(page.locator('.jp-garden').is_hidden(),'Garden printed')
            require(page.locator('#pages article').count()=={'guide':1,'guide3':3,'guide7':7,'guide15':15}[name],'Guide depth broken')
            page.emulate_media(media='screen')
        # Reduced motion and decoration layering are stable, nonanimated CSS.
        page.goto(BASE+'/site-operations.html',wait_until='networkidle')
        require(page.locator('.jp-garden').evaluate("e=>getComputedStyle(e).pointerEvents")=='none','Garden blocks controls')
        require(page.evaluate("matchMedia('(prefers-reduced-motion:reduce)').matches"),'Reduced motion not exercised')
        ctx.close()
    finally: server.terminate();server.wait()
    OUT.mkdir(parents=True,exist_ok=True)
    (OUT/'results.json').write_text(json.dumps({'baseline':BASELINE,'matrix':results,'widths':WIDTHS,'checks':['shared shell','mobile menu / Escape','active routes','no horizontal overflow','no JS / asset errors','AA serious / critical axe','clipboard / removal','print depths','reduced motion','project context']},indent=2))
    print('BOTANICAL_THEME_PASS',len(results),'route/viewport combinations')

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--skip-before',action='store_true');args=parser.parse_args()
    with sync_playwright() as pw:
        browser=pw.chromium.launch(**browser_options())
        try:
            if not args.skip_before:before(browser)
            after(browser)
        finally:browser.close()
