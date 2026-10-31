# First-party UI assets

React and React DOM are the unchanged 18.3.1 production UMD files from npm. Their
versioned filenames may be cached immutably; licenses are in vendor/. When
upgrading, change the versioned filenames, index.html script URLs, support.js
fallback URLs and integrity hashes together.

Inter and JetBrains Mono are Latin variable WOFF2 files from
@fontsource-variable/inter@5.2.8 and @fontsource-variable/jetbrains-mono@5.2.8.
Space Grotesk reuses the font already supplied with the video projects. Font
licenses are included alongside the files. All families use font-display: swap.

No browser connection to a script/font CDN is needed for the site UI. YouTube
media, player API and thumbnails still use YouTube's own services.
