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
  across all 13 layouts. Portrait overlay behavior remains unchanged; PR #42 merged.
- [x] Replace native YouTube URL queues for both COI and ZeroToAct with single
  video embeds plus explicit loadVideoById. Only a confirmed ENDED event advances
  the site list, with duplicate-event protection. All 17 choices pass adversarial
  player simulations on mobile/desktop, including wrong initial metadata,
  next/previous, end wrapping, stale events and saved-position restoration.
  Eleven playback and six component checks pass; live media remains blocked.


- [x] Added “Nobody Went First” (`ur2qzPD1Yds`) first in ZeroToAct's playlist,
  preserving all 13 existing entries. The official Signal dated 1 November 2026
  embeds that ID and YouTube metadata confirms the title:
  https://www.zerotoact.com/signals/nobody-went-first/
  All eleven playback and six component checks pass. The playlist browser suite
  verifies all 14 ZeroToAct choices and all four COI choices at 390/1440px with
  the adversarial API double; this does not verify live media playback.


- [x] Refined the existing UI: display type and concise introduction; quieter
  panels and controls; readable channel names; all four mobile choices visible
  in a two-column menu; clearer current-video status and automatic playlist
  reveal without page jumps. Enlarged controls on touch tablets and moved the
  local-film fullscreen button away from opening titles. Same four-channel
  structure, media, newest-first order, fullscreen and resume behavior.
  Relevant playback, component, 13-layout, exact-selection and performance
  checks pass. See UI_REFINEMENT.md for evidence and scope.


- [x] Fixed COI and ZeroToAct playlist title overflow. Rows no longer shrink
  below their content, titles wrap inside their buttons, and oversized current
  items open at their top rather than hiding the beginning. The new geometry
  regression reproduced the original defect before the fix. Checks cover row
  padding, neighbouring-row separation, enlarged labels and exact playback.

- [x] Moved YouTube fullscreen/previous/next/playlist controls into a compact
  toolbar below the picture so native volume controls stay accessible. Retained
  full-frame aspect ratios, translucent desktop COI sidebar and local-film controls.
- [x] Explicit playlist, next/previous and channel choices request audible
  playback immediately; the API still retries muted if a browser blocks sound.
  Return visits retain the initial autoplay policy and saved viewing position.
- [x] Updated the introduction to include “practical wisdom that helps build
  lives, homes, businesses and nations.” Removed the decorative hero watermark,
  softened active-channel accents and simplified control/status typography.
  Eleven playback and eight component checks, all 13 responsive layouts and all
  18 playlist choices across four widths pass. UI payload is 191,307 bytes;
  throttled mobile FCP 3.14s, desktop 0.42s, CLS below 0.001. Live YouTube media
  remains blocked in this environment; playlist/audio assertions use the API double.

- [x] ZeroToAct playlist rows now show each video's publish date under its
  title (muted label, `[data-playlist-date]`). Dates for 15 of 17 videos are
  exact, sourced from zerotoact.com's own Signal archive (confirmed via its
  `/signals/feed.xml` RSS feed, cross-checked against YouTube's own relative
  "X ago" labels). The two oldest videos ("ZeroToAct Weekly Brief..." and
  "ZeroToAct: The Execution Movement...") predate the Signal-article format
  and have no matching archive entry; these show a month-only approximate
  date ("Sep 2026" / "Aug 2026") rather than a fabricated exact day. Fixed the
  playlist order itself in the same pass: the two approximate-date videos were
  sitting out of chronological order. `tests/playlist-browser.py` had a stale
  hardcoded ZeroToAct count of 14 (from before 3 videos were added in an
  earlier session); updated to 17. All four test files pass:
  `browser-smoke.py` (14 layouts), `playback.test.cjs` (11), `playlist.test.cjs`
  (8), `playlist-browser.py` (8, all 17+4 exact-ID choices across 4 widths),
  plus `performance-smoke.py` (payload/FCP/CLS budgets). COI was left out of
  scope (not asked for); it still has no per-video date field.

