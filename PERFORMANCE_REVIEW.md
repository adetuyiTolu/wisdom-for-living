# Responsive and performance review

The UI no longer depends on unpkg or Google Fonts to render. Pinned React
production files and licensed WOFF2 fonts are served from the same origin, scripts
are deferred, and the headline font is preloaded. Versioned vendor scripts have
immutable cache headers for Netlify. Posters and full-size player layouts remain.

Playback time updates now throttle synchronous storage writes to at most once per
second, skip unchanged snapshots and stop background polling work when hidden.
Pause/seek/pagehide/channel changes still flush immediately. Selecting the active
channel no longer reloads the video. Blocked muted autoplay retries only once.

For usability, channel cards support Enter/Space, the channel list uses native
buttons, invisible card links are removed from the tab order, playlists support
Escape and focus return, and content has a main landmark. Short desktop windows
scroll instead of squeezing content. Tablet headlines scale to width, mobile
collapsed cards show full channel names, and vector arrows avoid missing glyphs.
The fullscreen button remains visible on every channel, without reserved spacing.

## Verification

- Browser suite: 13 layouts, 320–2560px; portrait, landscape, breakpoint edges,
  keyboard input, playlist focus, fullscreen wiring, no overflow/hero clipping,
  local film geometry and return-visit playback/scroll restoration.
- Eight unit checks: audio policy fallback, blocked-playback retry cap, storage
  errors, saved YouTube time, write throttling, forced flushes and hidden polling.
- Local reduced-motion performance check: UI payload about 185KiB (gzip text plus
  WOFF2; excludes logos and video/player downloads), below the 220KiB test budget.
- Mobile preview with 4x CPU slowdown, 150ms latency and 1.6Mbps throughput:
  first contentful paint 3.30s; cumulative layout shift 0.00114.
- Unthrottled desktop preview: first contentful paint 0.38s; layout shift 0.00006.
- No requests to external script/font CDNs in either loading check.

Measurements use the local preview, which does not gzip text responses, so the
payload budget is a compressed-size estimate, not measured production transfer.
These are not Lighthouse scores or real-user Core Web Vitals. YouTube requests
are blocked in this environment; production media loading, Safari fullscreen,
and device-specific autoplay permission remain outside this verification.
