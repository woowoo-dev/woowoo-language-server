# Changelog

All notable changes to the WooWoo Language Server are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

The changelog starts with version 1.2.0; earlier releases are documented in the commit
history only.

## [Unreleased]

### Added

- `tests/smoke_test.py` starts the server over stdio and checks the main requests. The
  *Test* workflow runs it on every pull request with Python 3.10 to 3.15.
- `AGENTS.md` with the rules for working on the server.

## [1.2.0] - 2026-10-31

### Added

- `requirements.txt` declares the runtime dependencies of the server (`pygls` 1.3.0,
  `lsprotocol` 2023.0.1 and `wuff` 1.3.0 or newer). Until now the pins existed only in
  the VS Code extension, so the repository did not state which pygls it needs.
- The bundled FIT-Math dialect (`dialects/fit_math.yaml`) marks the `equation`, `align`
  and `gather` outer environments with `math: true`. This lets `wuff` recognise them as
  math environments, so it highlights their bodies and highlights anonymous (indented)
  blocks as LaTeX without duplicating what the client's own grammar already colours.
  A `wuff` that ignores the key stays unaffected.
- The dialect is in sync with the fit-pdf and fit-html templates again: the wobjects
  `Concept`, `Video` and `Procedure` and the environments `paragraph`, `youtube`,
  `geogebra`, `pseudocode` and `dot` were added, together with the meta keys those
  templates accept (`nonumber` on the numbered wobjects, `noindent` on `paragraph`,
  `playlist` and `aspect` on `youtube`, `linenumber` on `pseudocode`, `language` on `code`,
  `bullet` on `item`, `invert` on `image` and `tikz`, `alt` on `tikz`, `plain_title` on the
  document parts).

### Changed

- The dialect version is now 1.2.0 (`version_code: 3`); 1.1.0 introduced the `math` flag.
- Every environment accepts the generic `skip`/`only` keys, which is what the templates do
  and what wobjects already had.
- Descriptions corrected where they lagged behind the templates: `code` is typeset by
  minted/pygments, `caption` belongs to a Figure, Table or Video float.
- Hover hints use the dialect to their full extent: entry descriptions are Markdown, so
  they can span several paragraphs, and the hint lists the meta-block fields of the
  construct (required ones marked) with a short help text where the dialect provides one.
  The dialect therefore documents keys such as `aspect` (default `16x9`) or `nonumber`
  next to the field instead of in a YAML comment.
- README: the *Semantic Highlighting* section no longer claims the server highlights only
  meta-blocks. It now documents anonymous (indented) math blocks as the second construct
  that a client-side TextMate grammar cannot recognise, and the `math: true` requirement
  that goes with it.

### Requirements

- Anonymous math highlighting and the meta-block field list in hover hints require `wuff`
  1.3.0 or newer. With an older `wuff` the dialect keys it does not know are ignored and
  the server behaves as before.
- The server requires Python 3.10 or newer (the README said 3.8), following `wuff` 1.3.0,
  which dropped 3.8 and 3.9 because both are past end of life.
