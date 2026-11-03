# UI refinement

Refines the existing four-channel layout, dark olive palette, local typefaces,
player frames and expanding channel rail. No new dependency, font or media asset.

## Changes

- Larger, more balanced display type and a shorter introduction that retains
  the seed metaphor, media formats and practical-wisdom purpose.
- Subtle panel contrast, consistent corners and controls, a lighter seed
  watermark and fewer decorative indicators.
- Full channel names in the desktop rail. On phones, all four channel choices
  fit in a two-column selector without a horizontal swipe. Collapsed cards
  use readable horizontal labels; active details align to one left edge.
- More readable channel summaries and links; shorter ZeroToAct and Builders
  descriptions preserve their existing offers.
- Playlists show the item count, newest-first order and one “Now playing”
  label. Reopening reveals the current row by scrolling only the playlist.
- Larger touch controls on tablets as well as phones. The fullscreen control
  moves to the top-right for local films to clear opening titles.

## Verification

- Eleven playback/storage and six component tests.
- Responsive suite: 13 layouts, 320–2560px, including the 820/821px breakpoint
  and short landscape windows; native fullscreen wiring, navigation, video
  geometry, overflow, focus/Escape and saved channel/time/scroll restoration.
- Exact-selection integration: all four COI and 14 ZeroToAct entries on mobile
  and desktop, duplicate/stale events, end-only advancement and resume. Added
  checks for the current row being visible and no page jump on reopening.
- Touch-tablet checks at 1024×768 and 1194×834: 44px controls with no overlap.
- Reviewed all four channel views on 390px and 1440px. External YouTube media
  is blocked in local QA; playlist behavior uses the existing API double.
- UI payload remains below 220KiB (gzip text plus WOFF2). Throttled mobile
  first contentful paint was 3.11s with 4× CPU slowdown and 1.6Mbps/150ms
  emulated networking. Desktop was 0.36s. Measured layout shift was below
  0.002. These are Chromium lab checks, not live-media or device scores.

Existing portrait/landscape handling, translucent COI sidebar, native movie
controls, newest-first playlists and return-visit resume are preserved.


## Playlist overflow repair

Playlist buttons now retain their intrinsic content height instead of shrinking
inside the scrolling flex column. Long titles wrap within the text column; full
titles and the current-item label are preserved. Oversized current items align
to the top of the list when revealed. A new browser regression failed on the
previous layout and checks row padding and non-overlap at 320, 390, 821 and 1440px,
including enlarged text. Additional geometry checks passed at 768, 844, 1024 and
1920px.
