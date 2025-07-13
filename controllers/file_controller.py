# controllers/file_controller.py

import os
from flask import Blueprint, request, Response, abort
from pathlib import Path
import mimetypes

file_bp = Blueprint("file", __name__)
MEDIA_DIR = Path(__file__).resolve().parent.parent / "media_data"

@file_bp.route("/file/<path:filename>", methods=["GET"])
def download_file(filename):
    file_path = MEDIA_DIR / filename
    if not file_path.is_file():
        abort(404, description="Arquivo não encontrado.")

    file_size = os.path.getsize(file_path)
    range_header = request.headers.get("Range", None)
    byte1 = 0
    byte2 = None

    if range_header:
        parts = range_header.replace("bytes=", "").split("-")
        if parts[0]:
            byte1 = int(parts[0])
        if len(parts) > 1 and parts[1]:
            byte2 = int(parts[1])

    byte2 = byte2 if byte2 is not None else file_size - 1
    length = byte2 - byte1 + 1

    def generate():
        with open(file_path, "rb") as f:
            f.seek(byte1)
            remaining = length
            chunk_size = 1024 * 1024  # 1 MB
            while remaining > 0:
                read_size = min(chunk_size, remaining)
                data = f.read(read_size)
                if not data:
                    break
                yield data
                remaining -= len(data)

    status_code = 206 if range_header else 200
    mimetype, _ = mimetypes.guess_type(str(file_path))
    headers = {
        "Content-Type": mimetype or "application/octet-stream",
        "Accept-Ranges": "bytes",
        "Content-Length": str(length),
    }
    if range_header:
        headers["Content-Range"] = f"bytes {byte1}-{byte2}/{file_size}"

    return Response(generate(), status_code, headers)
