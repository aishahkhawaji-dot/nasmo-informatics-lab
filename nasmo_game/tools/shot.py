import sys, asyncio
from playwright.sync_api import sync_playwright
src, out, w, h = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4])
full = len(sys.argv) > 5 and sys.argv[5] == "full"
with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(viewport={"width": w, "height": h})
    msgs = []
    pg.on("console", lambda m: msgs.append(m.text) if m.type in ("error", "warning") else None)
    pg.on("pageerror", lambda e: msgs.append(str(e)))
    pg.goto("file://" + src)
    pg.wait_for_timeout(1500)
    pg.screenshot(path=out, full_page=full)
    ow = pg.evaluate("document.documentElement.scrollWidth - document.documentElement.clientWidth")
    print("horizontal overflow px:", ow, "| console:", msgs[:5])
    b.close()
