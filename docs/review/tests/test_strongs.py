import time
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b=p.chromium.launch(args=["--no-sandbox"])
    c=b.new_context(viewport={"width":1366,"height":900}); c.add_init_script("localStorage.setItem('verbo.welcomed','1')")
    pg=c.new_page(); pg.goto("http://localhost:8110/"); time.sleep(2)
    for key in ["G25","H430","H1"]:
        pg.evaluate("ui.bsb='';nav('search')"); time.sleep(.8)
        pg.fill(".page input",key); pg.keyboard.press("Enter"); time.sleep(6)
        t=pg.evaluate("document.querySelector('.page').innerText")
        j=t.find('verses with'); print(key, '| not used' if 'is not used' in t else '', '|', t[max(0,j-6):j+40].replace('\n',' ') if j>=0 else t[-200:].replace('\n',' '))
        if key=="G25": pg.screenshot(path="./f4-G25.png")
    b.close()
