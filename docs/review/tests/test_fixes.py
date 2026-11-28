import time,json
from playwright.sync_api import sync_playwright
import sys
U=sys.argv[1] if len(sys.argv)>1 else "http://localhost:8110/"; OUT="./"
AXE="node_modules/axe-core/axe.min.js"
res={}
def ctx(b,w=390,h=844,welcomed=True):
    c=b.new_context(viewport={"width":w,"height":h},has_touch=w<900)
    if welcomed: c.add_init_script("try{localStorage.setItem('verbo.welcomed','1')}catch(e){}")
    return c
with sync_playwright() as p:
    b=p.chromium.launch(args=["--no-sandbox"])
    errs=[]
    # F1 + F2 + F3 phone
    c=ctx(b); pg=c.new_page(); pg.on("pageerror",lambda e: errs.append(str(e)))
    pg.goto(U+"#v=John 3:16"); time.sleep(2.5)
    pg.evaluate("ui.sel=null;refresh()"); time.sleep(.5)
    pg.click('.reading .v[data-key="John 3:3"]'); time.sleep(.6)
    res['vpop']=pg.evaluate("!!document.getElementById('vpop')")
    pg.click('#vpop [data-action="bm"]'); time.sleep(.8)
    res['F1_bookmarks']=pg.evaluate("S.bookmarks.slice(0,2)")
    pg.evaluate("nav('bookmarks')") if pg.evaluate("typeof PAGES.bookmarks")=="function" else None
    time.sleep(1); pg.screenshot(path=OUT+"f1-bookmarks.png")
    res['F1_page_err']=pg.evaluate("document.body.innerText.includes('could not open')")
    # F2 highlight
    pg.goto(U+"#v=John 3:16"); time.sleep(2); pg.evaluate("ui.sel=null;refresh()"); time.sleep(.4)
    pg.click('.reading .v[data-key="John 3:5"]'); time.sleep(.6)
    pg.click('#vpop [data-action="hlToggle"]'); time.sleep(.8)
    sw=pg.locator('[data-action="hl"][data-c]:not([data-c="none"])')
    res['F2_swatches_visible']=sw.count()>0 and sw.first.is_visible()
    pg.screenshot(path=OUT+"f2-highlight.png")
    if res['F2_swatches_visible']:
        sw.first.click(); time.sleep(.5)
    res['F2_highlight_saved']=pg.evaluate("JSON.stringify(S.highlights['John 3:5']||null)")
    # F2 note
    pg.goto(U+"#v=John 3:16"); time.sleep(2); pg.evaluate("ui.sel=null;ui.stOpen=false;refresh()"); time.sleep(.4)
    pg.click('.reading .v[data-key="John 3:7"]'); time.sleep(.6)
    pg.click('#vpop [data-action="noteModal"]'); time.sleep(.9)
    res['F2_note_editor_visible']=pg.locator('#qnText').count()>0 and pg.locator('#qnText').is_visible()
    res['F2_note_focused']=pg.evaluate("document.activeElement&&document.activeElement.id")
    pg.screenshot(path=OUT+"f2-note.png")
    # F3
    res['F3_verse_label']=pg.evaluate("document.querySelector('.reading .v').getAttribute('aria-label')")
    # corrupt bookmark cleanup
    c.close()
    c=ctx(b); pg=c.new_page(); pg.on("pageerror",lambda e: errs.append(str(e)))
    pg.goto(U); time.sleep(1.5)
    pg.evaluate("S.bookmarks.unshift({t:Date.now()});save()")
    pg.reload(); time.sleep(2)
    res['F1_cleanup']=pg.evaluate("S.bookmarks.every(x=>x.ref)")
    c.close()
    # F4 Strong's (desktop)
    c=ctx(b,1366,900); pg=c.new_page(); pg.on("pageerror",lambda e: errs.append(str(e)))
    pg.goto(U); time.sleep(2)
    for key in ["G25","H430","G3056"]:
        pg.evaluate("ui.bsb='';nav('search')"); time.sleep(.8)
        pg.fill(".page input",key); pg.keyboard.press("Enter"); time.sleep(5)
        t=pg.evaluate("document.querySelector('.page').innerText")
        i=t.find('verse'); res['F4_'+key]=('is not used' not in t, t[t.find('Verses with')-40 if 'Verses with' in t else 0:][:90].replace('\n',' '))
    pg.screenshot(path=OUT+"f4-G25.png")
    # F5 ends
    pg.goto(U+"#v=Genesis 1:1"); time.sleep(2)
    pg.evaluate("adjChapter(-1)"); time.sleep(.3)
    res['F5_start']=pg.evaluate("[...document.querySelectorAll('.toast,#toast')].map(x=>x.innerText).join('|')")
    pg.goto(U+"#v=Revelation 22:1"); time.sleep(2)
    pg.evaluate("adjChapter(1)"); time.sleep(.3)
    res['F5_end']=pg.evaluate("[...document.querySelectorAll('.toast,#toast')].map(x=>x.innerText).join('|')")
    # F6 pills + modal
    res['F6_pill']=pg.evaluate("[...document.querySelectorAll('.pill[data-action=pickOpen],.pill[data-action=trOpen]')].map(x=>[x.getAttribute('aria-label'),x.innerText.trim()])")
    pg.focus('.pill[data-action=trOpen]'); pg.keyboard.press("Enter"); time.sleep(.6)
    res['F6_modal']=pg.evaluate("[document.getElementById('modal').getAttribute('aria-label'), document.getElementById('modal').contains(document.activeElement)]")
    pg.keyboard.press("Escape"); time.sleep(.4)
    res['F6_focus_return']=pg.evaluate("document.activeElement&&document.activeElement.dataset.action")
    pg.add_script_tag(path=AXE)
    ax=pg.evaluate("axe.run().then(r=>r.violations.map(v=>v.id+':'+v.nodes.length))")
    res['axe_reader_after']=ax
    c.close()
    # F7 welcome
    c=ctx(b,1366,900,welcomed=False); pg=c.new_page(); pg.goto(U); time.sleep(2)
    res['F7_text']=pg.evaluate("(document.querySelector('.wel-scrim')||{}).innerText")
    pg.keyboard.press("Escape"); time.sleep(.3)
    res['F7_welcomed']=pg.evaluate("localStorage.getItem('verbo.welcomed')")
    c.close()
    res['page_errors']=errs
    b.close()
for k,v in res.items(): print(k,'=>',v)
