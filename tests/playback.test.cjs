const {test}=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const vm=require('node:vm');
function setup(element, YT, saved=null) {
 const events={}; let sound, stored, writes=0, now=1000;
 element.addEventListener=(name,handler)=>events[name]=handler;
 element.removeEventListener=name=>delete events[name];
 const context={Date:{now:()=>now},window:{YT,addEventListener(){},removeEventListener(){},scrollY:0},YT, localStorage:{getItem:()=>JSON.stringify(saved),setItem(key,value){stored=JSON.parse(value);writes++}},setInterval:()=>1,clearInterval(){},document:{querySelector:()=>element,addEventListener(){},removeEventListener(){}},console};
 vm.createContext(context); vm.runInContext(fs.readFileSync('playback.js','utf8'),context);
 const playback=new context.window.WFLPlayback(value=>sound=value);
 playback.bind(); return {playback,events,sound:()=>sound,stored:()=>stored,writes:()=>writes,advance:ms=>now+=ms,context};
}
test('local video unmutes and plays after interaction',()=>{
 const video={tagName:'VIDEO',readyState:0,muted:true,paused:false,play:()=>Promise.resolve()};
 const {playback}=setup(video); playback.enableSound(); assert.equal(video.muted,false);
});
test('blocked audible autoplay falls back to muted playback and keeps prompt',async()=>{
 let calls=0;
 const video={tagName:'VIDEO',readyState:0,muted:true,play:()=>++calls===1?Promise.reject(new Error('NotAllowedError')):Promise.resolve()};
 const {playback,sound}=setup(video); playback.enableSound(); await Promise.resolve();
 assert.equal(video.muted,true);assert.equal(calls,2);assert.equal(sound(),false);
});
test('YouTube readiness unmutes; blocked autoplay falls back safely',async()=>{
 let options, muted=true,plays=0;
 const player={unMute(){muted=false},mute(){muted=true},setVolume(){},playVideo(){plays++},isMuted:()=>muted,getPlayerState:()=>1};
 const YT={Player:function(el,opts){options=opts;return player}};
 const {sound}=setup({tagName:'IFRAME'},YT);await Promise.resolve();options.events.onReady();
 assert.equal(muted,false);assert.equal(sound(),true);
 options.events.onAutoplayBlocked();assert.equal(muted,true);assert.equal(sound(),false);assert.equal(plays,2);
});
test('saved sessions validate channel and discard removed videos',()=>{
 const context={window:{},localStorage:{getItem:()=>JSON.stringify({version:1,positions:{},active:1,activeVideoIndex:0,videoId:'removed',scrollY:80})}};
 vm.createContext(context);vm.runInContext(fs.readFileSync('playback.js','utf8'),context);
 const saved=context.window.WFLPlayback.restore([{videos:[{id:'current'}]},{}]);
 assert.equal(saved.manualVideoId,null);assert.equal(saved.activeVideoIndex,0);assert.equal(saved.scrollY,80);
});
test('corrupted or unavailable storage never prevents playback',()=>{
 const context={window:{},localStorage:{getItem(){throw Error('denied')}}};
 vm.createContext(context);vm.runInContext(fs.readFileSync('playback.js','utf8'),context);
 assert.equal(context.window.WFLPlayback.restore([{}]),null);
});
test('YouTube restores the saved timestamp before recording progress',async()=>{
 let options,time=0;
 const player={getVideoData:()=>({video_id:'saved-video'}),getCurrentTime:()=>time,seekTo(value){time=value},unMute(){},setVolume(){},playVideo(){},isMuted:()=>false,getPlayerState:()=>1};
 const YT={Player:function(el,opts){options=opts;return player}};
 const saved={version:1,positions:{'youtube:saved-video':42.5}};
 const {playback,stored}=setup({tagName:'IFRAME'},YT,saved);
 playback.bind({active:1,activeVideoIndex:1,manualVideoId:'saved-video'});
 await Promise.resolve();options.events.onReady();assert.equal(time,42.5);
 time=48;playback.capture();assert.equal(stored().positions['youtube:saved-video'],48);
 assert.equal(stored().videoId,'saved-video');
});
test('time updates throttle storage but pausing flushes the latest position',()=>{
 const video={tagName:'VIDEO',readyState:1,muted:true,paused:false,duration:30,currentTime:1,getAttribute:()=>'/intro.mp4',play:()=>Promise.resolve()};
 const {playback,events,writes,stored,advance,context}=setup(video);
 playback.bind({active:2,activeVideoIndex:2});playback.capture();
 for(let t=2;t<=8;t++) {video.currentTime=t;events.timeupdate();}
 assert.equal(writes(),1);
 events.pause();assert.equal(writes(),2);assert.equal(stored().positions['local:/intro.mp4'],8);
 playback.capture(true);assert.equal(writes(),2,'identical snapshots are not rewritten');
 context.document.visibilityState='hidden';video.currentTime=9;advance(2000);playback.tick();assert.equal(writes(),2);
});
test('muted autoplay retries once when the browser blocks all playback',async()=>{
 let options,plays=0;
 const player={mute(){},playVideo(){plays++}};
 const YT={Player:function(el,opts){options=opts;return player}};
 setup({tagName:'IFRAME'},YT);await Promise.resolve();
 options.events.onAutoplayBlocked();options.events.onAutoplayBlocked();
 assert.equal(plays,1);
});
test('explicit playlist choices restart only that video; other resume positions remain',()=>{
 const saved={version:1,positions:{'youtube:selected':29,'youtube:other':12}};
 const {playback}=setup({tagName:'VIDEO',readyState:0},undefined,saved);
 playback.restartVideo('selected');
 assert.equal(playback.positions['youtube:selected'],0);
 assert.equal(playback.positions['youtube:other'],12);
});
