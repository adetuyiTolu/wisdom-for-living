# Intro film sources

Both films are 1920×1080, 30fps, exactly 30 seconds. They retain the existing
repository-supplied narration and music. No new external footage or audio was
licensed. The book jackets are original illustrative cover studies.

Read each project's AGENTS.md, SPEC.md and REVIEW.md before editing.

Use Node 22+, Chromium and FFmpeg. From each project:

```sh
npm run check
npx hyperframes@0.8.222 snapshot --review
npx hyperframes@0.8.222 preview --background
npx hyperframes@0.8.222 render --quality delivery --output /tmp/master.mp4
```

On a machine with Chromium, set HYPERFRAMES_BROWSER_PATH to its path. On this
managed environment use npm_config_cache=/tmp/wfl-npm, XDG_CACHE_HOME=/tmp/wfl-cache
and XDG_STATE_HOME=/tmp/wfl-state; the account home directory is read-only.

From the repository root, normalize the final masters, enforce a 30-second mux,
create posters and record delivery measurements:

```sh
python video-projects/finalize.py --builders-master /tmp/builders-master.mp4 --books-master /tmp/books-master.mp4
```

DELIVERY.json records actual codec, dimensions, duration and FFmpeg loudness.
Audio is measured, not listened to by the agent. Look at decoded frames before
replacing published films. HyperFrames state and review sheets remain local in
.hyperframes; source, specs and delivery reports are committed.
