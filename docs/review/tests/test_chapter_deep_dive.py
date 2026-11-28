import time,sys,os
from playwright.sync_api import sync_playwright
O="./"
refs=sys.argv[1:] or ["Acts|13","Matthew|26","Romans|8","Genesis|1","Psalms|23","1 Kings|18"]
with sync_playwright() as p:
    b=p.chromium.launch(args=["--no-sandbox"])
    for r in refs:
        bk,ch=r.split("|")
        for w,h in [(390,844)]:
            c=b.new_context(viewport={"width":w,"height":h},has_touch=True); c.add_init_script("localStorage.setItem('verbo.welcomed','1')")
            pg=c.new_page(); errs=[]; pg.on("pageerror",lambda e: errs.append(str(e))); pg.on("console",lambda m: errs.append(m.text) if m.type=="error" else None)
            pg.goto(f"http://localhost:8110/#v={bk} {ch}:1"); time.sleep(2.5)
            if r=="Romans|8": pg.evaluate("S.highlights['Romans 8:28']={c:'gold',t:Date.now()};S.highlights['Romans 8:1']={c:'blue',t:Date.now()};S.bookmarks.push({ref:'Romans 8:38',t:Date.now()});save()")
            pg.evaluate(f"ui.sel=null;A.chOv({{dataset:{{b:'{bk}',c:'{ch}'}}}})"); time.sleep(6)
            info=pg.evaluate("""(()=>({tabs:[...document.querySelectorAll('.cov-tabs button')].map(b=>b.textContent),
              secs:[...document.querySelectorAll('.cov-body>section')].map(s=>s.id+':'+[...s.querySelectorAll('.cov-h3')].map(x=>x.textContent).join('/')),
              glance:[...document.querySelectorAll('.cov-glance dt')].map(x=>x.textContent).join(','),
              xrefs:document.querySelectorAll('#cov-con [data-action=peekRef]').length, par:document.querySelectorAll('#cov-con [data-action=parOpen]').length,
              map:!!document.querySelector('.cov-map svg'), skel:document.querySelectorAll('.cov .skel').length, h:document.querySelector('#main').scrollHeight}))()""")
            print(r, info, 'errs', errs[:2])
            tag=r.replace('|','').replace(' ','')
            for sid in ['cov-set','cov-con','cov-q']:
                if pg.evaluate(f"!!document.getElementById('{sid}')"):
                    pg.evaluate(f"document.getElementById('{sid}').scrollIntoView()"); time.sleep(.5); pg.screenshot(path=O+f"{tag}-{sid}.png")
            c.close()
    b.close()
