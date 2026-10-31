"""Run with Playwright and local React/Babel test dependencies (see VALIDATION.md)."""
import os
from pathlib import Path
from playwright.sync_api import sync_playwright
DEPS=Path(os.environ.get('WFL_TEST_DEPS','/tmp/wfl-browser-deps/node_modules'))
with sync_playwright() as p:
 browser=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
 for width,height in [(320,740),(390,844),(768,1024),(1440,900)]:
  page=browser.new_page(viewport={'width':width,'height':height})
  errors=[]
  page.on('pageerror',lambda e:errors.append(str(e)))
  def route(r):
   mapping={'react@18.3.1/umd/react.production.min.js':'react/umd/react.production.min.js','react-dom@18.3.1/umd/react-dom.production.min.js':'react-dom/umd/react-dom.production.min.js','@babel/standalone@7.29.0/babel.min.js':'@babel/standalone/babel.min.js'}
   for key,value in mapping.items():
    if key in r.request.url:
     r.fulfill(path=str(DEPS/value),content_type='application/javascript');return
   r.abort()
  page.route('https://**/*',route)
  page.goto('http://127.0.0.1:8000',wait_until='networkidle')
  assert page.locator('h1').inner_text()=='Insight sees.\nWisdom builds.'
  assert not errors,errors
  assert page.evaluate('document.documentElement.scrollWidth <= innerWidth'),f'overflow {width}'
  if width<=820:
   nav=page.locator('[data-mobile-nav]')
   assert nav.is_visible()
   nav.get_by_role('button',name='ZeroToAct',exact=True).click()
   assert page.locator('[data-screen-label="Narration"]').get_attribute('data-video-orientation')=='portrait'
   for selector in ['[data-sound-button]','[aria-label="Next video"]','[data-playlist-toggle]']:
    box=page.locator(selector).bounding_box();assert box['height']>=43.9,(selector,box)
   page.locator('[data-playlist-toggle]').click()
   assert page.locator('[data-playlist-panel]').is_visible()
   page.locator('[data-playlist-item]').first.click()
   assert not page.locator('[data-playlist-panel]').is_visible()
   nav.get_by_role('button',name='The Builders',exact=True).click()
   page.wait_for_function("document.querySelector('video')?.controls === true")
  page.screenshot(path=f'/tmp/wfl-{width}.png',full_page=True)
  print(f'PASS {width}x{height}: rendering, overflow, mobile navigation and controls')
  page.close()
 browser.close()