- [x] Added Global Builder Summit as a new Wisdom for Living initiative/pillar,
  distinct from "The Builders" reality series: it's the annual gathering where
  builders prepare for the new year with practical insight into their local and
  global economy (same premise pitched on zerotoact.com's summit). New tab uses
  a mountain/summit icon (vs. Builders' bar-chart icon) and copy that names it
  as a gathering, not a series. Domain `globalbuildersummit.com` is shown as
  plain, non-clickable text with a "Coming soon" badge since the site doesn't
  resolve yet. Inserted as the second pillar (after ZeroToAct), which renumbered
  the hand-authored tab blocks for Builders (2→3) and Books (3→4) — the Pillar
  list sidebar and mobile nav are `sc-for`-driven and needed no changes. Fixed
  stale hardcoded indices in `tests/browser-smoke.py` that assumed Builders was
  at index 2 (channel count 4→5, selection indices, and the reload
  `activeVideoIndex` assertion). All five test files pass: `browser-smoke.py`
  (14 layouts), `playback.test.cjs` (11), `playlist.test.cjs` (8),
  `playlist-browser.py` (8), `performance-smoke.py` (payload/FCP/CLS budgets).
  No standalone logo asset was made; the inline SVG icon follows the site's
  existing per-pillar icon pattern.
- [x] Replaced the placeholder mountain icon with the user-supplied Global
  Builder Summit logo mark (gold ascending steps + cream skyline/baseline,
  120x120 viewBox) in both the expanded and collapsed tab states. Kept its own
  brand colors (#C9A24A / #F4EDE0) rather than the shared `accentColor`, since
  it's a distinct brand mark. All 14 `browser-smoke.py` layout checks re-pass;
  verified via Playwright screenshots at desktop and mobile widths.
- [x] Global Builder Summit is live at globalbuildersummit.com. Removed the
  "Coming soon" badge, replaced the plain domain text with a clickable
  external link (matching the Chronicles of Innovation/ZeroToAct pattern),
  and removed `comingSoon` from its `pillarsData` entry so the sidebar no
  longer shows a "Soon" tag for it (The Builders/Books remain coming soon).
  All 14 `browser-smoke.py` and all 8 `playlist-browser.py` checks pass.
- [x] Added the user-supplied Global Builder Summit video (`videos/global-builder-summit.mp4`,
  ~60s, 1920x1080, with audio) as its `localVideo`, with a poster frame extracted
  from the clip (`videos/global-builder-summit-poster.jpg`). Selecting the
  Summit tab now plays this film, same as The Builders/Books. Extended
  `tests/browser-smoke.py`'s local-film full-frame loop to cover pillar index 2
  (Global Builder Summit) alongside 3/4 (Builders/Books).
- [x] Fixed the active-pillar indicator bar in the right-column Pillar list
  (under the video player): its height was hardcoded to 25% (correct only for
  4 pillars), so after Global Builder Summit became the 5th pillar the bar no
  longer matched each row's height/position, especially for later rows
  (Builders, Books). Now computed as `100 / pillarsData.length`, so it stays
  correct regardless of pillar count. Verified via Playwright that the
  indicator's vertical center falls within each visible row's bounds for all
  pillars (ZeroToAct intentionally hides this sidebar on desktop, unchanged).
  All 14 `browser-smoke.py`, all 8 `playlist-browser.py`, 11 `playback.test.cjs`,
  8 `playlist.test.cjs`, and `performance-smoke.py` budgets pass.

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
YouTube's individual watch pages (youtube.com/watch?v=...) return a bot-check
wall in this environment, even with pacing between requests, so live playback
and per-video metadata cannot be scraped that way. YouTube's playlist pages
(youtube.com/playlist?list=...) work fine and return real titles plus coarse
relative-time labels ("3mo ago"). zerotoact.com is not blocked at all and is
the better source for exact ZeroToAct dates going forward; check its
`/signals/` archive and `/signals/feed.xml` RSS feed before resorting to
YouTube scraping or approximation.
