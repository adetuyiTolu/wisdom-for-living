"""Run with Python Playwright and Chromium; external media is blocked."""
import os
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
 browser=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
 for width,height in [(320,740),(360,800),(390,844),(768,1024),(820,1180),(821,900),(844,390),(1024,768),(1280,720),(1366,640),(1440,900),(1920,1080),(2560,1440)]:
  page=browser.new_page(viewport={'width':width,'height':height},has_touch=width<=820)
  errors=[]
  page.on('pageerror',lambda e:errors.append(str(e)))
  page.route('https://**/*',lambda route: route.abort())
  page.goto(os.environ.get('WFL_TEST_URL','http://127.0.0.1:8001'),wait_until='networkidle')
  page.evaluate('document.fonts.ready')
  page.wait_for_timeout(600)  # Let the intentional entrance animations finish before measuring clipping.
  assert page.locator('main').count()==1
  resources=page.evaluate('performance.getEntriesByType("resource").map(r=>r.name)')
  assert not any('unpkg.com' in r or 'fonts.googleapis.com' in r or 'fonts.gstatic.com' in r for r in resources),resources
  hero=page.locator('[data-screen-label="Hero"]').bounding_box()
  for child in page.locator('[data-screen-label="Hero"] > h1, [data-screen-label="Hero"] > p').all():
   box=child.bounding_box()
   assert box['y']>=hero['y']-1 and box['y']+box['height']<=hero['y']+hero['height']+1,(width,height,hero,box)
  assert page.locator('h1').inner_text()=='Insight sees.\nWisdom builds.'
  assert not errors,errors
  assert page.evaluate('document.documentElement.scrollWidth <= innerWidth'),f'overflow {width}'
  assert page.locator('[data-sound-button]').count()==0
  # COI has no reserved control strip; its 16:9 picture reaches a frame edge.
  coi_frame=page.locator('[data-screen-label="Narration"]').bounding_box()
  coi_video=page.locator('iframe').bounding_box()
  assert abs(coi_video['width']/coi_video['height']-16/9)<.01
  assert coi_video['width']>=coi_frame['width']-.5 or coi_video['height']>=coi_frame['height']-.5,(coi_frame,coi_video)
  assert page.locator('[data-player-area]').evaluate("e=>getComputedStyle(e).paddingBottom")=='0px'
  fullscreen=page.get_by_role('button',name='View full screen',exact=True)
  assert fullscreen.is_visible()
  fullscreen_box=fullscreen.bounding_box()
  playlist_box=page.locator('[data-video-controls]').bounding_box()
  assert fullscreen_box['x']+fullscreen_box['width']<=playlist_box['x'],(width,fullscreen_box,playlist_box)
  # Spy on the browser API to check button wiring without entering headless fullscreen.
  page.locator('iframe').evaluate('(el) => { el.requestFullscreen = () => { window.fullscreenTarget = el.tagName; return Promise.resolve(); }; }')
  fullscreen.click()
  assert page.evaluate('window.fullscreenTarget')=='IFRAME'

  page.locator('[data-playlist-toggle]').click()
  assert page.locator('[data-playlist-panel]').is_visible()
  page.keyboard.press('Escape')
  assert not page.locator('[data-playlist-panel]').is_visible()
  assert page.locator('[data-playlist-toggle]').evaluate('e=>e===document.activeElement')

  # Keyboard selection supports both activation keys without resetting the current channel.
  cards=page.locator('[data-screen-label="Pillars"]')
  cards.get_by_role('button',name='ZeroToAct',exact=True).focus()
  page.keyboard.press('Enter')
  assert page.locator('[data-wfl-grid]').get_attribute('data-video-layout')=='youtube-portrait'
  cards.get_by_role('button',name='Chronicles of Innovation',exact=True).focus()
  page.keyboard.press('Space')
  assert page.locator('[data-wfl-grid]').get_attribute('data-video-layout')=='youtube-landscape'
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
   page.evaluate('window.existingVideo=document.querySelector("video")')
   if width<=820:
    page.locator('[data-mobile-nav]').get_by_role('button',name=['The Builders','Books'][channel_index-2],exact=True).click()
   else:
    channels.nth(channel_index).click()
   assert page.evaluate('window.existingVideo===document.querySelector("video")'), 'Selecting the active channel should not reload media'
   assert page.locator('video').get_attribute('poster'), 'Local film needs its cover before loading'
   assert page.get_by_role('button',name='View full screen',exact=True).is_visible()
   page.locator('video').evaluate('(el) => { el.requestFullscreen = () => { window.fullscreenTarget = el.tagName; return Promise.resolve(); }; }')
   page.get_by_role('button',name='View full screen',exact=True).click()
   assert page.evaluate('window.fullscreenTarget')=='VIDEO'

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
  assert not errors,errors
  page.close()
 browser.close()
