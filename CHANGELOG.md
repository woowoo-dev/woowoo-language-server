# Changelog

All notable changes to the WooWoo Language Server are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

The changelog starts with version 1.2.0; earlier releases are documented in the commit
history only.

## [1.2.0] - 2026-10-24

### Added

- The bundled FIT-Math dialect (`dialects/fit_math.yaml`) marks the `equation`, `align`
  and `gather` outer environments with `math: true`. This lets `wuff` recognise them as
  math environments, so it highlights their bodies and highlights anonymous (indented)
  blocks as LaTeX without duplicating what the client's own grammar already colours.
  A `wuff` that ignores the key stays unaffected.

### Changed

- The dialect version is now 1.1.0 (`version_code: 2`) — the first bump since the dialect
  was introduced at 1.0.0.
- README: the *Semantic Highlighting* section no longer claims the server highlights only
  meta-blocks. It now documents anonymous (indented) math blocks as the second construct
  that a client-side TextMate grammar cannot recognise, and the `math: true` requirement
  that goes with it.

### Requirements

- Anonymous math highlighting requires `wuff` 1.3.0 or newer. With an older `wuff` the
  dialect key is ignored and the server behaves as before.
