import json
import zlib
import base64
import struct


def encode_evo_payload(data):
    raw = json.dumps(data, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    compressed = zlib.compress(raw)
    payload = struct.pack(">I", len(raw)) + compressed
    return base64.b64encode(payload).decode("ascii").rstrip("=")
