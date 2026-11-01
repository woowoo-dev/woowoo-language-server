"""Smoke test: starts the server over stdio like an editor does and checks that the main
requests return a result.

    python tests/smoke_test.py               # starts `python server.py`
    python tests/smoke_test.py CMD [ARG...]  # starts another command, e.g. the VS Code bundle

Exits with code 1 when the server crashes, reports an error or returns an empty result.
"""

import json
import pathlib
import subprocess
import sys

TESTS_DIR = pathlib.Path(__file__).resolve().parent
WORKSPACE = TESTS_DIR / "workspace"
DOCUMENT = WORKSPACE / "sample.woo"

command = sys.argv[1:] or [sys.executable, str(TESTS_DIR.parent / "server.py")]
# stderr is inherited, so a traceback of the server ends up in the output
server = subprocess.Popen(command, cwd=WORKSPACE, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
last_id = 0


def fail(reason):
    print(f"FAIL: {reason}", file=sys.stderr)
    server.kill()
    sys.exit(1)


def send(method, params, notification=False):
    global last_id
    message = {"jsonrpc": "2.0", "method": method, "params": params}
    if not notification:
        last_id += 1
        message["id"] = last_id
    body = json.dumps(message).encode()
    server.stdin.write(b"Content-Length: %d\r\n\r\n%s" % (len(body), body))
    server.stdin.flush()
    return last_id


def receive():
    length = 0
    while True:
        line = server.stdout.readline()
        if not line:
            fail("the server exited")
        line = line.strip()
        if not line:
            break
        name, _, value = line.partition(b":")
        if name.lower() == b"content-length":
            length = int(value)
    return json.loads(server.stdout.read(length))


diagnostics = {}  # the last published diagnostics by document URI


def request(method, params, expect_empty=False):
    request_id = send(method, params)
    while True:
        message = receive()
        if message.get("method") in ("window/showMessage", "window/logMessage"):
            if message["params"]["type"] == 1:  # MessageType.Error
                fail(f"server error: {message['params']['message']}")
        elif message.get("method") == "textDocument/publishDiagnostics":
            diagnostics[message["params"]["uri"]] = message["params"]["diagnostics"]
        elif message.get("id") == request_id:
            if "error" in message:
                fail(f"{method}: {message['error']}")
            if bool(message.get("result")) == expect_empty:
                fail(f"{method}: {'a' if expect_empty else 'an empty'} result")
            print(f"ok  {method}")
            return message["result"]


def position_of(text, offset=1):
    lines = DOCUMENT.read_text().splitlines()
    line = next(i for i, content in enumerate(lines) if text in content)
    return {"line": line, "character": lines[line].index(text) + offset}


def check(condition, reason):
    if not condition:
        fail(reason)


uri = DOCUMENT.as_uri()
document = {"textDocument": {"uri": uri}}

request("initialize", {
    "processId": None,
    "rootUri": WORKSPACE.as_uri(),
    "workspaceFolders": [{"uri": WORKSPACE.as_uri(), "name": "workspace"}],
    "capabilities": {},
    "initializationOptions": {"dialectFilePath": ""},  # the bundled FIT-Math dialect
})
send("initialized", {}, notification=True)
send("textDocument/didOpen", {"textDocument": {
    "uri": uri, "languageId": "woowoo", "version": 1, "text": DOCUMENT.read_text()}},
    notification=True)

request("textDocument/hover", {**document, "position": position_of(".equation")})
request("textDocument/semanticTokens/full", document)
request("textDocument/foldingRange", document)
request("textDocument/definition", {**document, "position": position_of("ch-smoke has")})

# the bibliography of the Woofile: references.bib
completion = request("textDocument/completion", {**document, "position": position_of("Smoke_2026", 0),
                                                 "context": {"triggerKind": 1}})
check(any(item["label"] == "Smoke_2026" for item in completion["items"]), "no Smoke_2026 in the completion")
cited = request("textDocument/definition", {**document, "position": position_of("Smoke_2026")})
check(cited["uri"].endswith("references.bib"), f"definition of the citation: {cited}")
hover = request("textDocument/hover", {**document, "position": position_of("Smoke_2026")})
check("Smoke Testing" in hover["contents"]["value"], f"hover of the citation: {hover}")
request("textDocument/prepareRename", {**document, "position": position_of("ch-smoke has")})
request("textDocument/prepareRename", {**document, "position": position_of("Smoke_2026")}, expect_empty=True)
warnings = [d["message"] for d in diagnostics.get(uri, []) if d.get("severity") == 2]
check(warnings == ["'Smoke_2025' is not in the bibliography (references.bib)"], f"warnings: {warnings}")
print("ok  bibliography")

send("shutdown", None)
send("exit", None, notification=True)
if server.wait(timeout=10) != 0:
    fail(f"the server exited with code {server.returncode}")
print("smoke test passed")
