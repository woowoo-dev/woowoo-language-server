"""When the server cannot start (an old wuff, a broken dialect), the user gets one clear message
instead of a crash or silence.

    python -m pytest tests/test_startup.py
"""

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

from utils import wuff_version_error  # noqa: E402


def test_old_wuff_message():
    message = wuff_version_error("1.3.0")
    assert "1.3.0" in message
    assert "pip install -U wuff" in message


def test_new_enough_wuff():
    assert wuff_version_error("1.4.0") is None
    assert wuff_version_error("1.10.0") is None
    assert wuff_version_error("2.0.0rc1") is None


def test_unknown_wuff_version():
    # a development build without package metadata
    assert wuff_version_error(None) is None


def test_broken_dialect_message(tmp_path, monkeypatch):
    from lsprotocol.types import ClientCapabilities, InitializeParams, WorkspaceFolder
    from woowoo_language_server import WooWooLanguageServer

    bundled = pathlib.Path(__file__).resolve().parent.parent / "dialects" / "fit_math.yaml"
    dialect = tmp_path / "broken.yaml"
    dialect.write_text(bundled.read_text().replace("target: bibliography", "target: bibliograhpy"))

    server = WooWooLanguageServer("WooWoo Language Server", "test")
    messages = []
    monkeypatch.setattr(server, "show_message", lambda message, msg_type=None: messages.append(message))
    server.initialize(InitializeParams(
        capabilities=ClientCapabilities(),
        workspace_folders=[WorkspaceFolder(uri=tmp_path.as_uri(), name="workspace")],
        initialization_options={"dialectFilePath": str(dialect)},
    ))

    assert not server.ready
    assert len(messages) == 1
    assert str(dialect) in messages[0] and "Unknown reference target 'bibliograhpy'" in messages[0]
