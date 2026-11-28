import time
from playwright.sync_api import sync_playwright
U="http://localhost:8110/"
init="localStorage.setItem('verbo.welcomed','1');localStorage.setItem('verbo.packsPause',String(Date.now()))"
with sync_playwright() as p:
    b=p.chromium.launch(args=["--no-sandbox"])
    c=b.new_context(viewport={"width":390,"height":844},has_touch=True); c.add_init_script(init)
    pg=c.new_page(); errs=[]; pg.on("pageerror",lambda e: errs.append(str(e)))
    pg.goto(U+"#v=John 3:1"); time.sleep(3); pg.evaluate("ui.sel=null;refresh()"); time.sleep(.8)
    print('13 pill tucked mid-chapter:',pg.evaluate("document.querySelector('.rfloat').classList.contains('rf-tuck')"))
    pg.evaluate("const c=document.querySelector('.reader-col');c.scrollTop=c.scrollHeight"); time.sleep(.8)
    print('13 pill at end shown:',not pg.evaluate("document.querySelector('.rfloat').classList.contains('rf-tuck')"),'| endnav:',pg.evaluate("[...document.querySelectorAll('.ch-endnav button')].map(b=>b.innerText.trim())"))
    pg.screenshot(path="./f14-endnav.png")
    pg.click('.ch-endnav .btn.primary'); time.sleep(1.5); print('   next ->',pg.evaluate("S.reading.book+' '+S.reading.ch"))
    # 14 targets
    small=pg.evaluate("""(()=>{const s=[];document.querySelectorAll('.rtop button,.rtop .pill').forEach(b=>{const r=b.getBoundingClientRect();r.width&&(r.height<44||r.width<44)&&s.push((b.dataset.action||b.className)+':'+Math.round(r.width)+'x'+Math.round(r.height))});return s})()""")
    print('14 small header targets:',small)
    pg.evaluate("ui.sel=null;refresh()"); time.sleep(.5)
    pg.click('.reading .v[data-key="John 4:3"]'); time.sleep(.6); pg.click('#vpop [data-action="hlToggle"]'); time.sleep(.8)
    print('14 swatch size:',pg.evaluate("[...document.querySelectorAll('[data-action=hl][data-c]')].filter(x=>x.offsetParent).slice(0,2).map(x=>Math.round(x.getBoundingClientRect().width)+'x'+Math.round(x.getBoundingClientRect().height))"))
    pg.screenshot(path="./f14-swatches.png")
    # 10 picker and search
    pg.goto(U+"#v=John 3:1"); time.sleep(2); pg.evaluate("ui.sel=null;refresh()"); time.sleep(.5)
    pg.click('.rtop .pill >> nth=0'); time.sleep(.8)
    for q in ["Jhon","Mathew 5","Revelations 21","Psalm 23","Jn 3"]:
        pg.fill('#pkQ',q); time.sleep(.5); print('10 picker',q,'->',pg.evaluate("(document.querySelector('#pkSug .pk-sug.first')||{innerText:'NONE'}).innerText.replace(/\\n/g,' ')"))
    pg.fill('#pkQ','Mathew 5'); pg.keyboard.press('Enter'); time.sleep(1); print('   Enter ->',pg.evaluate("S.reading.book+' '+S.reading.ch"))
    print('10 gsSearch Jhon 3:16:',pg.evaluate("JSON.stringify(gsSearch('Jhon 3:16')[0]).slice(0,160)"))
    print('10 gsSearch Paul 2 (no false hit):',pg.evaluate("JSON.stringify(gsSearch('Paul 2')[0]||null).slice(0,80)"), '| fuzzy Mark:',pg.evaluate("(fuzzyBook('Mrak')||{}).n"),'| fuzzy Job vs John?',pg.evaluate("(fuzzyBook('Jon')||{n:null}).n"))
    # 4 dialog trap
    c.close(); c=b.new_context(viewport={"width":1366,"height":900}); c.add_init_script(init); pg=c.new_page(); pg.goto(U+"#v=John 3:1"); time.sleep(3)
    pg.focus('.pill[data-action=trOpen]'); pg.keyboard.press('Enter'); time.sleep(.8)
    out=0
    for i in range(40):
        pg.keyboard.press('Tab'); out+= pg.evaluate("!document.getElementById('modalBg').contains(document.activeElement)")
    print('4 Tabs that left the dialog:',out,'| app inert:',pg.evaluate("document.getElementById('app').inert"))
    pg.keyboard.press('Escape'); time.sleep(.4); print('   after close inert:',pg.evaluate("document.getElementById('app').inert"),'focus:',pg.evaluate("document.activeElement.dataset.action"))
    print('errs',errs[:3]); b.close()
