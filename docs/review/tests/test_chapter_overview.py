import time,sys
from playwright.sync_api import sync_playwright
O="./"
REF=sys.argv[1] if len(sys.argv)>1 else "Romans|8"
bk,chn=REF.split("|")
with sync_playwright() as p:
    b=p.chromium.launch(args=["--no-sandbox"])
    for name,w,h in [("phone",390,844),("desk",1366,900)]:
        c=b.new_context(viewport={"width":w,"height":h},has_touch=w<900); c.add_init_script("localStorage.setItem('verbo.welcomed','1')")
        pg=c.new_page(); errs=[]; pg.on("pageerror",lambda e: errs.append(str(e))); pg.on("console",lambda m: errs.append(m.text) if m.type=="error" else None)
        pg.goto(f"http://localhost:8110/#v={bk} {chn}:1"); time.sleep(2.5)
        pg.evaluate(f"ui.sel=null;A.chOv({{dataset:{{b:'{bk}',c:'{chn}'}}}})"); time.sleep(3)
        tag=f"{name}-{bk}{chn}".replace(' ','')
        print(name,'height',pg.evaluate("document.querySelector('#main').scrollHeight"),'cov:',pg.evaluate("!!document.querySelector('.cov')"),'tabs:',pg.evaluate("[...document.querySelectorAll('.cov-tabs button')].map(b=>b.textContent)"))
        pg.screenshot(path=O+f"{tag}-0.png")
        if name=="phone":
            pg.evaluate("document.querySelector('#main').scrollTop=700"); time.sleep(.6); pg.screenshot(path=O+f"{tag}-1.png")
            pg.click('[data-cov-go=wk-com]'); time.sleep(1); pg.screenshot(path=O+f"{tag}-2.png")
            oi=pg.locator('.cov-oi[data-action=covGo]')
            if oi.count()>2:
                pg.evaluate("document.querySelector('#main').scrollTop=0"); oi.nth(2).click(); time.sleep(1.5)
                print('outline tap ->', pg.evaluate("[ui.page,S.reading.book,S.reading.ch,ui.sel]"), 'vpop:', pg.evaluate("!!document.getElementById('vpop')"))
                pg.screenshot(path=O+f"{tag}-3-after-outline-tap.png")
        else:
            pg.screenshot(path=O+f"{tag}-full.png",full_page=True)
        print('errors',errs[:3])
        c.close()
    b.close()
