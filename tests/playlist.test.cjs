const {test}=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const vm=require('node:vm');
function component(){
 const html=fs.readFileSync('index.html','utf8');
 const start=html.indexOf('class Component extends DCLogic');
 const code=html.slice(start,html.indexOf('</script>',start));
 const context={DCLogic:class {props={};setState(update,done){Object.assign(this.state,typeof update==='function'?update(this.state):update);done?.();}}};
 vm.createContext(context);vm.runInContext(code+';globalThis.instance = new Component();',context);
 const c=context.instance;c.state.active=1;c.state.activeVideoIndex=1;
 return c;
}
test('every ZeroToAct click matches the embed, effective queue, and current row',()=>{
 const c=component(),p=c.getVideoPillar();
 assert.equal(p.videos.length,13);
 for(const [i,video] of p.videos.entries()){
  c._playback={enableSound(){},restartVideo(){},capture(){c.state.playingVideoId=p.videos[(i+1)%p.videos.length].id;}};
  c.selectVideo(video.id);
  const url=new URL(c.getVideoSrc(p,c.state.manualVideoId));
  const following=url.searchParams.get('playlist').split(',');
  const queue=[url.pathname.split('/').pop(),...following];
  assert.ok(!following.includes(video.id),'the initial video must not be duplicated');
  assert.equal(url.pathname,'/embed/'+video.id);
  assert.equal(queue[0],video.id);
  assert.equal(new Set(queue).size,p.videos.length);
  assert.deepEqual(queue,Array.from(p.videos.slice(i).concat(p.videos.slice(0,i)),v=>v.id));
  assert.equal(c.getCurrentVideoId(p),video.id);
  assert.deepEqual(Array.from(c.renderVals().playlistVideos).filter(v=>v.isCurrent==='true').map(v=>v.id),[video.id]);
 }
});
test('automatic advancement updates the current row without reloading the embed',()=>{
 const c=component(),p=c.getVideoPillar();c.selectVideo(p.videos[3].id);
 const src=c.renderVals().videoSrc, playerKey=c.renderVals().videoPlayerKey;
 c.state.playingVideoId=p.videos[4].id;
 assert.equal(c.renderVals().videoSrc,src);
 assert.equal(c.renderVals().videoPlayerKey,playerKey);
 assert.equal(c.renderVals().playlistVideos.filter(v=>v.isCurrent==='true')[0].id,p.videos[4].id);
 c.playNext();assert.equal(c.state.manualVideoId,p.videos[5].id);
 c.playPrevious();assert.equal(c.state.manualVideoId,p.videos[4].id);
});
test('invalid selection cannot replace a listed video',()=>{
 const c=component();c.selectVideo('not-a-listed-video');assert.equal(c.state.manualVideoId,null);
});

test('reselecting the original video after auto-advance recreates its player',()=>{
 const c=component(),p=c.getVideoPillar();c.selectVideo(p.videos[2].id);
 const key=c.renderVals().videoPlayerKey,src=c.renderVals().videoSrc;
 c.state.playingVideoId=p.videos[3].id;c.selectVideo(p.videos[2].id);
 assert.equal(c.renderVals().videoSrc,src);
 assert.notEqual(c.renderVals().videoPlayerKey,key);
 assert.equal(c.getCurrentVideoId(p),p.videos[2].id);
});
