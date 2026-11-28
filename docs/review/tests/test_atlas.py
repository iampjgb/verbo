"""Atlas: Follow the Journey (Paul's first journey). Run with a local server on port 8110 from the repo root:
python3 -m http.server 8110   then   python3 docs/review/tests/test_atlas.py
"""
import time, sys
from playwright.sync_api import sync_playwright
U = "http://localhost:8110/"
INIT = "localStorage.setItem('verbo.welcomed','1');localStorage.setItem('verbo.packsPause',String(Date.now()))"
fails = []
def ok(cond, msg):
    print(("PASS " if cond else "FAIL ") + msg)
    cond or fails.append(msg)

def open_atlas(pg):
    pg.goto(U + "#v=Acts 14:1"); time.sleep(3)
    pg.evaluate("void jmLoad().catch(()=>{})"); time.sleep(1)
    pg.evaluate("nav('journey',{jmId:'paul1'})"); time.sleep(2)
    pg.click("[data-action=alOpen]"); time.sleep(2.5)

def state(pg):
    return pg.evaluate("""(()=>{const s=document.getElementById('al-svg');return{
      name:(document.querySelector('.al-name')||{}).textContent,
      step:(document.querySelector('.al-step')||{}).textContent,
      done:s.querySelectorAll('.al-leg.done').length, cur:s.querySelectorAll('.al-leg.cur').length,
      todo:s.querySelectorAll('.al-leg.todo').length, curPt:(s.querySelector('.al-pt.cur')||{dataset:{}}).dataset.p,
      tlCur:(document.querySelector('.al-tli.cur .al-tnm')||{}).textContent}})()""")

