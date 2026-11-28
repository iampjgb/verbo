import time
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b=p.chromium.launch(args=["--no-sandbox"])
    c=b.new_context(viewport={"width":390,"height":844}); c.add_init_script("localStorage.setItem('verbo.welcomed','1');localStorage.setItem('verbo.packsAuto','done');localStorage.setItem('verbo.packsRemoved','[\"words\",\"dict\",\"places\",\"mh\",\"com\"]')")
    pg=c.new_page(); errs=[]; pg.on("pageerror",lambda e: errs.append(str(e)))
    pg.goto("http://localhost:8110/"); time.sleep(3); c.set_offline(True)
    pg.evaluate("A.chOv({dataset:{b:'Ezekiel',c:'37'}})"); time.sleep(6)
    print('offline Ezekiel 37: off msgs',pg.evaluate("document.querySelectorAll('.cov-off').length"),'skel',pg.evaluate("document.querySelectorAll('.cov .skel').length"),'sections',pg.evaluate("[...document.querySelectorAll('.cov-body>section')].map(s=>s.id).join(',')"),'errs',errs[:2])
    pg.screenshot(path="./f13-offline.png")
    b.close()
