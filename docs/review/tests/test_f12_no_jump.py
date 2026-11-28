import time
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b=p.chromium.launch(args=["--no-sandbox"])
    c=b.new_context(viewport={"width":390,"height":844},has_touch=True); c.add_init_script("localStorage.setItem('verbo.welcomed','1');localStorage.setItem('verbo.packsAuto','done');localStorage.setItem('verbo.packsRemoved','[\"words\",\"dict\",\"places\",\"mh\",\"com\"]')")
    def slow(route):
        u=route.request.url
        if '/bible/' in u and '/kjv/' not in u: time.sleep(1.5)
        route.continue_()
    c.route("**/*",slow)
    pg=c.new_page(); pg.goto("http://localhost:8110/"); time.sleep(2)
    pg.evaluate("A.chOv({dataset:{b:'Matthew',c:'26'}})"); time.sleep(1.5)
    print('sections at 1.5 s:',pg.evaluate("[...document.querySelectorAll('.cov-body>section')].map(s=>s.id).join(',')"))
    sid=pg.evaluate("(()=>{const s=document.getElementById('wk-com')||document.querySelector('.cov-body>section:last-child');document.getElementById('main').scrollTop+=s.getBoundingClientRect().top-120;return s.id})()"); time.sleep(.4)
    tops=[]
    for i in range(10):
        tops.append(pg.evaluate(f"Math.round((document.getElementById('{sid}')||{{getBoundingClientRect:()=>({{top:-999}})}}).getBoundingClientRect().top)")); time.sleep(1)
    print('reading',sid,'top over 10 s (should stay near 120):',tops)
    print('sections at end:',pg.evaluate("[...document.querySelectorAll('.cov-body>section')].map(s=>s.id).join(',')"))
    b.close()
