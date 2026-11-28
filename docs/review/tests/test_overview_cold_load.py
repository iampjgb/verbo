import time
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b=p.chromium.launch(args=["--no-sandbox"])
    c=b.new_context(viewport={"width":390,"height":844},has_touch=True); c.add_init_script("localStorage.setItem('verbo.welcomed','1')")
    def slow(route):
        u=route.request.url
        if '/bible/' in u and not '/kjv/' in u: time.sleep(2)
        route.continue_()
    c.route("**/*",slow)
    pg=c.new_page(); errs=[]; pg.on("pageerror",lambda e: errs.append(str(e)))
    # go straight to the overview from Today, no reader visit
    pg.goto("http://localhost:8110/"); time.sleep(1.5)
    pg.evaluate("S.reading.book='Genesis';S.reading.ch=1;A.chOv({dataset:{b:'Genesis',c:'1'}})"); time.sleep(.5)
    pg.screenshot(path="./cold-top.png")
    time.sleep(14)
    pg.evaluate("document.querySelectorAll('#wk-com details.ex-sec').forEach(d=>d.open=true)"); time.sleep(.3)
    print('skel left in commentary:',pg.evaluate("document.querySelectorAll('#wk-com .skel').length"),'| henry len:',pg.evaluate("(document.querySelector('#wk-com .cm-body')||{innerText:''}).innerText.length"),'| people section:',pg.evaluate("!!document.getElementById('wk-ppl')"))
    pg.evaluate("document.getElementById('wk-com').scrollIntoView()"); time.sleep(.4)
    pg.screenshot(path="./cold-com.png")
    print('errs',errs)
    b.close()
