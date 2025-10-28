from pathlib import Path
from flask import send_file

BASE_LOG_DIR = Path(__file__).resolve().parent.parent / "logs"

LOG_FILES = {
    "supervisor": BASE_LOG_DIR / "supervisor.log",
    "app": BASE_LOG_DIR / "app.txt",
    "critical": BASE_LOG_DIR / "critical_errors.txt"
}

def get_log_file(log_type: str):
    path = LOG_FILES.get(log_type)
    if path and path.exists():
        return send_file(str(path), as_attachment=True)
    return ("Arquivo de log não encontrado", 404)
