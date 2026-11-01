import os
import re
from pathlib import Path
from typing import Optional
from urllib.parse import unquote, urlparse

# the bundled dialect uses bibliography references, which wuff knows since 1.4.0
MINIMUM_WUFF = (1, 4, 0)


def get_absolute_path(relative_path: str):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(script_dir, relative_path)


def uri_to_path(uri: str) -> Path:
    """Converts a URI to a Path object, with handling for Windows paths."""
    path = urlparse(uri).path
    path = unquote(path)

    # If running on Windows and the path contains a colon (drive letter), remove the leading '/'
    if ":" in path:
        path = path.lstrip("/")

    return Path(path)


def wuff_version_error(version: Optional[str]) -> Optional[str]:
    """The message for the user when the installed wuff is too old, None when it is new enough.

    `version` is None for a wuff without package metadata (a development build); it is trusted.
    """
    if version is None:
        return None
    numbers = tuple(int(number) for number in re.findall(r"\d+", version)[:3])
    if numbers >= MINIMUM_WUFF:
        return None
    minimum = ".".join(str(number) for number in MINIMUM_WUFF)
    return (f"WooWoo: wuff {version} is too old; this server needs {minimum} or newer. "
            "Run: pip install -U wuff")
