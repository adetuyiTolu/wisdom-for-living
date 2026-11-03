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
 for width,height in [(320,740),(390,844),(821,900),(1440,900)]:
  for channel,count in [('Chronicles of Innovation',4),('ZeroToAct',14)]:
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
   picture=page.locator('iframe').bounding_box()
   transport=page.locator('[data-player-toolbar]').bounding_box()
   assert picture['y']+picture['height']<=transport['y']+.5,(channel,width,picture,transport)
   def verify(video_id):
    page.wait_for_function('(id)=>window.activePlayer.getVideoData().video_id===id && document.querySelector(\'[data-playlist-item][aria-current="true"]\')?.dataset.videoId===id',arg=video_id)
    assert page.locator('[data-playlist-item][aria-current="true"]').count()==1
    source=page.locator('iframe').get_attribute('src')
    assert source.split('/embed/')[1].split('?')[0]==video_id
    assert 'playlist=' not in source and '?list=' not in source
    assert page.evaluate('window.activePlayer.commands.at(-1).videoId')==video_id
   def verify_row_bounds():
    issues=page.locator('[data-playlist-item]').evaluate_all("""rows=>rows.flatMap(row=>{
     const box=row.getBoundingClientRect(),copy=row.querySelector('[data-playlist-copy]');
     const text=copy.getBoundingClientRect(),thumb=row.querySelector('img').getBoundingClientRect();
     const next=row.nextElementSibling?.getBoundingClientRect();
     const outside=text.top<box.top+7||text.bottom>box.bottom-7||text.left<box.left+7||text.right>box.right-7;
     const overlap=next&&box.bottom>next.top+1;
     return outside||overlap||copy.scrollWidth>copy.clientWidth+1||thumb.bottom>box.bottom-7
      ?[{id:row.dataset.videoId,row:box.toJSON(),text:text.toJSON()}]:[];
    })""")
    assert not issues,(channel,width,issues)

   def choose(index):
    entry=entries[index%count]
    if not page.locator('[data-playlist-panel]').is_visible():page.locator('[data-playlist-toggle]').click()
    verify_row_bounds()
    page.evaluate('window.previousPlayer=window.activePlayer')
    page.locator(f'[data-playlist-item][data-video-id="{entry["id"]}"]').click()
    verify(entry['id'])
    assert page.evaluate('window.activePlayer.time')==0
    assert 'mute=0' in page.locator('iframe').get_attribute('src')
    assert page.evaluate('!window.activePlayer.muted'), 'Selected videos should request audible playback'
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
   choose(count-1)
   # Reopening reveals a saved/current entry without moving the page itself.
   if not page.locator('[data-playlist-panel]').is_visible():
    before_scroll=page.evaluate('scrollY')
    page.locator('[data-playlist-toggle]').evaluate('e=>e.click()')
    assert page.evaluate('scrollY')==before_scroll
   row=page.locator('[data-playlist-item][aria-current="true"]').bounding_box()
   frame=page.locator('[data-playlist-scroll]').bounding_box()
   if row['height']>frame['height']:
    assert abs(row['y']-frame['y'])<=1,(channel,width,row,frame)
   else:
    assert row['y']>=frame['y']-1 and row['y']+row['height']<=frame['y']+frame['height']+1,(channel,width,row,frame)
   assert page.locator('[data-playing-label]').count()==1
   assert page.locator('[data-playlist-meta]').inner_text()==f'{count} videos · Newest first'
   page.evaluate('window.activePlayer.finish()');verify(entries[0]['id'])
   choose(2)
   page.evaluate('window.activePlayer.time=17;window.dispatchEvent(new Event("pagehide"))')
   saved=page.evaluate('JSON.parse(localStorage.getItem("wfl.watch.v1"))')
   assert saved['videoId']==entries[2]['id']
   page.reload(wait_until='networkidle');verify(entries[2]['id'])
   page.wait_for_function('window.activePlayer.time===17')
   # Larger text must remain within each button, rather than overlap its neighbours.
   if not page.locator('[data-playlist-panel]').is_visible():page.locator('[data-playlist-toggle]').click()
   page.add_style_tag(content='[data-playlist-item] [data-playlist-title]{font-size:20px!important}[data-playlist-item] [data-playing-label]{font-size:16px!important}')
   verify_row_bounds()
   assert not errors,errors
   print(f'PASS {channel} {width}px: every choice, exact API ID, stale events, rapid choices, end-only advancement, next/previous and resume')
   page.close()
 browser.close()
