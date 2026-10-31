# Authorized work and continuation

The user authorized implementing, committing and merging these changes without
further routine confirmation. Continue unfinished work after an interruption.
Do not claim automatic thread execution: no automation/scheduling tool is exposed
in this session. This file preserves context when a new session opens the repo.

- [x] Newest-first curated playback and sound: PR #31 merged.
- [x] Mobile navigation, controls, inline playback: PR #32 merged.
- [x] Resume channel, video, timestamp and scroll: implementation and reload tests
  pass; PR creation and merge next on branch fix/resume-viewing.
- [ ] Rebuild the two local intro films (The Builders and Books), each exactly
  30 seconds. Existing projects are video-projects/the-builders and books.
  Read their AGENTS.md, HyperFrames skills, check, snapshot, review, render,
  measure, replace videos/*.mp4, commit, PR and merge.
- [ ] Final verification and links to merged PRs; candidly report restrictions.

Browser: range-capable server port 8001. Python Playwright + /usr/bin/chromium.
Test dependencies: /tmp/wfl-browser-deps/node_modules. Run
`python tests/browser-smoke.py`, `node tests/playback.test.cjs`.

HyperFrames CLI is pinned 0.8.222; use npm_config_cache=/tmp/wfl-npm.
Installed skills available under
/tmp/wfl-npm/_npx/1eaf384c6202202f/node_modules/hyperframes/dist/skills/.
The default home is not writable: use writable, task-specific config/cache flags,
never repurpose HOME or CODEX_HOME. Network calls require additional network access.
YouTube is blocked in this environment, so live dates/playback cannot be checked.