with sync_playwright() as p:
    b = p.chromium.launch(executable_path="/usr/bin/google-chrome", args=["--no-sandbox"])
    for w, h in [(390, 844), (820, 1180), (1366, 900)]:
        print(f"--- {w}x{h}")
        c = b.new_context(viewport={"width": w, "height": h}, has_touch=w < 900); c.add_init_script(INIT)
        pg = c.new_page(); errs = []; pg.on("pageerror", lambda e: errs.append(str(e)))
        open_atlas(pg)
        ok(pg.evaluate("ui.page") == "atlas", "opens from the journey page")
        st = state(pg)
        ok(st["step"].startswith("Stop 1 of 15") and st["name"].startswith("Antioch"), f"starts at stop 1 ({st['step']})")
        ok(pg.evaluate("document.querySelectorAll('#al-svg .al-leg').length") == 14, "14 route legs drawn")
        ok(pg.evaluate("document.querySelectorAll('#al-svg .al-pt').length") == 10, "10 places marked")
        ok(pg.evaluate("!!document.querySelector('#al-svg image.al-relief')"), "terrain layer present")
        ok(pg.evaluate("document.querySelector('.al-zoom [data-f=\".75\"] svg')!==null"), "zoom-in button has its icon")
        # next / prev
        for _ in range(3): pg.click("#al-ctl [data-action=alStep][data-d='1']"); time.sleep(.2)
        st = state(pg)
        ok(st["step"].startswith("Stop 4") and st["done"] == 2 and st["cur"] == 1 and st["todo"] == 11, f"route progress after 3 steps {st}")
        ok(st["curPt"] == "pap" and "Paphos" in st["tlCur"], "map and timeline follow the stop")
        pg.click("#al-ctl [data-action=alStep][data-d='-1']"); time.sleep(.2)
        ok(state(pg)["step"].startswith("Stop 3"), "previous works")
        ok(pg.evaluate("document.activeElement.id") == "al-name", "focus moves to the stop name")
        # timeline row
        if w < 900: pg.click("#al-grab"); time.sleep(.4)
        ok(w >= 900 or pg.evaluate("document.getElementById('atl').classList.contains('open')"), "sheet opens from the handle")
        pg.click(".al-tli[data-i='8']"); time.sleep(.4)
        st = state(pg)
        ok(st["name"].startswith("Derbe"), "timeline row jumps to Derbe")
        ok(pg.evaluate("document.querySelector('.al-cert').textContent") == "Site uncertain", "Derbe shows Site uncertain")
        ok(pg.evaluate("document.querySelectorAll('#al-svg .al-alt.show').length") == 2, "other proposed Derbe sites shown")
        ok("Kerti" in pg.evaluate("document.querySelector('.al-facts').textContent"), "most likely modern site named")
        ok("pleiades.stoa.org/places/648620" in pg.evaluate("document.querySelector('.al-facts').innerHTML"), "Pleiades link for Derbe")
        # tap a city on the map
        if w < 900: pg.click("#al-grab"); time.sleep(.5)
        box = pg.evaluate("(()=>{const r=document.querySelector('#al-svg .al-pt[data-p=\"sal\"] .al-city').getBoundingClientRect();return[r.x+r.width/2,r.y+r.height/2]})()")
        pg.mouse.click(box[0], box[1]); time.sleep(.4)
        ok(state(pg)["name"].startswith("Salamis"), "tapping a city goes to that stop")
        # keyboard
        if w >= 900:
            pg.keyboard.press("ArrowRight"); time.sleep(.3)
            ok(state(pg)["name"].startswith("Paphos"), "right arrow goes to next stop")
        # play
        pg.evaluate("A.alGo({dataset:{i:'0'}})"); time.sleep(.2)
        pg.click("#al-ctl .al-play"); time.sleep(5)
        ok(state(pg)["step"].startswith("Stop 2"), "play moves to the next stop")
        ok(pg.evaluate("document.querySelector('#al-ctl .al-play').getAttribute('aria-pressed')") == "true", "play button shows pressed")
        pg.click("#al-ctl .al-play"); time.sleep(.2)
        # layout
        if w >= 900:
            ok(abs(pg.evaluate("document.querySelector('.al-side').getBoundingClientRect().width") - 400) < 2, "desktop sidebar 400px")
        else:
            r = pg.evaluate("(()=>{const m=document.getElementById('al-mapwrap').getBoundingClientRect(),s=document.querySelector('.al-side').getBoundingClientRect();return[m.height,s.top,innerHeight]})()")
            ok(r[0] > 250 and r[1] < r[2], f"phone map above sheet {r}")
        # map style
        if w == 1366:
            pg.click("[data-action=alTheme]"); time.sleep(.3)
            ok(pg.evaluate("document.getElementById('atl').classList.contains('t-light')"), "map style switches to plain")
            pg.click("[data-action=alTheme]"); time.sleep(.3)
            ok(pg.evaluate("document.getElementById('atl').classList.contains('t-parch')"), "map style back to old map")
            pg.add_script_tag(path="node_modules/axe-core/axe.min.js")
            v = pg.evaluate("axe.run(document.getElementById('atl'),{rules:{'color-contrast':{enabled:true}}}).then(r=>r.violations.map(v=>v.id+':'+v.nodes.length))")
            ok(not v, f"axe on atlas: {v}")
        # read in context
        pg.click(".al-read"); time.sleep(1.5)
        ok(pg.evaluate("ui.page") == "reader" and pg.evaluate("S.reading.book+' '+S.reading.ch") == "Acts 13", "Read goes to the passage")
        ok(not errs, f"no page errors {errs[:2]}")
        c.close()

    print("--- entry from chapter overview, dark mode, offline")
    c = b.new_context(viewport={"width": 390, "height": 844}, has_touch=True); c.add_init_script(INIT); pg = c.new_page()
    pg.goto(U + "#v=Acts 13:1"); time.sleep(3)
    pg.evaluate("void jmLoad().catch(()=>{})"); time.sleep(1)
    pg.evaluate("ui.sel=null;A.chOv({dataset:{b:'Acts',c:'13'}})"); time.sleep(4)
    ok(pg.evaluate("!!document.querySelector('.al-follow[data-id=paul1]')"), "Acts 13 overview offers Follow the journey")
    pg.evaluate("S.theme='dark';S.themeAuto=false;save()")
    pg.evaluate("A.alOpen({dataset:{id:'paul1'}})"); time.sleep(2.5)
    ok(pg.evaluate("document.getElementById('atl').classList.contains('t-dark')"), "dark mode uses the night map")
    c.close()
    c = b.new_context(viewport={"width": 390, "height": 844}, service_workers="block"); c.add_init_script(INIT); pg = c.new_page()
    pg.route("**/bible/fact/atlas.json", lambda r: r.abort())
    pg.goto(U + "#v=Acts 13:1"); time.sleep(3)
    pg.evaluate("nav('atlas',{atJ:'paul1'})")
    for _ in range(20):
        time.sleep(1)
        if "could not load" in pg.evaluate("document.querySelector('.main').textContent"): break
    ok("could not load" in pg.evaluate("document.querySelector('.main').textContent"), "offline message when atlas data is missing")
    c.close(); b.close()
print("\n" + ("ALL PASS" if not fails else f"{len(fails)} FAILED: {fails}"))
sys.exit(1 if fails else 0)
