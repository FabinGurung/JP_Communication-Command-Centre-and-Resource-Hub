"""Offline fake-CDN regression: never certify a mismatched attachment as an original."""
import ast
import json
import hashlib
import re
import tempfile
from pathlib import Path
from urllib.parse import urlparse

nb=json.loads(Path("ops/discord/A9_CWO_DISCORD_TWO_CHANNEL_DAILY_COLLECTOR_v1.0.ipynb").read_text())
collector_cell = next(cell for cell in nb["cells"] if cell.get("id") == "a9-cwo-c02-collector")
code = "".join(collector_cell["source"])
tree=ast.parse(code)
func=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=="media_archive")

class Response:
    ok=True
    status_code=200
    headers={"Content-Type":"text/html","Content-Length":"10","Content-Encoding":"identity"}
    url="https://cdn.discordapp.com/attachments/example"
    def __enter__(self): return self
    def __exit__(self, *args): return False
    def iter_content(self,chunk_size): yield b"<html>gone"

class RequestStub:
    @staticmethod
    def get(url, stream, timeout, headers):
        assert url.startswith("https://cdn.discordapp.com/")
        assert headers.get("Accept-Encoding")=="identity"
        assert "Authorization" not in headers
        return Response()

def forbidden_upload(*args,**kwargs):
    raise AssertionError("Mismatch must not upload as an original")

env={
    "MAX_ATTACHMENT_BYTES":100*1024*1024, "re":re, "urlparse":urlparse,
    "requests":RequestStub, "children":lambda parent,name:None,
    "progress":lambda m:None, "tempfile":tempfile,
    "hashlib":hashlib, "MediaFileUpload":forbidden_upload,
}
exec(compile(ast.Module(body=[func],type_ignores=[]),"<collector-media-archive>", "exec"),env)
try:
    env["media_archive"]("fake_folder",{"id":"100"},{"id":"200","size":123,
         "filename":"example.jpg","content_type":"image/jpeg",
         "url":"https://cdn.discordapp.com/attachments/example"})
except RuntimeError as ex:
    message=str(ex)
    assert "declared=123" in message
    assert "observed=10" in message
    assert "content_type=text/html" in message
    assert "content_length_header=10" in message
    assert "first16_hex=" in message
    assert "https://" not in message
else:
    raise AssertionError("Mismatched attachment did not fail closed")
print("PASS: CDN mismatched bytes include safe diagnostics and are never uploaded as originals")
