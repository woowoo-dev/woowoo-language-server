# WooWoo Language Server

The `woowoo-language-server` is an implementation of the [Language Server Protocol](https://microsoft.github.io/language-server-protocol/) for the WooWoo language.
It uses the [pygls](https://github.com/openlawlibrary/pygls) LSP framework and the [wuff](https://github.com/woowoo-dev/wuff) Python package, written in C++, as backend for analysis.

### Requirements

- `Python >=3.10`
- `wuff` 1.4.0 or newer [(available on PyPI)](https://pypi.org/project/wuff/); with an older
  one the server shows an error asking for `pip install -U wuff`
- `pygls` 1.3.0 and `lsprotocol` 2023.0.1 — the versions the VS Code extension bundles

All of them are pinned in [`requirements.txt`](requirements.txt):

```sh
pip install -r requirements.txt
python server.py
```

### Testing

`tests/smoke_test.py` starts the server over stdio and checks that hover, semantic tokens,
folding, go to definition and the bibliography features answer without errors, using the
small project in `tests/workspace`. `tests/test_startup.py` checks the messages for an
old `wuff` and a broken dialect:

```sh
python tests/smoke_test.py
python -m pytest tests/test_startup.py
```

The *Test* workflow runs both on every pull request with Python 3.10 to 3.15.


## Dialect

As the language support in WooWoo is highly dependent on the dialect which is being used by the author, the dialect has to be specified in the initialization stage. More specifically, the server expects `dialectFilePath` field in the `InitializeParams` parameters sent by the client. The value of the field should be an absolute path to the dialect file. If a dialect is not specified by this way, the server defaults to using the `FIT-Math` dialect, which is defined in [dialects/fit_math.yaml](dialects/fit_math.yaml) file.

## Features

The language server provides the following features.

### Bibliography

A project's `Woofile` can name its BibTeX file:

```yaml
builder:
  bibtex: references.bib
```

For citations (`.cite:Trefethen_Bau_1997` in the FIT math dialect) the server then completes the
keys (with the authors, year and title next to each), goes to the entry in the `.bib` file,
finds all citations of a key, shows the entry on hover and warns about keys that are not in the
bibliography. Changes to the `Woofile` or the `.bib` file are picked up without a restart.
Which constructs cite is defined by the dialect (`references: - target: bibliography`).

### Hover

- **Hints for dialect-specific keywords**
  - types of document parts, environments, wobjects
  - the hint is Markdown: the description from the dialect, followed by the meta-block
    fields the construct accepts (required ones are marked, with a short help text where
    the dialect provides one), and a note when the fragile form (`!tikz:`) is needed
- **Citations**: the title, authors, year and type of the bibliography entry

### Code Linting

- **Syntax error detection**
- **Unknown citation keys** (a warning)

### Auto-completion

- **References**
  - where possible for inner environments, suggest possible references
  - dialect-specific
  - also with Ctrl+Space inside a value already typed (`.reference:sec-`)
  - citation keys from the project's bibliography
- **`.include` statement** 
  - auto-complete the `.include` statement
  - suggest files to include (`.woo` files from the same _project_)

### Code Folding

- **Region folding** of document parts, blocks, and wobjects 

### Find References

- **Find All References** of any referencable meta-block field, or from any reference to it
  (`.reference:x`, `"…"#x`, `.cite:key`)

### Go to Definition

- **Go to definition** of any referencable meta-block field.
  - can be executed on referencing short inner environment, environment shorthands or referencing meta-block fields
  - a citation opens its entry in the `.bib` file
- **Go to file** included from the `.include` statement

### Symbol Renaming

- **Project-wide rename** of symbols
  - can be executed on any referencable meta-block field or any reference to it, to rename all its references
  - similar to _find all references_, but in addition, it performs the rename
  - citation keys cannot be renamed (the editor says so): rename the key in the `.bib` file and use
    _find all references_ and the warnings to update the citations

### File Renaming

- **Project-wide rename** of files
  - refactors all `.include` statements to reflect the filename changes

### Semantic Highlighting

The server is capable of handling all aspects of highlighting, but it deliberately limits this
functionality to constructs that a client-side TextMate grammar cannot recognise. Everything else is
left to the grammar, which is faster.

- **Meta-blocks**, which are highly dependent on context.
- **Anonymous (indented) math blocks.** In the FIT math dialect an indented block is an unnumbered
  equation, but a TextMate rule cannot express "indented deeper than the enclosing block", so the
  grammar has to treat such a line as ordinary text. The server reports the LaTeX elements of the
  block with standard token types mirroring the grammar's own math scopes, so both render alike and
  no client configuration is needed. This requires a dialect that marks the math environments
  (`equation`, `align`, `gather`) with `math: true`.

## Changelog

See [CHANGELOG.md](CHANGELOG.md).
