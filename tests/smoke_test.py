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


def request(method, params):
    request_id = send(method, params)
    while True:
        message = receive()
        if message.get("method") in ("window/showMessage", "window/logMessage"):
            if message["params"]["type"] == 1:  # MessageType.Error
                fail(f"server error: {message['params']['message']}")
        elif message.get("id") == request_id:
            if "error" in message:
                fail(f"{method}: {message['error']}")
            if not message.get("result"):
                fail(f"{method}: empty result")
            print(f"ok  {method}")
            return message["result"]


def position_of(text):
    lines = DOCUMENT.read_text().splitlines()
    line = next(i for i, content in enumerate(lines) if text in content)
    return {"line": line, "character": lines[line].index(text) + 1}


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

send("shutdown", None)
send("exit", None, notification=True)
if server.wait(timeout=10) != 0:
    fail(f"the server exited with code {server.returncode}")
print("smoke test passed")
