"""F20 batch 4: items 11, 12, 21, 25, 27, 28, 29.
Run with a local server on port 8110 from the repo root:
python3 -m http.server 8110   then   python3 docs/review/tests/test_f20_batch4.py [shots]
Takes about 100 seconds. Pass "shots" as the first argument to also write docs/review/screenshots/after/f20-*.png
"""
import time, sys, os
from playwright.sync_api import sync_playwright
U = os.environ.get("VERBO_URL", "http://localhost:8110/")
SHOTS = "shots" in sys.argv[1:]
SHOTDIR = os.environ.get("VERBO_SHOTDIR", os.path.join(os.path.dirname(__file__), "..", "screenshots", "after"))
INIT = ("localStorage.setItem('verbo.welcomed','1');localStorage.setItem('verbo.packsPause',String(Date.now()));"
        "new MutationObserver(()=>{const t=document.getElementById('toast');if(t&&t.textContent&&t.textContent!==window.__lt){window.__lt=t.textContent;(window.__toasts=window.__toasts||[]).push(t.textContent)}})"
        ".observe(document,{subtree:true,childList:true,characterData:true})")
AXE = os.path.join(os.path.dirname(__file__), "..", "..", "..", "node_modules", "axe-core", "axe.min.js")
fails = []
def ok(cond, msg):
    print(("PASS " if cond else "FAIL ") + msg)
    cond or fails.append(msg)
def shot(pg, name):
    if SHOTS:
        os.makedirs(SHOTDIR, exist_ok=True)
        pg.screenshot(path=os.path.join(SHOTDIR, name))
def toasts(pg): return pg.evaluate("window.__toasts||[]")
def newctx(b, w, h, touch=False, sw=True):
    c = b.new_context(viewport={"width": w, "height": h}, has_touch=touch, service_workers="block")
    c.add_init_script(INIT)
    pg = c.new_page(); errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)))
    return c, pg, errs
def lum(rgb):
    def f(v):
        v /= 255
        return v / 12.92 if v <= .03928 else ((v + .055) / 1.055) ** 2.4
    r, g, b = rgb
    return .2126 * f(r) + .7152 * f(g) + .0722 * f(b)
def ratio(a, b):
    la, lb = lum(a), lum(b)
    if la < lb: la, lb = lb, la
    return (la + .05) / (lb + .05)

