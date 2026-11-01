import functools
import importlib.metadata
import logging
from typing import List, Optional
from urllib.parse import unquote

from lsprotocol.types import (
    CompletionList,
    CompletionParams,
    DefinitionParams,
    DeleteFilesParams,
    FoldingRange,
    FoldingRangeParams,
    Hover,
    InitializeParams,
    Location,
    MarkupContent,
    MarkupKind,
    MessageType,
    PrepareRenameParams,
    Range,
    ReferenceParams,
    RenameFilesParams,
    RenameParams,
    SemanticTokens,
    SemanticTokensParams,
    TextDocumentPositionParams,
    WorkspaceEdit,
    WorkspaceFolder,
)
from pygls.server import LanguageServer
from pygls.workspace import TextDocument
from wuff import (
    DefinitionParams as WuffDefinitionParams,
)
from wuff import (
    Position as WuffPosition,
)
from wuff import (
    ReferenceParams as WuffReferenceParams,
)
from wuff import (
    RenameParams as WuffRenameParams,
)
from wuff import (
    TextDocumentIdentifier as WuffTextDocumentIdentifier,
)
from wuff import (
    WooWooAnalyzer,
)

import utils
from constants import token_modifiers, token_types
from convertors import (
    completion_params_ls_to_wuff,
    wuff_completion_item_to_ls,
    wuff_diagnostic_to_ls,
    wuff_folding_range_to_ls,
    wuff_location_to_ls,
    wuff_range_to_ls,
    wuff_workspace_edit_to_ls, text_document_position_ls_to_wuff,
)


def when_ready(empty=lambda: None):
    """Answer with `empty()` instead of asking wuff when the server could not start (an old wuff)."""
    def decorate(method):
        @functools.wraps(method)
        def answer(self, *args, **kwargs):
            if not self.ready:
                return empty()
            return method(self, *args, **kwargs)
        return answer
    return decorate


class WooWooLanguageServer(LanguageServer):
    def __init__(self, name: str, version: str):
        self.logger = logging.getLogger(__name__)
        self.logger.debug("Constructing WooWooLanguageServer.")
        super().__init__(name, version)
        self.analyzer = self.initialize_analyzer()
        self.ready = False

    def initialize(self, params: InitializeParams):
        try:
            wuff_version = importlib.metadata.version("wuff")
        except importlib.metadata.PackageNotFoundError:
            wuff_version = None
        error = utils.wuff_version_error(wuff_version)
        if error:
            self.logger.error(error)
            self.show_message(error, MessageType.Error)
            return

        if len(params.workspace_folders) != 1:
            self.logger.error(
                "Exactly one workspace has to be opened. No other options are supported for now."
            )

        # default: "" --> FIT-Math
        dialect_path = params.initialization_options.get('dialectFilePath', "")
        self.set_dialect(dialect_path)

        self.load_workspace(params.workspace_folders[0])
        self.ready = True

    def initialize_analyzer(self) -> WooWooAnalyzer:
        analyzer = WooWooAnalyzer()
        analyzer.set_token_types(token_types)
        analyzer.set_token_modifiers(token_modifiers)
        return analyzer

    def load_workspace(self, workspace: WorkspaceFolder):
        uri = unquote(workspace.uri)
        self.analyzer.load_workspace(uri)

    def set_dialect(self, dialect_file_path: str) -> None:
        if dialect_file_path != "":
            self.analyzer.set_dialect(dialect_file_path)
        else:
            self.analyzer.set_dialect(utils.get_absolute_path("dialects/fit_math.yaml"))

    @when_ready()
    def diagnose(self, doc_uri: str):
        doc_uri = unquote(doc_uri)
        diagnostics = self.analyzer.diagnose(WuffTextDocumentIdentifier(doc_uri))
        lsdiagnostics = []
        for diagnostic in diagnostics:
            lsdiagnostic = wuff_diagnostic_to_ls(diagnostic)
            lsdiagnostic.source = self.name
            lsdiagnostics.append(lsdiagnostic)

        self.publish_diagnostics(doc_uri, lsdiagnostics)

    @when_ready()
    def go_to_definition(self, params: DefinitionParams) -> Optional[Location]:
        wuff_params = WuffDefinitionParams(
            WuffTextDocumentIdentifier(params.text_document.uri),
            WuffPosition(params.position.line, params.position.character),
        )

        return wuff_location_to_ls(self.analyzer.go_to_definition(wuff_params))

    @when_ready(list)
    def references(self, params: ReferenceParams) -> List[Location]:
        wuff_params = WuffReferenceParams(
            WuffTextDocumentIdentifier(params.text_document.uri),
            WuffPosition(params.position.line, params.position.character),
            params.context.include_declaration,
        )

        return [
            wuff_location_to_ls(loc) for loc in self.analyzer.references(wuff_params)
        ]

    @when_ready()
    def rename(self, params: RenameParams) -> WorkspaceEdit:
        wuff_params = WuffRenameParams(
            WuffTextDocumentIdentifier(params.text_document.uri),
            WuffPosition(params.position.line, params.position.character),
            params.new_name,
        )

        return wuff_workspace_edit_to_ls(self.analyzer.rename(wuff_params))

    @when_ready()
    def prepare_rename(self, params: PrepareRenameParams) -> Optional[Range]:
        result = self.analyzer.prepare_rename(text_document_position_ls_to_wuff(params))
        return wuff_range_to_ls(result) if result is not None else None

    @when_ready()
    def open_document(self, document_uri: str):
        self.analyzer.open_document(WuffTextDocumentIdentifier(unquote(document_uri)))

    @when_ready()
    def rename_files(self, params: RenameFilesParams) -> WorkspaceEdit:
        renames = []
        # build parameters for wuff
        for file_rename in params.files:
            renames.append((file_rename.old_uri, file_rename.new_uri))

        return wuff_workspace_edit_to_ls(self.analyzer.rename_files(renames))

    @when_ready()
    def did_delete_files(self, params: DeleteFilesParams) -> None:
        deleted_files_uris = [file_delete.uri for file_delete in params.files]
        self.analyzer.did_delete_files(deleted_files_uris)

    @when_ready()
    def document_did_change(self, document: TextDocument) -> None:
        self.analyzer.document_did_change(
            WuffTextDocumentIdentifier(document.uri), document.source
        )

    @when_ready(lambda: CompletionList(is_incomplete=False, items=[]))
    def completion(self, params: CompletionParams) -> CompletionList:
        params = completion_params_ls_to_wuff(params)
        completion_items_result = self.analyzer.complete(params)
        items = [wuff_completion_item_to_ls(item) for item in completion_items_result]
        return CompletionList(is_incomplete=False, items=items)

    @when_ready()
    def hover(self, params: TextDocumentPositionParams) -> Hover:
        result = self.analyzer.hover(text_document_position_ls_to_wuff(params))
        content = MarkupContent(MarkupKind.Markdown, value=result)
        return Hover(contents=content)

    @when_ready(lambda: SemanticTokens(data=[]))
    def semantic_tokens(self, params: SemanticTokensParams) -> SemanticTokens:
        data = self.analyzer.semantic_tokens(
            WuffTextDocumentIdentifier(unquote(params.text_document.uri))
        )
        return SemanticTokens(data=data)

    @when_ready(list)
    def folding_range(self, params: FoldingRangeParams) -> List[FoldingRange]:
        folding_ranges = self.analyzer.folding_ranges(
            WuffTextDocumentIdentifier(unquote(params.text_document.uri))
        )
        return [wuff_folding_range_to_ls(item) for item in folding_ranges]
