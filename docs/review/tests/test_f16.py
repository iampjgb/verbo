import time
from playwright.sync_api import sync_playwright
U="http://localhost:8110/"; O="./"
init="localStorage.setItem('verbo.welcomed','1');localStorage.setItem('verbo.packsPause',String(Date.now()))"
with sync_playwright() as p:
    b=p.chromium.launch(args=["--no-sandbox"])
    c=b.new_context(viewport={"width":390,"height":844},has_touch=True,color_scheme="light"); c.add_init_script(init)
    pg=c.new_page(); errs=[]; pg.on("pageerror",lambda e: errs.append(str(e)))
    pg.goto(U+"#v=John 3:1"); time.sleep(3); pg.evaluate("ui.sel=null;refresh()"); time.sleep(.5)
    pg.click('.reading .v[data-key="John 3:16"]'); time.sleep(.6)
    print('16 popup before:',pg.evaluate("document.querySelector('#vpop [data-action=bm]').innerText.trim()"))
    pg.click('#vpop [data-action=bm]'); time.sleep(1)
    pg.evaluate("ui.sel='John 3:16';refresh()"); time.sleep(.8)
    print('16 popup after save:',pg.evaluate("(()=>{const b=document.querySelector('#vpop [data-action=bm]');return b?b.innerText.trim()+' pressed='+b.getAttribute('aria-pressed'):'no popup'})()"))
    pg.evaluate("S.highlights['John 3:16']={c:'blue',t:Date.now()};ui.sel=null;save();refresh()"); time.sleep(.8)
    print('16 verse:',pg.evaluate("(()=>{const v=document.querySelector('.reading .v[data-key=\"John 3:16\"]');return v.className+' | describedby='+v.getAttribute('aria-describedby')})()"))
    pg.evaluate("document.querySelector('.reading .v[data-key=\"John 3:16\"]').scrollIntoView({block:'center'})"); time.sleep(.4); pg.screenshot(path=O+"f16-marker.png")
    # copy unaffected
    print('16 text still clean:',pg.evaluate("document.querySelector('.reading .v[data-key=\"John 3:16\"]').innerText.slice(0,40)"))
    # 26 mark read: jump to end immediately
    pg.goto(U+"#v=Philemon 1:25"); time.sleep(4)
    print('26 read after 4 s jump:',pg.evaluate("!!(S.chRead||{})[Object.keys(S.chRead||{}).find(k=>k.startsWith(String(BOOKS.findIndex(b=>b.n==='Philemon'))))]"),pg.evaluate("Object.keys(S.chRead||{}).length"))
    time.sleep(36)
    print('26 after 40 s:',pg.evaluate("Object.keys(S.chRead||{}).length"),'toast',pg.evaluate("[...document.querySelectorAll('.toast,#toast')].map(x=>x.innerText).join('|')"))
    # 20 auto theme
    pg.evaluate("nav('settings')"); time.sleep(1)
    print('20 settings buttons:',pg.evaluate("[...document.querySelectorAll('[data-action=setTheme]')].map(b=>b.innerText.trim()+(b.classList.contains('on')?'*':''))"),'themeAuto',pg.evaluate("S.themeAuto"))
    pg.emulate_media(color_scheme="dark"); time.sleep(1)
    print('20 after OS dark:',pg.evaluate("S.theme"),pg.evaluate("document.documentElement.dataset.theme"))
    pg.click('[data-action=setTheme][data-v=light]'); time.sleep(.5); pg.emulate_media(color_scheme="light"); time.sleep(.3); pg.emulate_media(color_scheme="dark"); time.sleep(.5)
    print('20 manual light stays:',pg.evaluate("S.theme"),pg.evaluate("S.themeAuto"))
    pg.click('[data-action=setTheme][data-v=auto]'); time.sleep(.5); print('20 back to auto:',pg.evaluate("S.theme"),pg.evaluate("S.themeAuto"))
    pg.screenshot(path=O+"f16-settings.png")
    print('errs',errs[:3]); b.close()
