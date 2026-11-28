import time,sys
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b=p.chromium.launch(args=["--no-sandbox"])
    c=b.new_context(viewport={"width":390,"height":844}); c.add_init_script("localStorage.setItem('verbo.welcomed','1');localStorage.setItem('verbo.packsPause',String(Date.now()))")
    pg=c.new_page(); pg.goto("http://localhost:8110/"); time.sleep(2)
    for bk,ch in [("Psalms",22),("Acts",13),("John",13),("2 Chronicles",18),("Isaiah",53)]:
        pg.evaluate(f"A.chOv({{dataset:{{b:'{bk}',c:'{ch}'}}}})"); time.sleep(5)
        print(bk,ch,'| parallels:',pg.evaluate("[...document.querySelectorAll('#cov-con [data-action=parOpen] .cov-t')].map(x=>x.textContent)"),'| xrefs:',pg.evaluate("[...document.querySelectorAll('#cov-con [data-action=peekRef]')].map(x=>x.dataset.ref)"))
    b.close()
