const {test}=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const vm=require('node:vm');
function setup(element, YT, saved=null) {
 const events={}; let sound, stored;
 element.addEventListener=(name,handler)=>events[name]=handler;
 element.removeEventListener=name=>delete events[name];
 const context={window:{YT,addEventListener(){},removeEventListener(){},scrollY:0},YT, localStorage:{getItem:()=>JSON.stringify(saved),setItem(key,value){stored=JSON.parse(value)}},setInterval:()=>1,clearInterval(){},document:{querySelector:()=>element,addEventListener(){},removeEventListener(){}},console};
 vm.createContext(context); vm.runInContext(fs.readFileSync('playback.js','utf8'),context);
 const playback=new context.window.WFLPlayback(value=>sound=value);
 playback.bind(); return {playback,events,sound:()=>sound,stored:()=>stored};
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
