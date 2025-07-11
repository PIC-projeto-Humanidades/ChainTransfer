from flask import Blueprint, request, jsonify
from pathlib import Path
import json

monitoring_bp = Blueprint("monitoring", __name__)
LOG_FILE = Path(__file__).resolve().parent.parent / "media_data" / "bundles_log.json"

def load_logs():
    if LOG_FILE.exists():
        with open(LOG_FILE, "r") as f:
            return json.load(f)
    return {}

def save_logs(data):
    with open(LOG_FILE, "w") as f:
        json.dump(data, f, indent=2)

@monitoring_bp.route("/monitoring/feedback", methods=["POST"])
def feedback():
    data = request.get_json()
    if not data or "hash" not in data:
        return jsonify({"error": "Parâmetros inválidos"}), 400

    logs = load_logs()
    logs[data["hash"]] = {
        "status": data.get("status", "ok"),
        "session": data.get("session"),
        "destination_node": data.get("destination_node")
    }
    save_logs(logs)
    return jsonify({"message": "Feedback recebido"}), 200

@monitoring_bp.route("/monitoring/status", methods=["GET"])
def status():
    logs = load_logs()
    return jsonify(logs)
