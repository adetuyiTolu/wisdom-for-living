"""Exact-ID integration for both playlists with an adversarial YouTube API double.
No live playback claim: the double starts on the wrong ID until loadVideoById.
"""
import os
from playwright.sync_api import sync_playwright
MOCK_YOUTUBE="""
window.testPlayers=[];
window.YT={Player:class {
 constructor(el,options){
  this.el=el;this.options=options;this.id='unexpected-next-video';this.commands=[];
  this.state=1;this.time=0;this.muted=true;window.testPlayers.push(this);window.activePlayer=this;
  queueMicrotask(()=>this.options.events.onReady({target:this}));
 }
 getIframe(){return this.el}
 loadVideoById(request){this.commands.push(request);this.id=request.videoId;this.time=request.startSeconds;this.state=1}
 getVideoData(){return {video_id:this.id}}
 getCurrentTime(){return this.time}
 seekTo(seconds){this.time=seconds}
 unMute(){this.muted=false}
 mute(){this.muted=true}
 setVolume(){}
 isMuted(){return this.muted}
 getPlayerState(){return this.state}
 playVideo(){this.state=1;this.emit()}
 emit(){this.options.events.onStateChange({target:this,data:this.state})}
 finish(){this.state=0;this.time=30;this.emit();this.emit()}
 destroy(){this.destroyed=true}
}};
"""
with sync_playwright() as p:
 browser=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
 for width,height in [(390,844),(1440,900)]:
  for channel,count in [('Chronicles of Innovation',4),('ZeroToAct',13)]:
   page=browser.new_page(viewport={'width':width,'height':height})
   errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
   page.add_init_script(MOCK_YOUTUBE)
   page.route('https://**/*',lambda route:route.abort())
   page.goto(os.environ.get('WFL_TEST_URL','http://127.0.0.1:8001'),wait_until='networkidle')
   if channel=='ZeroToAct':
    if width<821:page.locator('[data-mobile-nav]').get_by_role('button',name=channel,exact=True).click()
    else:page.locator('[data-screen-label="Pillars"]').get_by_role('button',name=channel,exact=True).click()
   page.wait_for_function('(n)=>document.querySelectorAll("[data-playlist-item]").length===n',arg=count)
   entries=page.locator('[data-playlist-item]').evaluate_all('(rows)=>rows.map(r=>({id:r.dataset.videoId,title:r.innerText}))')
   assert len(entries)==count
   def verify(video_id):
    page.wait_for_function('(id)=>window.activePlayer.getVideoData().video_id===id && document.querySelector(\'[data-playlist-item][aria-current="true"]\')?.dataset.videoId===id',arg=video_id)
    assert page.locator('[data-playlist-item][aria-current="true"]').count()==1
    source=page.locator('iframe').get_attribute('src')
    assert source.split('/embed/')[1].split('?')[0]==video_id
    assert 'playlist=' not in source and '?list=' not in source
    assert page.evaluate('window.activePlayer.commands.at(-1).videoId')==video_id
   def choose(index):
    entry=entries[index%count]
    if not page.locator('[data-playlist-panel]').is_visible():page.locator('[data-playlist-toggle]').click()
    page.evaluate('window.previousPlayer=window.activePlayer')
    page.locator(f'[data-playlist-item][data-video-id="{entry["id"]}"]').click()
    verify(entry['id'])
    assert page.evaluate('window.activePlayer.time')==0
    page.evaluate('window.previousPlayer.emit()')
    verify(entry['id'])
   for index in range(count):choose(index)
   for index in [0,1,2]:choose(index)
   # Finishing advances exactly one item; duplicate ENDED events cannot skip two.
   page.evaluate('window.finishedPlayer=window.activePlayer;window.activePlayer.finish()')
   verify(entries[3]['id'])
   assert page.evaluate('window.finishedPlayer!==window.activePlayer')
   page.evaluate('window.finishedPlayer.emit()');verify(entries[3]['id'])
   choose(2)
   page.locator('[aria-label="Next video"]').click();verify(entries[3]['id'])
   page.locator('[aria-label="Next video"]').click();verify(entries[4%count]['id'])
   page.locator('[aria-label="Previous video"]').click();verify(entries[3]['id'])
   # Last item wraps to the first, with no native playlist queue to skip a choice.
   choose(count-1);page.evaluate('window.activePlayer.finish()');verify(entries[0]['id'])
   choose(2)
   page.evaluate('window.activePlayer.time=17;window.dispatchEvent(new Event("pagehide"))')
   saved=page.evaluate('JSON.parse(localStorage.getItem("wfl.watch.v1"))')
   assert saved['videoId']==entries[2]['id']
   page.reload(wait_until='networkidle');verify(entries[2]['id'])
   page.wait_for_function('window.activePlayer.time===17')
   assert not errors,errors
   print(f'PASS {channel} {width}px: every choice, exact API ID, stale events, rapid choices, end-only advancement, next/previous and resume')
   page.close()
 browser.close()
