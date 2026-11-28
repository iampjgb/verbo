import time
from playwright.sync_api import sync_playwright
U="http://localhost:8110/"
init="localStorage.setItem('verbo.welcomed','1');localStorage.setItem('verbo.packsAuto','done');localStorage.setItem('verbo.packsRemoved','[\"words\",\"dict\",\"places\",\"mh\",\"com\"]')"
with sync_playwright() as p:
    b=p.chromium.launch(args=["--no-sandbox"])
    def ov(bk,ch,w=390,h=844,off=False,shot=None):
        c=b.new_context(viewport={"width":w,"height":h},has_touch=True); c.add_init_script(init)
        pg=c.new_page(); errs=[]; pg.on("pageerror",lambda e: errs.append(str(e)))
        pg.goto(U+f"#v={bk} {ch}:1"); time.sleep(2.5)
        if off: c.set_offline(True)
        pg.evaluate(f"ui.sel=null;A.chOv({{dataset:{{b:'{bk}',c:'{ch}'}}}})"); time.sleep(5)
        return c,pg,errs
    for bk,ch in [("Matthew","13"),("Isaiah","53"),("Psalms","119")]:
        c,pg,errs=ov(bk,ch)
        print(bk,ch,'outline:',pg.evaluate("[...document.querySelectorAll('#cov-outline .cov-oi')].slice(0,4).map(x=>x.innerText.replace(/\\n/g,' | ')).join(' || ')"),'| meta:',pg.evaluate("(document.querySelector('#cov-outline .cov-meta')||{}).textContent"),'errs',errs[:2])
        if bk=="Psalms": pg.evaluate("document.getElementById('cov-outline').scrollIntoView()"); time.sleep(.4); pg.screenshot(path="./f13-ps119-outline.png")
        c.close()
    for bk,ch in [("Exodus","1"),("Matthew","28"),("Obadiah","1"),("Genesis","1"),("Revelation","22")]:
        c,pg,errs=ov(bk,ch)
        print(bk,ch,'prev/next:',pg.evaluate("[...document.querySelectorAll('.cov-pn')].map(x=>x.innerText.trim())"))
        c.close()
    c,pg,errs=ov("Acts","13")
    pg.evaluate("document.querySelectorAll('#cov-words details').forEach(d=>d.open=true)"); time.sleep(.5)
    print('words summaries:',pg.evaluate("[...document.querySelectorAll('#cov-words summary')].map(x=>x.innerText.trim())"),'| codes visible:',pg.evaluate("[...document.querySelectorAll('#cov-words .gd-word .s')].some(x=>x.offsetParent)"),'| chips shown:',pg.evaluate("[...document.querySelectorAll('#cov-words .chips')].map(c=>[...c.children].filter(x=>x.offsetParent&&x.tagName=='BUTTON').length)"))
    print('questions h2:',pg.evaluate("(document.querySelector('#cov-q h2')||{}).textContent"),'| sources items:',pg.evaluate("document.querySelectorAll('#wk-src li').length"))
    pg.evaluate("document.getElementById('cov-words').scrollIntoView()"); time.sleep(.4); pg.screenshot(path="./f13-words.png")
    c.close()
    c,pg,errs=ov("Jude","1",off=True)
    print('offline Jude 1: off msgs',pg.evaluate("document.querySelectorAll('.cov-off').length"),'skel',pg.evaluate("document.querySelectorAll('.cov .skel').length"),'errs',errs[:2])
    pg.screenshot(path="./f13-offline.png",full_page=True); c.close()
    # F10 bar
    c=b.new_context(viewport={"width":390,"height":844}); c.add_init_script("localStorage.setItem('verbo.welcomed','1')")
    pg=c.new_page(); pg.goto(U); time.sleep(14)
    print('bar:',pg.evaluate("(document.querySelector('.cov-bar')||{}).innerText"))
    pg.screenshot(path="./f13-bar.png")
    pg.click('.cov-bar button'); time.sleep(1)
    print('after Not now: pause set',pg.evaluate("!!localStorage.getItem('verbo.packsPause')"),'toast',pg.evaluate("[...document.querySelectorAll('.toast,#toast')].map(x=>x.innerText).join('|')"))
    c.close(); b.close()