with sync_playwright() as p:
    b = p.chromium.launch(executable_path="/usr/bin/google-chrome", args=["--no-sandbox"])
    allerrs = []

    # ---------------------------------------------------------------- 12 storage full
    for w, h, t in [(390, 844, True), (1366, 900, False)]:
        print(f"--- #12 storage full {w}x{h}")
        c, pg, errs = newctx(b, w, h, t)
        pg.goto(U + "#v=Romans 8:1"); time.sleep(3)
        pg.evaluate("""(()=>{window.__full=true;const o=Storage.prototype.setItem;
          Storage.prototype.setItem=function(k,v){if(window.__full&&k==='biblestudy.v1')throw new DOMException('full','QuotaExceededError');return o.apply(this,arguments)}})()""")
        ok(pg.evaluate("!document.getElementById('f20-save-warn')"), "no warning before a failed save")
        pg.evaluate("ui.sel='Romans 8:1';A.hl({dataset:{c:'gold'}})"); time.sleep(.4)
        tl = toasts(pg)
        ok(pg.evaluate("!!document.getElementById('f20-save-warn')"), "warning appears after a failed save")
        ok(not any(x == "Highlighted" for x in tl) and any("Not saved" in x for x in tl), f"no success toast, failure text instead {tl}")
        time.sleep(3.5)
        ok(pg.evaluate("document.getElementById('toast').className")  == "toast", "toast is gone after 2 seconds")
        ok(pg.evaluate("!!document.getElementById('f20-save-warn')"), "warning is still there after the toast is gone")
        wt = pg.evaluate("document.getElementById('f20-save-warn').innerText")
        ok("not being saved" in wt and "Export" in wt, "warning says saving failed and offers Export")
        ok(pg.evaluate("document.getElementById('f20-save-warn').getAttribute('role')") == "alert", "warning has role=alert")
        hs = pg.evaluate("[...document.querySelectorAll('#f20-save-warn button')].map(b=>[b.textContent,b.getBoundingClientRect().height,b.getBoundingClientRect().width])")
        ok(all(x[1] >= 44 for x in hs), f"warning buttons are at least 44px tall {hs}")
        shot(pg, f"f20-12-warning-{w}.png")
        import json
        dl = None
        try:
            with pg.expect_download(timeout=8000) as di:
                pg.click("#f20-save-warn [data-action=f20Export]")
            dl = di.value
        except Exception as ex:
            print("  (no file download in this browser:", type(ex).__name__, ")")
        time.sleep(.8)
        data = {}
        if dl:
            try: data = json.load(open(dl.path()))
            except Exception as ex: print("  bad export file", ex)
        ok(not pg.evaluate("!!document.getElementById('f20-save-warn')"), "Export hides the warning")
        ok(bool(dl) and dl.suggested_filename.startswith("verbo-export-") and data.get("highlights", {}).get("Romans 8:1", {}).get("c") == "gold",
           "Export (the existing export action) downloads a file that holds the highlight that could not be saved")
        ok(pg.evaluate("S.highlights['Romans 8:1']&&S.highlights['Romans 8:1'].c")=="gold", "the highlight is still in memory, so Export has it")
        pg.evaluate("closeModal()")
        # a note: the editor status must not say Saved
        pg.evaluate("window.__full=true;A.newNote()"); time.sleep(1)
        pg.click("#wBody"); pg.keyboard.type("Test note"); time.sleep(1.6)
        st = pg.evaluate("W.status")
        ok(st == "Not saved", f"note editor status says Not saved, not Saved ({st!r})")
        pg.evaluate("nav('dashboard')")
        # a later successful save removes the warning
        pg.evaluate("window.__full=false;save()"); time.sleep(.3)
        ok(pg.evaluate("!document.getElementById('f20-save-warn')"), "warning goes away after a save works again")
        ok(pg.evaluate("localStorage.getItem('biblestudy.v1')").count("gold") >= 1, "the data is written once storage works")
        # dismiss
        pg.evaluate("window.__full=true;save()"); time.sleep(.3)
        ok(pg.evaluate("!!document.getElementById('f20-save-warn')"), "warning returns on the next failure")
        pg.click("#f20-save-warn [data-action=f20WarnClose]"); time.sleep(.2)
        ok(pg.evaluate("!document.getElementById('f20-save-warn')"), "Dismiss hides it")
        ok(errs == [], f"no page errors {errs}"); allerrs += errs
        c.close()

    # ---------------------------------------------------------------- 11 offline
    print("--- #11 offline, phone")
    c, pg, errs = newctx(b, 390, 844, True)
    c.route("**/bible/web/**", lambda r: r.abort())
    pg.goto(U + "#v=Psalms 23:1"); time.sleep(3)
    pg.evaluate("loadBook('KJV','Isaiah').catch(()=>{})"); time.sleep(1.2)
    c.set_offline(True)
    ok(pg.evaluate("navigator.onLine") is False, "browser is offline")
    ok(not pg.evaluate("bookLoaded('WEB','Psalms')"), "WEB Psalms is not saved (test set-up)")
    pg.evaluate("A.setTr({dataset:{v:'WEB'}})"); time.sleep(2.5)
    main = pg.evaluate("document.getElementById('main').innerText")
    ok(pg.evaluate("!!document.querySelector('.f20-nosaved')"), "unsaved WEB chapter shows the not-saved state")
    ok("not saved for offline use in WEB" in main, "state says: not saved for offline use in WEB")
    ok("maketh me to lie down" not in main and "I shall not want" not in main, "no KJV wording is shown under the WEB label")
    ok("published app" not in main and "sample passages" not in main and "sample verses" not in main, "old wording (published app, sample passages) is gone")
    ok(pg.evaluate("S.reading.tr") == "WEB" and "WEB" in pg.evaluate("document.querySelector('[data-action=trOpen]').textContent"), "the version pill still says WEB")
    bh = pg.evaluate("[...document.querySelectorAll('.f20-nosaved button')].map(b=>[b.textContent.trim(),b.getBoundingClientRect().height])")
    ok(len(bh) == 2 and all(x[1] >= 44 for x in bh) and any("KJV" in x[0] for x in bh), f"Try again and Read in KJV buttons, 44px tall {bh}")
    pg.evaluate("ui.sel=null;refresh()"); time.sleep(.6)
    shot(pg, "f20-11-offline-web-phone.png")
    # (c) not marked read on failure: the old code marked it after 30 s
    t0 = time.time()
    pg.evaluate("window.scrollTo(0,document.body.scrollHeight);(document.querySelector('.reader-col')||{}).scrollTop=1e5")
    time.sleep(33)
    ok(pg.evaluate("Object.keys(S.chRead||{}).filter(k=>/^18[-:|]/.test(k)||k.indexOf('Psalms')>=0).length") == 0
       and not any("marked as read" in x for x in toasts(pg)), f"not marked as read after 33 s on the failed chapter {toasts(pg)}")
    ok(pg.evaluate("window.covReadOk(()=>{})") is False, "covReadOk refuses while the chapter failed to load")
    # read in KJV works offline (KJV Psalms was loaded)
    pg.click(".f20-nosaved [data-action=f20Kjv]"); time.sleep(1.5)
    ok(pg.evaluate("S.reading.tr") == "KJV" and "The LORD is my shepherd" in pg.evaluate("document.getElementById('main').innerText"), "Read in KJV shows the KJV text, labelled KJV")
    # offline partial KJV (sample) chapter keeps an honest notice
    pg.evaluate("S.reading.book='Genesis';S.reading.ch=1;save();refresh()"); time.sleep(1.5)
    pg.evaluate("BIB.KJV[0]=null;BIBFAIL.add('KJV:0');refresh()"); time.sleep(1)
    mt = pg.evaluate("document.getElementById('main').innerText")
    ok(pg.evaluate("!!document.querySelector('.f20-partial')") and "bundled sample" not in mt and "Only part of this chapter" in mt, "KJV sample fallback uses the plain partial notice")
    ok(pg.evaluate("window.covReadOk(()=>{})") is False, "covReadOk refuses while only part of the chapter is shown")
    ok(errs == [], f"no page errors {errs}"); allerrs += errs
    c.close()

    print("--- #11 offline, desktop: Words tab")
    c, pg, errs = newctx(b, 1366, 900)
    c.route("**/bible/ilx/**", lambda r: r.abort())
    pg.goto(U + "#v=Psalms 23:1"); time.sleep(3)
    pg.evaluate("loadBook('KJV','Isaiah').catch(()=>{})"); time.sleep(1.2)
    c.set_offline(True)
    pg.evaluate("openRef('Isaiah 53:5')"); time.sleep(1)
    pg.evaluate("ui.panelTab='orig';refresh()"); time.sleep(3)
    ok(pg.evaluate("document.querySelectorAll('.panel-b .skel').length") == 0, "Words tab has no skeleton bars offline")
    pt = pg.evaluate("(document.querySelector('.panel-b')||document.body).innerText")
    ok("not saved for offline use" in pt and "Hebrew and Greek word study" in pt, "Words tab says it is not saved for offline use and names the set")
    shot(pg, "f20-11-offline-words-desktop.png")
    c.set_offline(False); c.unroute("**/bible/ilx/**")
    pg.click(".panel-b .f20-nowords [data-action=retryLoad]"); time.sleep(4)
    ok(pg.evaluate("document.querySelectorAll('.panel-b .ilw').length") > 3, "Try again online loads the words")
    ok(errs == [], f"no page errors {errs}"); allerrs += errs
    c.close()

    # ---------------------------------------------------------------- 27 jump
    print("--- #27 jump then tap")
    for w, h, t in [(390, 844, True), (1366, 900, False)]:
        c, pg, errs = newctx(b, w, h, t)
        pg.goto(U + "#v=John 3:16"); time.sleep(3.5)
        ok(pg.evaluate("ui.sel") == "John 3:16" and pg.evaluate("document.querySelectorAll('.v-mark').length") >= 1, f"{w}: #v=John 3:16 opens with the verse marked and selected")
        if w < 900:
            ok(pg.evaluate("document.querySelector('.bottomnav').getBoundingClientRect().top") < h, f"{w}: bottom nav is on screen after the jump")
        pg.click(".v[data-key='John 3:16']"); time.sleep(.6)
        ok(pg.evaluate("ui.sel") == "John 3:16", f"{w}: first tap keeps the verse selected")
        ok(pg.evaluate("document.querySelectorAll('.v-mark').length") == 0 and pg.evaluate("ui.markV") is None, f"{w}: jump marker is cleared")
        ok(pg.evaluate("document.querySelectorAll('.v.sel').length") == 1, f"{w}: the verse shows as selected")
        shot(pg, f"f20-27-after-first-tap-{w}.png")
        pg.click(".v[data-key='John 3:16']"); time.sleep(.5)
        ok(pg.evaluate("ui.sel") is None, f"{w}: second tap deselects as before")
        pg.click(".v[data-key='John 3:17']"); time.sleep(.5)
        ok(pg.evaluate("ui.sel") == "John 3:17", f"{w}: another verse selects")
        ok(errs == [], f"no page errors {errs}"); allerrs += errs
        c.close()
    # search style jump (quiet): nav stays for a few seconds, first tap selects
    c, pg, errs = newctx(b, 390, 844, True)
    pg.goto(U); time.sleep(2)
    pg.evaluate("loadBook('KJV','John').catch(()=>{})"); time.sleep(1.5)
    pg.evaluate("ui.gsOpening=true;openRefQuiet('John 3:16')"); time.sleep(1.2)
    ok(pg.evaluate("document.querySelector('.v[data-key=\"John 3:16\"]').getBoundingClientRect().top") < 300, "search jump: the verse is scrolled into view")
    ok(pg.evaluate("document.querySelector('.bottomnav').getBoundingClientRect().top") < 844 and pg.evaluate("!document.querySelector('.app').classList.contains('bars-hidden')"), "search jump: bottom nav visible after 1.2 s")
    shot(pg, "f20-27-nav-after-jump-phone.png")
    time.sleep(2)
    ok(pg.evaluate("document.querySelector('.bottomnav').getBoundingClientRect().top") < 844, "search jump: bottom nav still visible after 3.2 s")
    pg.click(".v[data-key='John 3:16']"); time.sleep(.6)
    ok(pg.evaluate("ui.sel") == "John 3:16" and pg.evaluate("!!document.getElementById('vpop')"), "search jump: first tap selects and opens the verse menu")
    ok(pg.evaluate("ui.flashV") is None, "flash state is cleared by the tap")
    ok(errs == [], f"no page errors {errs}"); allerrs += errs
    c.close()

    # ---------------------------------------------------------------- 21 references
    print("--- #21 references")
    c, pg, errs = newctx(b, 390, 844, True)
    pg.goto(U + "#v=Genesis 51"); time.sleep(1.6)
    shot(pg, "f20-21-genesis-51.png")
    time.sleep(2.4)
    tl = toasts(pg)
    ok(pg.evaluate("ui.page") == "reader" and pg.evaluate("S.reading.book+' '+S.reading.ch") == "Genesis 50", "#v=Genesis 51 opens Genesis 50")
    ok(any("Genesis has 50 chapters" in x for x in tl), f"toast says why {tl}")
    ok(pg.evaluate("location.hash") != "#v=Genesis 51", "the odd hash is replaced")
    pg.goto(U); time.sleep(2)
    pg.evaluate("openRef('John 22')"); time.sleep(1.5)
    ok(pg.evaluate("S.reading.book+' '+S.reading.ch") == "John 21" and any("John has 21 chapters" in x for x in toasts(pg)), "John 22 opens John 21 with a toast")
    pg.evaluate("openRef('Psalm 151')"); time.sleep(1.5)
    ok(pg.evaluate("S.reading.book+' '+S.reading.ch") == "Psalms 150", "Psalm 151 opens Psalms 150")
    n0 = len(toasts(pg))
    pg.evaluate("openRef('Foo 12')"); time.sleep(.5)
    ok(toasts(pg)[n0:] == ["Reference not recognized"], "nonsense still says Reference not recognized")
    pg.evaluate("openRef('John 3:99')"); time.sleep(2)
    ok(pg.evaluate("S.reading.book+' '+S.reading.ch") == "John 3" and pg.evaluate("ui.sel") is None, "John 3:99 opens the chapter and no verse panel")
    ok(any("John 3 has 36 verses" in x for x in toasts(pg)), f"toast says John 3 has 36 verses {toasts(pg)[-3:]}")
    ok(pg.evaluate("!document.getElementById('vpop')"), "no verse menu for a verse that does not exist")
    pg.evaluate("openRef('3 John 15')"); time.sleep(1.5)
    ok(any("3 John 1 has 14 verses" in x or "3 John has 14 verses" in x for x in toasts(pg)), f"3 John 15 is rejected {toasts(pg)[-2:]}")
    n0 = len(toasts(pg))
    pg.evaluate("openRef('John 3:16')"); time.sleep(1)
    ok(pg.evaluate("ui.sel") == "John 3:16" and toasts(pg)[n0:] == [], "a valid verse still opens with no toast")
    # cold link to a bad verse (chapter text not loaded yet)
    pg.close(); pg = c.new_page(); pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto(U + "#v=John 3:99"); time.sleep(4)
    ok(pg.evaluate("ui.page") == "reader" and pg.evaluate("S.reading.book+' '+S.reading.ch") == "John 3" and pg.evaluate("ui.sel") is None, "#v=John 3:99 (cold) ends on John 3 with nothing selected")
    ok(any("John 3 has 36 verses" in x for x in toasts(pg)), f"cold link toast {toasts(pg)}")
    # DRC label
    lab = pg.evaluate("TRANSLATIONS.DRC")
    ok("Catholic" not in lab and "66 books" in lab, f"DRC label is accurate ({lab})")
    pg.click("[data-action=trOpen]"); time.sleep(.8)
    dt = pg.evaluate("document.getElementById('modal').innerText")
    ok("Douay-Rheims" in dt and "Catholic" not in dt and "66 books" in dt, "the version dialog no longer says Catholic")
    shot(pg, "f20-21-version-dialog-drc.png")
    pg.evaluate("closeModal()")
    ok(errs == [], f"no page errors {errs}"); allerrs += errs
    c.close()

    # ---------------------------------------------------------------- 28 hyphens, footnote label, United Monarchy
    print("--- #28 hyphens, footnote label, era")
    c, pg, errs = newctx(b, 390, 844, True)
    pg.goto(U + "#v=John 1:1"); time.sleep(3)
    ok(pg.evaluate("getComputedStyle(document.querySelector('.scripture .v')).hyphens") == "none", "scripture text has hyphens: none")
    pg.evaluate("document.querySelector('.reading').classList.add('paper')")
    ok(pg.evaluate("getComputedStyle(document.querySelector('.scripture')).hyphens") == "none", "paper layout has hyphens: none")
    for tr, want in [("WEB", "Shown when reading the World English Bible (WEB)"), ("BSB", "Shown when reading the Berean Standard Bible (BSB)")]:
        pg.evaluate(f"A.setTr({{dataset:{{v:'{tr}'}}}})"); time.sleep(1.5)
        pg.evaluate("A.readerMore()"); time.sleep(.8)
        mt = pg.evaluate("document.getElementById('modal').innerText")
        ok(want in mt, f"footnote label for {tr}: {want}")
        pg.evaluate("closeModal()")
    pg.evaluate("A.setTr({dataset:{v:'KJV'}})"); time.sleep(1.5)
    pg.evaluate("A.readerMore()"); time.sleep(.8)
    mt = pg.evaluate("document.getElementById('modal').innerText")
    ok("Not available in KJV" in mt and "Shown when reading the WEB" not in mt and "Shown when reading the World English Bible" not in mt, "footnote label for KJV says notes are not available there")
    pg.evaluate("document.querySelector('[data-action=togFn]').scrollIntoView({block:'center'})"); time.sleep(.3)
    shot(pg, "f20-28-footnote-label-kjv.png")
    pg.evaluate("closeModal()")
    pg.evaluate("nav('timelines')"); time.sleep(1.5)
    tt = pg.evaluate("document.getElementById('main').innerText")
    ok("United Monarchy" in tt and "United Kingdom" not in tt, "timeline era reads United Monarchy")
    shot(pg, "f20-28-timeline-era.png")
    pg.evaluate("fbData()"); time.sleep(2)
    ok(pg.evaluate("fbData().events.some(x=>x.n==='United Monarchy')") and not pg.evaluate("fbData().events.some(x=>x.n==='United Kingdom')"), "Factbook period (Jerusalem pill) is United Monarchy")
    pg.evaluate("nav('characters')"); time.sleep(1)
    ok("United Kingdom" not in pg.evaluate("JSON.stringify([CHARACTERS.david.period,CHARACTERS.solomon.period])") and "United Monarchy" in pg.evaluate("CHARACTERS.david.period"), "David and Solomon periods say United Monarchy")
    ok(errs == [], f"no page errors {errs}"); allerrs += errs
    c.close()

    # ---------------------------------------------------------------- 29 contrast and empty h2
    print("--- #29 dark verse number, empty note blocks")
    for w, h, t in [(390, 844, True), (1366, 900, False)]:
        c, pg, errs = newctx(b, w, h, t)
        pg.goto(U + "#v=Romans 8:1"); time.sleep(3)
        pg.evaluate("S.theme='dark';S.themeAuto=false;save();refresh()"); time.sleep(1)
        pg.click("[data-action=textSize]"); time.sleep(.9)
        col = pg.evaluate("""(()=>{const a=document.querySelector('.aa-prev .aa-vn');if(!a)return null;const c=getComputedStyle(a).color.match(/\\d+/g).map(Number);let el=a,bg;
          while(el){bg=getComputedStyle(el).backgroundColor;if(bg!=='rgba(0, 0, 0, 0)')break;el=el.parentElement}return [c,bg.match(/\\d+/g).map(Number)]})()""")
        r = ratio(col[0][:3], col[1][:3]) if col else 0
        ok(r >= 4.5, f"{w}: dark Aa verse number contrast {r:.2f}:1 (needs 4.5)")
        pg.add_script_tag(path=AXE)
        res = pg.evaluate("axe.run('.aa-prev',{runOnly:['color-contrast']}).then(r=>r.violations.length)")
        ok(res == 0, f"{w}: axe color-contrast on the preview has no violations")
        shot(pg, f"f20-29-aa-preview-dark-{w}.png")
        pg.evaluate("closeModal()")
        # notes
        pg.evaluate("A.newNote()"); time.sleep(1.2)
        ok(pg.evaluate("document.getElementById('wBody').innerHTML") == "<h2><br></h2>", f"{w}: a new note starts with an empty heading line in the editor (set-up)")
        pg.click("#wBody"); pg.keyboard.type("Hello note"); time.sleep(1.6)
        body = pg.evaluate("S.notes[0].body")
        ok("<h2><br></h2>" not in body and "<h2></h2>" not in body and "Hello note" in body, f"{w}: saved body has no empty heading {body!r}")
        pg.evaluate("nav('notes')"); time.sleep(.5)
        ok("<h2><br></h2>" not in pg.evaluate("S.notes[0].body"), f"{w}: still none after leaving the editor")
        # real heading and a blank middle line are kept
        kept = pg.evaluate("clean('<h2>Title</h2><p>One</p><p><br></p><p>Two</p><h2><br></h2><p><br></p>')")
        ok(kept == "<h2>Title</h2><p>One</p><p><br></p><p>Two</p>", f"{w}: real headings and blank lines between text are kept {kept!r}")
        ok(pg.evaluate("clean('<p><br></p><h3> </h3><p>Hi</p>')") == "<p>Hi</p>", f"{w}: empty leading blocks are removed")
        ok(errs == [], f"no page errors {errs}"); allerrs += errs
        c.close()

    # ---------------------------------------------------------------- 25 tabs count, initials
    print("--- #25 tabs button, initials")
    c, pg, errs = newctx(b, 390, 844, True)
    pg.goto(U + "#v=Romans 8:1"); time.sleep(3)
    tb = pg.evaluate("(()=>{const b=document.querySelector('.rtop-i .tabs-btn');const r=b.getBoundingClientRect();return {label:b.getAttribute('aria-label'),text:b.textContent.trim(),svg:!!b.querySelector('svg'),w:r.width,h:r.height,vis:getComputedStyle(b).display}})()")
    ok(tb["text"] == "" and tb["svg"], f"one tab: no boxed number, an icon instead {tb}")
    ok(tb["label"].startswith("Tabs, 1 open"), f"button keeps its name {tb['label']!r}")
    ok(tb["w"] >= 44 and tb["h"] >= 44, f"tabs button is at least 44px {tb['w']}x{tb['h']}")
    shot(pg, "f20-25-tabs-button-one-phone.png")
    pg.click(".rtop-i .tabs-btn"); time.sleep(.8)
    ok(pg.evaluate("!!document.getElementById('tabsView')"), "tapping the button opens the tabs screen")
    pg.keyboard.press("Escape"); time.sleep(.4)
    pg.goto(U + "#v=Romans 8:1"); time.sleep(2.5)
    pg.evaluate("A.tabNew()"); time.sleep(1.2)
    pg.evaluate("openRef('John 3:16')"); time.sleep(1.2)
    t2 = pg.evaluate("(()=>{const b=document.querySelector('.rtop-i .tabs-btn');return b?[b.getAttribute('aria-label'),b.textContent.trim()]:null})()")
    ok(t2 and t2[1] == "2" and t2[0].startswith("Tabs, 2 open"), f"two tabs: the count shows {t2}")
    ok(errs == [], f"no page errors {errs}"); allerrs += errs
    c.close()
    c, pg, errs = newctx(b, 1366, 900)
    pg.goto(U + "#v=Romans 8:1"); time.sleep(3)
    av = pg.evaluate("document.querySelector('#btnProfile .avatar').innerHTML")
    ok("DR" not in pg.evaluate("document.querySelector('#btnProfile .avatar').textContent") and "svg" in av, "desktop: no name known, so a person icon, not DR")
    shot(pg, "f20-25-avatar-desktop-icon.png")
    pg.evaluate("window.USERNAME='Pat Lee';refresh()"); time.sleep(.8)
    ok(pg.evaluate("document.querySelector('#btnProfile .avatar').textContent") == "PL", "desktop: initials from the user's name (Pat Lee gives PL)")
    shot(pg, "f20-25-avatar-desktop-initials.png")
    pg.evaluate("window.USERNAME='Dina Reyes';refresh()"); time.sleep(1.5)
    a1 = pg.evaluate("document.querySelector('#btnProfile .avatar').textContent"); time.sleep(1)
    a2 = pg.evaluate("document.querySelector('#btnProfile .avatar').textContent")
    ok(a1 == a2 and a1.replace("​", "") == "DR", "a real name with the initials DR is stable")
    ok(pg.evaluate("document.querySelectorAll('.tabs-btn:not(.only-m)').length") >= 0, "desktop header renders")
    ok(errs == [], f"no page errors {errs}"); allerrs += errs
    c.close()

    # axe on the reader after all changes. These are the same results as before F20.
    print("--- axe on the reader")
    for w, h, tch, allowed in [(390, 844, True, {"aria-allowed-attr", "region"}), (1366, 900, False, {"aria-required-children"})]:
        c, pg, errs = newctx(b, w, h, tch)
        pg.goto(U + "#v=Romans 8:1"); time.sleep(3)
        pg.add_script_tag(path=AXE)
        v = pg.evaluate("axe.run(document,{resultTypes:['violations']}).then(r=>r.violations.map(v=>v.id+' x'+v.nodes.length))")
        ok(set(x.split(" ")[0] for x in v) <= allowed, f"axe reader {w}px: nothing new, only the earlier results {v}")
        ok(errs == [], f"no page errors {errs}"); allerrs += errs
        c.close()
    b.close()

print()
print("ALL PASS" if not fails else "FAILURES:\n- " + "\n- ".join(fails))
sys.exit(1 if fails else 0)
