"""Player synchronization integration test using a controllable YouTube API double.
It verifies our embed/queue contract, not YouTube's live media or title metadata.
"""
import os
from playwright.sync_api import sync_playwright
MOCK_YOUTUBE="""
window.testPlayers=[];
window.YT={Player:class {
 constructor(el,options){
  this.el=el;this.options=options;const url=new URL(el.src);this.queue=[url.pathname.split('/').pop(),...url.searchParams.get('playlist').split(',')];
  this.index=0;this.time=0;this.muted=true;window.testPlayers.push(this);window.activePlayer=this;
  queueMicrotask(()=>this.options.events.onReady({target:this}));
 }
 getIframe(){return this.el}
 getVideoData(){return {video_id:this.queue[this.index]}}
 getCurrentTime(){return this.time}
 seekTo(seconds){this.time=seconds}
 unMute(){this.muted=false}
 mute(){this.muted=true}
 setVolume(){}
 isMuted(){return this.muted}
 getPlayerState(){return 1}
 playVideo(){this.emit()}
 emit(){this.options.events.onStateChange({target:this,data:1})}
 advance(){this.index=(this.index+1)%this.queue.length;this.time=0;this.emit()}
 destroy(){this.destroyed=true}
}};
"""
with sync_playwright() as p:
 browser=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
 for width,height in [(390,844),(1440,900)]:
  page=browser.new_page(viewport={'width':width,'height':height})
  errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
  page.add_init_script(MOCK_YOUTUBE)
  page.route('https://**/*',lambda route:route.abort())
  page.goto(os.environ.get('WFL_TEST_URL','http://127.0.0.1:8001'),wait_until='networkidle')
  if width<821:page.locator('[data-mobile-nav]').get_by_role('button',name='ZeroToAct',exact=True).click()
  else:page.locator('[data-screen-label="Pillars"]').get_by_role('button',name='ZeroToAct',exact=True).click()
  page.wait_for_function('window.activePlayer?.queue.length===13')
  entries=page.locator('[data-playlist-item]').evaluate_all('(rows)=>rows.map(r=>({id:r.dataset.videoId,title:r.innerText}))')
  assert len(entries)==13
  def verify(video_id):
   page.wait_for_function('(id)=>window.activePlayer.getVideoData().video_id===id && document.querySelector(\'[data-playlist-item][aria-current="true"]\')?.dataset.videoId===id',arg=video_id)
   assert page.locator('[data-playlist-item][aria-current="true"]').count()==1
   assert page.locator('iframe').get_attribute('src').split('/embed/')[1].split('?')[0]==video_id
  for entry in entries:
   if width<821:page.locator('[data-playlist-toggle]').click()
   page.evaluate('window.previousPlayer=window.activePlayer')
   page.locator(f'[data-playlist-item][data-video-id="{entry["id"]}"]').click()
   verify(entry['id'])
   # A delayed event from the replaced player must not change the selected row.
   page.evaluate('window.previousPlayer.emit()')
   verify(entry['id'])
  # Rapid selection keeps the last choice; then YouTube advances in our displayed order.
  for entry in entries[:3]:
   if width<821:page.locator('[data-playlist-toggle]').click()
   page.locator(f'[data-playlist-item][data-video-id="{entry["id"]}"]').click()
  verify(entries[2]['id'])
  page.evaluate('window.existingFrame=document.querySelector("iframe");window.activePlayer.time=29;window.dispatchEvent(new Event("pagehide"));window.activePlayer.advance()')
  page.wait_for_function('(id)=>document.querySelector(\'[data-playlist-item][aria-current="true"]\')?.dataset.videoId===id',arg=entries[3]['id'])
  assert page.evaluate('window.existingFrame===document.querySelector("iframe")')
  # Reselecting the original embed video after auto-advance must actually reload it.
  if width<821:page.locator('[data-playlist-toggle]').click()
  page.locator(f'[data-playlist-item][data-video-id="{entries[2]["id"]}"]').click()
  verify(entries[2]['id'])
  assert page.evaluate('window.existingFrame!==document.querySelector("iframe")')
  assert page.evaluate('window.activePlayer.time')==0, 'Explicit selections must not resume near the previous ending'
  page.locator('[aria-label="Next video"]').click();verify(entries[3]['id'])
  page.locator('[aria-label="Next video"]').click();verify(entries[4]['id'])
  page.locator('[aria-label="Previous video"]').click();verify(entries[3]['id'])
  page.evaluate('window.activePlayer.time=17;window.dispatchEvent(new Event("pagehide"))')
  saved=page.evaluate('JSON.parse(localStorage.getItem("wfl.watch.v1"))')
  assert saved['videoId']==entries[3]['id']
  page.reload(wait_until='networkidle');verify(entries[3]['id'])
  page.wait_for_function('window.activePlayer.time===17')
  assert not errors,errors
  print(f'PASS {width}px: all 13 selections, stale events, rapid clicks, auto-advance, next/previous and resume')
  page.close()
 browser.close()
