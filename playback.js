/* Shared media lifecycle. YouTube owns autoplay permission; a visible sound button
   remains available when a browser requires a gesture. */
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
  class Playback {
    constructor(onSound) { this.onSound = onSound; }
    bind() {
      const element = document.querySelector('[data-wfl-video]');
      if (!element || element === this.element) return;
      this.release();
      this.element = element;
      if (element.tagName === 'VIDEO') {
        this.change = () => this.onSound(!element.muted && !element.paused);
        element.addEventListener('volumechange', this.change);
        element.addEventListener('play', this.change);
        this.loaded = () => this.enableSound();
        element.addEventListener('loadeddata', this.loaded);
        if (element.readyState >= 2) this.enableSound();
      } else {
        youtubeReady().then(() => {
          if (this.element !== element) return;
          this.player = new YT.Player(element, { events: {
            onReady: () => this.enableSound(),
            onStateChange: () => this.onSound(!this.player.isMuted() && this.player.getPlayerState() === 1),
            onAutoplayBlocked: () => {
              this.player.mute(); this.player.playVideo(); this.onSound(false);
            }
          }});
        });
      }
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
      }
      // Do not destroy the iframe: it belongs to the component renderer.
      this.player = null;
      this.element = null;
    }
    destroy() { this.release(); }
  }
  window.WFLPlayback = Playback;
})();
