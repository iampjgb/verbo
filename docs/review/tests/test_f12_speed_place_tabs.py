import time,collections
from playwright.sync_api import sync_playwright
U="http://localhost:8110/"
with sync_playwright() as p:
    b=p.chromium.launch(args=["--no-sandbox"])
    init="localStorage.setItem('verbo.welcomed','1');localStorage.setItem('verbo.packsAuto','done');localStorage.setItem('verbo.packsRemoved','[\"words\",\"dict\",\"places\",\"mh\",\"com\"]')"
    c=b.new_context(viewport={"width":390,"height":844},has_touch=True); c.add_init_script(init)
    pg=c.new_page(); errs=[]; pg.on("pageerror",lambda e: errs.append(str(e)))
    reqs=collections.Counter(); pg.on("request",lambda r: reqs.update([r.url.split('8110/')[-1]]) if '/bible/' in r.url else None)
    pg.goto(U+"#v=Acts 13:1"); time.sleep(3); reqs.clear()
    pg.evaluate("window.__m=0;const m0=MOUNT.chapter;MOUNT.chapter=()=>{window.__m++;m0()}")
    pg.evaluate("A.chOv({dataset:{b:'Acts',c:'13'}})"); time.sleep(10)
    print('36 mounts',pg.evaluate("window.__m"),'| max repeats',reqs.most_common(3),'| total',sum(reqs.values()))
    # 38 sticky tabs: scroll down then bars visible
    pg.evaluate("document.getElementById('main').scrollTop=1500"); time.sleep(.5)
    pg.evaluate("document.querySelector('.app').classList.remove('bars-hidden')"); time.sleep(.4)
    print('38 tabs top',pg.evaluate("Math.round(document.querySelector('.cov-tabs').getBoundingClientRect().top)"),'topbar bottom',pg.evaluate("Math.round(document.querySelector('.topbar').getBoundingClientRect().bottom)"))
    pg.screenshot(path="./f12-sticky.png")
    # 39 back keeps place: scroll to Connections, open a parallel, then back
    pg.evaluate("document.getElementById('cov-con').scrollIntoView()"); time.sleep(.8)
    before=pg.evaluate("Math.round(document.getElementById('cov-con').getBoundingClientRect().top)")
    pg.click('#cov-con [data-action=parOpen]'); time.sleep(1.5); print('  page after tap',pg.evaluate("ui.page"))
    pg.evaluate("bkBack()"); time.sleep(2.5)
    after=pg.evaluate("Math.round((document.getElementById('cov-con')||{getBoundingClientRect:()=>({top:-999})}).getBoundingClientRect().top)")
    print('39 in-app back: page',pg.evaluate("ui.page"),'section top before',before,'after',after)
    pg.click('#cov-con [data-action=parOpen]'); time.sleep(1.5); pg.go_back(); time.sleep(2.5)
    print('39 browser back: page',pg.evaluate("ui.page"),'section top',pg.evaluate("Math.round((document.getElementById('cov-con')||{getBoundingClientRect:()=>({top:-999})}).getBoundingClientRect().top)"))
    # 40 map does not change reading position
    pg.evaluate("S.reading.book='Romans';S.reading.ch=8;save();A.chOv({dataset:{b:'Acts',c:'13'}})"); time.sleep(3)
    pg.click('.cov-map'); time.sleep(2)
    print('40 page',pg.evaluate("ui.page"),'reading',pg.evaluate("S.reading.book+' '+S.reading.ch"),'atlas text', pg.evaluate("(document.querySelector('.main').innerText.match(/\\d+ places? in [^\\n]+/)||[''])[0]"))
    pg.evaluate("bkBack()"); time.sleep(2); print('   back from map ->',pg.evaluate("ui.page"), pg.evaluate("(ui.chBook||'')+' '+(ui.chNum||'')"))
    print('errs',errs[:3]); c.close()
    # 37 two tabs
    c=b.new_context(viewport={"width":390,"height":844}); c.add_init_script(init)
    t1=c.new_page(); t1.goto(U+"#v=John 3:1"); time.sleep(3)
    t2=c.new_page(); t2.goto(U+"#v=John 3:1"); time.sleep(3)
    t2.evaluate("S.highlights['John 3:16']={c:'gold',t:Date.now()};save()"); time.sleep(1)
    t1.evaluate("S.bookmarks.push({ref:'John 3:3',t:Date.now()});save()"); time.sleep(1)
    print('37 tab1 sees tab2 highlight:',t1.evaluate("!!S.highlights['John 3:16']"),'| stored has both:',t1.evaluate("(()=>{const s=JSON.parse(localStorage.getItem('biblestudy.v1'));return !!s.highlights['John 3:16']&&s.bookmarks.some(b=>b.ref==='John 3:3')})()"))
    c.close(); b.close()
