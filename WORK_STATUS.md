# Authorized work and continuation

The user authorized implementing, committing and merging these changes without
further routine confirmation. Continue unfinished work after an interruption.
Do not claim automatic thread execution: no automation/scheduling tool is exposed
in this session. This file preserves context when a new session opens the repo.

- [x] Newest-first curated playback and sound: PR #31 merged.
- [x] Mobile navigation, controls, inline playback: PR #32 merged.
- [x] Resume channel, video, timestamp and scroll: PR #33 merged;
  browser reload and YouTube timestamp tests pass.
- [x] Rebuild the two local intro films (The Builders and Books), each exactly
  30 seconds. Full checks and visual reviews pass; final MP4s, posters,
  editable sources and measured delivery reports are included.
- [x] Final browser checks at 320/390/768/1440px; six playback/storage tests pass.
- [x] Film replacements merged in PR #35.
- [x] Remove the custom sound button and enlarge YouTube playback. ZeroToAct
  spans the full desktop right column; narrower desktops use a playlist overlay.
  Builders/Books sources and layout are preserved. Six screen widths and six
  playback tests pass; PR #36 is merged.
- [x] Builders and Books now maximize their player frame without the old control
  padding; cover posters load before video, and native controls keep the artwork
  unobstructed. Six screen widths and saved playback restoration verified; PR #37 merged.
- [x] COI uses its full landscape player without the reserved 48px/60px control
  strip. Playlist controls overlay the top corner; native fullscreen stays
  available. All six screen widths and playback/storage checks pass; PR #38 merged.
- [x] Restore the visible Full screen button on every channel as an overlay.
  Compact COI playlist controls on mobile so the fullscreen label remains
  visible without overlap or reserved player space. Browser checks cover
  fullscreen API wiring for both YouTube and local videos; PR #39 merged.
- [x] Responsive/performance/UX review: first-party deferred UI libraries and
  licensed fonts, storage-write throttling, keyboard navigation, playlist focus,
  short-window layouts, readable channel labels and responsive typography.
  All 13 layout scenarios and eight playback checks pass, plus throttled
  first-paint/layout-shift and first-party-loading checks; PR #40 merged.
  See PERFORMANCE_REVIEW.md.
- [x] ZeroToAct selection sync: explicit choices recreate the player even when
  reselecting the original embed after auto-advance, start selected videos at
  zero, and expose the API-tracked current row. Nine playback checks, four
  component checks and all 13 choices on desktop/mobile API simulations pass.
  Return visits still resume. Live YouTube titles/media remain unverified (403);
  PR #41 merged.
- [x] COI desktop playlist opens as a translucent sidebar and stays open after
  choosing a video. Mobile retains its dismissing overlay. Opening/closing
  preserves the current iframe; transparency and side-by-side geometry verified
  across all 13 layouts. Portrait overlay behavior remains unchanged.

Automatic execution after session expiry is unavailable: no automation tool is
exposed. Reopening this repository preserves these instructions but does not
itself schedule an agent.

Browser: range-capable server port 8001. Python Playwright + /usr/bin/chromium.
UI dependencies are bundled; use Python Playwright and Chromium. Run
`python tests/browser-smoke.py`, `node tests/playback.test.cjs`.

HyperFrames CLI is pinned 0.8.222; use npm_config_cache=/tmp/wfl-npm.
Installed skills available under
/tmp/wfl-npm/_npx/1eaf384c6202202f/node_modules/hyperframes/dist/skills/.
The default home is not writable: use writable, task-specific config/cache flags,
never repurpose HOME or CODEX_HOME. Network calls require additional network access.
YouTube is blocked in this environment, so live dates/playback cannot be checked.
