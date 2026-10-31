Run `node --test tests/*.test.cjs` for playback lifecycle checks.

Browser checks use Python Playwright and Chromium. Serve the repository on port
8000, install React 18.3.1, React DOM 18.3.1 and Babel standalone 7.29.0 into a
temporary directory, then set WFL_TEST_DEPS to its node_modules directory and run
`python tests/browser-smoke.py`. The test supplies these pinned dependencies and
blocks external media requests so layout checks do not depend on YouTube/network
availability. Real YouTube autoplay permission must also be checked on a device.

Video projects include their own check, snapshot and render scripts. Reviews and
render measurements are recorded with each project.
