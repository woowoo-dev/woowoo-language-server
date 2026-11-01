"""The server needs wuff 1.4.0 (bibliography references in the dialect). An older wuff gets a
clear message instead of a crash.

    python -m pytest tests/test_version_check.py
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
