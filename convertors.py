from typing import Optional
from urllib.parse import unquote

from lsprotocol.types import (
    CompletionItem,
    CompletionItemKind,
    CompletionParams,
    Diagnostic,
    DiagnosticSeverity,
    FoldingRange,
    FoldingRangeKind,
    InsertTextFormat,
    Location,
    MarkupContent,
    MarkupKind,
    Position,
    Range,
    TextDocumentPositionParams,
    TextEdit,
    WorkspaceEdit,
)
from wuff import CompletionContext as WuffCompletionContext
from wuff import CompletionItem as WuffCompletionItem
from wuff import CompletionItemKind as WuffCompletionItemKind
from wuff import CompletionParams as WuffCompletionParams
from wuff import CompletionTriggerKind as WuffCompletionTriggerKind
from wuff import Diagnostic as WuffDiagnostic
from wuff import DiagnosticSeverity as WuffDiagnosticSeverity
from wuff import FoldingRange as WuffFoldingRange
from wuff import InsertTextFormat as WuffInsertTextFormat
from wuff import Location as WuffLocation
from wuff import Position as WuffPosition
from wuff import Range as WuffRange
from wuff import TextDocumentIdentifier as WuffTextDocumentIdentifier
from wuff import TextDocumentPositionParams as WuffTextDocumentPositionParams
from wuff import TextEdit as WuffTextEdit
from wuff import WorkspaceEdit as WuffWorkspaceEdit


def wuff_completion_item_to_ls(wuff_item: WuffCompletionItem) -> CompletionItem:
    item = CompletionItem(label=wuff_item.label)
    if wuff_item.kind is not None:
        # looked up here, not at import: an old wuff without `Reference` must not stop the server from starting
        kinds = {
            WuffCompletionItemKind.Snippet: CompletionItemKind.Snippet,
            WuffCompletionItemKind.Text: CompletionItemKind.Text,
            WuffCompletionItemKind.Reference: CompletionItemKind.Reference,
        }
        item.kind = kinds.get(wuff_item.kind, CompletionItemKind.Text)
    if wuff_item.insertTextFormat is not None:
        item.insert_text_format = (InsertTextFormat.Snippet if wuff_item.insertTextFormat == WuffInsertTextFormat.Snippet
                                   else InsertTextFormat.PlainText)
    item.insert_text = wuff_item.insertText
    item.detail = wuff_item.detail
    if wuff_item.documentation:
        item.documentation = MarkupContent(kind=MarkupKind.Markdown, value=wuff_item.documentation)
    if wuff_item.text_edit is not None:
        item.text_edit = wuff_text_edit_to_ls(wuff_item.text_edit)
    return item


def wuff_diagnostic_to_ls(wuff_diagnostic: WuffDiagnostic) -> Diagnostic:
    # Convert start and end positions
    start_position = Position(
        line=wuff_diagnostic.range.start.line,
        character=wuff_diagnostic.range.start.character,
    )
    end_position = Position(
        line=wuff_diagnostic.range.end.line,
        character=wuff_diagnostic.range.end.character,
    )
    diagnostic_range = Range(start=start_position, end=end_position)

    severity = None
    if wuff_diagnostic.severity:
        severity_map = {
            WuffDiagnosticSeverity.Error: DiagnosticSeverity.Error,
            WuffDiagnosticSeverity.Warning: DiagnosticSeverity.Warning,
            WuffDiagnosticSeverity.Information: DiagnosticSeverity.Information,
            WuffDiagnosticSeverity.Hint: DiagnosticSeverity.Hint,
        }
        severity = severity_map.get(wuff_diagnostic.severity, None)

    # Construct and return the LSP Diagnostic object
    return Diagnostic(
        range=diagnostic_range,
        message=wuff_diagnostic.message,
        severity=severity,
        source=wuff_diagnostic.source,
    )


def wuff_workspace_edit_to_ls(wuff_workspace_edit: WuffWorkspaceEdit) -> WorkspaceEdit:
    ls_changes = {}
    changes = wuff_workspace_edit.changes
    for uri, change_list in changes.items():
        ls_change_list = [wuff_text_edit_to_ls(te) for te in change_list]
        ls_changes[uri] = ls_change_list
    return WorkspaceEdit(changes=ls_changes)


def wuff_text_edit_to_ls(wuff_text_edit: WuffTextEdit) -> TextEdit:
    return TextEdit(wuff_range_to_ls(wuff_text_edit.range), wuff_text_edit.new_text)


def wuff_folding_range_to_ls(wuff_folding_range: WuffFoldingRange) -> FoldingRange:
    return FoldingRange(
        start_line=wuff_folding_range.start_line,
        start_character=wuff_folding_range.start_character,
        end_line=wuff_folding_range.end_line,
        end_character=wuff_folding_range.end_character,
        kind=FoldingRangeKind(wuff_folding_range.kind),
    )


def wuff_location_to_ls(wuff_location: WuffLocation) -> Optional[Location]:
    if wuff_location.uri == "":
        return None

    return Location(uri=wuff_location.uri, range=wuff_range_to_ls(wuff_location.range))


def wuff_position_to_ls(wuff_position: WuffPosition) -> Position:
    return Position(line=wuff_position.line, character=wuff_position.character)


def wuff_range_to_ls(wuff_range: WuffRange) -> Range:
    return Range(
        start=wuff_position_to_ls(wuff_range.start),
        end=wuff_position_to_ls(wuff_range.end),
    )


def text_document_position_ls_to_wuff(
    ls_params: TextDocumentPositionParams,
) -> WuffTextDocumentPositionParams:
    doc_uri = unquote(ls_params.text_document.uri)

    return WuffTextDocumentPositionParams(
        WuffTextDocumentIdentifier(doc_uri),
        WuffPosition(ls_params.position.line, ls_params.position.character),
    )


def completion_params_ls_to_wuff(ls_params: CompletionParams) -> WuffCompletionParams:
    doc_uri = unquote(ls_params.text_document.uri)
    line = ls_params.position.line
    character = ls_params.position.character

    text_document = WuffTextDocumentIdentifier(doc_uri)
    position = WuffPosition(line, character)

    context = None
    if hasattr(ls_params, "context") and ls_params.context is not None:
        trigger_kind = ls_params.context.trigger_kind
        trigger_character = (
            ls_params.context.trigger_character
            if hasattr(ls_params.context, "trigger_character")
            else None
        )

        if trigger_kind == 1:
            my_trigger_kind = WuffCompletionTriggerKind.Invoked
        elif trigger_kind == 2:
            my_trigger_kind = WuffCompletionTriggerKind.TriggerCharacter
        elif trigger_kind == 3:
            my_trigger_kind = WuffCompletionTriggerKind.TriggerForIncompleteCompletions
        else:
            raise ValueError("Unknown trigger kind")

        context = WuffCompletionContext(my_trigger_kind, trigger_character)

    return WuffCompletionParams(text_document, position, context)
