# AGENTS.md

The WooWoo Language Server: a thin [pygls](https://github.com/openlawlibrary/pygls) layer over
[wuff](https://github.com/woowoo-dev/wuff), the C++ analysis engine from PyPI. The
[VS Code extension](https://github.com/woowoo-dev/vscode-woowoo-lsp) bundles this repository as
a git submodule (`bundled/tool/woowoo_pygls`) and starts `server.py` from there.

## Run and test

```sh
pip install -r requirements.txt
python tests/smoke_test.py                     # starts the server and checks the main LSP requests
python -m pytest tests/test_version_check.py   # the message for a too old wuff (needs pytest)
```

The *Test* workflow runs both on every PR with Python 3.10 to 3.15. `tests/workspace` is a small
project (a `Woofile` with a bibliography) that the smoke test opens.

## Layout

- `server.py`: registers the LSP features; `woowoo_language_server.py` passes each of them to
  `wuff.WooWooAnalyzer`.
- `convertors.py`: conversion between `lsprotocol` and `wuff` types.
- `constants.py`: semantic token types and modifiers (`wuff` returns indices into these lists).
- `dialects/fit_math.yaml`: the default FIT-Math dialect, used when the client sends no
  `dialectFilePath`.

## Rules

- The analysis belongs in `wuff`; this server only converts between LSP and `wuff` types.
- `pygls` 1.3.0 and `lsprotocol` 2023.0.1 are the versions the VS Code extension bundles (its
  `requirements.in`). Change them in both repositories at once. pygls 2 has a different API
  and needs a port of the server.
- A feature that needs a newer `wuff` raises the minimum in `requirements.txt` and
  `MINIMUM_WUFF` in `utils.py` (users who only run `pip install wuff` may still have an old
  one), and works only once that `wuff` is on PyPI.
- When the dialect changes, copy it to `tests/files/fit_math.yaml` in wuff.
- Modules import each other at top level (`from constants import ...`); the VS Code extension
  puts this folder on `sys.path` for that.
- Users get a change only after the VS Code extension moves its submodule to it and makes a
  release. Record user-visible changes under `## [Unreleased]` in `CHANGELOG.md`.
- Do not create releases or tags; that is up to a maintainer.
