Run `node tests/playback.test.cjs` for eight playback/storage checks.

Browser checks use Python Playwright and Chromium. Run `python tests/serve.py`
from the repository (port 8001), then `python tests/browser-smoke.py`. Set
WFL_TEST_URL to another local preview if needed. UI libraries/fonts are bundled;
no npm test dependencies or external UI assets are required.

The browser suite checks 13 phone/tablet/desktop layouts from 320 to 2560px,
including 820/821px breakpoints and short landscape windows. It checks overflow,
hero clipping, fullscreen button wiring/overlap, playlist controls, Escape/focus
return, keyboard channel selection, avoiding active-channel reloads, both local
films, and saved playback/scroll restoration. Screenshots are written to /tmp.
External media requests are blocked deliberately, so this is not a live YouTube
playback or autoplay-permission test. Real device Safari fullscreen still needs
a device check.

Run `python tests/performance-smoke.py` for a 220KiB compressed UI budget, first
paint and layout-shift checks, first-party UI loading, and reduced-motion support.
The mobile case emulates 4x CPU slowdown, 150ms latency and 1.6Mbps throughput.
These are local Chromium checks, not Lighthouse scores or production field data.
See PERFORMANCE_REVIEW.md for the measured results and limitations.

Video projects have their own checks and render measurements; film source and
media are unchanged by this optimization pass.
