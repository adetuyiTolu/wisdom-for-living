"""Run with Playwright and local React/Babel test dependencies (see VALIDATION.md)."""
import os
from pathlib import Path
from playwright.sync_api import sync_playwright
DEPS=Path(os.environ.get('WFL_TEST_DEPS','/tmp/wfl-browser-deps/node_modules'))
with sync_playwright() as p:
 browser=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
 for width,height in [(320,740),(390,844),(768,1024),(1024,768),(1440,900),(1920,1080)]:
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
  page.goto(os.environ.get('WFL_TEST_URL','http://127.0.0.1:8001'),wait_until='networkidle')
  assert page.locator('h1').inner_text()=='Insight sees.\nWisdom builds.'
  assert not errors,errors
  assert page.evaluate('document.documentElement.scrollWidth <= innerWidth'),f'overflow {width}'
  assert page.locator('[data-sound-button]').count()==0
  if width<=820:
   nav=page.locator('[data-mobile-nav]')
   assert nav.is_visible()
   nav.get_by_role('button',name='ZeroToAct',exact=True).click()
   assert page.locator('[data-screen-label="Narration"]').get_attribute('data-video-orientation')=='portrait'
   for selector in ['[data-fullscreen-button]','[aria-label="Next video"]','[data-playlist-toggle]']:
    box=page.locator(selector).bounding_box();assert box['height']>=43.9,(selector,box)
   page.locator('[data-playlist-toggle]').click()
   assert page.locator('[data-playlist-panel]').is_visible()
   page.locator('[data-playlist-item]').first.click()
   assert not page.locator('[data-playlist-panel]').is_visible()
   nav.get_by_role('button',name='The Builders',exact=True).click()
   page.wait_for_function("document.querySelector('video')?.controls === true")
  else:
   channels=page.locator('[data-screen-label="Pillars"] > div')
   channels.nth(1).click()
   page.wait_for_timeout(600)
   panel=page.locator('[data-screen-label="Narration"]').bounding_box()
   video=page.locator('iframe').bounding_box()
   assert video['height']>=panel['height']*.90,(width,panel,video)
   assert abs(video['width']/video['height']-9/16)<.01
   assert not page.locator('[data-screen-label="Pillar list"]').is_visible()
   if width<1200:
    page.locator('[data-playlist-toggle]').click()
    assert page.locator('[data-playlist-panel]').is_visible()
    page.locator('[data-playlist-close]').click()
   page.screenshot(path=f'/tmp/wfl-z2a-{width}.png',full_page=True)
   channels.nth(2).click()
   page.wait_for_function("document.querySelector('video')?.controls === true")
   assert page.locator('[data-screen-label="Pillar list"]').is_visible()
   assert page.locator('[data-player-area]').evaluate("e=>getComputedStyle(e).paddingTop")=='0px'
  # Local films use the full available frame, including their native controls.
  for channel_index in [2,3]:
   if width<=820:
    page.locator('[data-mobile-nav]').get_by_role('button',name=['The Builders','Books'][channel_index-2],exact=True).click()
   else:
    channels.nth(channel_index).click()
   page.wait_for_timeout(500)
   frame=page.locator('[data-screen-label="Narration"]').bounding_box()
   movie=page.locator('video').bounding_box()
   assert abs(movie['width']/movie['height']-16/9)<.01
   assert movie['width']>=frame['width']-.5 or movie['height']>=frame['height']-.5,(frame,movie)
   assert page.locator('video').get_attribute('poster'), 'Local film needs its cover before loading'
   assert not page.locator('[data-fullscreen-button]').is_visible(), 'Native local controls keep artwork unobstructed'
   assert page.locator('[data-player-area]').evaluate("e=>getComputedStyle(e).paddingTop")=='0px'
  # Leave Builders selected for the existing reload/progress check.
  if width<=820:
   page.locator('[data-mobile-nav]').get_by_role('button',name='The Builders',exact=True).click()
  else:
   channels.nth(2).click()
  page.wait_for_timeout(600)
  page.screenshot(path=f'/tmp/wfl-{width}.png',full_page=True)
  print(f'PASS {width}x{height}: rendering, overflow, mobile navigation and controls')
  if width==390:
   page.wait_for_function("document.querySelector('video')?.readyState >= 2")
   page.locator('video').evaluate('(v) => { v.pause(); v.currentTime = 11.5; }')
   page.evaluate('window.scrollTo(0, 600)')
   page.wait_for_timeout(1200)
   saved=page.evaluate("JSON.parse(localStorage.getItem('wfl.watch.v1'))")
   assert saved['activeVideoIndex']==2,saved
   assert saved['positions']['local:./videos/the-builders-intro.mp4']>=11,saved
   page.reload(wait_until='networkidle')
   page.wait_for_function("document.querySelector('video')?.currentTime >= 11")
   page.wait_for_function('(expected) => Math.abs(scrollY - expected) <= 2',arg=saved['scrollY'])
   print('PASS reload restores channel, local playback time and page position')
  page.close()
 browser.close()
