# P1200: what each host lets a page do, as read on 2026-11-26

This file holds the facts that the main session read itself about the hosts. The research file
([research.md](research.md)) holds the web sources, and the brief cites both.

## H1. The Claude Artifact in a browser

- [H1-1] The page runs in a frame on its own origin, `<slug>.frame.claudeusercontent.com`, inside claude.ai. The
  frame's `allow` attribute names eight features, and `serial` and `usb` are not among them:

  ```text
  allow="translator; language-detector; fullscreen; clipboard-write; gamepad; xr-spatial-tracking; screen-wake-lock; autoplay"
  sandbox="allow-scripts allow-same-origin allow-forms allow-pointer-lock allow-popups"
  ```

  E a read-only script in Chrome 158 on macOS, on the PO's private artifact "proj circuit"
  (https://claude.ai/artifact/KaDKtHDuxyvhomGu8a5hn6), 2026-11-26 15:08 CET. The script read the attributes of the
  `iframe` elements and changed nothing · caveat: one artifact, one browser, one day. The host can change the
  attribute at any time.
- [H1-2] The top page claude.ai itself allows `serial` and `usb` by its own policy. The `allowsFeature` call gave true
  for both. If the frame's `allow` attribute does not name a feature, a frame of another origin does not get it. So
  the top page's policy does not reach the frame · E the same script · E the Web Serial standard. The `serial` feature's
  default allowlist is `'self'`. Chromium checks it before `requestPort()` (research.md, question 1 and the
  summary's lines 2 and 3, https://serial.spec.whatwg.org/, read 2026-11-26) · caveat: the result follows from the
  read attribute and the standard. Nobody pressed a "pick a port" button inside an artifact.
- [H1-3] The page runs under a content security policy. Scripts load inline or from cdnjs.cloudflare.com,
  cdn.jsdelivr.net/npm/, unpkg.com and a few others. A `fetch`, an XMLHttpRequest or a WebSocket to another host is
  blocked. The frame refuses a download that the page starts. The `downloads` capability lifts that · E the
  claude-artifacts server's guide, topic "pages", read 2026-11-26 15:05 CET.
- [H1-4] The frame refuses camera, microphone, location, service workers and WebRTC. The guide does not name serial or
  USB · E the same guide · caveat: H1-1 is the direct evidence for serial and USB.
- [H1-5] The `files` capability reads a Claude Code project's files as the viewer: `list` and `read`, with a `revision`.
  It needs the project's id (`chan_...`), and it cannot write · E describe_capabilities "files", contract 0.2.99, read
  2026-11-26 · caveat: whether a local spark project folder has such an id was not checked.

## H2. The Claude Artifact installed as a desktop app

- [H2-1] The Claude desktop app can install an artifact as an app with its own window. In that window, and only there,
  `claude.use("desktop")` gives three modules: `fs` reads and writes files, `childProcess` runs a program, and `pty`
  opens a terminal. Each needs the `"full-access"` permission. The page declares it in a manifest tag. The person
  allows it in a dialog · E describe_capabilities "desktop" with its types, contract 0.2.99, read 2026-11-26 15:06 CET.
- [H2-2] `"full-access"` is allowed only on an artifact of the person's own organization that no one outside it wrote
  in, or one written by an owner Anthropic approved. In a browser, the artifact panel and the mobile apps, only
  `install` exists · E the same types · caveat: a public spark page for other people does not get it.
- [H2-3] If the page declares camera, microphone or location, the desktop window grants them. The types do not name
  serial or USB · E the same types · caveat: whether Web Serial works in that window was not tested. With
  `childProcess`, the page can run spark's own deploy command instead, so the browser needs no serial access.
- [H2-4] An Allow of a permission lasts until a newer published version of the artifact loads, and then the next call
  asks again · E the same types · caveat: spark republishes the page after each request today (the `/spark:page`
  command's description), so the person can see this dialog often.

## H3. A local server on the person's computer, and H4. a server of spark's own

The facts for these two hosts are in research.md, questions 1 and 9.
