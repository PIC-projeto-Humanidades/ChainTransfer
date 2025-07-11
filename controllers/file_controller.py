from flask import Blueprint, send_from_directory, abort
from pathlib import Path

file_bp = Blueprint("file", __name__)
MEDIA_DIR = Path(__file__).resolve().parent.parent / "media_data"

@file_bp.route("/file/<path:filename>", methods=["GET"])
def download_file(filename):
    try:
        return send_from_directory(MEDIA_DIR, filename, as_attachment=True)
    except FileNotFoundError:
        abort(404, description="Arquivo não encontrado.")
