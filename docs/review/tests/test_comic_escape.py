import time
from playwright.sync_api import sync_playwright
O="./"
with sync_playwright() as p:
    b=p.chromium.launch(args=["--no-sandbox"])
    c=b.new_context(viewport={"width":390,"height":844},has_touch=True); c.add_init_script("localStorage.setItem('verbo.welcomed','1')")
    pg=c.new_page(); errs=[]; pg.on("pageerror",lambda e: errs.append(str(e)))
    pg.goto("http://localhost:8110/#v=Romans 8:1"); time.sleep(2)
    pg.evaluate("S.reading.tr='BSB';S.reading.view='comic';save();refresh()"); time.sleep(1)
    pg.screenshot(path=O+"F8-comic-empty.png")
    pg.click('.cm-back'); time.sleep(1)
    print('A empty-page button -> view:', pg.evaluate("S.reading.view"), '| verses shown:', pg.evaluate("document.querySelectorAll('.reading .v').length"))
    pg.evaluate("S.reading.view='comic';save();refresh()"); time.sleep(1)
    pg.click('.rtop .pill >> nth=1'); time.sleep(.8)
    pg.screenshot(path=O+"F8-comic-sheet.png")
    pg.click('#pop .cm-back-mi'); time.sleep(1)
    print('B sheet button -> view:', pg.evaluate("S.reading.view"), '| verses shown:', pg.evaluate("document.querySelectorAll('.reading .v').length"))
    print('errors', errs)
    b.close()
