import time
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b=p.chromium.launch(args=["--no-sandbox"])
    c=b.new_context(viewport={"width":390,"height":844}); c.add_init_script("localStorage.setItem('verbo.welcomed','1')")
    pg=c.new_page(); errs=[]; pg.on("pageerror",lambda e: errs.append(str(e)))
    toasts=[]
    pg.goto("http://localhost:8110/"); 
    for i in range(40):
        time.sleep(3)
        t=pg.evaluate("[...document.querySelectorAll('.toast,#toast')].map(x=>x.innerText).join('|')")
        t and t not in toasts and toasts.append(t)
        st=pg.evaluate("JSON.stringify({s:PWA.status,b:Object.keys(PWA.busy),k:localStorage.getItem('verbo.packsAuto')})")
        if i%5==0: print(i*3,'s',st)
        if '"k":"done"' in st: print('DONE at',i*3,'s', st); break
    print('toasts',toasts); 
    # remove one and reload: must not come back
    pg.evaluate("A.pwaRemove({dataset:{id:'mh'}})"); time.sleep(3); pg.reload(); time.sleep(20)
    print('after remove+reload:',pg.evaluate("JSON.stringify({mh:PWA.status.mh,busy:Object.keys(PWA.busy),rm:localStorage.getItem('verbo.packsRemoved')})"))
    print('errs',errs)
    b.close()
