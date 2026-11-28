import time
from playwright.sync_api import sync_playwright
U="http://localhost:8110/"; O="./"
init="localStorage.setItem('verbo.welcomed','1');localStorage.setItem('verbo.packsPause',String(Date.now()))"
with sync_playwright() as p:
    b=p.chromium.launch(args=["--no-sandbox"])
    for w,h in [(390,844),(1366,900)]:
        c=b.new_context(viewport={"width":w,"height":h},has_touch=w<900); c.add_init_script(init)
        pg=c.new_page(); errs=[]; pg.on("pageerror",lambda e: errs.append(str(e)))
        for bk,ch in [("Romans",8),("Matthew",13),("Psalms",119)]:
            pg.goto(U+f"#v={bk} {ch}:1"); time.sleep(2.5)
            pg.evaluate(f"ui.sel=null;A.chOv({{dataset:{{b:'{bk}',c:'{ch}'}}}})"); time.sleep(4)
            pg.evaluate("document.getElementById('cov-outline').scrollIntoView()"); time.sleep(.3)
            st0=pg.evaluate("document.getElementById('main').scrollTop")
            pg.click('#cov-outline .cov-oi >> nth=1'); time.sleep(1.5)
            info=pg.evaluate("({page:ui.page,title:(document.querySelector('#modal .modal-h h2')||{}).textContent,label:(document.querySelector('.covs-lbl')||{}).textContent,verses:document.querySelectorAll('.covs-v').length,gaps:document.querySelectorAll('.covs-gap').length,mh:!!document.querySelector('.covs-mh'),focusIn:document.getElementById('modal').contains(document.activeElement)})")
            print(w,bk,ch,info)
            if w==390 and bk in("Romans","Matthew"): pg.screenshot(path=O+f"f15-{bk}-sheet.png")
            pg.click('#modal [data-action=covSecStep][data-d="1"]'); time.sleep(1); print('   next ->',pg.evaluate("document.querySelector('#modal .modal-h h2').textContent"))
            pg.keyboard.press('Escape'); time.sleep(.6)
            print('   closed:',not pg.evaluate("document.getElementById('modalBg').classList.contains('show')"),'page',pg.evaluate("ui.page"),'scroll kept',abs(pg.evaluate("document.getElementById('main').scrollTop")-st0)<5,'focus back on row:',pg.evaluate("document.activeElement.classList.contains('cov-oi')"))
        # read in context
        pg.click('#cov-outline .cov-oi >> nth=0'); time.sleep(1.2); pg.click('#modal [data-action=covRead]'); time.sleep(1.5)
        print('   read in context ->',pg.evaluate("ui.page+' '+S.reading.book+' '+S.reading.ch"),'vpop',pg.evaluate("!!document.getElementById('vpop')"))
        # key verse + notes rows
        pg.evaluate("S.highlights['Romans 8:28']={c:'gold',t:Date.now()};save();A.chOv({dataset:{b:'Romans',c:'8'}})"); time.sleep(3)
        pg.evaluate("document.getElementById('wk-key').scrollIntoView()"); time.sleep(.3)
        pg.click('#wk-key [data-action=covSec]'); time.sleep(1); print('   key verse sheet:',pg.evaluate("(document.querySelector('#modal .modal-h h2')||{}).textContent"),'nav buttons',pg.evaluate("document.querySelectorAll('#modal [data-action=covSecStep]').length")); pg.keyboard.press('Escape'); time.sleep(.4)
        pg.evaluate("document.getElementById('cov-q').scrollIntoView()"); time.sleep(.3)
        pg.click('#cov-q [data-action=covSec]'); time.sleep(1); print('   note row sheet:',pg.evaluate("(document.querySelector('#modal .modal-h h2')||{}).textContent")); pg.keyboard.press('Escape')
        if w>900:
            pg.click('#cov-outline .cov-oi >> nth=0'); time.sleep(1); pg.screenshot(path=O+"f15-desktop.png")
            pg.add_script_tag(path="node_modules/axe-core/axe.min.js"); print('   axe sheet:',pg.evaluate("axe.run(document.getElementById('modalBg')).then(r=>r.violations.map(v=>v.id+':'+v.nodes.length))"))
        print('errs',errs[:3]); c.close()
    b.close()
