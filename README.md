# WooWoo Language Server

The `woowoo-language-server` is an implementation of the [Language Server Protocol](https://microsoft.github.io/language-server-protocol/) for the WooWoo language.
It uses the [pygls](https://github.com/openlawlibrary/pygls) LSP framework and the [wuff](https://github.com/Magmi183/wuff) Python package, written in C++, as backend for analysis.

### Requirements

- `Python >=3.8`
- `wuff` Python package [(available on PyPI)](https://pypi.org/project/wuff/)
  - `pip install wuff`


## Dialect

As the language support in WooWoo is highly dependent on the dialect which is being used by the author, the dialect has to be specified in the initialization stage. More specifically, the server expects `dialectFilePath` field in the `InitializeParams` parameters sent by the client. The value of the field should be an absolute path to the dialect file. If a dialect is not specified by this way, the server defaults to using the `FIT-Math` dialect, which is defined in [dialects/fit_math.yaml](dialects/fit_math.yaml) file.

## Features

The language server provides the following features.

### Hover

- **Hints for dialect-specific keywords**
  - types of document parts, environments, wobjects

### Code Linting

- **Syntax error detection**

### Auto-completion

- **References**
  - where possible for inner environments, suggest possible references
  - dialect-specific
- **`.include` statement** 
  - auto-complete the `.include` statement
  - suggest files to include (`.woo` files from the same _project_)

### Code Folding

- **Region folding** of document parts, blocks, and wobjects 

### Find References

- **Find All References** of any referencable meta-block field

### Go to Definition

- **Go to definition** of any referencable meta-block field.
  - can be executed on referencing short inner environment, environment shorthands or referencing meta-block fields
- **Go to file** included from the `.include` statement

### Symbol Renaming

- **Project-wide rename** of symbols
  - can be executed on any referencable meta-block field to rename all its references
  - similar to _find all references_, but in addition, it performs the rename

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
