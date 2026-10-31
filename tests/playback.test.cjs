const {test}=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const vm=require('node:vm');
function setup(element, YT) {
 const events={}; let sound;
 element.addEventListener=(name,handler)=>events[name]=handler;
 element.removeEventListener=name=>delete events[name];
 const context={window:{YT},YT, document:{querySelector:()=>element},console};
 vm.createContext(context); vm.runInContext(fs.readFileSync('playback.js','utf8'),context);
 const playback=new context.window.WFLPlayback(value=>sound=value);
 playback.bind(); return {playback,events,sound:()=>sound};
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
