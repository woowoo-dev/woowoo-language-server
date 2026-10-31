import logging
from typing import List, Optional

from lsprotocol.types import (
    INITIALIZE,
    INITIALIZED,
    TEXT_DOCUMENT_COMPLETION,
    TEXT_DOCUMENT_DEFINITION,
    TEXT_DOCUMENT_DID_CHANGE,
    TEXT_DOCUMENT_DID_OPEN,
    TEXT_DOCUMENT_DID_SAVE,
    TEXT_DOCUMENT_FOLDING_RANGE,
    TEXT_DOCUMENT_HOVER,
    TEXT_DOCUMENT_REFERENCES,
    TEXT_DOCUMENT_RENAME,
    TEXT_DOCUMENT_SEMANTIC_TOKENS_FULL,
    WORKSPACE_DID_DELETE_FILES,
    WORKSPACE_WILL_RENAME_FILES,
    CompletionList,
    CompletionOptions,
    CompletionParams,
    DefinitionParams,
    DeleteFilesParams,
    DidChangeTextDocumentParams,
    DidOpenTextDocumentParams,
    DidSaveTextDocumentParams,
    FoldingRange,
    FoldingRangeParams,
    Hover,
    InitializedParams,
    InitializeParams,
    Location,
    ReferenceParams,
    RenameFilesParams,
    RenameParams,
    SemanticTokens,
    SemanticTokensLegend,
    SemanticTokensParams,
    TextDocumentPositionParams,
    WorkspaceEdit,
)

from constants import no_filter, token_modifiers, token_types, trigger_characters
from woowoo_language_server import WooWooLanguageServer

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

SERVER = WooWooLanguageServer("WooWoo Language Server", "v1.2.0")


@SERVER.feature(INITIALIZE)
def initiliaze(ls: WooWooLanguageServer, params: InitializeParams) -> None:
    logger.debug("[INITIALIZE]")

    ls.initialize(params)


@SERVER.feature(INITIALIZED)
def initiliazed(_ls: WooWooLanguageServer, params: InitializedParams) -> None:
    logger.debug("[INITIALIZED] Connection was established.")


@SERVER.feature(TEXT_DOCUMENT_DID_OPEN)
def did_open(ls: WooWooLanguageServer, params: DidOpenTextDocumentParams) -> None:
    logger.debug("[TEXT_DOCUMENT_DID_OPEN] SERVER.feature called")

    ls.open_document(params.text_document.uri)
    ls.diagnose(params.text_document.uri)


@SERVER.feature(TEXT_DOCUMENT_DID_SAVE)
def did_save(ls: WooWooLanguageServer, params: DidSaveTextDocumentParams) -> None:
    logger.debug("[TEXT_DOCUMENT_DID_SAVE] SERVER.feature called")

    ls.diagnose(params.text_document.uri)


@SERVER.feature(WORKSPACE_WILL_RENAME_FILES, no_filter)
def did_rename_files(
    ls: WooWooLanguageServer, params: RenameFilesParams
) -> WorkspaceEdit:
    logger.debug("[WORKSPACE_WILL_RENAME_FILES] notification received")

    return ls.rename_files(params)


@SERVER.feature(WORKSPACE_DID_DELETE_FILES, no_filter)
def did_delete_files(ls: WooWooLanguageServer, params: DeleteFilesParams) -> None:
    logger.debug("[WORKSPACE_DID_DELETE_FILES] notification received")

    ls.did_delete_files(params)


"""
# https://github.com/openlawlibrary/pygls/issues/376

@SERVER.feature(WORKSPACE_DID_CHANGE_WATCHED_FILES, DidChangeWatchedFilesRegistrationOptions(
    watchers=[FileSystemWatcher(glob_pattern="**/*")]
))
def did_change_watched_files(ls: WooWooLanguageServer, params: DidChangeWatchedFilesParams):
    
    pass
"""


@SERVER.feature(TEXT_DOCUMENT_DID_CHANGE)
def did_change(ls: WooWooLanguageServer, params: DidChangeTextDocumentParams) -> None:
    logger.debug("[TEXT_DOCUMENT_DID_CHANGE] SERVER.feature called")

    doc = ls.workspace.get_text_document(params.text_document.uri)
    ls.document_did_change(doc)
    ls.diagnose(doc.uri)


@SERVER.feature(
    TEXT_DOCUMENT_COMPLETION, CompletionOptions(trigger_characters=trigger_characters)
)
def completions(ls: WooWooLanguageServer, params: CompletionParams) -> CompletionList:
    logger.debug("[TEXT_DOCUMENT_COMPLETION] SERVER.feature called")

    return ls.completion(params)


@SERVER.feature(TEXT_DOCUMENT_HOVER)
def on_hover(ls: WooWooLanguageServer, params: TextDocumentPositionParams) -> Hover:
    logger.debug("[TEXT_DOCUMENT_HOVER] SERVER.feature called")

    return ls.hover(params)


@SERVER.feature(
    TEXT_DOCUMENT_SEMANTIC_TOKENS_FULL,
    SemanticTokensLegend(token_types=token_types, token_modifiers=token_modifiers),
)
def semantic_tokens(
    ls: WooWooLanguageServer, params: SemanticTokensParams
) -> SemanticTokens:
    logger.debug("[TEXT_DOCUMENT_SEMANTIC_TOKENS_FULL] SERVER.feature called")

    return ls.semantic_tokens(params)


@SERVER.feature(TEXT_DOCUMENT_DEFINITION)
def definition(
    ls: WooWooLanguageServer, params: DefinitionParams
) -> Optional[Location]:
    logger.debug("[TEXT_DOCUMENT_DEFINITION] SERVER.feature called")

    return ls.go_to_definition(params)


@SERVER.feature(TEXT_DOCUMENT_REFERENCES)
def references(ls: WooWooLanguageServer, params: ReferenceParams) -> List[Location]:
    logger.debug("[TEXT_DOCUMENT_REFERENCES] SERVER.feature called")

    return ls.references(params)


@SERVER.feature(TEXT_DOCUMENT_RENAME)
def rename(ls: WooWooLanguageServer, params: RenameParams) -> WorkspaceEdit:
    logger.debug("[TEXT_DOCUMENT_RENAME] SERVER.feature called")

    return ls.rename(params)


@SERVER.feature(TEXT_DOCUMENT_FOLDING_RANGE)
def folding_range(
    ls: WooWooLanguageServer, params: FoldingRangeParams
) -> List[FoldingRange]:
    logger.debug("[TEXT_DOCUMENT_FOLDING_RANGE] SERVER.feature called")

    return ls.folding_range(params)


def start() -> None:
    SERVER.start_io()


if __name__ == "__main__":
    start()
