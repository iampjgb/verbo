import time,sys
from playwright.sync_api import sync_playwright
O="./out/"
import os; os.makedirs(O,exist_ok=True)
with sync_playwright() as p:
    b=p.chromium.launch(args=["--no-sandbox"])
    def page(w,h,dark=False):
        c=b.new_context(viewport={"width":w,"height":h},has_touch=w<900,color_scheme="dark" if dark else "light"); c.add_init_script("localStorage.setItem('verbo.welcomed','1')")
        pg=c.new_page(); errs=[]; pg.on("pageerror",lambda e: errs.append(str(e))); pg.on("console",lambda m: errs.append(m.text) if m.type=="error" else None)
        pg.goto("http://localhost:8110/#v=Romans 8:1"); time.sleep(2.5)
        if dark: pg.evaluate("document.documentElement.dataset.theme='dark'")
        return c,pg,errs
    def ov(pg): pg.evaluate("ui.sel=null;A.chOv({dataset:{b:'Romans',c:'8'}})"); time.sleep(3)
    # 1 outside Claude: no Meaning
    c,pg,errs=page(390,844); ov(pg)
    print('outside: tabs',pg.evaluate("[...document.querySelectorAll('.cov-tabs button')].map(b=>b.textContent)"),'| interpretation text present:',pg.evaluate("/Guard against|Find the meaning|Interpretation/.test(document.querySelector('.cov').innerText)"))
    for i in range(4):
        pg.screenshot(path=O+f"phone-{i}.png"); pg.evaluate("document.querySelector('#main').scrollTop+=720"); time.sleep(.5)
    pg.click('[data-cov-go=cov-q]'); time.sleep(.8); pg.click('details.cov-q>summary'); time.sleep(.5); pg.screenshot(path=O+"phone-questions.png")
    pg.click('[data-cov-go=wk-com]'); time.sleep(.8); pg.click('#wk-com details.ex-sec>summary >> nth=0'); time.sleep(.8); pg.screenshot(path=O+"phone-henry-open.png")
    print('errors',errs[:3]); c.close()
    # 2 inside Claude (simulated): button
    c,pg,errs=page(390,844); pg.evaluate("SAMPLE=SAMPLE||{}"); ov(pg)
    print('inside: button:',pg.evaluate("!!document.querySelector('#cov-ai [data-action=genStudy]')"),'tabs',pg.evaluate("[...document.querySelectorAll('.cov-tabs button')].map(b=>b.textContent)"))
    pg.evaluate("document.getElementById('cov-ai').scrollIntoView()"); time.sleep(.4); pg.screenshot(path=O+"phone-ai-button.png")
    # 3 generated study present
    pg.evaluate("S.genStudies=S.genStudies||{};S.genStudies[normRef('Romans 8')]=Object.assign({},STUDIES['Romans 8:28'],{t:Date.now()});save();A.chOv({dataset:{b:'Romans',c:'8'}})"); time.sleep(2)
    print('generated: meaning shown:',pg.evaluate("(document.getElementById('cov-ai')||{innerText:''}).innerText.slice(0,160)"))
    pg.evaluate("document.getElementById('cov-ai').scrollIntoView()"); time.sleep(.4); pg.screenshot(path=O+"phone-ai-written.png")
    print('errors',errs[:3]); c.close()
    # desktop + dark
    c,pg,errs=page(1366,900); ov(pg); pg.screenshot(path=O+"desk-0.png"); pg.screenshot(path=O+"desk-full.png",full_page=True); print('desk errors',errs[:3]); c.close()
    c,pg,errs=page(390,844,True); ov(pg); pg.screenshot(path=O+"phone-dark.png")
    pg.add_script_tag(path="node_modules/axe-core/axe.min.js")
    print('axe dark', pg.evaluate("axe.run(document.querySelector('.cov')).then(r=>r.violations.map(v=>v.id+':'+v.nodes.length))"))
    c.close()
    c,pg,errs=page(390,844); ov(pg); pg.add_script_tag(path="node_modules/axe-core/axe.min.js")
    print('axe light', pg.evaluate("axe.run(document.querySelector('.cov')).then(r=>r.violations.map(v=>v.id+':'+v.nodes.length))")); c.close()
    b.close()
