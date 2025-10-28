from flask import Blueprint, jsonify, abort, send_file
import os

LOGS_DIR = os.path.join(os.path.dirname(__file__), '../logs')
LOG_FILES = {
    'supervisor': 'supervisor.log',
    'app': 'app.txt',
    'critical': 'critical_errors.txt',
    'all': None  # especial: retorna todos
}

logs_bp = Blueprint('logs', __name__)

@logs_bp.route('/preview-log/<log_type>', methods=['GET'])
def preview_log(log_type):
    if log_type == 'all':
        lines = []
        for key in ['supervisor', 'app']:
            file_path = os.path.join(LOGS_DIR, LOG_FILES[key])
            if os.path.isfile(file_path):
                with open(file_path, 'r') as f:
                    content = f.readlines()[-50:]
                    lines.append(f"--- {LOG_FILES[key]} ---\n" + ''.join(content))
        return jsonify({'lines': lines})
    if log_type not in LOG_FILES or LOG_FILES[log_type] is None:
        abort(404, 'Tipo de log inválido.')
    file_path = os.path.join(LOGS_DIR, LOG_FILES[log_type])
    if not os.path.isfile(file_path):
        abort(404, 'Arquivo de log não encontrado.')
    with open(file_path, 'r') as f:
        lines = f.readlines()[-50:]
    return jsonify({'lines': lines})

@logs_bp.route('/download-log/<log_type>', methods=['GET'])
def download_log(log_type):
    if log_type not in LOG_FILES or LOG_FILES[log_type] is None:
        abort(404, 'Tipo de log inválido.')
    file_path = os.path.join(LOGS_DIR, LOG_FILES[log_type])
    if not os.path.isfile(file_path):
        abort(404, 'Arquivo de log não encontrado.')
    return send_file(
        file_path,
        as_attachment=True,
        download_name=LOG_FILES[log_type],
        mimetype='text/plain',
        max_age=0
    )
