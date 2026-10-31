/* Shared media lifecycle. YouTube owns autoplay permission; viewers can use
   the native player controls when their browser requires a gesture for sound. */
(() => {
  let api;
  function youtubeReady() {
    if (window.YT?.Player) return Promise.resolve();
    if (!api) api = new Promise(resolve => {
      const previous = window.onYouTubeIframeAPIReady;
      window.onYouTubeIframeAPIReady = () => { previous?.(); resolve(); };
      const script = document.createElement('script');
      script.src = 'https://www.youtube.com/iframe_api';
      script.async = true;
      document.head.appendChild(script);
    });
    return api;
  }
  const STORAGE_KEY = 'wfl.watch.v1';
  function readSession() {
    try {
      const value = JSON.parse(localStorage.getItem(STORAGE_KEY));
      return value?.version === 1 && value.positions && typeof value.positions === 'object' ? value : null;
    } catch { return null; }
  }
  class Playback {
    static restore(pillars) {
      const saved = readSession();
      if (!saved || !Number.isInteger(saved.activeVideoIndex) || !pillars[saved.activeVideoIndex]) return null;
      const pillar = pillars[saved.activeVideoIndex];
      const id = pillar.videos?.some(v => v.id === saved.videoId) ? saved.videoId : null;
      return {
        active: Number.isInteger(saved.active) && pillars[saved.active] ? saved.active : saved.activeVideoIndex,
        activeVideoIndex: saved.activeVideoIndex, manualVideoId: id,
        playlistOpen: saved.playlistOpen === true,
        scrollY: Number.isFinite(saved.scrollY) ? Math.max(0, saved.scrollY) : 0
      };
    }
    constructor(onSound, onVideo, onEnded) {
      this.onSound = onSound;
      this.onVideo = onVideo;
      this.onEnded = onEnded;
      this.positions = readSession()?.positions || {};
      this.flush = () => this.capture(true);
      this.tick = () => { if (document.visibilityState !== 'hidden') this.capture(); };
      this.hidden = () => { if (document.visibilityState === 'hidden') this.capture(true); };
      window.addEventListener('pagehide', this.flush);
      document.addEventListener('visibilitychange', this.hidden);
      this.poll = setInterval(this.tick, 1000);
    }
    bind(context) {
      this.context = context || this.context;
      const element = document.querySelector('[data-wfl-video]');
      if (!element || element === this.element) return;
      this.release();
      this.element = element;
      this.restoredKey = null;
      this.mutedAutoplayTried = false;
      this.endedHandled = false;
      this.pendingVideoId = null;
      if (element.tagName === 'VIDEO') {
        this.change = () => this.onSound(!element.muted && !element.paused);
        element.addEventListener('volumechange', this.change);
        element.addEventListener('play', this.change);
        this.loaded = () => { this.restoreTime(); this.enableSound(); };
        element.addEventListener('loadedmetadata', this.loaded);
        element.addEventListener('pause', this.flush);
        element.addEventListener('seeked', this.flush);
        element.addEventListener('timeupdate', this.tick);
        element.addEventListener('loadeddata', this.loaded);
        if (element.readyState >= 1) { this.restoreTime(); this.enableSound(); }
      } else {
        youtubeReady().then(() => {
          if (this.element !== element) return;
          this.player = new YT.Player(element, { events: {
            onReady: () => {
              if (this.element !== element) return;
              const id = this.context?.videoId || this.context?.manualVideoId;
              if (id && this.player.loadVideoById) {
                this.pendingVideoId = id;
                const saved = this.positions[`youtube:${id}`];
                this.player.loadVideoById({ videoId: id, startSeconds: Number.isFinite(saved) && saved >= 0 ? saved : 0 });
              }
              this.restoreTime(); this.enableSound();
            },
            onStateChange: (event = {}) => {
              if (this.element !== element || !this.player) return;
              this.onSound(!this.player.isMuted() && this.player.getPlayerState() === 1);
              this.restoreTime();
              this.capture();
              const state = event.data ?? this.player.getPlayerState();
              if (state === 1) this.endedHandled = false;
              if (state === 0 && this.mediaKey() && !this.endedHandled) {
                this.endedHandled = true;
                this.onEnded?.();
              }
            },
            onAutoplayBlocked: () => {
              if (this.element !== element || !this.player) return;
              this.onSound(false);
              if (!this.mutedAutoplayTried) {
                this.mutedAutoplayTried = true;
                this.player.mute(); this.player.playVideo();
              }
            }
          }});
        });
      }
    }
    mediaKey() {
      if (!this.element) return null;
      if (this.element.tagName === 'VIDEO') return `local:${this.element.getAttribute('src')}`;
      const id = this.player?.getVideoData?.().video_id;
      // Ignore transitional metadata for another video until the exact request
      // has been acknowledged. Late events must not move the current row.
      if (this.pendingVideoId && id !== this.pendingVideoId) return null;
      if (id === this.pendingVideoId) this.pendingVideoId = null;
      return id ? `youtube:${id}` : null;
    }
    // An explicit playlist choice starts that video, rather than resuming near
    // its previous ending and immediately advancing again. Return visits retain
    // their saved timestamp because restoration does not call this method.
    restartVideo(id) {
      this.positions[`youtube:${id}`] = 0;
    }
    restoreTime() {
      const key = this.mediaKey();
      if (!key || this.restoredKey === key) return;
      this.restoredKey = key;
      const seconds = this.positions[key];
      if (!Number.isFinite(seconds) || seconds < 0) return;
      if (this.element.tagName === 'VIDEO') {
        const duration = this.element.duration;
        this.element.currentTime = Number.isFinite(duration) ? Math.min(seconds, Math.max(0, duration - 0.1)) : seconds;
      } else this.player.seekTo(seconds, true);
    }
    capture(force = false) {
      if (!this.context) return;
      const key = this.mediaKey();
      const seconds = this.element?.tagName === 'VIDEO' ? this.element.currentTime : this.player?.getCurrentTime?.();
      if (key && Number.isFinite(seconds) && seconds >= 0 && this.restoredKey === key) this.positions[key] = seconds;
      const id = key?.startsWith('youtube:') ? key.slice(8) : null;
      if (id && id !== this.currentId) { this.currentId = id; this.onVideo?.(id); }
      try {
        const now = Date.now();
        if (!force && this.savedAt !== undefined && now - this.savedAt < 1000) return;
        const snapshot = JSON.stringify({
          version: 1, ...this.context, videoId: id || this.context.manualVideoId,
          positions: this.positions, scrollY: window.scrollY
        });
        if (snapshot !== this.savedSnapshot) {
          localStorage.setItem(STORAGE_KEY, snapshot);
          this.savedSnapshot = snapshot;
        }
        this.savedAt = now;
      } catch { /* Playback stays available in private mode or when storage is full. */ }
    }
    enableSound() {
      const element = this.element;
      if (!element) return;
      if (element.tagName === 'VIDEO') {
        element.muted = false;
        const attempt = element.play();
        attempt?.catch(() => {
          element.muted = true;
          element.play()?.catch(() => {});
          this.onSound(false);
        });
      } else if (this.player?.unMute) {
        this.player.unMute(); this.player.setVolume(100); this.player.playVideo();
        this.onSound(!this.player.isMuted());
      }
    }
    release() {
      if (this.element?.tagName === 'VIDEO') {
        this.element.removeEventListener('volumechange', this.change);
        this.element.removeEventListener('play', this.change);
        this.element.removeEventListener('loadeddata', this.loaded);
        this.element.removeEventListener('loadedmetadata', this.loaded);
        this.element.removeEventListener('pause', this.flush);
        this.element.removeEventListener('seeked', this.flush);
        this.element.removeEventListener('timeupdate', this.tick);
      }
      // React owns connected DOM. Once it has replaced an iframe, dispose of
      // YouTube's detached player and message listeners as well.
      if (this.player?.getIframe && !this.element?.isConnected) this.player.destroy();
      this.player = null;
      this.element = null;
    }
    destroy() {
      this.capture(true);
      clearInterval(this.poll);
      window.removeEventListener('pagehide', this.flush);
      document.removeEventListener('visibilitychange', this.hidden);
      this.release();
    }
  }
  window.WFLPlayback = Playback;
})();
